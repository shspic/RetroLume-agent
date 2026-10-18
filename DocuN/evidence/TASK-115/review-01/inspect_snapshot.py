"""只读文件身份、差异和已有方法导航，不导入或运行产品。"""
import ast
import datetime as dt
import hashlib
import json
from pathlib import Path
import stat

ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).resolve().parent
C02=ROOT/'DocuN/evidence/TASK-114/implementation/continuation-02'
MANIFEST=ROOT/'DocuN/evidence/TASK-115/orchestration-review01-20261013/input-manifest.json'

def ordinary(path):
    for p in (path,*path.parents):
        if not p.exists():continue
        info=p.lstat()
        if stat.S_ISLNK(info.st_mode) or getattr(info,'st_file_attributes',0)&0x400:
            raise RuntimeError('不穿过链接或重解析点读取')

def sha(path):
    ordinary(path)
    return hashlib.sha256(path.read_bytes()).hexdigest()

def save(name,value):
    p=OUT/name;ordinary(p.parent)
    p.write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf-8')

def verify(rows,base=ROOT):
    result=[]
    for row in rows:
        p=Path(row['path'])
        if not p.is_absolute():p=base/p
        ordinary(p)
        exists=p.is_file();expected_exists=row.get('exists',True)
        actual=sha(p) if exists else None
        result.append({'path':str(p),'exists':exists,'sha256':actual,'expected_sha256':row.get('sha256'),
            'match':exists==expected_exists and (not exists or actual==row.get('sha256'))})
    return result

def methods(path):
    tree=ast.parse(path.read_text(encoding='utf-8-sig'));result={}
    def walk(body,prefix=''):
        for node in body:
            if isinstance(node,ast.ClassDef):walk(node.body,prefix+node.name+'.')
            elif isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)):
                result[prefix+node.name]={'ast_sha256':hashlib.sha256(ast.dump(node,include_attributes=False).encode()).hexdigest(),'line':node.lineno}
    walk(tree.body)
    return result

def main():
    m=json.loads(MANIFEST.read_text(encoding='utf-8-sig'))
    checks={'current':verify(m['current']), 'final_source':verify(m['final_source_snapshot'],C02/'final/source'),
            'pre':verify(m['pre'],C02/'pre'),'rules':verify(m['rules']),
            'contracts_and_control':verify([m[k] for k in ('adopted_contract','engineering_task','final_manifest','method_index',
                  'latest_owned_metadata','engineering_control','engineering_events','protected_original_audit_report')]),
            'prior_audit_evidence':verify(m['protected_original_audit_evidence']),
            'raw_batch_evidence':verify([r for b in m['raw_batches'] for r in b['files']])}
    save('identity-before.json',checks)
    relevant=[r['path'] for r in m['current'] if r['exists'] and r['path'].startswith('backend/app/data_exit/') and r['path'].endswith('.py')]
    deltas={};asrun_checks={}
    for nav in m['as_run_delta_navigation']:
        folder=C02/'as-run'/nav['label']
        a=json.loads((folder/'manifest.json').read_text(encoding='utf-8-sig'))
        entries=a['files'] if isinstance(a,dict) else a
        asrun_checks[nav['label']]=verify(entries,folder)
        changed={}
        for rel in relevant:
            older=folder/rel
            if not older.is_file():
                changed[rel]={'added_after_batch':True};continue
            if sha(older)==sha(ROOT/rel):continue
            previous,current=methods(older),methods(ROOT/rel)
            changed[rel]={'byte_changed':True,'methods_changed':[
                 {'name':n,'before':previous.get(n),'final':current.get(n)} for n in sorted(set(previous)|set(current))
                 if previous.get(n,{}).get('ast_sha256')!=current.get(n,{}).get('ast_sha256')]}
        deltas[nav['label']]=changed
    save('as-run-identity-and-method-deltas.json',{'checks':asrun_checks,'actual_method_deltas':deltas})
    changes=[]
    for row in m['current']:
        old=C02/'pre'/row['path'];new=ROOT/row['path']
        if row['exists'] and (not old.is_file() or sha(old)!=sha(new)):
            changes.append({'path':row['path'],'before_exists':old.is_file(),'before_sha256':sha(old) if old.is_file() else None,'final_sha256':sha(new)})
    save('current-deltas.json',changes)
    logs=[]
    for p in sorted((C02/'offline').glob('*.log')):
        raw=p.read_text(encoding='utf-8-sig',errors='replace')
        logs.append({'path':str(p),'sha256':sha(p),'bytes':p.stat().st_size,
             'last_lines':raw.splitlines()[-12:],'claimed_method_names':[]})
    save('rebuilt-offline-navigation.json',{'source':'实际日志，不改工程 method-index 中空的 offline_exact',
         'logs':logs,'unknown_fields':['独立同点采样的每个方法耗时','未在原事件中给出的完整 argv'],'reconstructed_not_original_sampling':True})
    save('protected-before.json',{'manifest_sha256':sha(MANIFEST),
         'files':[r for rows in checks.values() for r in rows if r['exists']]})
    print(json.dumps({'groups':{k:{'entries':len(v),'matches':sum(r['match'] for r in v),
       'mismatches':[r['path'] for r in v if not r['match']]} for k,v in checks.items()},
       'asrun_count':len(asrun_checks),'asrun_mismatches':{k:[r['path'] for r in v if not r['match']] for k,v in asrun_checks.items() if any(not r['match'] for r in v)},
       'changed_files':[r['path'] for r in changes],
       'final_batch_deltas':deltas.get('c02-boundaries-1161322062000000'),
       'offline_log_names':[Path(r['path']).name for r in logs]},ensure_ascii=False))

if __name__=='__main__':main()
