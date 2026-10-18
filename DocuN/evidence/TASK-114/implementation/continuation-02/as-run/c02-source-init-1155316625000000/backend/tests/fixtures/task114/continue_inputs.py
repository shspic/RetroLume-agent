"""真实合成文件输入边界，保全部坏输入；不启动PG、不解压到目标。"""
import json
import os
from pathlib import Path
import stat
import struct
import zipfile
from uuid import uuid4
from budget import ROOT,EVIDENCE
import sys
sys.path.insert(0,str(ROOT/'backend'))
from app.data_exit.packages import PackageReader
from app.data_exit.contracts import DataError,Limits,canonical,digest
from app.data_exit.files import safe_root

def main():
    root=ROOT/'DocuN/evidence/TASK-114/synthetic/scratch'/('c01-inputs-'+str(uuid4()));root.mkdir()
    src=ROOT/'DocuN/evidence/TASK-114/synthetic/backup-root/packages/737bf7ba-18c2-436c-a011-3aabbc1a8b2b.rldata'
    with zipfile.ZipFile(src) as z:entries={n:z.read(n) for n in z.namelist()}
    sentinel=ROOT/'DocuN/evidence/TASK-114/synthetic/sentinel-root'/('c01-sentinel-'+str(uuid4()))
    sentinel.write_bytes(b'EXACT OWNED SENTINEL\n');before=digest(sentinel.read_bytes())
    results=[]
    def trial(name,extra=None,transform=None,compress=False,mode=None,limits=None,raw=None):
        path=root/(name+'.rldata')
        if raw is not None:path.write_bytes(raw)
        else:
            content=dict(entries)
            if transform:content=transform(content)
            with zipfile.ZipFile(path,'x',compression=zipfile.ZIP_STORED,allowZip64=False) as z:
                for n,data in content.items():z.writestr(n,data)
                if extra is not None:
                    item=zipfile.ZipInfo(extra);item.compress_type=zipfile.ZIP_DEFLATED if compress else zipfile.ZIP_STORED
                    if mode is not None:item.create_system=3;item.external_attr=mode<<16
                    z.writestr(item,b'NEVER PUBLISHED')
        try:
            with PackageReader(path,limits):pass
        except DataError as e:results.append({'name':name,'path':str(path),'code':e.code,'sha256':digest(path.read_bytes())})
        else:raise RuntimeError('坏输入没有拒绝: '+name)
    for i,name in enumerate(('../escape.txt','C:/escape.txt','//host/share/escape','README.txt:ADS','originals/','manifest.json','readme.TXT','migration.sql','nested.rldata')):
        trial('path-'+str(i),extra=name)
    trial('symlink-entry',extra='texts/'+'a'*64+'.txt',mode=stat.S_IFLNK|0o777)
    trial('deflate-entry',extra='texts/'+'b'*64+'.txt',compress=True)
    trial('truncated',raw=src.read_bytes()[:-17])
    def corrupt(values):values['README.txt']=b'wrong original bytes';return values
    trial('changed-content',transform=corrupt)
    def unsafe_metadata(values):
        member='metadata/source_control.json';row=json.loads(values[member]);row['maintenance_key']='C01_NEVER_AUTHORIZES_MARKER'
        values[member]=canonical(row).encode('utf-8');m=json.loads(values['manifest.json'])
        for item in m['contents']:
            if item['path']==member:item['sha256']=digest(values[member]);item['bytes']=str(len(values[member]))
        m.pop('root_sha256');m['root_sha256']=digest(canonical(m));values['manifest.json']=canonical(m).encode('utf-8');return values
    trial('control-secret-even-correct-hashes',transform=unsafe_metadata)
    trial('members-limit',limits=Limits(members=2))
    trial('rows-limit',limits=Limits(rows=1))
    oversized=bytearray(src.read_bytes());pos=oversized.rfind(b'PK\x05\x06');struct.pack_into('<I',oversized,pos+12,9*1024**2)
    trial('EOCD-directory-bound',raw=bytes(oversized))
    link=root/'real-redirect.rldata'
    try:
        os.symlink(src,link)
        try:
            with PackageReader(link):pass
        except DataError as e:results.append({'name':'actual-filesystem-symlink','code':e.code,'path':str(link)})
        else:raise RuntimeError('真实文件重定向未拒绝')
    except OSError as e:results.append({'name':'actual-filesystem-symlink','state':'not_run','errno':e.errno,'reason':'host privilege; no install/escalation'})
    if digest(sentinel.read_bytes())!=before or digest(src.read_bytes())!='45177d58ea58fcaa704bfdd48641aceade7ca6e6f4fe5d6759b3a46bf2671665':raise RuntimeError('输入拒绝改变旧成果/哨兵')
    result={'state':'passed_executed_cases_only','results':results,'sentinel_unchanged':True,'old_package_unchanged':True,'restore_target_writes':0,
            'actual_test_low_limits':{'members':2,'rows':1,'directory_bytes':8*1024**2},'retained_root':str(root)}
    path=EVIDENCE/'observations'/('input-boundaries-'+str(uuid4())+'.json');path.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'executed_rejections':len([e for e in results if 'code'in e]),'not_run':len([e for e in results if e.get('state')=='not_run']),'evidence':str(path)}))

if __name__=='__main__':main()
