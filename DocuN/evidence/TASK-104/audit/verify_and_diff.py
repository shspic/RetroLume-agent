from metadata import *
import difflib
index=load(ROOT/'DocuN/evidence/TASK-104/orchestration-setup-20261007/audit-input.json')
locked={x['absolute_path']:x['sha256'] for x in load(ROOT/'DocuN/evidence/v4-migration-20260930/rules-snapshot.json')}
postroot=ROOT/'DocuN/evidence/TASK-103/continuation-02/final/post'
checks=[]
for rel,expected in index['current_files'].items():
    cur=ROOT/rel; post=postroot/rel
    checks.append({'group':'current+complete-post','path':str(cur),'post':str(post),'sha256':sha(cur),'expected':expected,'snapshot_sha256':sha(post),'full_bytes_equal':cur.read_bytes()==post.read_bytes(),'match':sha(cur)==sha(post)==expected})
for group in ('protected_files','rules_and_contracts','goal_contracts'):
    for x in index[group]:
        path=Path(x['path']) if Path(x['path']).is_absolute() else ROOT/x['path']
        actual=sha(path); match=actual==x['sha256']
        if str(path) in locked: match=match and locked[str(path)]==x['sha256']
        checks.append({'group':group,'path':str(path),'expected':x['sha256'],'actual':actual,'match':match})
assert len(index['current_files'])==291 and all(x['match'] for x in checks)
save('initial-identity-check.json',{'at':stamp(),'rows':len(checks),'matched':len(checks),'checks':checks})
patches=[]; scopes=[]
for x in index['product_scope_changed_existing']+index['product_scope_new']:
    rel=x['relative_path']; current=read(ROOT/rel); initial=read(x['initial_bytes_path']) if x['initial_bytes_path'] else ''
    if x['initial_bytes_path']: assert sha(x['initial_bytes_path'])==x['initial_sha256']
    patch=''.join(difflib.unified_diff(initial.splitlines(keepends=True),current.splitlines(keepends=True),fromfile='a/'+rel if x['initial_bytes_path'] else '/dev/null',tofile='b/'+rel))
    patches.append(patch)
    scopes.append({'path':rel,'initial_sha256':x['initial_sha256'],'final_sha256':sha(ROOT/rel),'lines':len(current.splitlines()),'changed_lines_plus':sum(l.startswith('+') and not l.startswith('+++') for l in patch.splitlines()),'changed_lines_minus':sum(l.startswith('-') and not l.startswith('---') for l in patch.splitlines()),'hunks':[l for l in patch.splitlines() if l.startswith('@@')]})
save('product-diff-current.patch',''.join(patches))
save('product-scope.json',scopes)
receipt=load(OWN/'audit-receipt.json'); receipt['isolation_exception']='本会话有先前TASK-101独立审计历史；未参与102/103方案、实现或验证，未继承其实现聊天或自评；不冒称技术上完全空白的新会话。'; save('audit-receipt.json',receipt)
finish('current-post-protected-rules-and-initial-delta',{'identity_rows':len(checks),'complete_copy_matches':291,'protected':20,'rules_contract_rows':9,'goals':5,'product_scope':scopes})
