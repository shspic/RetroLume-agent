"""Only the data-owned adapter; physical StopProof verification remains the normal recovery's job."""
from pathlib import Path
from tempfile import mkdtemp
import unittest
from uuid import uuid4
from app.data_exit.control import ControlHub
from app.data_exit.maintenance import MutationGate
from app.data_exit.contracts import DataContext
from app.preview.production_supervisor import PreviewController
from app.preview.process import OwnershipUnknown

class RecoveryDataTests(unittest.TestCase):
    def setUp(self):
        self.hub=ControlHub(Path(mkdtemp(prefix='retrolume-owned-recovery-')))
        context=DataContext(self.hub.control_id,0,str(uuid4()),str(uuid4()),'normal')
        self.gate=MutationGate(self.hub,lambda:context)
        self.registry={'preview_id':str(uuid4()),'generation':1,'parent':{'pid':123,'birth':456},'cid':None,'complete':True,
                       'intent':{'image_id':'sha256:'+'a'*64,'nonce':'b'*64,'labels':{'retrolume.boot':str(uuid4())}}}
        r=self.registry
        with self.gate.acquire():
            self.owned=self.gate.register_owned('preview',{'preview_id':r['preview_id'],'native_registry_id':r['preview_id'],
                'parent':r['parent'],'generation':r['generation'],'boot_id':r['intent']['labels']['retrolume.boot']})
        self.gate.end_owned(self.owned,confirmed=False)
        self.controller=object.__new__(PreviewController);self.controller.mutation_gate=self.gate
        self.proof={'tree_confirmation':'never_started','cid':None,'image_id':r['intent']['image_id'],'nonce':r['intent']['nonce'],
                    'parent_lifetime_ended':True,'owned_reaper_ended':True}
    def tearDown(self):self.hub.lock.close();self.hub.operation_lock.close()
    def test_exact_verified_adapter_closes_unknown_and_replay_is_readonly(self):
        self.controller._end_recovered_owned(self.registry,self.proof)
        self.assertEqual(self.hub.state()['owned'][self.owned]['state'],'ended')
        before=self.hub.path.read_bytes();self.controller._end_recovered_owned(self.registry,self.proof)
        self.assertEqual(self.hub.path.read_bytes(),before)
    def test_foreign_nonce_or_registered_birth_never_closes_work(self):
        before=self.hub.path.read_bytes()
        with self.assertRaises(OwnershipUnknown):self.controller._end_recovered_owned(self.registry,{**self.proof,'nonce':'c'*64})
        changed={**self.registry,'parent':{'pid':123,'birth':457}}
        with self.assertRaises(OwnershipUnknown):self.controller._end_recovered_owned(changed,self.proof)
        self.assertEqual(self.hub.path.read_bytes(),before)

if __name__=='__main__':unittest.main()
