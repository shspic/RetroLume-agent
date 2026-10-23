"""TASK122 标准库资料整理与整数核算；不导入、不调用产品。"""
from copy import deepcopy
from datetime import datetime, timezone
from decimal import Decimal, ROUND_CEILING
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
NOW = datetime.now(timezone.utc).isoformat()

def rawsha(value):
    return hashlib.sha256(value if isinstance(value, bytes) else value.encode('utf-8')).hexdigest()

def canon(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False)

def save(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

samples_path = ROOT / 'DocuN/evidence/TASK-116/design/sample-inputs.json'
samples = json.loads(samples_path.read_text(encoding='utf-8'))
old_path = ROOT / 'DocuN/evidence/TASK-119/design/call-matrix.json'
old = json.loads(old_path.read_text(encoding='utf-8'))
adoption = json.loads((ROOT / 'DocuN/evidence/TASK-120/orchestration-20261018/adoption-receipt.json').read_text(encoding='utf-8'))
sources, fragments = [], []
for source in samples['sources']:
    # 仅对已冻结的 LF 文本按已读源码规则作长度算术；没有运行分片器。
    offset = 0
    count = 0
    for line_number, text in enumerate(source['text'].splitlines(keepends=True), 1):
        count += (len(text) + 2047) // 2048
        for start in range(0, len(text), 2048):
            part = text[start:start+2048]
            fragments.append({'alias': source['alias'], 'line': line_number,
                'start_offset': offset+start, 'end_offset': offset+start+len(part),
                'codepoints': len(part), 'utf8_bytes': len(part.encode('utf-8')),
                'raw_text_sha256': rawsha(part), 'json_string_sha256': rawsha(canon(part)),
                'json_string_bytes': len(canon(part).encode('utf-8')),
                'source_id': None, 'version_id': None, 'revision': None, 'evidence_id': None})
        offset += len(text)
    sources.append({'alias': source['alias'], 'filename': source['filename'],
        'input_pointer': f"{samples_path.as_posix()}#/sources/{len(sources)}/text",
        'codepoints': len(source['text']), 'utf8_bytes': len(source['text'].encode('utf-8')),
        'raw_text_sha256': rawsha(source['text']), 'expected_lines': source['expected_lines'],
        'statically_required_fragments': count})
top_four = sorted(fragments, key=lambda f:f['json_string_bytes'], reverse=True)[:4]
empty_embedding = len(canon({'model':'embedding-3','input':[],'dimensions':512}).encode('utf-8'))
batch_wire_upper = empty_embedding + sum(x['json_string_bytes'] for x in top_four) + 3
query_pointers = ['numeric_goal','concept_goal','ambiguous_goal','ambiguous_clarification','no_evidence_query','conflict_query','interview_goal']
queries = [{'pointer': f'/inputs/{key}', 'utf8_bytes':len(samples['inputs'][key].encode('utf-8')),
            'raw_text_sha256':rawsha(samples['inputs'][key]),
            'payload_bytes':len(canon({'model':'embedding-3','input':[samples['inputs'][key]],'dimensions':512}).encode('utf-8'))}
           for key in query_pointers]
program = next(x['text'] for x in samples['sources'] if x['alias']=='P')
queries.append({'pointer':'/sources/2/text','utf8_bytes':len(program.encode('utf-8')),
    'raw_text_sha256':rawsha(program),'payload_bytes':len(canon({'model':'embedding-3','input':[program],'dimensions':512}).encode('utf-8'))})
save('sample-fragments.json', {'status':'STATIC_RULE_ARITHMETIC_NOT_PRODUCT_FRAGMENTATION',
    'created_at':NOW,'frozen_samples_sha256':rawsha(samples_path.read_bytes()),
    'rule_sources':['backend/app/retrieval/evidence.py:59-74,166-175','backend/app/materials/locations.py:9-15','backend/app/retrieval/service.py:148-151'],
    'assumptions':['精确使用 JSON 内八份 LF 正文，无尾换行改写、无用户补充、无 PDF 加入收费目录',
        '每份原文为一个 ready SourceTextUnit；真实导入、UUID/version/revision/currentness 尚未发生'],
    'sources':sources,'fragments':fragments,'total_fragments':len(fragments),'source_index_calls':(len(fragments)+3)//4,
    'actual_batch_order':'未来按真实 evidence_id 排序；此处不伪造 ID 或分组',
    'any_four_fragment_payload_bytes_upper_bound':batch_wire_upper,
    'any_four_raw_text_utf8_bytes_upper_bound':sum(sorted((x['utf8_bytes'] for x in fragments),reverse=True)[:4]),
    'max_item_utf8_bytes':max(x['utf8_bytes'] for x in fragments),'queries':queries,
    'tokens_per_item_and_batch':None,'token_bound_verified':False,
    'capacity_status':'UNKNOWN；小字节数不是官方 token 证明，3072 单项及保守整批门均未获证'})

def ceiling(request_bytes, output_tokens, input_rate='2', output_rate='8', framing=4096):
    value=(Decimal(request_bytes+framing)*Decimal(input_rate)+Decimal(output_tokens)*Decimal(output_rate))*Decimal('1.25')
    return int(value.to_integral_value(rounding=ROUND_CEILING))

price_classes={
    'embedding_shared_absolute_65536':ceiling(65536,0),
    'learning_256_absolute_65536':ceiling(65536,256),
    'teaching_interview_2048_absolute_65536':ceiling(65536,2048),
    'html_4096_absolute_65536':ceiling(65536,4096),
    'embedding_own_rate_absolute_65536':ceiling(65536,0,'0.5','0'),
    'embedding_own_rate_draft_32768':ceiling(32768,0,'0.5','0'),
    'source_batch_shared_byte_illustration':ceiling(batch_wire_upper,0),
}

rows=deepcopy(old['rows'])
rows[0]['index_calls']=(len(fragments)+3)//4
rows[0]['notes']='八份冻结正文按逐行规则静态推得24片；空缓存为6批。真实ID排序及当前性在新normal零费用冻结时核对；不执行分片实验。'
rows.append({'id':'Q12','scenarios':['L05'],'activity':'learning',
    'action':'extra_independent_retest_exercise_240m_1min;evaluate_4mps;local_same_key_read_and_exposure_checks',
    'model_calls':2,'query_calls':2,'index_calls':0,'html_calls':0,
    'notes':'把原119有条件追加的4次纳入正常最坏路径。无暴露的两份独立实例才可推进；去重/assisted机制沿已验层继承。',
    'max_request_bytes_per_call':65536,'max_response_bytes_per_call':65536,
    'max_output_tokens':{'model':2048,'embedding':0,'html':0}})
for row in rows:
    row['requests']=sum(row[k] for k in ('model_calls','query_calls','index_calls','html_calls'))
    row['reserve_microunits']=row['requests']*250000
    row['conditional_shared_rate_ceiling_microunits']=(row['model_calls']*price_classes['teaching_interview_2048_absolute_65536']
       +(row['query_calls']+row['index_calls'])*price_classes['embedding_shared_absolute_65536']+row['html_calls']*price_classes['html_4096_absolute_65536'])
    row['status']='NOT_RUN_REAL_Q_COMPLETED_0'
    row['actual_billable_ceiling_microunits']=None

roster=deepcopy(adoption['roster'])
for allocation in roster:
    group=[x for x in rows if x['activity']==allocation['role']]
    allocation['planned_requests']=sum(x['requests'] for x in group)
    allocation['planned_reserve_microunits']=allocation['planned_requests']*250000
    allocation['remaining_requests_after_normal_path']=allocation['max_requests']-allocation['planned_requests']
    allocation['remaining_reserve_microunits_after_normal_path']=allocation['max_cost_microunits']-allocation['planned_reserve_microunits']
    allocation['conditional_shared_rate_ceiling_microunits']=sum(x['conditional_shared_rate_ceiling_microunits'] for x in group)
    allocation['remaining_now_requests']=allocation['max_requests']
    allocation['remaining_now_reserve_microunits']=allocation['max_cost_microunits']

rubrics={
 'L01':'长错答保留120÷2的算术认可，指出分钟换秒与单位；针对题2m/s、独立复测3m/s；feedback/progress及继续理由真实保存。',
 'L02':'1m/s、60m/min、完整肯定换算三个独立答案版本分别认可，不能仅匹配数字。',
 'L03':'60m/s、1m、1000m/s分别定位60倍、维度、1000倍问题；保留正确部分。',
 'L04':'否定不能判对；不确定保留unknown/必要追问，不声称能力事实。',
 'L05':'两个不同且未暴露、无冲突、required met实例及引用理由才推进一次；同键去重、暴露后assisted。',
 'L06':'概念正例获认可、反例指出不能互推、partial认可原子性并补持久性。',
 'L07':'认可1→3→6；指出range不含4；无执行程序或shell。',
 'L08':'两份Java先澄清；显式改为J-CODE及新目标，旧检索/父失效而草稿历史保留。',
 'L09':'缺资料明确不足；冲突同时展示两源及120/120=1，不因排序掩盖矛盾。',
 'L10':'当前长错答feedback后立即生成；固定d/t 120/120=1、t240=0.5、t0/未定义字段拒、reset=1；ACK/PNG/StopProof。',
 'I01':'R+M不完整答产生必要probe；有据认可20%耗时下降，保留追问/修正版/finish；无商业推断。',
 'I02':'R-only参与获认可，测量缺证和个人分工自报分开；不得全盘否定。',
 'I03':'虚构履历/吞吐/利润拒绝；范围外M拒引；M行2位置正确仍不支持利润50%。',
 'X01':'坏输入独立失败、PDF全页核对、替换/草稿与当前性传播。',
 'X02':'记忆修订/撤销/删除抑制旧资格正文，保留回答/成本；记忆不作源。',
 'X03':'同键/异体/semantic slot/index竞争恰一次准入与效果，原账保留。',
 'X04':'scope/goal/source/view变化后的晚到抑制当前投影与后继，007事实保留。',
 'X05':'配置/费用/容量/身份/维度/owner发送前拒绝；不以恶意资料授权工具。',
 'X06':'发送后unknown保预留，非法received不授资格，取消不冒远端收回。',
 'X07':'整步query+model预览、逐笔持久门与四账重开不归零。',
 'X08':'COMMIT丢回包先GET原键，向量/回答/feedback一份，GET零调用。',
 'X09':'同normal停后重开保原身份/四账，原已提交处继续；不付费注入unknown。',
 'X10':'删除/currentness/cache/007抑制、原件fence和元数据成本保留。',
 'X11':'迁移/端口/内存/owner失败关闭，不动用户进程/卷，不借旧根重建。',
 'X12':'外发范围、kind/父/空间/只读隔离；无额外供应商或秘密外泄。',
 'P01':'非空升级旧行/NULL工具tokens/预算不变，当前profile精确核验。',
 'P02':'R01永久只读，旧链/旧profile可读且无新索引/执行。',
 'P03':'R02及当前R03按实际profile恢复；向量hash/删除overlay，损坏拒绝，不恢复secret/执行。',
}

actions=[]
pair_ids={}
row_by_id={r['id']:r for r in rows}
def pair(row_id, suffix, verb, source_aliases, literal, parents, expected, local_before=None):
    row=row_by_id[row_id]; label=f'{row_id}.{suffix}'
    query_goal={'Q01':'/inputs/numeric_goal','Q02':'/inputs/numeric_goal','Q03':'/inputs/numeric_goal','Q04':'/inputs/numeric_goal',
        'Q12':'/inputs/numeric_goal','Q05':'/inputs/concept_goal','Q06':'/sources/2/text',
        'Q09':'/inputs/interview_goal','Q11':'/inputs/interview_goal'}.get(row_id,literal)
    shared={'row':row_id,'activity':row['activity'],'source_aliases':source_aliases,'semantic_rubric':expected,
        'scenario_ids':row['scenarios'],'status':'NOT_RUN','actual_business_key':None,'actual_prepared_id':None,
        'actual_typed_request_sha256':None,'actual_payload_bytes_sha256':None,'actual_parent_record_ids':None,
        'process_contract':'EXACT_REQUEST_V2','failure_contract':'ORIGINAL_KEY_STOP_AND_ACCOUNT',
        'local_before':local_before or [],'operator_approval_required':True,'reserve_microunits':250000}
    q={**shared,'id':label+'.query','kind':'query_embedding','action':'query','input_pointer':query_goal,
        'parent_commits_required':parents,'domain_action_after_query':label+'.model','output_tokens':0,
        'output_evidence':['原retrieval命令received/current','007合格512维query向量','retrieval_ref/result_sha256','同head/scope/memory/space'],
        'conditional_cost_ceiling_microunits':price_classes['embedding_shared_absolute_65536']}
    m={**shared,'id':label+'.model','kind':'model','action':verb,'input_pointer':literal,
        'parent_commits_required':parents+[q['id']],'output_tokens':2048,
        'output_evidence':['原operation received及007完整性','typed/schema及严格returned_model','领域COMMIT/current head及引用','逐例rubric与本地计算/理由'],
        'conditional_cost_ceiling_microunits':price_classes['teaching_interview_2048_absolute_65536']}
    actions.extend((q,m));pair_ids[label]=[q['id'],m['id']]

for ordinal in range(6):
    actions.append({'id':f'Q00.batch{ordinal}','row':'Q00','activity':'interview','kind':'source_index_embedding','action':'source_index',
        'source_aliases':[x['alias'] for x in sources],'input_pointer':'sample-fragments.json#/fragments',
        'actual_sorted_fragment_ids':None,'batch_ordinal':ordinal,'actual_business_key':None,
        'parent_commits_required':['八源原文精确导入/ready/version/revision/currentness COMMIT','A2 interview.v2 start(goal=null)及8源scope COMMIT'],
        'all_batch_approvals_before_claim':[f'Q00.batch{n}' for n in range(6)],
        'process_contract':'EXACT_REQUEST_V2','failure_contract':'ORIGINAL_KEY_STOP_AND_ACCOUNT','operator_approval_required':True,
        'output_tokens':0,'reserve_microunits':250000,'conditional_cost_ceiling_microunits':price_classes['embedding_shared_absolute_65536'],
        'output_evidence':['对应batch operation/007/512维向量同COMMIT','index命令完整终态及24个current向量','每批成本原账'],
        'status':'NOT_RUN'})

all_index=[f'Q00.batch{n}' for n in range(6)]
pair('Q01','01','plan',['N'],'/inputs/numeric_goal',all_index+['A1 scope=N及numeric_goal COMMIT'],rubrics['L01'])
pair('Q01','02','exercise(initial)',['N'],'/inputs/numeric_initial_question',['Q01.01.model','accept_path/proposal/node COMMIT'],rubrics['L01'])
# 同一初始题的等价/反例先做，随后长错答成为当前版本，避免回用已失效feedback。
for i in range(3):pair('Q02',f'{i+1:02}','evaluate',['N'],f'/inputs/numeric_positive_answers/{i}',['Q01.02.model','当前题逐版本answer COMMIT'],rubrics['L02'],['kind=initial或revision；后续supersedes指当前答案链末端'])
for i in range(3):pair('Q03',f'{i+1:02}','evaluate',['N'],f'/inputs/numeric_negative_answers/{i}',['Q01.02.model','当前题逐版本answer COMMIT'],rubrics['L03'])
pair('Q04','01','evaluate',['N'],'/inputs/numeric_negative_answers/3',['Q01.02.model','当前题否定answer COMMIT'],rubrics['L04'])
pair('Q04','02','evaluate',['N'],'/inputs/numeric_ambiguous_answer',['Q01.02.model','当前题不确定answer COMMIT'],rubrics['L04'])
pair('Q01','03','evaluate',['N'],'/inputs/numeric_wrong_answer',['Q01.02.model','Q04.02.model','长错答作为当前revision COMMIT'],rubrics['L01'])
actions.append({'id':'Q10.html','row':'Q10','activity':'learning','kind':'html','action':'generate',
    'source_aliases':['N'],'input_pointer':'acceptance-contract.md L10 原固定d/t控件描述；精确描述正文须零费用冻结',
    'actual_description_sha256':None,'parent_commits_required':['Q01.03.model','当前feedback正文/parent/currentness复核'],
    'before':'Q01.04.query','output_tokens':4096,'reserve_microunits':250000,
    'conditional_cost_ceiling_microunits':price_classes['html_4096_absolute_65536'],'operator_approval_required':True,
    'process_contract':'EXACT_REQUEST_V2','failure_contract':'ORIGINAL_KEY_STOP_AND_ACCOUNT',
    'output_evidence':['description/artifact/parent/hash','原host_policy独立许可','真实ACK/读值/PNG/reset/StopProof'],
    'semantic_rubric':rubrics['L10'],'status':'NOT_RUN'})
pair('Q01','04','exercise(continuation)',['N'],'/inputs/targeted_question',['Q01.03.model','Q10.html已保存且教学head未变'],rubrics['L01'])
pair('Q01','05','evaluate',['N'],'/inputs/targeted_answer',['Q01.04.model','当前针对题answer COMMIT'],rubrics['L01'],['针对题可先明确expose reference，正确归assisted，不冒独立证据'])
pair('Q01','06','exercise(retest)',['N'],'/inputs/retest_question',['Q01.05.model'],rubrics['L01'])
pair('Q01','07','evaluate',['N'],'/inputs/retest_answer',['Q01.06.model','未暴露复测answer COMMIT'],rubrics['L01'])
pair('Q12','01','exercise(retest)',['N'],'acceptance-contract.md L05 240米/1分钟',['Q01.07.model','显式保存当前继续理由'],rubrics['L05'])
pair('Q12','02','evaluate',['N'],'acceptance-contract.md L05 4m/s',['Q12.01.model','第二独立题未暴露answer COMMIT'],rubrics['L05'],['同键重交仅GET；exposure/assisted规则引用原已验层，不新增付费复判'])
pair('Q07','01','plan',['J-CODE','J-COFFEE'],'/inputs/ambiguous_goal',['原numeric成果/理由保存','scope=两个Java及ambiguous_goal新版本 COMMIT'],rubrics['L08'])
pair('Q07','02','plan',['J-CODE'],'/inputs/ambiguous_clarification',['Q07.01.model','用户明确clarification；scope仅J-CODE、新goal COMMIT；旧ref失效'],rubrics['L08'])
pair('Q08','01','plan',['N'],'/inputs/no_evidence_query',['新scope=N及no_evidence目标 COMMIT'],rubrics['L09'])
pair('Q08','02','plan',['N','N-CONFLICT'],'/inputs/conflict_query',['Q08.01.model','scope=N+N-CONFLICT及conflict目标新版本 COMMIT'],rubrics['L09'])
pair('Q05','01','plan',['C'],'/inputs/concept_goal',all_index+['A3 scope=C及concept_goal COMMIT'],rubrics['L06'])
pair('Q05','02','exercise(initial)',['C'],'/inputs/concept_goal',['Q05.01.model','accept_path COMMIT'],rubrics['L06'])
for suffix,answer in [('03','concept_positive'),('04','concept_negative'),('05','concept_partial')]:
    pair('Q05',suffix,'evaluate',['C'],'/inputs/'+answer,['Q05.02.model','当前概念题对应answer版本 COMMIT'],rubrics['L06'])
pair('Q06','01','plan',['P'],'/sources/2/text',['概念结果与理由保存；scope=P及P完整原文作为有限goal COMMIT'],rubrics['L07'])
pair('Q06','02','exercise(initial)',['P'],'/sources/2/text',['Q06.01.model','accept_path COMMIT'],rubrics['L07'])
for suffix,answer in [('03','program_positive'),('04','program_negative')]:
    pair('Q06',suffix,'evaluate',['P'],'/inputs/'+answer,['Q06.02.model','当前程序推理题对应answer版本 COMMIT'],rubrics['L07'])
pair('Q09','01','ask(first)',['R'],'/inputs/interview_goal',all_index+['A2 scope改R；goal.target=interview_goal/focus=null及role COMMIT'],rubrics['I02'])
for suffix,answer in [('02','interview_supported_answer'),('03','interview_self_report'),('04','interview_invented_claim')]:
    pair('Q09',suffix,'review',['R'],'/inputs/'+answer,['Q09.01.model','该场当前question及原answer/correct_answer版本 COMMIT'],rubrics['I02']+' '+rubrics['I03'])
for suffix,answer in [('05','interview_self_report'),('06','interview_supported_answer')]:
    pair('Q09',suffix,'review_if_actual_probe',['R'],'/inputs/'+answer,['本轮真实probe已COMMIT且累计≤2','对应probe_answer COMMIT'],rubrics['I02'],['无真实probe则跳过此必要容量预留；不造题或补新回答'])
pair('Q11','01','ask(first)',['R','M'],'/inputs/interview_goal',['Q09本轮结果保存但不finish；同A2正常bind_scope R+M、goal/新轮head COMMIT'],rubrics['I01'])
pair('Q11','02','review',['R','M'],'/inputs/interview_incomplete_answer',['Q11.01.model','incomplete answer COMMIT'],rubrics['I01'],['本次必须产生必要probe；缺失即Must失败，不免费重抽'])
pair('Q11','03','review',['R','M'],'/inputs/interview_invented_claim',['Q11.02.model','实际probe当前question及invented answer COMMIT'],rubrics['I03'])
pair('Q11','04','review',['R','M'],'/inputs/interview_supported_answer',['Q11.03.model','同question当前correct_answer/supported版本 COMMIT'],rubrics['I01'])
pair('Q11','05','review_if_actual_probe',['R','M'],'/inputs/interview_supported_answer',['首个必要probe已占1；真实晚probe已COMMIT且总≤2','对应probe_answer COMMIT'],rubrics['I01'],['最后finish为本地命令；无第二probe则不发此容量预留'])

coverage=[]
for index, action in enumerate(actions):
    action['previous_external_action_commit_required'] = actions[index-1]['id'] if index else None
    action['max_request_bytes'] = 65536
    action['max_response_bytes'] = 65536
    action['expected_endpoint'] = ('https://open.bigmodel.cn/api/paas/v4/embeddings' if action['kind'] in ('query_embedding','source_index_embedding') else 'https://api.deepseek.com/chat/completions')
for scenario in samples['scenarios']:
    covering=[r['id'] for r in rows if scenario in r['scenarios']]
    coverage.append({'id':scenario,'rubric':rubrics[scenario],'row_ids':covering,
        'real_Q_status':'NOT_RUN' if covering else '真实收费语义不是本异常的证明层',
        'inherited_status':'原S及TASK120/TASK121有限关闭范围内继承，历史控制不通过保留',
        'future_layer':('真实provider逐例输出+正常UI/COMMIT；原安全机制不付费重放' if covering else '复用已验零外发/PG/Windows/UI原件；新normal只核实际身份/readiness，不重跑旧修复'),
        'evidence_required':(['typed/payload审批/原键','operation+007+领域COMMIT及currentness','引用位置与语义分开判定','逐例rubric实际结果'] if covering else ['原116 acceptance同编号','TASK121 review02及主控closure scope','新normal相关配置/身份/停止实证；不声称本卡运行'])})

totals={k:sum(r[k] for r in rows) for k in ('model_calls','query_calls','index_calls','html_calls','requests','reserve_microunits','conditional_shared_rate_ceiling_microunits')}
matrix={'schema':'retrolume.task122.remaining-must-matrix.v1','status':'NON_EXECUTABLE_DRAFT_Q_FROZEN','activation_eligible':False,
    'created_at':NOW,'source_matrix_sha256':rawsha(old_path.read_bytes()),'budget_adoption_source':'TASK120/orchestration-20261018/adoption-receipt.json',
    'real_completed_requests':0,'TESTONLY_deducted_requests':0,'global_max_requests':100,'global_max_cost_microunits':25000000,
    'reserve_per_request_microunits':250000,'roster':roster,'rows':rows,'actions_in_recommended_order':actions,'must_coverage':coverage,
    'totals':totals,'remaining_global_requests_after_normal_path':100-totals['requests'],
    'remaining_global_reserve_microunits_after_normal_path':25000000-totals['reserve_microunits'],
    'order_note':'初始题先完成Q02/Q03/Q04各精确答案版本，再以长错答成为当前版本走Q01错答→Q10→针对→复测→Q12；不在换题后回用旧feedback。其余每次新goal/scope须重建新query。',
    'normal_worst_scope':'仅冻结全部Must及原两轮最多各2个必要probe；模型不合rubric、额外问答、缓存失效或失败不保证余量。',
    'EXACT_REQUEST_V2':{
        'preconditions':['同一normal实例/原grant/固定活动；source/version/revision/space/currentness核齐','前一父领域及007真实COMMIT；未合格received不作父','query仅精确固定goal，不把派生字符串作任意query授权'],
        'freeze':['业务键与完整规范正文先持久保存','typed request、payload对象、canonical实际UTF8 bytes、provenance、endpoint/model/service/templates、head/scope/memory/binding一并冻结'],
        'operator':['本机inspect完整正文/字节及来源','按该prepared SHA256明确APPROVE；每批分别批准','批准不调用；GET原命令核状态后UI显式原键继续'],
        'success':['生产PG逐笔admit/mark/预扣COMMIT','最多一次transport；received+007+领域/向量结果合格COMMIT','GET当前资格后才推进下一动作；用户明确继续'],
        'privacy':['批准正文只在受信本机查看','无聊天密钥/DSN/整份账单；无本人资料或任意新memory']},
    'ORIGINAL_KEY_STOP_AND_ACCOUNT':{
        'accepted_unclaimed':'GET原键确认未claim且资格完整，精确重审/续批后用户显式继续原键原体',
        'claimed_unknown':'只读对账并停止该依赖，不续批重发，不换业务键绕UNKNOWN',
        'commit_ack_lost':'GET原command/operation/007/领域head，已COMMIT不重复提交；不存在/不明不猜成功',
        'bad_received':'保留收到事实及预扣，typed/identity/schema/semantic不合格不授父资格',
        'accounting':'准入后失败、not_sent、超时、UNKNOWN占原250000；无自动退款/重试。A2正常最坏已28/28，任何额外必要调用即精确报缺口并停。',
        'forbidden':['跨活动借分额','新grant/roster/数据库清账','恢复旧13元/TESTONLY余额','删Must或伪造已成功']},
    'cache_conditions':['同一真实source_id/version/revision/original/fragment bytes','同provider/configured_model/dimensions=512/space/recipe',
        '向量及PG摘要可核且无tombstone/currentness失效','八源一次注册导入，A1/A3复用A2已提交源向量；本卡无现存缓存证明，首次按全miss',
        'query只在原业务键完整body/head/parents/memory绑定不变时GET复用；跨动作同字不缓存'],
    'zero_fee_freeze_before_first_send':['24片真实ID/排序/批次；若不是24即时重算，不截断原文','HTML固定d/t描述和继续理由的确切有限文字/用途绑定',
        '所有未来typed/payload和operator principal在获准真实normal中冻结；本草案不伪造ID/哈希','正常T0/72h未开始；本卡不产生可用grant']}
save('remaining-must-matrix.json',matrix)
save('cost-calculation.json',{'created_at':NOW,'status':'CONDITIONAL_ARITHMETIC_ONLY_NOT_APPLICABLE_ACCOUNT_QUOTE',
    'currency_candidate':'CNY','microunits_per_CNY':1000000,'price_sources':['https://api-docs.deepseek.com/zh-cn/quick_start/pricing/','https://docs.bigmodel.cn/cn/guide/models/embedding/embedding-3'],
    'public_rates':{'DS_peak_cache_hit':'0.04','DS_peak_cache_miss':'2','DS_peak_output':'8','Embedding3_input':'0.5'},
    'formula':'ceil(((request_bytes+framing)*input_CNY_per_million+max_output_tokens*output_CNY_per_million)*1.25)',
    'conditions_not_verified':['完整输入token≤精确JSON线上bytes+framing','framing≤4096','thinking disabled额外计费上界','实际CNY含税最高价/无未知追加收费'],
    'framing_4096_status':'原设计可表达上限，绝非官方证明','classes_microunits':price_classes,
    'per_request_reservation':250000,'class_formal_comparisons':{k:{'ceiling':v,'below_reservation':v<=250000} for k,v in price_classes.items()},
    'matrix_totals':totals,'roster':roster,'actual_applicable_per_request_ceiling':None,
    'fallback_using_context_cap_only':{'model_context_tokens':1048576,'input_only_common_ceiling_microunits':int((Decimal(1048576)*2*Decimal('1.25')).to_integral_value(rounding=ROUND_CEILING)),
        'passes_250000':False,'meaning':'仅用官方1M上下文作上界已不足；不能据此绕过缺失的token/framing证明'},
    'real_paid_calls':0,'real_paid_cost_microunits':0})

draft={'schema':'retrolume.task122.preparation-draft.v1','enabled':False,'loadable_by_product':False,'activation_eligible':False,
    'actual_grant':None,'actual_manifest':None,'actual_binding':None,'actual_operator_approval':None,
    'actual_activation_receipt':None,'T0':None,'valid_until_utc':None,
    'adopted_budget':{'global_requests':100,'global_cost_microunits':25000000,'per_request':250000,'roster':adoption['roster']},
    'candidate_resource':{'created':False,'normal_name':'retrolume-q-first-normal','database_name':'retrolume_q_first_normal',
        'volume_name':'retrolume-q-first-normal-data','pg_loopback_port_candidate':55482,'api_loopback_port_candidate':18122,
        'ports_current_availability':'UNKNOWN_NOT_PROBED','image_candidate':'sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f',
        'image_cache_current':'UNKNOWN_NOT_PROBED','pg_cpu':1,'pg_memory_MiB':512,'pg_pids_limit':128,'restart':'no','bind_host':'127.0.0.1',
        'normal_profile_candidate':'data_exit.v1.r03','exact_CID':None,'cluster_system_identifier':None,'database_oid':None,
        'data_root':None,'backup_root':None,'restore_root':None,'control_root':None,'operator_principals':None,
        'one_pg_ledger_for_both_providers_and_all_three_activities':True,'old_TESTONLY_resources_eligible':False,
        'resource_permission':'仅后续主控精确资源/日历/工具wall/持有许可生效后创建；不继承TASK120根数或96h'},
    'activity_configuration_outline':{'not_a_loader_configuration':True,'provider':'deepseek_chat_completions','model':'deepseek-flash',
        'base_url':'https://api.deepseek.com','thinking':'disabled','api_key_env':'RETROLUME_MODEL_API_KEY',
        'activity_defaults':{'deadline_hours':24,'max_running_seconds':3600,'reserve_cost_microunits':250000,'max_request_bytes':65536,
            'max_output_tokens':4096,'max_requests':48,'max_cost_microunits':12000000,'allowed_tools':['finite_calculate'],'max_tool_calls':8},
        'roster_limit_note':'正常create_activity从受信v2 grant按固定UUID覆盖48/28/24及12/7/6元；无需逐活动改defaults。未绑定grant的活动不能事后换绑。',
        'service':{'timeout_seconds':10,'max_output_tokens_limit':4096,'max_request_bytes':65536,'max_response_bytes':65536,'returned_models':[]},
        'learning':{'profile':'learning.v2','max_output_tokens':256},'teaching':{'profile':'teaching.v3','max_output_tokens':2048,'enable_calculation':True},
        'interview':{'profile':'interview.v2','max_output_tokens':2048,'max_followups_per_round':2},
        'html':{'profile':'html_explanation.v2','max_output_tokens':4096},'memory_context':None,
        'candidate_returned_model_allowlist':['deepseek-flash'],'allowlist_verification':'公开示例仅候选，实际账号返回身份尚未核'},
    'price_snapshot_outline':{'status':'draft','enabled':False,'currency':None,'tax_inclusive':None,'applicable_entity':None,
        'input_rate_cny_per_million':None,'output_rate_cny_per_million':None,'framing_token_upper_bound':None,
        'token_upper_bound_verified':False,'capabilities_verified':False,'account_terms_verified':False,
        'additional_reasoning_upper_bound':None,'expires_at':None,'price_snapshot_sha256':None},
    'activation_body_outline':{'status':'draft','enabled':False,'issuing_task':None,'stage':'Q-preparation-only',
        'approved_receipt_sha256':rawsha((ROOT/'DocuN/evidence/TASK-120/orchestration-20261018/adoption-receipt.json').read_bytes()),
        'source_manifest_sha256':None,'price_snapshot_sha256':None,'instance_binding_sha256':None,
        'independent_audit_result_sha256':None,'normal_readiness_evidence_sha256':None,'matrix_sha256':None,'valid_from_utc':None,'valid_until_utc':None},
    'digest_order':['固定正常资源真实binding及模板/derivation policy','冻结24片manifest及fixed_inputs，计算canonical manifest摘要',
        '固定适用price原文件bytes摘要','主控真实首次activation body只引用前序对象及独审/readiness/matrix，不含grant/root自身摘要',
        'grant引用activation原文件bytes摘要、manifest canonical摘要、price原文件bytes摘要及binding canonical摘要',
        'root bundle含grant/manifest/binding/templates/atoms/operator principals，部署绑定记录再并列所有摘要',
        '每个prepared完成后DecisionBody先在锁内固定event_seq/clock再摘要得approval_id，不把approval_id放回其自身输入']}
save('deployment-package.draft.json',draft)
integration=json.loads((ROOT/'config/integration.example.json').read_text(encoding='utf-8'))
integration['enabled']=False
save('integration.disabled.draft.json',integration)
save('q-approval.disabled.draft.json',json.loads((ROOT/'config/q-approval.example.json').read_text(encoding='utf-8')))
save('account-attestation.draft.json',{'schema':'retrolume.task122.account-facts-draft.v1','enabled':False,'status':'UNVERIFIED',
    'record_values_locally_only':'只需非敏感事实。不得填写key/DSN/验证码/账单全文/个人截图/账号登录信息。',
    'providers':[{'provider':p,'nonsecret_account_alias':None,'region_and_legal_entity':None,'model_permission':None,
        'prepaid_balance_sufficient_for_fixed_budget':None,'billing_currency':None,'tax_inclusive':None,
        'applicable_max_input_CNY_per_million':None,'applicable_max_output_CNY_per_million':None,
        'cache_miss_highest_used':None,'extra_reasoning_or_other_fees_upper_bound':None,'input_output_rights_confirmed':None,
        'training_and_retention_contract_reference':None,'training_optout_applies_to_API':None,'exact_API_retention':None,
        'official_current_tokenizer_and_template_binding_reference':None,'attested_at':None,'attested_by_nonsecret_role':None}
        for p in ('deepseek_chat_completions/deepseek-flash','zhipu_embeddings/embedding-3')]})
print(json.dumps({'created_at':NOW,'fragments':len(fragments),'index_calls':6,'max_item_utf8_bytes':max(x['utf8_bytes'] for x in fragments),
    'max_any_four_payload_bytes':batch_wire_upper,'totals':totals,'roster':roster,'actions':len(actions),'price_classes':price_classes},ensure_ascii=False,indent=2))
