"""TASK-101 只读原件分类、方法日志及版本身份核对。无产品导入、无测试调用。"""
import ast
import hashlib
import json
import pathlib
import re
import sys
import time
import difflib
from html.parser import HTMLParser
from collections import Counter
from datetime import datetime, timezone

ROOT = pathlib.Path('D:/shspic/project_NO3_RetroLume-agent')
OWN = ROOT / 'DocuN/evidence/TASK-101'
RAW = ROOT / 'DocuN/evidence/TASK-100/continuation-02'

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def read(p):
    if any(s in p.name for s in ('result-prefix', 'result-before', 'work-decision', 'verification-index')):
        raise ValueError('不读实现者结论')
    value = p.read_text(encoding='utf-8-sig')
    with (OWN / 'reads.jsonl').open('a', encoding='utf-8') as log:
        log.write(json.dumps({'utc':datetime.now(timezone.utc).isoformat(), 'path':p.relative_to(ROOT).as_posix(), 'first':1, 'last':len(value.splitlines()), 'sha256':sha(p), 'reader':'evidence_scan'}, ensure_ascii=False)+'\n')
    return value

def load(p):
    return json.loads(read(p))

def save(name, value):
    target = OWN / name
    if target.exists():
        raise ValueError('不覆盖 ' + name)
    target.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

def methods():
    out = []
    for p in sorted((ROOT/'backend/tests').glob('test_*teaching*.py')) + sorted((ROOT/'backend/tests').glob('test_task100*.py')):
        tree=ast.parse(read(p))
        for cls in tree.body:
            if not isinstance(cls, ast.ClassDef):
                continue
            for method in cls.body:
                if isinstance(method,(ast.FunctionDef,ast.AsyncFunctionDef)) and method.name.startswith('test_'):
                    out.append({'path':p.relative_to(ROOT).as_posix(),'class':cls.name,'method':method.name,'line':method.lineno,'end':method.end_lineno})
    save('test-method-outline.json',out)
    for row in out:
        print(f"{row['path']}:{row['line']}-{row['end']} {row['class']}.{row['method']}")

def logs_versions():
    snapshot=load(OWN/'input-snapshot.json')
    final={row['path']:row['sha256'] for row in snapshot['source_files']+snapshot['protected_product_files']}
    versions=[]; logs=[]
    for directory in sorted(RAW.glob('20*-*')):
        if not directory.is_dir():
            continue
        manifest=directory/'as-run-files.json'
        if manifest.is_file():
            content=load(manifest)
            if not isinstance(content,dict) or not all(isinstance(v,str) for v in content.values()):
                raise ValueError('未预期版本索引形状 '+str(manifest))
            diffs=[{'path':name,'as_run_sha256':value,'final_sha256':final.get(name)} for name,value in content.items() if name in final and value!=final[name]]
            versions.append({'batch':directory.name,'manifest':manifest.relative_to(ROOT).as_posix(),'sha256':sha(manifest),'matched_final':sum(v==final.get(n) for n,v in content.items()),'changed':diffs})
        for logdir in sorted(directory.glob('*-raw')):
            if logdir.name not in ('repository-raw','http-raw','offline-raw','windows-raw','browser-main-raw','browser-raw','build-raw','typecheck-raw'):
                continue
            status=load(logdir/'result.json') if (logdir/'result.json').is_file() else None
            log=logdir/'stderr.txt'
            lines=read(log).splitlines() if log.is_file() else []
            parsed=[]
            for n,line in enumerate(lines,1):
                found=re.match(r'(test_\w+) \(([^)]+)\)\s*(.*)',line)
                if found:
                    method,identity,tail=found.groups()
                    verdict=tail.rsplit(' ... ',1)[-1].strip() if ' ... ' in tail else tail.removeprefix('...').strip()
                    if not verdict and n<len(lines):
                        verdict=lines[n].rsplit(' ... ',1)[-1].strip()
                    parsed.append({'method':method,'identity':identity,'verdict':verdict,'line':n})
            logs.append({'batch':directory.name,'stage':logdir.name,'result':status,'path':log.relative_to(ROOT).as_posix(),'sha256':sha(log) if log.is_file() else None,'methods':parsed,'summary':[x for x in lines if x.startswith(('Ran ','OK','FAILED','ERROR:','FAIL:'))]})
    save('original-method-logs.json',logs)
    save('as-run-final-identity.json',versions)
    for row in versions:
        print(row['batch'], '一致',row['matched_final'],'变化',[(x['path'],x['as_run_sha256'][:12]) for x in row['changed']])
    for row in logs:
        if row['stage'] in ('repository-raw','http-raw','offline-raw','build-raw'):
            print(row['batch'], row['stage'],row['result'],Counter(x['verdict'] for x in row['methods']),row['summary'])
    seen={}
    for row in logs:
        if row['stage'] not in ('repository-raw','http-raw'):
            continue
        for method in row['methods']:
            seen.setdefault(method['identity'],[]).append({'batch':row['batch'],'stage':row['stage'],'verdict':method['verdict'],'line':method['line']})
    save('database-http-method-runs.json',seen)

def windows():
    directory=RAW/'2026-10-05T033911.225278-0000-main-combo'
    facts=load(directory/'windows-facts.json')
    events=[]
    for p in sorted((directory/'observations').glob('*.json')):
        value=load(p)
        events.append({'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p),'value':value})
    save('windows-individual-observations.json',events)
    outcomes=facts['session_outcomes']
    links=[]
    for outcome in outcomes:
        matching=[e for e in events if e['value']['value'].get('run_tag')==outcome['run_tag'] or e['value']['value'].get('job_name')==outcome['job_name'] or e['value']['pid']==outcome.get('manager_pid') or (e['value']['kind']=='sup_created' and e['value']['value'].get('pid')==outcome.get('manager_pid'))]
        links.append({'run_tag':outcome['run_tag'],'activity_id':outcome['activity_id'],'generation':outcome['generation'],'worker_pid':outcome.get('pid'),'worker_created_100ns':outcome.get('worker_created_100ns'),'manager_pid':outcome.get('manager_pid'),'manager_created_100ns':outcome.get('manager_created_100ns'),'state':outcome['state'],'active_processes_at_end':outcome['active_processes_at_end'],'cleanup_incomplete':outcome['cleanup_incomplete'],'observations':[{'path':e['path'],'sha256':e['sha256'],'event':e['value']['kind']} for e in matching]})
    save('windows-outcome-links-corrected.json',{'correction':'首稿误把观察kind/value当event/run_tag，零关联是审计辅助解析错误，不是产品事实；原稿保留。','cases':facts['cases'],'outcomes':links,'event_keys':sorted(set(k for e in events for k in e['value'])),'event_types':dict(Counter(e['value']['kind'] for e in events))})
    print('结构',list(facts),'outcomes',len(outcomes),'observations',len(events))
    print('events',Counter(e['value']['kind'] for e in events))
    print('首个原始观察',events[0]['value'])
    print('逐窗关联',[(x['run_tag'],x['state'],len(x['observations']),x['active_processes_at_end'],x['cleanup_incomplete']) for x in links])

def locate():
    hashes=load(OWN/'independent-hashes.json')['objects']
    identities=load(OWN/'as-run-final-identity.json')
    index={}
    for row in hashes:
        index.setdefault(row['actual'],[]).append(row['path'])
    rows=[]
    for batch in identities:
        for changed in batch['changed']:
            rows.append({'batch':batch['batch'],**changed,'available_byte_copies':index.get(changed['as_run_sha256'],[])})
    save('intermediate-byte-locators.json',rows)
    for row in rows:
        if '-main-combo' in row['batch'] and ('/app/' in row['path'] or '/test_task100_integration.py' in row['path'] or '/test_teaching_api.py' in row['path'] or 'task100-browser' in row['path']):
            print(row['batch'],row['path'],row['as_run_sha256'][:12],row['available_byte_copies'])

def relink():
    events=load(OWN/'windows-individual-observations.json')
    directory=RAW/'2026-10-05T033911.225278-0000-main-combo'
    facts=load(directory/'windows-facts.json')
    links=[]
    for outcome in facts['session_outcomes']:
        matching=[e for e in events if e['value']['value'].get('run_tag')==outcome['run_tag'] or e['value']['value'].get('job_name')==outcome['job_name'] or e['value']['pid']==outcome.get('manager_pid') or (e['value']['kind']=='sup_created' and e['value']['value'].get('pid')==outcome.get('manager_pid'))]
        links.append({'run_tag':outcome['run_tag'],'activity_id':outcome['activity_id'],'generation':outcome['generation'],'worker_pid':outcome.get('pid'),'worker_created_100ns':outcome.get('worker_created_100ns'),'manager_pid':outcome.get('manager_pid'),'manager_created_100ns':outcome.get('manager_created_100ns'),'state':outcome['state'],'active_processes_at_end':outcome['active_processes_at_end'],'cleanup_incomplete':outcome['cleanup_incomplete'],'observations':[{'path':e['path'],'sha256':e['sha256'],'event':e['value']['kind']} for e in matching]})
    save('windows-outcome-links-corrected.json',{'correction':'首稿误把观察kind/value当event/run_tag，零关联是审计辅助解析错误，不是产品事实；原稿保留。','cases':facts['cases'],'outcomes':links,'event_types':dict(Counter(e['value']['kind'] for e in events))})
    print('事件',Counter(e['value']['kind'] for e in events))
    print('逐窗',[(x['run_tag'],x['state'],len(x['observations'])) for x in links])

def controls():
    ledger=load(RAW/'attempt-ledger.json')
    events=ledger['events']
    counted=[{'at':e['at'],'counter':e['counter'],'count':e['count'],'detail':e.get('detail')} for e in events if e.get('event')=='before_action']
    totals=Counter(e['counter'] for e in counted)
    seconds={k:sum(e['seconds'] for e in events if e.get('event')=='elapsed' and e.get('category')==k) for k in ('offline','real','cleanup')}
    approvals=[]
    for name,baseline in (
        ('supplementary-permit-20261005.json','attempt-ledger-before-supplement-20261005.json'),
        ('browser-supplementary-permit-20261005.json','attempt-ledger-before-browser-supplement-20261005.json'),
        ('preflight-supplementary-permit-20261005.json','attempt-ledger-before-preflight-supplement-20261005.json')):
        permit=load(RAW/name);prior=load(RAW/baseline)
        approvals.append({'path':(RAW/name).relative_to(ROOT).as_posix(),'permit':permit,'baseline_path':(RAW/baseline).relative_to(ROOT).as_posix(),'baseline_hash_match':sha(RAW/baseline)==permit['baseline_ledger_sha256'],'baseline_counts_match':prior['counts']==permit['baseline_counts']})
    cleanup=[];segments=[]
    for directory in sorted(RAW.glob('20*-main-combo')):
        cleanup.append({'batch':directory.name,'raw':load(directory/'cleanup.json')})
        segments.append({'batch':directory.name,'raw':load(directory/'segments.json')})
    result={'ledger_sha256':sha(RAW/'attempt-ledger.json'),'counts':ledger['counts'],'event_counts':dict(totals),'counts_match':dict(totals)==ledger['counts'],'seconds':ledger['seconds'],'elapsed_event_sums':seconds,'before_actions':counted,'approvals':approvals,'cleanup':cleanup,'segments':segments,'old_usage':ledger['old_usage']}
    save('control-events-and-approvals.json',result)
    print('计数',ledger['counts'],'事件复算',dict(totals),'时间',ledger['seconds'],'事件复算',seconds)
    print('批准前hash/计数',[(a['path'],a['baseline_hash_match'],a['baseline_counts_match'],a['permit']['registered_at']) for a in approvals])
    print('入口',[(e['at'],e['count']) for e in counted if e['counter']=='real_entries'])
    print('收尾',[(c['batch'],c['raw']['status'],c['raw']['elapsed'],Counter(f['action'] for f in c['raw']['facts']),[f for f in c['raw']['facts'] if f.get('error_type')]) for c in cleanup])
    for s in segments:print('阶段',s['batch'],[(x['name'],x['status']) for x in s['raw']])

def browser_artifact():
    old=RAW/'post-browser-fix/pre/frontend/tests/task100-browser.cjs'
    final=ROOT/'frontend/tests/task100-browser.cjs'
    old_text=read(old);new_text=read(final)
    diff=''.join(difflib.unified_diff(old_text.splitlines(True),new_text.splitlines(True),fromfile=old.relative_to(ROOT).as_posix(),tofile=final.relative_to(ROOT).as_posix()))
    target=OWN/'last-browser-script-independent.diff'
    if target.exists():raise ValueError('不覆盖')
    target.write_text(diff,encoding='utf-8')
    print(diff)
    directory=RAW/'2026-10-05T041623.670843-0000-main-combo/browser-controls'
    html=read(directory/'failure-dom.html')
    class Document(HTMLParser):
        def __init__(self):super().__init__();self.scripts=[];self.text=[];self.inside=False
        def handle_starttag(self,tag,attrs):
            if tag=='script':self.inside=True;self.scripts.append({'attrs':dict(attrs),'text':''})
        def handle_endtag(self,tag):
            if tag=='script':self.inside=False
        def handle_data(self,data):
            self.text.append(data)
            if self.inside:self.scripts[-1]['text']+=data
    doc=Document();doc.feed(html)
    text=''.join(doc.text)
    correction='用户补充：单位解释待核对。中文🙂 <script>window.__task100Executed=true</script>'
    timeline=load(directory/'timeline.json')
    receipts=[e for e in timeline if e['kind']=='actual_command_receipt']
    save('last-browser-original-artifact-check.json',{'layer':'原DOM的离线独立读取，非新浏览器执行或全局探针','html_sha256':sha(directory/'failure-dom.html'),'correction_literal_present':correction in text,'injected_text_is_script_element':any('__task100Executed' in s['text'] for s in doc.scripts),'script_elements':doc.scripts,'actual_receipts':receipts,'page_errors':[e for e in timeline if e['kind']=='pageerror'],'post_requests':[e for e in timeline if e.get('method')=='POST'],'old_script_sha256':sha(old),'final_script_sha256':sha(final)})
    print('DOM字面',correction in text,'作为script节点',any('__task100Executed' in s['text'] for s in doc.scripts),'实际收据',[(r['receipt']['action'],r['receipt']['status'],r['receipt']['operation_id']) for r in receipts])

def reconstruct():
    identities=load(OWN/'as-run-final-identity.json')
    wanted={}
    for batch in identities:
        for changed in batch['changed']:
            wanted.setdefault((changed['path'],changed['as_run_sha256']),[]).append(batch['batch'])
    candidates={};errors=[]
    def add(path,text,origin):
        normal=text.replace('\r\n','\n').replace('\r','\n')
        for eol,value in (('LF',normal),('CRLF',normal.replace('\n','\r\n'))):
            for bom in (False,True):
                data=(b'\xef\xbb\xbf' if bom else b'')+value.encode('utf-8')
                digest=hashlib.sha256(data).hexdigest()
                candidates.setdefault((path,digest),[]).append({'origin':origin,'line_endings':eol,'bom':bom})
    for path,digest in wanted:
        p=ROOT/path
        if p.is_file() and p.suffix in ('.py','.ts','.tsx','.cjs','.json','.md'):
            add(path,read(p),'最终源码同内容换行候选')
    for patch_name in ('diff-from-pre.patch','diff-from-pre-final-20261005.patch'):
        p=RAW/patch_name
        lines=read(p).splitlines()
        starts=[n for n,line in enumerate(lines) if line.startswith('--- pre/')]
        for offset,start in enumerate(starts):
            end=starts[offset+1] if offset+1<len(starts) else len(lines)
            path=lines[start][len('--- pre/'):]
            if not any(name==path for name,digest in wanted):continue
            oldpath=RAW/'pre'/path
            old=read(oldpath).replace('\r\n','\n').splitlines() if oldpath.is_file() else []
            output=[];oldpos=0;pos=start+2
            try:
                while pos<end:
                    header=re.match(r'@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@',lines[pos])
                    if not header:pos+=1;continue
                    oldstart=int(header.group(1));count=int(header.group(2) or 1)
                    upto=oldstart-1 if oldstart else 0
                    output.extend(old[oldpos:upto]);oldpos=upto;pos+=1
                    consumed=0;produced=0;newcount=int(header.group(4) or 1)
                    while pos<end and (consumed<count or produced<newcount):
                        row=lines[pos]
                        if row.startswith(' '):
                            assert old[oldpos]==row[1:],'上下文不一致'
                            output.append(row[1:]);oldpos+=1;consumed+=1;produced+=1
                        elif row.startswith('-'):
                            assert old[oldpos]==row[1:],'删除行不一致'
                            oldpos+=1;consumed+=1
                        elif row.startswith('+'):output.append(row[1:]);produced+=1
                        elif row.startswith('\\'):pass
                        else:break
                        pos+=1
                    assert consumed==count and produced==newcount,'hunk数量不一致'
                output.extend(old[oldpos:])
                add(path,'\n'.join(output)+'\n',patch_name+'从pre独立重建')
            except (AssertionError,IndexError) as exc:errors.append({'patch':patch_name,'path':path,'reason':str(exc)})
    result=[]
    for (path,digest),batches in wanted.items():
        result.append({'path':path,'as_run_sha256':digest,'batches':batches,'exact_reconstruction_candidates':candidates.get((path,digest),[])})
    save('reconstructed-version-bindings-corrected.json',{'bindings':result,'reconstruction_errors':errors,'note':'首稿不支持新增文件且误以源码中---/+++作为hunk结束，辅助程序已修正；仅字节SHA相等才视为重建成功。首稿保留。'})
    for row in result:
        if row['exact_reconstruction_candidates'] or ('/app/' in row['path'] and any('-main-combo' in b for b in row['batches'])):
            print(row['path'],row['as_run_sha256'][:12],row['exact_reconstruction_candidates'])
    print('重建错误',errors)

def oracle():
    directory=RAW/'2026-10-05T033911.225278-0000-main-combo'
    events=load(OWN/'windows-individual-observations.json')
    running={};rows=[];all_outcomes=[]
    for event in sorted(events,key=lambda e:e['value']['at']):
        value=event['value'];kind=value['kind'];payload=value['value'];pid=value['pid']
        if kind=='provider_started':
            messages=payload['payload']['messages']
            doc=json.loads(next(m['content'] for m in messages if m['role']=='user'))
            running[pid]=(event,doc)
        elif kind=='provider_returned' and pid in running:
            start,doc=running.pop(pid);output=payload['content'];catalog={e['id']:e for e in doc['evidence']}
            uses=[]
            def walk(obj,at=''):
                if isinstance(obj,dict):
                    for key,item in obj.items():
                        if key=='citations':
                            for citation in item:uses.append({'field':at+'.citations','id':citation,'catalog_entry':catalog.get(citation)})
                        else:walk(item,at+'.'+key)
                elif isinstance(obj,list):
                    for i,item in enumerate(obj):walk(item,at+'.'+str(i))
            walk(output)
            rows.append({'pid':pid,'start':start['path'],'return':event['path'],'task':doc['task'],'output':output,'catalog':doc['evidence'],'citation_uses':uses})
        if kind=='session_outcome':all_outcomes.append({'path':event['path'],'sha256':event['sha256'],'outcome':payload})
    save('independent-content-citation-read.json',{'pairs':rows,'provider_starts_without_return':[{'pid':pid,'path':event['path'],'task':doc['task']} for pid,(event,doc) in running.items()],'note':'逐份读取实际合成传输出入原件；内容语义由审计者独立按资料核定，非新业务执行。'})
    save('all-21-window-outcomes.json',{'outcomes':all_outcomes,'note':'包括主链17窗及浏览器重开另4窗；仅实际session_outcome原件，不把继承汇总当新窗。'})
    for row in rows:
        task=row['task'];print(task['kind'],task.get('node_id'),row['output']['result_type'],[(x['field'],x['catalog_entry']['lines'],x['catalog_entry']['text']) for x in row['citation_uses'][:5]])
    print('全部结果窗',len(all_outcomes),'传输配对',len(rows),'无返回',len(running))

def bindings():
    logs=load(OWN/'original-method-logs.json');versions=load(OWN/'as-run-final-identity.json')
    versions={v['batch']:v for v in versions}
    methods=load(OWN/'test-method-outline.json')
    outlines={(m['class'],m['method']):m for m in methods}
    lines=['# TASK-101 逐方法原件与版本绑定','',
        'A为原始实际动态观察，B为当前源码静态核定，C为合成显示或受控传输的语义限制，D为未执行。A不自动代表完整合同通过。',
        '每项采用最后一次实际ok的原stderr；保留其早期ERROR/FAIL。完整原字节及as-run清单见independent-hashes.json、as-run-final-identity.json；前两PG批涉及三个教学产品中间版本，不升级为最终模块通过。','']
    final=next(r for r in logs if r['batch']=='2026-10-05T042236.572512-0000-offline' and r['stage']=='offline-raw')
    lines+=['## 最终58离线方法','',f"原件 [stderr](D:/shspic/project_NO3_RetroLume-agent/{final['path']})，SHA256 {final['sha256']}。最终108个as-run对象全部同字节；0skip、exit0。类为原日志实际类，控制源码/替身断言不等于Windows树的动态证明。",'']
    for m in final['methods']:
        cls,method=m['identity'].rsplit('.',2)[-2:];loc=outlines.get((cls,method))
        location=f"；[当前断言](D:/shspic/project_NO3_RetroLume-agent/{loc['path']}:{loc['line']})" if loc else ''
        lines.append(f"- {m['identity']}：{m['verdict']}，原stderr第{m['line']}行{location}。")
    for stage,title in [('repository-raw','29个不同PG方法'),('http-raw','4个不同HTTP方法')]:
        lines+=['',f'## {title}',''];all_methods={}
        for row in logs:
            if row['stage']!=stage:continue
            for method in row['methods']:all_methods.setdefault(method['identity'],[]).append((row,method))
        for identity,runs in all_methods.items():
            ok=[pair for pair in runs if pair[1]['verdict']=='ok']
            if not ok:continue
            row,method=ok[-1];version=versions[row['batch']];cls,name=identity.rsplit('.',2)[-2:];loc=outlines[(cls,name)]
            source=ROOT/loc['path'];test_sha=next((c['as_run_sha256'] for c in version['changed'] if c['path']==loc['path']),sha(source))
            product_drift=[c for c in version['changed'] if '/app/' in c['path']]
            test_drift=test_sha!=sha(source)
            level='A中间产品版本；当前仅B，旧受影响语义不得继承' if product_drift else ('A当前产品；方法中间字节，未恢复完整旧断言' if test_drift else 'A当前产品与当前方法同字节')
            failures=[f"{r['batch']}:{m['line']} {m['verdict']}" for r,m in runs if m['verdict']!='ok']
            lines+=[f'- {identity}',
                f"  原件 [stderr第{method['line']}行](D:/shspic/project_NO3_RetroLume-agent/{row['path']}:{method['line']})；{row['batch']}；SHA256 {row['sha256']}。",
                f"  [当前方法](D:/shspic/project_NO3_RetroLume-agent/{loc['path']}:{loc['line']})；被测方法所在文件SHA256 {test_sha}；判定：{level}。",
                '  早期失败：'+('；'.join(failures) if failures else '无已记录失败')+'。']
    lines+=['','## 可采边界','',
        '首批仓储9及恢复7的测试文件为最终字节，运行依赖的teaching_repository、teaching_service、teaching_views是中间版本；第二批9个integration通过也依赖同三中间版本。静态当前实现、后续冻结产品的真实Windows/HTTP观察可支持相应有限不变量，但不能将这25个旧方法整体签为最终版本全覆盖。',
        '154155的单快照和纠错相反反馈2方法、HTTP3方法具有最终产品字节；当时测试文件仍是中间版本。033911引用HTTP方法及041623两PG方法的产品与测试文件均为最终字节。',
        '精确中间模块字节在657原件中未找到；两份diff独立重建也未匹配上述三个模块的as-run SHA。自己的重建辅助首稿错误已保留并修正；部分diff无法按hunk计数完整重建，仅作差异线索，不提供伪造中间文件。',
        '迁移六场景、Windows21个原始SessionOutcome、浏览器各实际控制、构建及有限内容核查另外按报告具体原件/字节绑定；本文件不以方法数量替代V01—V20覆盖。','']
    target=OWN/'method-bindings.md'
    if target.exists():raise ValueError('不覆盖')
    target.write_text('\n'.join(lines),encoding='utf-8')
    print('已保存逐方法绑定；离线',len(final['methods']),'；PG/HTTP详见',target)

started=time.perf_counter()
{'methods':methods,'logs':logs_versions,'windows':windows,'locate':locate,'relink':relink,'controls':controls,'browser':browser_artifact,'reconstruct':reconstruct,'oracle':oracle,'bindings':bindings}[sys.argv[1]]()
with (OWN/'auxiliary-times.jsonl').open('a',encoding='utf-8') as log:
    log.write(json.dumps({'utc':datetime.now(timezone.utc).isoformat(),'action':sys.argv[1],'elapsed_seconds':time.perf_counter()-started})+'\n')
