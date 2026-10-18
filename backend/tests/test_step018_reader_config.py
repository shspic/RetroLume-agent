"""The sealed-reader profile cannot adopt writer configuration."""
import json,os,unittest
from pathlib import Path
from tempfile import mkdtemp
from unittest.mock import patch
from app.data_exit.config import load_profile
from app.data_exit.contracts import DataError

class ReaderConfigTests(unittest.TestCase):
    def setUp(self):
        self.path=Path(mkdtemp(prefix='retrolume-reader-config-'))/'reader.json'
        self.value={'enabled':True,'reader':{'readonly_url_env':'RETROLUME_READER_DATABASE_URL',
            'target_id':'00000000-0000-4000-8000-000000000001','dataset_id':'00000000-0000-4000-8000-000000000002',
            'instance_id':'00000000-0000-4000-8000-000000000003','schema_profile':'data_exit.v1.r01'}}
    def load(self,value):
        self.path.write_text(json.dumps(value),encoding='utf-8')
        with patch.dict(os.environ,{'RETROLUME_DATA_EXIT_CONFIG':str(self.path)}):return load_profile()
    def test_reader_without_source_snapshot_or_maintenance(self):
        self.assertEqual(self.load(self.value),self.value)
    def test_writer_capabilities_cannot_be_mixed_with_reader(self):
        for field in ('factory','snapshot_url_env','maintenance_key_env','limits'):
            with self.subTest(field=field):
                with self.assertRaises(DataError):self.load({**self.value,field:{}})
    def test_missing_identity_and_unknown_profile_fail_closed(self):
        for field in ('target_id','dataset_id','instance_id','schema_profile'):
            reader=dict(self.value['reader']);reader.pop(field)
            with self.subTest(missing=field):
                with self.assertRaises(DataError):self.load({**self.value,'reader':reader})
        with self.assertRaises(DataError):self.load({**self.value,'reader':{**self.value['reader'],'schema_profile':'untrusted.v99'}})

if __name__=='__main__':unittest.main()
