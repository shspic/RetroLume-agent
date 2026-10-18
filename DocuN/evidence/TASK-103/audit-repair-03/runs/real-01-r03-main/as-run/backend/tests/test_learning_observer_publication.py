"""真实Windows文件并发复验；不创建SUP/Job、进程、端口或数据库。"""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import hashlib, json, threading, unittest
from uuid import uuid4
from tests.fixtures.task097.publication import publish_once

ROOT=Path(__file__).resolve().parents[2]
class PublicationTests(unittest.TestCase):
    def test_immutable_records_under_concurrent_reader_and_two_writers(self):
        root=ROOT/'DocuN/evidence/TASK-097/continuation-01/publication-stress'/str(uuid4())
        root.mkdir(parents=True);done=threading.Event();observed=set();errors=[]
        def reader():
            while not done.is_set():
                for p in root.glob('reservation-*.json'):
                    try:
                        value=json.loads(p.read_text(encoding='utf-8'));self.assertEqual(value['record'],p.stem);observed.add(p.name)
                    except Exception as e:errors.append(repr(e))
        def writer(offset):
            for n in range(offset,150,2):publish_once(root,f'reservation-{n}.json',{'record':f'reservation-{n}','counted':True})
        with ThreadPoolExecutor(max_workers=3) as pool:
            future=pool.submit(reader)
            writers=[pool.submit(writer,i) for i in range(2)]
            for f in writers:f.result()
            done.set();future.result()
        self.assertFalse(errors,errors);self.assertEqual(len(list(root.glob('reservation-*.json'))),150)
        old=root/'reservation-0.json';before=hashlib.sha256(old.read_bytes()).hexdigest()
        with self.assertRaises(OSError):publish_once(root,old.name,{'record':'overwrite forbidden'})
        self.assertEqual(hashlib.sha256(old.read_bytes()).hexdigest(),before)
        for p in list((ROOT/'backend/tests/fixtures/task097').glob('*.py')):compile(p.read_bytes(),str(p),'exec')
        print(json.dumps({'actual_os':'Windows','published_records':150,'concurrent_read_errors':errors,'observed_records':len(observed),'duplicate_overwrite_rejected':True,'sup_launches':0,'scope':'fixture record publication only; no complete Windows business revalidation'}))
