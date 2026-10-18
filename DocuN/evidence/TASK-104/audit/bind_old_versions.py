from metadata import *
index=load(ROOT/'DocuN/evidence/TASK-104/orchestration-setup-20261007/audit-input.json');nav=load(OWN/'old-run-navigation.json')
product={x['relative_path'] for x in index['product_scope_changed_existing']+index['product_scope_new']}
checks=[]
for group in nav:
    for run in group['runs']:
        p=Path(run['directory'])/'execution.json';v=load(p)
        before={x['path']:x['sha256'] for x in v.get('before',[])};after={x['path']:x['sha256'] for x in v.get('after',[])}
        delta=[rel for rel in product if rel in before and before[rel]!=index['current_files'].get(rel)]
        same=all(before[k]==after.get(k) for k in before)
        checks.append({'name':run['name'],'execution_path':str(p),'execution_sha256':sha(p),'root':group['evidence_root'],'before_count':len(before),'after_count':len(after),'during_run_identity_equal':same,'product_delta_to_final':sorted(delta),'product_missing_from_asrun':sorted(product-set(before)),'exit_code':v.get('exit_code')})
save('all-run-version-applicability.json',{'at':stamp(),'runs':checks,'note':'只核执行身份与最终差异；不将汇总PASS代具体结果，也未全量重采旧原件'})
chain=load(ROOT/'DocuN/evidence/TASK-103/continuation-01/final/bundle-chain.json')
build=load(chain['build_execution']);buildmap={x['path']:x['sha256'] for x in build['before']}
front=[]
for item in chain['source_matches_build']:
    rel=item['path'];okay=sha(ROOT/rel)==item['source_sha256']==buildmap[rel]
    assert okay
    front.append({'path':rel,'sha256':item['source_sha256'],'build_asrun_current_same':okay})
assets=[]
for directory in ('continuation-02/browser','continuation-02/browser-02','continuation-01/browser-03'):
    for filename in ('index-D7dvfnOT.js','index-COpEVDbn.css'):
        old=ROOT/'DocuN/evidence/TASK-103'/directory/filename;current=ROOT/'frontend/dist/assets'/filename
        if old.exists():
            assert old.read_bytes()==current.read_bytes()
            assets.append({'raw_complete_loaded_bytes':str(old),'current':str(current),'sha256':sha(current),'bytes':len(old.read_bytes()),'full_equal':True})
assert len(front)==24 and len(assets)>=4
save('final-bundle-source-and-old-native-load-binding.json',{'at':stamp(),'frontend_sources':front,'loaded_complete_assets':assets,'new_browser':False})
for x in checks:
    if '/continuation-01' in x['root'] or '/continuation-02' in x['root']:
        print(json.dumps({k:x[k] for k in ('name','during_run_identity_equal','product_delta_to_final','exit_code')},ensure_ascii=False))
print(json.dumps({'all_execution_records':len(checks),'front_sources_bound':24,'actual_loaded_complete_asset_copies':len(assets)},ensure_ascii=False))
finish('old-actual-run-version-and-native-byte-binding',{'records':len(checks),'no_old_runs_restarted':True})
