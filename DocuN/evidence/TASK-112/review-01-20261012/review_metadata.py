"""TASK112增量复核元数据工具，只用标准库，不加载产品或夹具。"""
import pathlib,sys,json,hashlib,datetime,time,re,collections

ROOT=pathlib.Path('D:/shspic/project_NO3_RetroLume-agent')
OUT=pathlib.Path(__file__).resolve().parent
def utc():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def write(name,data):
    (OUT/name).write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
def log(name,row):
    with (OUT/name).open('a',encoding='utf-8') as f:f.write(json.dumps(row,ensure_ascii=False)+'\n')
def path(s):
    p=pathlib.Path(s);return p if p.is_absolute() else ROOT/p
def read(s,purpose='只读解析'):
    p=path(s);b=p.read_bytes();log('reads.jsonl',dict(utc=utc(),mono_ns=time.perf_counter_ns(),path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b),purpose=purpose));return b
def obj(s):
    p=path(s);text=read(s).decode('utf-8-sig')
    return [json.loads(l) for l in text.splitlines() if l.strip()] if p.suffix=='.jsonl' else json.loads(text)
def walk(x):
    if isinstance(x,dict):
        yield x
        for v in x.values():yield from walk(v)
    elif isinstance(x,list):
        for v in x:yield from walk(v)
def shape(x,depth=0):
    if isinstance(x,dict):
        if len(x)>28:return {'count':len(x),'first_keys':list(x)[:8]}
        return {k:shape(v,depth+1) for k,v in x.items()} if depth<2 else {'keys':list(x)}
    if isinstance(x,list):return {'count':len(x),'first':shape(x[0],depth+1) if x else None}
    if isinstance(x,str) and len(x)>700:return {'chars':len(x),'prefix':x[:160]}
    return x
def digest(x):return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode('utf-8')).hexdigest()
def save_result(name,data):
    write(name,data);print(json.dumps(dict(saved=str(OUT/name),summary=shape(data)),ensure_ascii=False,indent=2))
def numbered(s,a=1,z=None):
    lines=read(s,'必要正文范围').decode('utf-8-sig').splitlines();z=min(z or len(lines),len(lines));print(path(s))
    for i in range(a-1,z):
        line=lines[i]
        if len(line)>1600:line=line[:180]+' [长行省略，字符数='+str(len(line))+']'
        print(f'{i+1}: {line}')

log('commands.jsonl',dict(utc=utc(),mono_ns=time.perf_counter_ns(),argv=sys.argv,scope='文件元数据，无业务运行'))
mode=sys.argv[1]
if mode=='init':
    baseline=read('DocuN/results/TASK-112-result.md','首轮原字节基线')
    h=hashlib.sha256(baseline).hexdigest()
    if len(baseline)!=36048 or h!='ea51e0f49f556fd6f07aea11741d26099a534550850c0c68dfa49a9ab4c3b522':raise RuntimeError('原112基线漂移，不覆盖')
    (OUT/'TASK-112-original-result.md').write_bytes(baseline)
    write('receipt.json',dict(task='TASK-112',r='R-106',review='review-01',permit='TASK-112-G11-REVIEW01-20261012',received_tool_utc='2026-10-12T00:48:53.3841165Z',received_qpc=10375971557863,qpc_frequency=10000000,new_cap_seconds=7200,cumulative_cap_seconds=10800,prior_observed_seconds=3347.3488145,prior_preclock_preparation='unknown，未重置',recorded_utc=utc(),recorded_mono_ns=time.perf_counter_ns(),business_run_allowance=0,client='Codex desktop',model='基于GPT-6，精确后缀及推理档未暴露',window='用户明确指定接续原112独立窗口；无可核窗口ID，不冒工具确认',independence='本会话未参与111续作07产品修复，未收到其聊天或推理，没有子Agent',baseline_bytes=len(baseline),baseline_sha256=h))
    print('已保存接收、累计预算和原字节基线')
elif mode=='read':numbered(sys.argv[2],int(sys.argv[3]) if len(sys.argv)>3 else 1,int(sys.argv[4]) if len(sys.argv)>4 else None)
elif mode=='shape':print(json.dumps(shape(obj(sys.argv[2])),ensure_ascii=False,indent=2))
elif mode=='field':
    x=obj(sys.argv[2])
    for k in sys.argv[3].split('.'):x=x[int(k)] if isinstance(x,list) else x[k]
    print(json.dumps(x,ensure_ascii=False,indent=2))
elif mode=='stop-paths':
    x=obj(sys.argv[2]);print(json.dumps([dict(preview_id=r['preview_id'],name=r['name'],elapsed=r['elapsed_seconds'],paths={k:r[k]['path'] for k in ('kernel','proof','registry')}) for r in x],ensure_ascii=False,indent=2))
elif mode=='stamp':
    p=OUT/sys.argv[2];b=read(p,'独立检查点正文固化');save_result(p.stem+'-receipt.json',dict(path=str(p),utc=utc(),mono_ns=time.perf_counter_ns(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),basis='独立形成，不读工程结果或候选摘要文件'))
elif mode=='keys':
    x=obj(sys.argv[2]);print(json.dumps({k:x.get(k) for k in sys.argv[3:]} if len(sys.argv)>3 else x,ensure_ascii=False,indent=2))
elif mode=='freeze':
    x=obj(sys.argv[2]);seen=set();results=[]
    for v in walk(x):
        s=v.get('path') or v.get('absolute_path');h=v.get('sha256') or v.get('expected_sha256')
        if not isinstance(s,str) or not isinstance(h,str) or len(h)!=64 or s in seen:continue
        seen.add(s)
        try:
            b=read(s,'冻结身份核对');actual=hashlib.sha256(b).hexdigest();results.append(dict(path=str(path(s)),bytes=len(b),expected=h,actual=actual,match=h==actual))
        except OSError as e:results.append(dict(path=s,expected=h,match=False,error=str(e)))
    write('frozen-'+sys.argv[3]+'.json',results)
    print(json.dumps(dict(count=len(results),mismatches=[r for r in results if not r['match']]),ensure_ascii=False,indent=2))
elif mode=='diff-check':
    x=obj(sys.argv[2]);rows=[]
    for r in x['changes']:
        pre='DocuN/evidence/TASK-111/execution/continuation-07/pre/'+r['path'].replace('/','__')
        before=read(pre,'真实pre字节');after=read(r['path'],'当前post字节')
        import difflib
        actual=''.join(difflib.unified_diff(before.decode('utf-8').replace('\r\n','\n').splitlines(keepends=True),after.decode('utf-8').replace('\r\n','\n').splitlines(keepends=True),fromfile='C06/'+r['path'],tofile='C07/'+r['path']))
        dp='DocuN/evidence/TASK-111/execution/continuation-07/final/source-diff/'+r['path'].replace('/','__')+'.diff'
        original=read(dp,'已保存diff')
        rows.append(dict(path=r['path'],pre_sha256=hashlib.sha256(before).hexdigest(),post_sha256=hashlib.sha256(after).hexdigest(),pre_matches=hashlib.sha256(before).hexdigest()==r['before'],post_matches=hashlib.sha256(after).hexdigest()==r['after'],diff_bytes_equal=actual.encode('utf-8')==original,diff_text_equal_after_CRLF_normalization=actual==original.decode('utf-8').replace('\r\n','\n')))
    save_result('actual-diff-verification.json',rows)
elif mode=='node-offline':
    x=obj(sys.argv[2]);directory=path(sys.argv[2]).parent;py=obj(directory/'python-domain-result.json');node=obj(directory/'node-host-result.json');pym={r['name']:r for r in py['rows']};nodem={r['name']:r for r in node['rows']};rows=[]
    for item in x['cases']:
        hb=bytes.fromhex(item['header_hex']);bb=bytes.fromhex(item['body_hex']);h=json.loads(hb.decode('utf-8-sig'));n=nodem[item['name']]
        rows.append(dict(name=item['name'],expected=item['expected'],Python=pym[item['name']]['accepted'],Node=n['actual'],same_acceptance=pym[item['name']]['accepted']==n['actual']==item['expected'],gate=n['gate'],header_size=n['header_bytes']==len(hb),header_hash=n['header_sha256']==hashlib.sha256(hb).hexdigest(),body_size=h['body_bytes']==len(bb)==n['body_bytes'],body_hash=h['body_sha256']==n['body_sha256']==hashlib.sha256(bb).hexdigest(),header_BOM=hb.startswith(b'\xef\xbb\xbf'),body_BOM=bb.startswith(b'\xef\xbb\xbf'),browser_boundary=n['host']['browserReached'],internal_BOM_preserved=None if item['name']!='internal_BOM' else json.loads(bb)['description']['title']==item['internal_title']))
    save_result('node-ingress-originals-verification.json',dict(source=str(directory),rows=rows,case_count=len(rows),real_browser_started=node['browser_started']))
elif mode=='load-manifest':
    x=obj(sys.argv[2]);p=path(sys.argv[2]);rows=[]
    for name,expected in x['files'].items():
        b=read(p.parent/name,'本地load对象身份');actual=hashlib.sha256(b).hexdigest();rows.append(dict(name=name,expected=expected,actual=actual,match=actual==expected,bytes=len(b)))
    save_result('load-manifest-independent.json',dict(manifest_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),metadata={k:v for k,v in x.items() if k!='files'},count=len(rows),mismatches=[r for r in rows if not r['match']],rows=rows))
