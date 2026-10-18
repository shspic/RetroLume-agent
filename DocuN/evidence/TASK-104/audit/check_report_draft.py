from metadata import *
draft=read(OWN/'result-draft.md')
assert '*' not in draft and not any(x.startswith('|') for x in draft.splitlines())
assert '综合结论不通过' in draft and '浏览器未启动' in draft and 'R104-F01/P1' in draft
print(json.dumps({'report_utf8_bytes':len(draft.encode()),'sections':sum(x.startswith('#') for x in draft.splitlines()),'last_identity':load(OWN/'final-identity-check.json')['match'],'final_resource_saved':(OWN/'final-readonly-resource-state.json').exists(),'active_checkpoint_seconds':time.monotonic()-load(OWN/'audit-receipt.json')['fixed_active_monotonic_origin']},ensure_ascii=False))
