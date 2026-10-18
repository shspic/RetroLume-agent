"""交回前只核已改源码和证据一致性，不重启资源或重跑业务。"""
import ast,difflib,hashlib,json,time
from pathlib import Path
from .control import ROOT,EVIDENCE,CONTINUE_ROOT,batch,phase,atomic,source_snapshot,read_state,locked,event,run

def main():
    out=CONTINUE_ROOT/'close-checks';out.mkdir(exist_ok=False);phase('implementation_offline')
    with batch('offline','C03-changed-source-and-receipt-consistency',maximum=120):
        source_snapshot(out)
        checks=json.loads((CONTINUE_ROOT/'input-check.json').read_text(encoding='utf-8'));changes=[]
        diffdir=out/'diffs';diffdir.mkdir()
        for row in checks['sources']:
            p=Path(row['path']);relative=p.relative_to(ROOT);old=CONTINUE_ROOT/'pre'/relative
            digest=hashlib.sha256(p.read_bytes()).hexdigest()
            if digest!=row['actual']:
                changes.append({'path':relative.as_posix(),'pre_sha256':row['actual'],'post_sha256':digest})
                if p.suffix in ('.py','.cjs','.tsx','.sql'):
                    text=''.join(difflib.unified_diff(old.read_text(encoding='utf-8').splitlines(keepends=True),p.read_text(encoding='utf-8').splitlines(keepends=True),fromfile=relative.as_posix()+'.pre',tofile=relative.as_posix()+'.post'))
                    (diffdir/(relative.as_posix().replace('/','__')+'.diff')).write_text(text,encoding='utf-8')
        for p in list((ROOT/'backend/tests/fixtures/task111').glob('c03*.py'))+[ROOT/'backend/app/preview/process.py',ROOT/'backend/app/preview/production_supervisor.py',ROOT/'backend/app/preview/repository.py']:
            ast.parse(p.read_text(encoding='utf-8'))
        for p in list((ROOT/'frontend/tests/task111').glob('c03*.cjs'))+[ROOT/'deploy/preview/renderer-host.cjs',ROOT/'deploy/preview/renderer-protocol.cjs',ROOT/'deploy/preview/renderer-assembly.cjs',ROOT/'backend/tests/fixtures/task111/c03_fault_runtime.cjs']:
            run(['node','--check',str(p)],out,maximum=10,name='syntax-'+p.name)
        # 改动涉及的是新恢复读方法，原同COMMIT hook的方法正文仍可限定继承。
        def functions(path):
            tree=ast.parse(path.read_text(encoding='utf-8'));return {n.name:ast.dump(n,include_attributes=False) for n in ast.walk(tree) if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))}
        repo=ROOT/'backend/app/preview/repository.py';old=CONTINUE_ROOT/'pre/backend/app/preview/repository.py';a,b=functions(old),functions(repo)
        unchanged={name:a[name]==b[name] for name in ('_write_html_outcome','_html_confirm_integrity','accept_html_command','reserve_html_preview','update_html_preview')}
        atomic(out/'source-changes-and-reuse.json',{'changes':changes,'unchanged_transaction_functions':unchanged,'original_runtime_four_files_unchanged':all(hashlib.sha256((ROOT/'deploy/preview'/n).read_bytes()).hexdigest()==hashlib.sha256((ROOT/'deploy/preview/build-contexts/v2-03'/n).read_bytes()).hexdigest() for n in ('runtime.cjs','runtime.css','runtime.html','descriptor.schema.json'))})
        atomic(out/'result.json',{'status':'PASS_SYNTAX_AND_SCOPED_CONSISTENCY_ONLY','business_replayed':False,'new_resources_started':0})
    # 精确资源复核按真实耗时追加清场账，不改原历史分类。
    receipt=json.loads((CONTINUE_ROOT/'final-exact-resource-check.json').read_text(encoding='utf-8'))
    with locked():
        current=read_state();current['time_seconds']['cleanup']+=receipt['cleanup_verification_seconds'];atomic(EVIDENCE/'budget.json',current)
    event('C03_final_exact_metadata_cleanup',{'seconds':receipt['cleanup_verification_seconds'],'containers':len(receipt['objects'])},cleanup=True)
    print('C03 close consistency checked; no new resource or business run')

if __name__=='__main__':main()
