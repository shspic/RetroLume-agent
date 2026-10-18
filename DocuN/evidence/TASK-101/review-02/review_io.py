"""TASK101 review02只读元数据；不导入/执行产品或测试。"""
import hashlib,json,pathlib,sys,time
from datetime import datetime,timezone
ROOT=pathlib.Path('D:/shspic/project_NO3_RetroLume-agent')
OWN=ROOT/'DocuN/evidence/TASK-101/review-02'
INDEX=ROOT/'DocuN/evidence/TASK-101/review-02-input.json'
FORBIDDEN=('TASK-100-result.md','result-header.md','work-decision','Config.Env')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def path(value):
    p=pathlib.Path(value)
    return p if p.is_absolute() else ROOT/p
def read(value,first=1,last=None):
    p=path(value)
    if any(x.casefold() in str(p).casefold() for x in FORBIDDEN):raise ValueError('禁止输入')
    started=time.perf_counter();data=p.read_text(encoding='utf-8-sig');lines=data.splitlines();last=min(last or len(lines),len(lines))
    with (OWN/'reads.jsonl').open('a',encoding='utf-8') as log:log.write(json.dumps({'at':datetime.now(timezone.utc).isoformat(),'path':str(p),'sha256':sha(p),'first':first,'last':last,'seconds':time.perf_counter()-started},ensure_ascii=False)+'\n')
    return lines[first-1:last]
def load(value):return json.loads('\n'.join(read(value)))
def save(name,value):
    p=OWN/name
    if p.exists():raise ValueError('不覆盖 '+name)
    p.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def verify(name):
    index=load(INDEX);out=[];started=time.perf_counter()
    for group in ('contracts','rules','current_objects','pre_objects','diff_objects','raw_files'):
        for item in index[group]:
            value=item.get('absolute_path',item.get('path'));p=path(value)
            if any(x.casefold() in str(p).casefold() for x in ('Config.Env','result-header.md')):
                out.append({'group':group,'path':str(p),'excluded_hash_only':True});continue
            expected=item.get('sha256',item.get('expected'));actual=sha(p) if p.is_file() else None
            out.append({'group':group,'path':str(p),'expected':expected,'actual':actual,'match':expected==actual})
    save(name,{'at':datetime.now(timezone.utc).isoformat(),'index_sha256':sha(INDEX),'seconds':time.perf_counter()-started,'objects':out})
    print('对象',len(out),'未匹配',[x for x in out if x.get('match') is False])
    if name=='initial-identities.json':
        old=ROOT/'DocuN/results/TASK-101-result.md';save('start.json',{'at':datetime.now(timezone.utc).isoformat(),'monotonic':time.perf_counter(),'prelude':'本轮首读AGENTS/卡/中性索引/状态顶部等工具墙钟约1.0秒，采样推理前段未独立计时。','limits':{'active':10800,'metadata':600},'old_report_sha256':sha(old),'old_report_bytes':old.stat().st_size,'resource_counts':{'entry':0,'PG_HTTP':0,'Docker':0,'app_static':0,'SUP_Job':0,'driver_browser':0,'model_tool':0,'build_compile_test':0,'network_git':0}})
        copy=OWN/'first-audit-original.md'
        if copy.exists():raise ValueError('不覆盖')
        copy.write_bytes(old.read_bytes())
        print('首轮结果SHA',sha(copy));print('变化',[(c['path'],c['kind']) for c in index['changes']])
        print('导航',index['author_indexes_for_navigation_only'],'批',index['raw_batch_paths'])
if __name__=='__main__':
    begun=time.perf_counter()
    if sys.argv[1]=='verify':verify(sys.argv[2])
    elif sys.argv[1]=='read':
        for value in sys.argv[2:]:
            p,first,last=value.rsplit(':',2);print(p)
            for i,line in enumerate(read(p,int(first),int(last)),int(first)):print(f'{i:5d} {line}')
    with (OWN/'helpers.jsonl').open('a',encoding='utf-8') as f:f.write(json.dumps({'at':datetime.now(timezone.utc).isoformat(),'action':sys.argv[1],'seconds':time.perf_counter()-begun})+'\n')
