"""TASK-112 只读元数据、文本和日志工具，不加载产品模块。"""
import sys, json, hashlib, time, datetime, pathlib, re

ROOT = pathlib.Path('D:/shspic/project_NO3_RetroLume-agent')
OUT = pathlib.Path(__file__).resolve().parent

def utc():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

def save(name, value):
    p = OUT / name
    p.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')

def resolve(s):
    p = pathlib.Path(s)
    return p if p.is_absolute() else ROOT / p

def read(s, purpose='metadata'):
    p = resolve(s)
    b = p.read_bytes()
    item = dict(utc=utc(), monotonic=time.perf_counter(), path=str(p), bytes=len(b), sha256=hashlib.sha256(b).hexdigest(), purpose=purpose)
    with (OUT / 'reads.jsonl').open('a', encoding='utf-8') as f:
        f.write(json.dumps(item, ensure_ascii=False) + '\n')
    return b

def obj(s):
    return json.loads(read(s).decode('utf-8-sig'))

def numbered(s, start=1, end=None):
    lines=read(s, 'text-range').decode('utf-8-sig').splitlines()
    end = min(end or len(lines), len(lines))
    print(str(resolve(s)))
    for i in range(start-1,end):
        line=lines[i]
        if len(line)>1800:
            line=line[:180]+' ... [长行省略，原字符数='+str(len(line))+', SHA256='+hashlib.sha256(line.encode('utf-8')).hexdigest()+']'
        print(f'{i+1}: {line}')

def walk_objects(v):
    if isinstance(v, dict):
        yield v
        for x in v.values(): yield from walk_objects(x)
    elif isinstance(v,list):
        for x in v: yield from walk_objects(x)

with (OUT / 'commands.jsonl').open('a', encoding='utf-8') as f:
    f.write(json.dumps(dict(utc=utc(), monotonic=time.perf_counter(), argv=sys.argv, scope='只读文件解析，禁止产品运行'),ensure_ascii=False)+'\n')

mode=sys.argv[1]
if mode=='init':
    save('receipt.json', dict(task='TASK-112', r='R-106', utc_tool_anchor='2026-10-11T15:06:14.1464331Z', windows_qpc_anchor=10026384166335, qpc_frequency=10000000, script_utc=utc(), script_monotonic=time.perf_counter(), cap_seconds=10800, business_run_allowance=0, client='Codex desktop', model='GPT-6 based agent; exact deployed model identifier not exposed', independence='本新会话仅收到根入口、TASK-112及用户指令；未参与110/111设计实现；无聊天或推理继承，无子Agent', preparation='工具时间固化前已读根AGENTS/TASK112/锁定快照及轻量记忆；初始准备缺少工具时点，不追造精确耗时', incidental='intake-control.json被完整输出，工具输出截断；可见部分为path/hash身份核对，无111自评。尚未读取111-result、received/receipt-07或methods-byte-check结论。'))
    print('receipt saved', utc())
elif mode=='read':
    numbered(sys.argv[2],int(sys.argv[3]) if len(sys.argv)>3 else 1,int(sys.argv[4]) if len(sys.argv)>4 else None)
elif mode=='shape':
    x=obj(sys.argv[2])
    if isinstance(x,dict): print(json.dumps({k: {'type':type(v).__name__,'size':len(v) if isinstance(v,(list,dict,str)) else v,'first':v[0] if isinstance(v,list) and v else None} for k,v in x.items()},ensure_ascii=False,indent=2))
    else: print(json.dumps(x[:2],ensure_ascii=False,indent=2))
elif mode=='hash':
    results=[]
    for p in sys.argv[2:]:
        b=read(p,'independent-hash')
        results.append(dict(path=str(resolve(p)),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b)))
    print(json.dumps(results,ensure_ascii=False,indent=2))
elif mode=='freeze':
    x=obj(sys.argv[2]); results=[]; seen=set()
    for v in walk_objects(x):
        p=v.get('absolute_path') or v.get('path') or v.get('file')
        h=v.get('sha256') or v.get('expected_sha256')
        if not isinstance(p,str) or not isinstance(h,str) or len(h)!=64 or p in seen: continue
        seen.add(p)
        path=resolve(p)
        try:
            b=read(str(path),'frozen-identity'); actual=hashlib.sha256(b).hexdigest()
            results.append(dict(path=str(path),expected=h,actual=actual,match=h.lower()==actual,bytes=len(b)))
        except (OSError,ValueError) as e:
            results.append(dict(path=str(path),expected=h,match=False,error=str(e)))
    save('frozen-identity-'+sys.argv[3]+'.json',results)
    print(json.dumps(dict(count=len(results),mismatches=[r for r in results if not r['match']]),ensure_ascii=False,indent=2))
elif mode=='keys':
    x=obj(sys.argv[2])
    print(json.dumps(x if len(sys.argv)<4 else {k:x.get(k) for k in sys.argv[3:]},ensure_ascii=False,indent=2))
elif mode=='grep':
    pattern=re.compile(sys.argv[3])
    for i,line in enumerate(read(sys.argv[2],'targeted-search').decode('utf-8-sig').splitlines(),1):
        if pattern.search(line): print(f'{i}: {line}')
elif mode=='copycheck':
    x=obj(sys.argv[2]); results=[]
    for item in x['C06_runtime_copies']:
        a=read(item['path'],'copy-identity'); b=read(item['original'],'original-identity')
        ha=hashlib.sha256(a).hexdigest(); hb=hashlib.sha256(b).hexdigest()
        results.append(dict(copy=item['path'],original=item['original'],expected=item['sha256'],copy_sha256=ha,original_sha256=hb,match=ha==hb==item['sha256'],bytes=len(a)))
    save('runtime-copy-verification.json',results)
    print(json.dumps(dict(count=len(results),mismatches=[r for r in results if not r['match']]),ensure_ascii=False,indent=2))
