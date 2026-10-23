"""Direct bounded role algorithm and real readonly ControlHub projection checks."""
import asyncio
from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace
from unittest import TestCase
from uuid import uuid4

from app.data_exit.contracts import DataError
from app.data_exit.control import ControlHub
from app.data_exit.files import RootLease
from app.data_exit.q_roles import check_role_capabilities
from app.memory.cleanup_projection import read_projected


def role(oid,name,privileges=(),login=False):
    return dict(oid=oid,rolname=name,privileges=list(privileges),rolcanlogin=login,
        **{k:False for k in ('rolsuper','rolcreatedb','rolcreaterole','rolreplication','rolbypassrls','schema_create','database_create','owns_objects','owns_definers')},control_privileges=[])


def edge(member,target,*,inherit=False,set=False,admin=False):
    return dict(member=member,roleid=target,grantor=4,inherit_option=inherit,set_option=set,admin_option=admin)


class RoleClosureTests(TestCase):
    def setUp(self):
        self.roles=[role(1,'retrolume_data_app',('SELECT','INSERT','UPDATE','DELETE')),
            role(2,'retrolume_data_snapshot',('SELECT',)),role(3,'retrolume_data_restore_loader',('SELECT','INSERT')),
            role(4,'retrolume_data_owner'),role(5,'existing_snapshot_login',('SELECT',),True),role(6,'bridge1'),role(7,'bridge2')]
        self.base=[edge(5,2,inherit=True,set=True)]
    def check(self,edges):return check_role_capabilities(self.roles,self.base+edges,'data_exit.v1.r03')
    def denied(self,edges):
        with self.assertRaises(DataError) as error:self.check(edges)
        self.assertEqual(error.exception.code,'data_role_capability_mismatch')
    def test_admin_target_later_set_capability(self):
        self.denied([edge(5,6,admin=True),edge(6,1,set=True)])
    def test_multilevel_admin_and_cycle_terminate(self):
        self.denied([edge(5,6,admin=True),edge(6,7,admin=True),edge(7,1,set=True)])
        self.check([edge(5,6,admin=True),edge(6,7,set=True),edge(7,6,set=True)])
        self.denied([edge(5,6,admin=True),edge(6,7,set=True),edge(7,6,set=True),edge(7,1,set=True)])
    def test_harmless_admin_and_inherit_only_not_set(self):
        self.check([edge(5,6,admin=True),edge(6,7,inherit=True)])
        self.check([edge(5,6,inherit=True),edge(6,1,set=True)])
    def test_capacity_closes(self):
        with self.assertRaises(DataError):check_role_capabilities(self.roles*150,self.base,'data_exit.v1.r03')


class ReadProjectionTests(TestCase):
    def test_persistent_pending_done_unknown_and_readonly_compatibility(self):
        import faulthandler
        faulthandler.dump_traceback_later(10,exit=True)
        root=Path(__file__).resolve().parents[2]/'.runtime/task120-audit07/offline08'/str(uuid4())
        root.mkdir(parents=True);hub=ControlHub(root);lock=RootLease(root,'.q-policy.lock')
        mid=str(uuid4());pid=str(uuid4())
        hub.q_decide('q.bind',lambda state,seq:{'fixture':'readonly metadata only, no authority grant'})
        hub.q_decide('q.prepared',lambda state,seq:{'prepared_id':pid,'dependencies':{'sources':[],'memories':[mid]}})
        hub.q_decide('q.cleanup_pending',lambda state,seq:{'prepared_id':pid,'cleanup':{'state':'pending','identity':None}})
        class Ledger:
            data_readonly=False
            mutation_gate=SimpleNamespace(hub=hub)
            async def q_snapshot_memory_cleanup_ids(self,identity):return [identity]
        ledger=Ledger()
        async def raw():return {'memory_id':mid,'state':'revoked','purge_state':'done'}
        async def check():
            before=hub.path.read_bytes()
            row=await read_projected(ledger,raw)
            self.assertEqual(row['purge_state'],'pending');self.assertTrue(row['cleanup_status_unconfirmed'])
            self.assertEqual(hub.path.read_bytes(),before)
            ledger.mutation_gate=SimpleNamespace(hub=ControlHub(root))
            self.assertEqual((await read_projected(ledger,raw))['purge_state'],'pending')
            # Reader holds shared policy before its PG-like operation. A
            # writer cannot enter until the complete combined view releases.
            async def held():
                with self.assertRaises(DataError):lock.acquire(True,timeout=0)
                return await raw()
            await read_projected(ledger,held)
            with lock.acquire(True,timeout=0):pass
            hub.q_decide('q.cleanup_done',lambda state,seq:{'prepared_id':pid,'outcome':'absent_confirmed'})
            self.assertEqual((await read_projected(ledger,raw))['purge_state'],'done')
            hub.artifact_path('q-prepared',pid).write_bytes(b'synthetic readonly identity probe')
            self.assertEqual((await read_projected(ledger,raw))['purge_state'],'pending')
            ledger.data_readonly=True
            self.assertEqual((await read_projected(ledger,raw))['purge_state'],'done')
            ledger.data_readonly=False
            hub.q_decide('q.prepared',lambda state,seq:{'prepared_id':str(uuid4())})
            with self.assertRaises(DataError):await read_projected(ledger,raw)
            with hub.path.open('ab') as stream:stream.write(b'partial uncommitted tail')
            with self.assertRaises(DataError):await read_projected(ledger,raw)
            ledger.mutation_gate=None
            self.assertEqual((await read_projected(ledger,raw))['purge_state'],'done')
        asyncio.run(check())
        faulthandler.cancel_dump_traceback_later()
