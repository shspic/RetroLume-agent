"""串行保存编排复盘裁定。原文保留为字节后缀，不改产品或执行者原件。"""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import hashlib
import json
import re

ROOT=Path('D:/shspic/project_NO3_RetroLume-agent')
OUT=Path(__file__).resolve().parent
timestamp=datetime.now(timezone(timedelta(hours=8))).isoformat()
review='DocuN/results/TASK-111-root-cause-review.md'
review_link='[完整根因复盘](D:/shspic/project_NO3_RetroLume-agent/'+review+')'

prefixes={
'DocuN/results/TASK-111-work-decision.md':f'''# TASK-111 / R-105 根因复盘裁定，暂停沿旧卡续跑

{timestamp}，Codex编排Agent。按用户最新要求先从108—111复盘原因，再判断是否继续。已回收C02及PG增量01，结果75828字节/31a88d3f…、交付66源及七规则指纹匹配。调度已返回，完整验收不通过；本轮没有新增执行许可或额度，没有派审计或新任务。

已定位DEF-027/P1。renderer-host.cjs:53把runtime当String.replace的字符串模板，runtime.cjs:51含美元符加单引号，导致固定脚本插入HTML结束标签。三个构建上下文均相同，15586字节脚本经实际替换语义只剩3352字节首script，CSP哈希不匹配。当前wait候选未修此根因。旧A类日志为Runtime undefined，本轮B类确定字节推导不冒浏览器复跑。

110有限数据与固定renderer方向已获采用且有109反证依据，维持有效。108无已证锚的强承诺、111过早铺开全链和错配的分类/次数门、执行层夹具/进程/配置错误共同造成往返。编排承担不合理顺序及预算设计责任，不能再只加一次PG或延长等待。

当前镜像3/3、主browser3/3、PG start7/7、model合成6/6；根8/9、Windows6/8、preview create4/14/start2/14。剩余10个preview不能容纳当前计划的2正常加10独立故障，且c02_faults仍未实现完整故障入口。新旧失败、费用13元及投入均保留，未用余额不自动恢复旧runner。

本轮精确PG与两个已启动preview只读核证均Exited/Pid0/no restart。正常ready/ACK/PNG及完整故障未验，G11/SEC003/B01/STEP/M1/项目不放行。事务回滚、权限拒绝、有限升级与生成子事实按对象版本保留，不再重跑充分部分。

下一合同须先定位修复与实际组装字节核对，再以最终镜像取得最小真实闭环，随后正确绑定合成活动、补完整UI和故障矩阵；全面核算资源与普通修正余量。按用户要求本轮只保存复盘和冻结通知，不发新执行卡，不要求重新批准110。详见{review_link}。原111执行者结果及原件不改，以下旧裁定保留原字节，仅为历史。

## 以下为先前裁定历史

''',
'DocuN/tasks/TASK-111.md':f'''# TASK-111 / R-105 旧执行入口冻结通知

{timestamp}，编排依据用户最新要求完成根因复盘。续作02与PG增量01已经返回并停止，旧镜像、主browser、PG及合成模型次数已到限；剩余额度不能满足完整剩余矩阵。本页下方旧许可为历史，不是重新启动runner的现行授权。

新发现DEF-027/P1，宿主实际页面组装损坏固定脚本，当前wait候选未解决。{review_link}保存原因、版本、证据和下次继续条件。本轮没有新许可、新预算或待转交执行任务；待编排形成自洽的新有效合同后才可续作，同TASK/R及旧失败投入保持。禁止照下方旧入口重试。

## 以下为已执行合同的完整历史

''',
'DocuS/架构动态文档.MD':f'''# 架构动态文档

文档v1.14，2026-10-10，Asia/Shanghai。需求v1.2、执行动态v2.36、task_model/07。以下v1.13及原历史保留。110采用保持，111未通过完整验证。

## G11固定renderer组装缺陷已定位，运行候选不放行

编排复盘发现DEF-027/P1。renderer-host的字符串replacement解释了runtime源码中的美元符加单引号，将HTML尾部插进脚本；v2-01/02/03构建字节均受影响。完整15586字节脚本变成3352字节首script，与CSP完整hash不符。两个真实启动在trusted_frame报Runtime undefined；当前附加等待仍保留同一缺陷，未构建未验证。此为代码与规范证据，不冒修后动态通过。

Python编译器字面替换与Node宿主实际组装未做等价核证，既有离线数值/descriptor和manifest正确不覆盖最终页面。后续在实际组装边界核字节与CSP后才做最小真实计算/ACK/PNG/停止，保固定程序、有限输入、sandbox和外部停止，不需恢复109任意脚本或再换引擎。

C02已取得最终模板的有限生成、Global/HostJob及Reaper实际PID关联、权限拒绝、hook同COMMIT回滚/UNKNOWN无artifact与部分升级拒绝证据。升级只证旧数据字段与旧主体ACL不变，新HTML owner九项SELECT如实登记；不宣raw ACL字节不变或该升级库001—012全原迁移重跑。两个启动失败对象有精确结束组合，未达到ready后完整工作树或M11全部故障验收。

活动预览预算config绑定image/load。新部署复用旧活动被拒是现状，不能重置持久次数或关身份校验造通过；最终镜像后须准备正确绑定的合成活动，跨部署旧活动兼容仍需明确边界。c02_faults仍只实现normal_http，不是完整故障入口。资源/次数错配与旧方案调整评估见{review_link}。

产品3次/180秒、reserve30—60、ready8/D-10、未知保留预扣、隔离与集中独立终审不降。没有改变主要模型或批准新资源；生产HTML默认关闭，旧充分G3—G10保持。Linux/Nginx与发布未提前放行。

## 以下为v1.13及更早历史

''',
'DocuS/执行动态文档.MD':f'''# 执行动态文档

文档v2.36，2026-10-10，Asia/Shanghai。唯一总状态账；需求v1.2、架构v1.14、task_model/07。以下v2.35及原历史保留。

## 111已返回，根因复盘完成，旧卡冻结且未发新卡

TASK111/R105续作02与PG增量01已真实执行并返回，纠正旧待转交状态。结果75828字节/SHA31a88d3f1ca1b724225eaafa33ca685a2eb526a88cb9082cd1b1b8692b32476c与收据一致，66项交付源及七规则匹配。代码轴存在新确定P1 DEF-027，证据轴部分有效且正常ready/ACK/PNG为未通过，控制轴旧超限/等待/夹具偏差均保留；整卡不验收通过、不派完整独立终审。

DEF-027为renderer-host.cjs:53固定脚本的字符串替换缺陷，runtime.cjs:51触发特殊替换，把结束标签插到脚本中间；三个构建上下文全有，15586→3352字节首script且CSP hash不符。现成两次启动报Runtime undefined，现有等待候选未修根因。详细B类推导、as-run对应和原规范见{review_link}，主控没有修产品或跑产品验证。

用户要求先从头复盘再编排。本轮已完成108未证前提、109真实反证、110合理且已批准转向、111实施/夹具和不合理预算顺序的复盘；编排承担分类硬门、前置顺序及资源余量未成套核算责任。不再只加一次启动或延时。旧111卡加冻结通知，所有旧合同/失败/证据保留；新运行许可0、实际派发0、TASK112未占。

实际累计根8/9、image build3/3、PG start7/7（执行窗口用户明确只加同一CID一次已用）、API3/4、主browser3/3、model合成6/6、Windows6/8、frontend2/3、preview create4/14/start2/14、Reaper验证2/3、HTTP156/5000、PNG/input0。旧global78加新8为86真实入口，不是86通过。已计real6541.282、offline200.828、cleanup44.4247405秒；旧分类unknown/超限和重叠口径及13元费用不清零。执行计划尚需2正常加10独立故障，10个余下preview连基线都不足，旧根/时间余额不能放宽其它硬限。

有限有效成果保留两项最终模板生成、离线计算/数据拒绝、权限拒绝、真实同事务回滚与UNKNOWN无artifact、限定非空升级和前置拒绝。v2-02/03两个容器实际启动失败均已退出，namespace早期及外部结束证据不签ready后的完整M11。当前精确PG1791a2d0…、preview03/14均Running=false/Pid0/restart0。只读停止核查未触其它容器，无新业务/构建/数据库/浏览器动作。

下一次仍沿TASK111/R105，先编成有根因、正确对象绑定、完整剩余方法和成套预算的新有效合同；修实际组装→最小真实renderer闭环→同最终镜像集成及故障→稳定完整成果一次隔离终审。旧window若上下文混淆可由新同等A+承接，失败和预算不重置。本轮未发该卡，不要求重批110，不宣G11/STEP015016/B01/SEC003/M1/项目通过。

本批CHG1170—1178，下一1179。证据DocuN/evidence/TASK-111/orchestration-review-03/，本次只读源码/证据/精确资源元数据与维护共享文档。公开规则未改，原始需求及执行者报告原件未改。

## 以下为v2.35及更早历史

'''
}

pre=OUT/'before-documents'
pre.mkdir(exist_ok=False)
saved={}
for rel in prefixes:
    path=ROOT/rel
    old=path.read_bytes()
    if b'root-cause-review.md' in old[:1600]:
        raise RuntimeError('本轮已保存，禁止重复置顶')
    saved[rel]=old
    (pre/rel.replace('/','__')).write_bytes(old)
change=ROOT/'DocuS/文档变更记录.MD'
change_before=change.read_bytes()
if b'CHG-1170' in change_before:
    raise RuntimeError('CHG编号已有归属')
(pre/'DocuS__文档变更记录.MD').write_bytes(change_before)

for rel, prefix in prefixes.items():
    path=ROOT/rel
    if path.read_bytes()!=saved[rel]:
        raise RuntimeError('共享文档在写入前改变')
    path.write_bytes(prefix.replace('\n','\r\n').encode('utf-8')+saved[rel])

entries=[
('DocuN/evidence/TASK-111/orchestration-review-03/trace_review.py','只读核证脚本，非产品测试；另有同目录record_review.py维护写入及字节保全。'),
('DocuN/evidence/TASK-111/orchestration-review-03/review-evidence.json','结果/66源/七规则匹配；三个as-built上下文与确定字符串推导，DEF-027根因。'),
('DocuN/evidence/TASK-111/orchestration-review-03/resource-metadata.json','同一精确PG与两个preview均Stopped，只读，不签完整工作树证明。'),
(review,'按用户要求复盘108—111方案、代码和控制原因；新P1与实际继续条件，不追加许可。'),
('DocuN/results/TASK-111-work-decision.md','接收C02和用户同CID一次PG增量事实；部分验收、DEF-027开放、停止盲续卡。'),
('DocuN/tasks/TASK-111.md','旧执行入口冻结通知；完整原卡保字节，新运行授权0。'),
('DocuS/架构动态文档.MD','v1.14记录组装缺陷、有限已证及正确对象绑定；110采用/隔离不变。'),
('DocuS/执行动态文档.MD','v2.36唯一状态账，111已返回、完整不通过；全部真实计数历史保留，新卡未发。'),
('DocuN/evidence/TASK-111/orchestration-review-03/delivery-proof.json','文档完整性、历史字节后缀、结果和源未改的一次交付核证。')]
append='\r\n'+''.join(f'\r\n- CHG-{1170+i:04d}，{timestamp}，Codex编排Agent，{rel}。{reason}\r\n' for i,(rel,reason) in enumerate(entries))
if change.read_bytes()!=change_before:
    raise RuntimeError('变更账在写入前改变')
change.write_bytes(change_before+append.encode('utf-8'))

def fingerprint(path):
    data=path.read_bytes()
    return {'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}

doc_checks=[]
for rel, prefix in prefixes.items():
    data=(ROOT/rel).read_bytes()
    ok=data.endswith(saved[rel])
    if not ok:raise RuntimeError('历史字节未保全')
    doc_checks.append({'path':rel,**fingerprint(ROOT/rel),'old_suffix_unchanged':ok})

body=(ROOT/review).read_text(encoding='utf-8')
local_links=re.findall(r'\]\((D:/[^)]+)\)',body)
for linked in local_links:
    target=re.sub(r':\d+$','',linked)
    if not Path(target).is_file():raise RuntimeError('报告引用文件不存在 '+target)
evidence=json.loads((OUT/'review-evidence.json').read_text(encoding='utf-8'))
source_ok=all(fingerprint(Path(r['path']))['sha256']==r['sha256'] for r in evidence['returned_sources'])
result_ok=fingerprint(ROOT/'DocuN/results/TASK-111-result.md')['sha256']==evidence['report']['sha256']
if not source_ok or not result_ok:raise RuntimeError('产品或执行者报告漂移')
proof={'at':timestamp,'documents':doc_checks,'review':fingerprint(ROOT/review),
       'local_report_links_checked':len(local_links),'legacy_changelog_prefix_unchanged':change.read_bytes().startswith(change_before),
       'result_unchanged':result_ok,'returned_sources_unchanged':source_ok,'source_count':len(evidence['returned_sources']),
       'new_execution_permit':False,'product_tests':0,'product_writes':0,'new_task_card_issued':False,
       'CHG_first':1170,'CHG_last':1178,'next_CHG':1179}
(OUT/'delivery-proof.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(proof,ensure_ascii=False))
