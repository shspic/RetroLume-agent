"""类型检查已过且产品未变，正式Vite构建一次，记录真实产物。"""
import json
from control import N,ROOT,guard,count,run,write,sha,sample
assert all(row['exit_code']==0 for row in json.loads((N/'product-checks-no-io.json').read_text(encoding='utf-8'))['checks'] if row['label'] in ('typecheck','browser-contract'))
assert 'OK' in (N/'approved-model-final.log').read_text(encoding='utf-8')
guard();count('frontend_builds')
code=run(['C:/Program Files/nodejs/node.exe',str(ROOT/'frontend/node_modules/vite/bin/vite.js'),'build'],'build-8',timeout=120,cwd=ROOT/'frontend')
rows=[{'path':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':sha(p.read_bytes())} for p in (ROOT/'frontend/dist').rglob('*') if p.is_file()]
write(N/'bundle-8.json',{'sample':sample(),'command':'node frontend/node_modules/vite/bin/vite.js build; prior typecheck bound to same product source','exit_code':code,'files':rows})
raise SystemExit(code)
