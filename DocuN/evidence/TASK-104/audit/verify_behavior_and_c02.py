from metadata import *
base=ROOT/'DocuN/evidence/TASK-103'
# 只读汇总原件的明确数据，不扩为新的实际验证。
items={}
for rel in ('memory-boundaries-result.json','migration-upgrade-resume-result.json','migration-fault-resume-result.json','integration-resume-result.json','continuation-01/gaps-result.json','continuation-01/cleanup-gaps-result.json'):
    p=base/rel;v=load(p);items[rel]={'sha256':sha(p),'cases':v['cases'],'whole_status':v['status']}
for rel in ('memory-boundaries-result.json','migration-fault-resume-result.json'):
    for c in items[rel]['cases']:
        for left,right in (('before_sha','after_sha'),('pre_sha','post_sha'),('rows_sha_before','rows_sha_after')):
            if left in c and right in c:assert c[left]==c[right]
assert items['migration-upgrade-resume-result.json']['cases'][0]['before_sha']==items['migration-upgrade-resume-result.json']['cases'][0]['after_sha']
# 原103前向函数后的成功清理收据是真实canonical TEXT。
core=load(base/'continuation-01/core-result.json')
meta=core['cases'][1]['result_meta']
assert meta==json.dumps(json.loads(meta),ensure_ascii=False,sort_keys=True,separators=(',',':'))
# C02真实陈旧POST、晚编辑回执与已存PG行绑定。
c02=base/'continuation-02';browser=load(c02/'browser/result.json');controller=load(c02/'browser/late-edit-controller.json');pg=load(c02/'tail/pg-before.json')
cas=browser['cases'][0];late=browser['cases'][1]
assert cas['response_status']==409 and cas['response']['detail']['code']=='memory_revision_conflict'
assert cas['preserved']['id']==cas['memory_id'] and cas['preserved']['text']=='B保留的陈旧版本草稿'
assert controller['receipt']==late['receipt'] and controller['status']==200
assert late['during']==late['after']
assert controller['request_at']<controller['server_response_at']<controller['release_attempt_at']<=controller['delivered_at']
body=controller['payload'];canonical_request={'schema':'memory.command.v1','action':body['action'],'memory_id':body['memory_id'],'expected_revision':body['expected_revision'],'body':body['body']}
request_sha=hashlib.sha256(json.dumps(canonical_request,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
assert request_sha==controller['receipt']['request_sha256']
cmd=next(x for x in pg['learning_memory_commands'] if x['business_key']==body['business_key'])
assert cmd['request_sha256']==request_sha and cmd['effect_applied']
actual_body=next(x for x in pg['learning_memory_bodies'] if x['memory_id']==body['memory_id'] and x['version']==1)
assert json.loads(actual_body['body'])['text']==body['body']['text']
assert not any(x['business_key']==cas['stale_key'] for x in pg['learning_memory_commands'])
switch=load(c02/'browser-02/late-switch-controller.json');switch_body=switch['payload'];switch_source=load(c02/'browser-02/result.json')
switch_cases=[x for x in switch_source['cases'] if '显式切换' in x['name']]
assert switch['status']==200 and len(switch_cases)==1 and switch_cases[0]['new_identity']==switch_cases[0]['after']
# 切换之后没有末后PG快照，严格保留此分层。
items['c02_verified']={'no_evidence':'六表/四账实值相等、409与零SUP已独立配对','CAS':'实际409、陈旧key未插入、B输入保留','late_edit':'请求hash=真实回执=PG M5，M3只保存提交正文，后续新输入未覆盖','late_switch':'真实200与网络/DOM身份成立，无末后PG快照，不升级为PG全证据','citation':'旧NOT_RUN，104三根前置FAIL、浏览器0，仍未补齐'}
save('verified-old-behavior-and-c02-pairing.json',{'at':stamp(),'evidence':items,'successful_canonical_purge_text':meta,'new_business_execution':False})
finish('specific-old-assertions-and-c02-data-paired',{'negative_sql_hash_pairs':True,'canonical_new_purge_text':True,'c02_receipt_request_PG_bind':True,'citation':'NOT_RUN','new_business':0})
