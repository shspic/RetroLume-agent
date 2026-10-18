from control import ROOT,HERE,begin_root,end_root,state,count,write,event,failure,sha
import ast,subprocess,sys
if state()['active_root'] is None:
    begin_root('ROOT03-最终前端与类型离线边界','offline')
if not any(x['label']=='ROOT03-initial-typecheck' for x in state()['failures']):
    failure('ROOT03-initial-typecheck','首个包装器相对路径在frontend cwd下导入control失败；其后tsc实际运行发现InterviewCommand缺type import，已定向补齐；首账本调用遗漏effect关键字，未写失败。',effect='保留原输出和方法失败，不重置运行根')
paths=list((ROOT/'backend/app').rglob('*.py'))
for p in paths:ast.parse(p.read_bytes(),filename=str(p))
result=subprocess.run([str(ROOT/'frontend/node_modules/.bin/tsc.cmd'),'--noEmit'],cwd=ROOT/'frontend',capture_output=True,timeout=60)
(HERE/'root03-typecheck.txt').write_bytes(result.stdout+result.stderr)
write(HERE/'root03-check.json',{'parsed_python_files':len(paths),'typescript_exit':result.returncode})
if result.returncode:print(result.stdout.decode('utf-8','replace'));raise SystemExit(1)
print('Python AST and final TypeScript passed')
