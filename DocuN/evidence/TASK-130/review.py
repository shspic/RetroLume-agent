"""只检查Git候选；敏感命中仅记录路径和类别。"""
from delivery import *
import os
import re

tracked=json.loads((E/'tracked.json').read_text('utf-8'))
untracked=json.loads((E/'untracked.json').read_text('utf-8'))
paths=sorted(set(tracked+untracked))
patterns={
 'private_key':re.compile(rb'-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----'),
 'github_token':re.compile(rb'\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,})\b'),
 'api_key':re.compile(rb'\bsk-(?:proj-)?[A-Za-z0-9_-]{24,}\b'),
 'connection_credential':re.compile(rb'(?:postgres(?:ql)?|mysql)://[^\s/"\x27:]+:[^\s/@"\x27]+@'),
 'bearer_literal':re.compile(rb'Bearer [A-Za-z0-9_.-]{24,}'),
}
entries=[]; findings=[]; issues=[]; total=0; start=time.monotonic()
for n,name in enumerate(paths):
    p=ROOT/name
    if n%2000==0: print(n,len(paths),round(time.monotonic()-start,1),flush=True)
    if name.startswith('DocuN/evidence/TASK-130/'):
        continue
    if p.is_symlink() or any(part.lower() in ('.runtime','browser-profile','chrome-profile') for part in p.parts):
        issues.append({'path':name,'category':'unsafe_path_not_read'});continue
    if not p.exists():
        entries.append({'path':name,'deleted':True});continue
    if not p.is_file():
        issues.append({'path':name,'category':'not_regular_file'});continue
    size=p.stat().st_size
    if size>100*1024*1024:
        issues.append({'path':name,'category':'over_100MiB','bytes':size});continue
    data=p.read_bytes(); total+=len(data)
    entries.append({'path':name,'bytes':size,'sha256':hashlib.sha256(data).hexdigest()})
    for category,pattern in patterns.items():
        for m in pattern.finditer(data):
            findings.append({'path':name,'category':category,'line':data.count(b'\n',0,m.start())+1})
save('candidate-files-before.json',entries)
save('review-findings.json',{'at':now(),'files':len(paths),'bytes':total,'seconds':time.monotonic()-start,
     'findings':findings,'issues':issues,'scope':'Git tracked及非忽略untracked；不枚举依赖、运行目录或忽略文件'})
print('done',len(entries),total,'findings',len(findings),'issues',len(issues),flush=True)
