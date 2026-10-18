from metadata import *
import re
source=load(OWN/'sql-source-app-function-binding.json')
expected={x['name']:x['app_expected'] for x in source['functions']}
catalog=load(ROOT/'DocuN/evidence/TASK-104/read-only-03/catalog-role-before.json')
checks=[]
for function in catalog['functions']:
    name=function['name'];actual=hashlib.sha256(re.sub(r'\s+','',function['source']).encode()).hexdigest()
    okay=name in expected and actual==expected[name]
    checks.append({'name':name,'actual_pg_source_hash':actual,'expected_source_app_hash':expected.get(name),'match':okay,'owner':function['owner'],'definer':function['definer'],'volatility':function['volatility'],'search_path':function['search_path'],'acl':function['acl']})
assert len(checks)==12 and all(x['match'] for x in checks)
assert all(x['definer']==(x['name']=='purge_learning_memory') for x in checks)
assert all(x['search_path']==['search_path=pg_catalog, pg_temp'] for x in checks)
assert next(x for x in checks if x['name']=='purge_learning_memory')['owner']=='retrolume_memory_purger'
save('sql-current-source-app-live-catalog-binding.json',{'at':stamp(),'actual_pg_source':'read-only-03/catalog-role-before.json','checks':checks,'roles':catalog['roles'],'memberships':catalog['memberships'],'ordinary_app':load(ROOT/'DocuN/evidence/TASK-104/read-only-03/ordinary-app-identity.json')})
print(json.dumps({'sql_functions_live_all_12_match':True,'functions':[{k:x[k] for k in ('name','owner','definer','volatility','match')} for x in checks]},ensure_ascii=False))
for group in ('continuation-01/final/bundle-chain.json','continuation-02/final/bundle-chain.json'):
    path=ROOT/'DocuN/evidence/TASK-103'/group;v=load(path)
    print(json.dumps({'bundle_file':str(path),'keys':list(v),'first_dist':v.get('dist',[])[:1],'first_loaded':v.get('loaded',[])[:1],'first_source':v.get('source_matches_build',[])[:1]},ensure_ascii=False))
js=ROOT/'frontend/dist/assets/index-D7dvfnOT.js'
text=read(js);needle='保存已确认，读取期间的新输入仍保留，请核对版本。';position=text.find(needle)
assert position>=0
excerpt=text[max(0,position-250):position+300]
save('R104-F01-final-bundle-excerpt.json',{'at':stamp(),'path':str(js),'sha256':sha(js),'message_offset':position,'excerpt':excerpt,'no_bundle_execution':True})
print(json.dumps({'current_JS_sha256':sha(js),'finding_message_offset':position,'compiled_excerpt':excerpt},ensure_ascii=False))
finish('sql-live-catalog-and-compiled-finding',{'sql_matches':12,'bundle_finding_present':True,'new_product_execution':0})
