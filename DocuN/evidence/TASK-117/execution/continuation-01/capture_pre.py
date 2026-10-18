"""补齐S02变更基线，后恢复的前像明确来源，不冒现场提前采样。"""
from pathlib import Path
import sys,json,hashlib
HERE=Path(__file__).resolve().parent;EXEC=HERE.parent;ROOT=EXEC.parents[3]
sys.path.insert(0,str(EXEC));from control import pre,write,sha,sample,event
old=json.loads((HERE/'s01-frozen/final-source-manifest.json').read_text())
index_path=HERE/'changes.json';index=json.loads(index_path.read_text()) if index_path.exists() else {}
recover={'backend/app/capabilities/contracts.py':lambda s:s.replace('    outbound_source_manifest: dict | None = Field(default=None, repr=False)\n','').replace('    outbound_source_manifest: dict | None = field(default=None, repr=False)\n',''),
'backend/app/worker/one_call.py':lambda s:s.replace('service = self.service.model_dump(mode="json", exclude={name for name in (\'outbound_grant\',\'outbound_source_manifest\') if getattr(self.service,name,None) is None})','service = self.service.model_dump(mode="json", exclude={\'outbound_grant\'} if self.service.outbound_grant is None else set())'),
'backend/tests/fixtures/step018/server.py':lambda s:s.split('\n\ndef main():',1)[0]+'\n',
'backend/app/main.py':lambda s:s.replace("model_copy(update={'outbound_grant':grant,'outbound_source_manifest':embedding_service.outbound_source_manifest})","model_copy(update={'outbound_grant':grant})")}
for relative,transform in recover.items():
    if relative in index:continue
    expected=next(x['post']['sha256'] for x in old['entries'] if x['path']==relative)
    current=(ROOT/relative).read_bytes();candidates=[]
    # 已实核文件混合CRLF/LF；整文件read_text规范化会损失S01原字节。
    if relative.endswith('contracts.py'):
        candidates=[b''.join(line for line in current.splitlines(keepends=True) if b'outbound_source_manifest:' not in line)]
    elif relative.endswith('server.py'):
        import re
        prefix=re.split(rb'\r?\n\r?\ndef main\(\):',current,maxsplit=1)[0].rstrip(b'\r\n')
        candidates=[prefix+ending*n for ending in (b'\n',b'\r\n') for n in range(1,5)]
    else:
        lines=current.splitlines(keepends=True)
        for ending in (b'\n',b'\r\n'):
            restored=[]
            for line in lines:
                if b'outbound_source_manifest' in line:
                    value=transform(line.decode().rstrip('\r\n')).encode()+ending
                    restored.append(value)
                else:restored.append(line)
            candidates.append(b''.join(restored))
    raw=next((r for r in candidates if sha(r)==expected),None)
    if raw is None:raise RuntimeError('无法按S01冻结hash恢复前像:'+relative)
    backup=HERE/'preimages'/relative;backup.parent.mkdir(parents=True,exist_ok=True);backup.write_bytes(raw)
    index[relative]={'exists':True,'bytes':len(raw),'sha256':expected,'backup':backup.relative_to(ROOT).as_posix(),'recorded':sample(),'provenance':'S02首改遗漏现场pre登记；由已知新增差异恢复，字节与S01冻结SHA完全相等，不追造采集时刻'}
write(index_path,index)
for item in old['entries']:
    relative=item['path']
    if relative not in index and not relative.startswith('frontend/dist/') and (ROOT/relative).is_file():pre(relative)
index=json.loads(index_path.read_text())
for name in ('control.py','runtime_control.py','root04_http.py','root04_start.py','root05_profiles.py'):
    relative=f'DocuN/evidence/TASK-117/execution/{name}';raw=(HERE/'preimages'/name).read_bytes()
    index[relative]={'exists':True,'bytes':len(raw),'sha256':sha(raw),'backup':(HERE/'preimages'/name).relative_to(ROOT).as_posix(),'recorded':json.loads((HERE/'receipt.json').read_text())['sample'],'provenance':'S02激活时真实复制的原控制器前像'}
write(index_path,index);event('S02_preimages_completed',entries=len(index),late_verified_preimages=list(recover));print('S02现有路径前像已登记，三项迟采前像来源明确')
