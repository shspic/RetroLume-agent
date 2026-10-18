"""合成内存替身仅用于验证资料HTTP契约，不代替PostgreSQL验证。"""
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from uuid import uuid4
from fastapi.testclient import TestClient
from app.main import create_app
from app.materials.repository import VersionConflict, DatabaseUnavailable

class MemoryMaterials:
    def __init__(self): self.rows = {}
    def list(self, limit=100, offset=0): return list(self.rows.values())[offset:offset+limit]
    def get(self, source_id): return self.rows.get(source_id)
    def save(self, *, source_id, expected_version, filename, format, sha256, size):
        previous = self.rows.get(source_id)
        if source_id and previous is None: raise KeyError(source_id)
        if previous and previous['version_id'] != expected_version: raise VersionConflict()
        sid = source_id or str(uuid4())
        row = dict(id=sid,title=filename,version_id=str(uuid4()),revision=previous['revision']+1 if previous else 1,filename=filename,format=format,sha256=sha256,size=size,created_at='2026-09-12T00:00:00+00:00')
        self.rows[sid] = row
        return row

class MaterialTests(unittest.TestCase):
    def setUp(self):
        self.data = tempfile.TemporaryDirectory(); self.backup = tempfile.TemporaryDirectory()
        self.addCleanup(self.data.cleanup); self.addCleanup(self.backup.cleanup)
        self.env = patch.dict(os.environ, {'RETROLUME_DATA_DIR':self.data.name,'RETROLUME_BACKUP_DIR':self.backup.name,'RETROLUME_DATABASE_URL':''})
        self.env.start();self.addCleanup(self.env.stop)
        self.repo = MemoryMaterials();self.client = TestClient(create_app(self.repo));self.addCleanup(self.client.close)
        self.token = self.client.get('/api/session').json()['token']
        self.headers={'x-retrolume-session':self.token,'origin':'http://127.0.0.1:8000'}
    def upload(self, name='note.md', body=b'# original', **params):
        return self.client.post('/api/materials',params={'filename':name,**params},content=body,headers=self.headers)
    def test_upload_list_read_plain_text(self):
        body=b'<script>alert(1)</script>\n# heading'
        row=self.upload(body=body).json()['material']
        self.assertEqual(self.client.get('/api/materials',headers=self.headers).json()['items'][0]['id'],row['id'])
        response=self.client.get('/api/materials/'+row['id']+'/content',headers=self.headers)
        self.assertEqual(response.json()['text'],body.decode())
        self.assertIn('application/json',response.headers['content-type'])
    def test_bad_files_do_not_block_good_file(self):
        # 'bad.pdf' 自 PDF 解析接入（FR-001 Must）后由解析器拒绝：合法扩展名进入
        # PDF 分支，损坏内容返回 422（pdf_invalid），不再是扩展名级的 415。
        for name,body,status in [('bad.pdf',b'x',422),('bad.txt',b'\xff',422),('empty.md',b' ',422),('../x.txt',b'x',400)]:
            self.assertEqual(self.upload(name,body).status_code,status)
        self.assertEqual(self.upload('good.txt',b'ok').status_code,200)
        self.assertEqual(len(self.repo.rows),1)
    def test_replacement_and_stale_version(self):
        old=self.upload().json()['material'];params=dict(source_id=old['id'],expected_version=old['version_id'])
        self.assertEqual(self.upload(body=b'\xff',**params).status_code,422)
        self.assertEqual(self.repo.get(old['id'])['version_id'],old['version_id'])
        new=self.upload(body=b'new',**params).json()['material']
        self.assertEqual(new['revision'],2)
        self.assertEqual(self.upload(body=b'stale',**params).status_code,409)
        self.assertEqual(self.repo.get(old['id'])['version_id'],new['version_id'])
        self.assertTrue((Path(self.data.name)/'originals'/old['sha256']).exists())
    def test_token_origin_and_non_caching(self):
        self.assertEqual(self.client.get('/api/materials').status_code,403)
        self.assertEqual(self.client.get('/api/session',headers={'origin':'https://evil.example'}).status_code,403)
        self.assertEqual(self.client.get('/api/materials',headers={**self.headers,'sec-fetch-site':'cross-site'}).status_code,403)
        self.assertEqual(self.client.get('/api/session').headers['cache-control'],'no-store')
    def test_stream_size_limit(self):
        with patch('app.materials.api.MAX_BYTES',3):
            self.assertEqual(self.upload(body=b'abcd').status_code,413)
            self.assertEqual(self.upload(body=b'abc').status_code,200)
    def test_missing_database_honest_unavailable(self):
        with TestClient(create_app()) as client:
            session=client.get('/api/session').json()
            self.assertFalse(session['storage_configured'])
            self.assertEqual(client.get('/api/materials',headers={'x-retrolume-session':session['token']}).status_code,503)
    def test_database_failure_does_not_replace_source(self):
        old=self.upload().json()['material']
        with patch.object(self.repo,'save',side_effect=DatabaseUnavailable('database unavailable')):
            self.assertEqual(self.upload(body=b'new',source_id=old['id'],expected_version=old['version_id']).status_code,503)
        self.assertEqual(self.repo.get(old['id']),old)

if __name__=='__main__':unittest.main()
