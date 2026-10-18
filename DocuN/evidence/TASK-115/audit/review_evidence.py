"""静态/原始方法继承的精确导航，禁止用 result.state 自签通过。"""
import ast
import collections
import datetime as dt
import json
from pathlib import Path
import re
import sys
from types import SimpleNamespace
from bootstrap import ROOT,AUDIT,save,digest
sys.path.insert(0,str(ROOT/'backend'))
from app.data_exit.schema import MIGRATIONS,MIGRATION_013,DATA_FUNCTIONS,BUSINESS_FUNCTIONS_013
from app.data_exit.control import ControlHub

def functions(path):
    tree=ast.parse(path.read_text(encoding='utf-8-sig'));result={}
    def walk(body,prefix=''):
        for node in body:
            if isinstance(node,ast.ClassDef):walk(node.body,prefix+node.name+'.')
            elif isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)):
                result[prefix+node.name]=ast.dump(node,include_attributes=False)
    walk(tree.body)
    return result

def main():
    c01=ROOT/'DocuN/evidence/TASK-114/implementation/continuation-01'
    relevant=['backend/app/data_exit/config.py','backend/app/data_exit/deletions.py',
      'backend/app/data_exit/maintenance.py','backend/app/data_exit/restore.py','backend/app/data_exit/schema_checks.py','backend/app/main.py']
    selected=['c01-restore-1131663078000000','c01-source-1133792718000000','c01-race-1134754921000000',
      'c01-fault-1138756812000000','c01-overlay-1139001578000000','c01-integrate-1139419843000000',
      'c01-integrate-1139729250000000','c01-harden-1139975718000000']
    delta={}
    for batch in selected:
        delta[batch]={}
        for name in relevant:
            p=c01/'as-run'/batch/name
            if not p.is_file():continue
            before,after=functions(p),functions(ROOT/name)
            changed=[fn for fn in sorted(set(before)|set(after)) if before.get(fn)!=after.get(fn)]
            if changed:delta[batch][name]=changed
    migrations=[]
    for p in sorted((ROOT/'backend/migrations').glob('*.sql')):
        if int(p.name[:3])>13:continue
        expected=MIGRATION_013 if p.name[:3]=='013' else MIGRATIONS[p.name]
        migrations.append({'path':str(p),'sha256':digest(p),'match':digest(p)==expected})
    sql=(ROOT/'backend/migrations/013_data_exit.sql').read_text(encoding='utf-8-sig')
    body={name:src for name,tag,src in re.findall(r'CREATE(?: OR REPLACE)? FUNCTION public\.(\w+)\(.*? AS \$(\w+)\$(.*?)\$\2\$;',sql,re.S)}
    fingerprints=[]
    import hashlib
    for name,expected in {**{n:v['sha256'] for n,v in DATA_FUNCTIONS.items()},**BUSINESS_FUNCTIONS_013}.items():
        source=body.get(name)
        observed=hashlib.sha256(re.sub(r'\s+','',source).encode()).hexdigest() if source is not None else None
        fingerprints.append({'function':name,'sha256':observed,'expected':expected,'match':observed==expected})
    old=ROOT/'DocuN/evidence/TASK-114/synthetic/control-root/journal.bin'
    events,tail=ControlHub._read(SimpleNamespace(path=old))
    state=ControlHub.replay(events)
    hub_summary={'bytes':old.stat().st_size,'sha256':digest(old),'complete_events':len(events),'tail_unconfirmed':tail,
      'selection':state['selection'],'fence':state['fence'],'jobs_by_state':dict(collections.Counter(j['state'] for j in state['jobs'].values())),
      'owned_states':dict(collections.Counter(o['state'] for o in state['owned'].values())),
      'targets_by_state':dict(collections.Counter(t['state'] for t in state['targets'].values())),
      'layer':'只读调用原 _read/replay，不调用写 ACL/初始化的构造器，不消费执行权'}
    save('static-and-inheritance.json',{'method_ast_deltas':delta,'trusted_migrations':migrations,
      'migration_vs_product_function_fingerprints':fingerprints,'original_hub_readonly':hub_summary})
    # 新 B 组原本误标 A1 resume，保留原事件，再保守单独扣一个诊断根，不回填伪 begin。
    receipt=json.loads((AUDIT/'control/receipt.json').read_text(encoding='utf-8'))
    if not receipt.get('reader_root_reconciled'):
        receipt['new_counts']['roots']+=1
        receipt['reader_root_reconciled']={'root':'B1-readonly-projection-diagnostic','original_label':'A1 root.resume',
            'first_actual_event_utc':'2026-10-13T07:07:21.665645+00:00','last_actual_end_utc':'2026-10-13T07:12:35.701471+00:00',
            'original_events_retained':True,'failure_count':2,'classification':'独立新增受控 reader 诊断单元，保守扣根一次；未有 PG/HTTP/Browser'}
        save('control/receipt.json',receipt)
    own=[json.loads(x) for x in (AUDIT/'control/events.jsonl').read_text(encoding='utf-8').splitlines()]
    # 原消费者开始登记稍后于 Popen，改以所在方法 root 事件到结束连续扣时的保守上界。
    charge=0;details=[]
    for end in [e for e in own if e['kind']=='consumer.end']:
        starts=[e for e in own if e['kind']=='consumer.begin' and e.get('pid')==end['pid']]
        root=[e for e in own if e['kind'] in ('root.begin','root.resume') and e.get('label')=='D1-final-bundle-controlled-responses'
              and e['mono_ns']<end['mono_ns']]
        first=max(root,key=lambda e:e['mono_ns'])
        seconds=(end['mono_ns']-first['mono_ns'])/1e9
        charge+=seconds;details.append({'pid':end['pid'],'original_registered_hold_seconds':end['seconds'],
          'conservative_charged_seconds':seconds,'charge_origin':first['utc'],'end_utc':end['utc']})
    receipt=json.loads((AUDIT/'control/receipt.json').read_text(encoding='utf-8'))
    receipt['registered_holding_seconds']=receipt['new_counts']['holding_seconds']
    receipt['new_counts']['holding_seconds']=max(charge,receipt['registered_holding_seconds'])
    receipt['holding_basis']='从每次真实方法 root/resume（早于创建）到准确 consumer.end 保守计；并行 API/Browser 分别计，不是精确净持有'
    receipt['stopped_consumers']=True
    receipt['failed_reader_methods']=2
    save('control/receipt.json',receipt)
    save('control/holding-reconciliation.json',details)
    print(json.dumps({'migration_matches':sum(r['match'] for r in migrations),'function_matches':sum(r['match'] for r in fingerprints),
      'function_mismatches':[r['function'] for r in fingerprints if not r['match']],
      'ast_deltas':delta,'hub_events':len(events),'tail':tail,
      'new_counts':receipt['new_counts']},ensure_ascii=False))

if __name__=='__main__':main()
