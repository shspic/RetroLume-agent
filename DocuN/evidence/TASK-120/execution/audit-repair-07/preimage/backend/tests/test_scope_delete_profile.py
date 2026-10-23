"""Exact forward-profile selection/rejection; PG authorization is tested separately."""
import copy
from pathlib import Path
import unittest
from app.data_exit.contracts import PROFILE,DataError,digest
from app.data_exit.schema_profiles import R02,R03,get_profile,check_scope_permissions,MIGRATION_015


def permission_rows(profile):
    grants={'<owner>':{'SELECT','INSERT','UPDATE','DELETE','TRUNCATE','REFERENCES','TRIGGER'},
      'retrolume_data_app':{'SELECT','INSERT','UPDATE'}|({'DELETE'} if profile==R03 else set()),
      'retrolume_data_owner':{'SELECT'},'retrolume_data_restore_loader':{'SELECT','INSERT'},
      'retrolume_interview_owner':{'SELECT'},'retrolume_html_owner':{'SELECT'}}
    if profile in (R02,R03):grants['retrolume_retrieval_owner']={'SELECT'}
    result=[dict(attname=None,grantee=role,privilege_type=p,is_grantable=False,trusted_grantor=True,owner_privileges=sorted(grants['<owner>'])) for role,privs in grants.items() for p in privs]
    result += [dict(attname=c,grantee='retrolume_data_snapshot',privilege_type='SELECT',is_grantable=False,trusted_grantor=True,owner_privileges=sorted(grants['<owner>'])) for c in ('activity_id','source_id','version_id','source_revision')]
    return [{**row,'mode_observed':'normal'} for row in result]


class ScopeDeleteProfile(unittest.TestCase):
    def test_exact_chain_no_implicit_upgrade(self):
        r01,r02,r03=map(get_profile,(PROFILE,R02,R03))
        self.assertNotIn('015_activity_scope_delete_permission.sql',r01.migration_chain)
        self.assertNotIn('015_activity_scope_delete_permission.sql',r02.migration_chain)
        self.assertEqual(r03.tables,r02.tables);self.assertEqual(r03.columns,r02.columns)
        self.assertEqual(r03.migration_chain,{**r02.migration_chain,'015_activity_scope_delete_permission.sql':MIGRATION_015})
        self.assertEqual(digest((Path(__file__).parents[1]/'migrations/015_activity_scope_delete_permission.sql').read_bytes()),MIGRATION_015)
        for name in ('data_exit.v1.r04','data_exit.v1.r03x',None):
            with self.assertRaises(DataError):get_profile(name)

    def test_scope_acl_exact_each_version(self):
        for p in (PROFILE,R02,R03):check_scope_permissions(permission_rows(p),p)
        for p,rows in ((R02,permission_rows(R03)),(R03,permission_rows(R02))):
            with self.assertRaises(DataError):check_scope_permissions(rows,p)

    def test_extra_acl_and_grant_option_rejected(self):
        rows=permission_rows(R03)
        for role,privilege in [('retrolume_data_snapshot','DELETE'),('retrolume_data_restore_loader','DELETE'),('retrolume_data_app','TRUNCATE'),('<public>','SELECT'),('foreign_role','SELECT')]:
            changed=copy.deepcopy(rows);changed.append({**rows[0],'grantee':role,'privilege_type':privilege})
            with self.assertRaises(DataError):check_scope_permissions(changed,R03)
        changed=copy.deepcopy(rows);next(r for r in changed if r['grantee']=='retrolume_data_app')['is_grantable']=True
        with self.assertRaises(DataError):check_scope_permissions(changed,R03)

    def test_existing_sealed_readonly_snapshot_read_is_not_normal_write(self):
        for profile in (PROFILE,R02,R03):
            rows=[{**r,'mode_observed':'restored_readonly'} for r in permission_rows(profile)]
            rows.append({**rows[0],'grantee':'retrolume_data_snapshot','privilege_type':'SELECT'})
            check_scope_permissions(rows,profile)
            with self.assertRaises(DataError):check_scope_permissions([{**r,'mode_observed':'normal'} for r in rows],profile)
            rows.append({**rows[0],'grantee':'retrolume_data_snapshot','privilege_type':'DELETE'})
            with self.assertRaises(DataError):check_scope_permissions(rows,profile)

if __name__=='__main__':unittest.main(verbosity=2)
