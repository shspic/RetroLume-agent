"""首push真实核对成功后保存收尾控制记录；不自行推送。"""
from delivery import *
import math

d=json.loads((E/'first-delivery.json').read_text('utf-8'))
assert d['identity_match'] and d['push_exit']==0
changed=git('-c','core.preloadIndex=false','diff-files','--name-only','-z').decode('utf-8').strip('\0').split('\0')
new=git('ls-files','--others','--exclude-standard','-z').decode('utf-8').strip('\0').split('\0')
delta=[p for p in changed+new if p]
assert all(p.startswith('DocuN/evidence/TASK-130/') or p=='DocuN/results/TASK-130-result.md' for p in delta), delta
assert not git('ls-files','--cached','--ignored','--exclude-standard','-z')
save('control-delta.json',{'at':now(),'paths':delta,'only_task130_controls':True,'note':'主体push后只有本卡首push回执、控制及收尾报告增量；本次自然收尾普通提交后不再为记录tip循环写文件。'})
issued=dt.datetime.fromisoformat('2026-10-23T12:44:20.263251+08:00')
elapsed=math.ceil((dt.datetime.fromisoformat(now())-issued).total_seconds()/60)*60
save('budget-close.json',{'at':now(),'precise_tool_seconds':'unknown','conservative_used_seconds':elapsed,'basis':'保守把permit签发以来全部墙钟时间上取整至分钟计入，早于实际接收，不把精确未知写0','total_seconds':5400,'remaining_including_final_operations':5400-elapsed,'final_operation_reserve_seconds':600,'calendar_until':'2026-10-24T12:44:20.263251+08:00','product_runtime':0,'provider_calls':0,'fees':0,'Q':'FROZEN'})
p=ROOT/'DocuN/results/TASK-130-result.md';text=p.read_text('utf-8')
text=text.replace('两份安装说明已收口，全部未忽略候选已完成普通Review；当前正在进行本地提交与指定GitHub同步，真实回执在下方追加。本记录不签产品、父STEP或发布通过。','两份安装说明已收口；全部未忽略项目候选已完成普通Review并提交至指定GitHub仓库main，主体快照实际远端commit/tree均核对一致。首push回执和本结果按任务卡纳入一次普通收尾提交，最终tip由回返消息及远端main核对。本记录不签产品、父STEP或发布通过。')
text+='\n## 首次提交及真实推送核对\n\n'
text+=f"{now()}。本地主体commit为{d['commit']}，tree为{d['tree']}，parent为{d['parent']}，分支main，origin为{d['remote']}。普通commit退出0，共3459文件变化；push退出0，实际ls-remote main指向该commit，再fetch取回的commit/tree分别与上述本地对象相同。见first-delivery.json及git-commands.jsonl。没有未推送的主体成果，没有新远端冲突。\n\n"
text+='3451项产品/测试/配置/DocuS及既有差异原字节保护检查全部一致，见worktree-preservation.json。主体push后差异仅本卡控制记录，见control-delta.json；未忽略项目文件没有另行排除。tracked-ignored始终为空。\n\n'
text+='补充真实操作限制。沙箱write-tree一次退出128，index.lock Permission denied，经正常权限申请后相同Git写操作及commit成功；属于权限边界，不是自动审批拒绝。初始fetch最终退出0，network-initial.json的unknown是当时观察，现已补齐。只读查询的主动中止、辅助脚本两次错误及误触只读重扫不改为成功，也未重置预算。没有第二次push恢复或强推。\n\n'
text+=f'完整精确工具投入unknown；保守按permit签发至本段写入的全部墙钟时间上取整计{elapsed}/5400秒，余{5400-elapsed}秒含600秒收尾保留，实际收尾Git操作继续占用此余量。见budget-close.json。日历未到限，旧任务投入及失败全部封存不变。\n\n'
text+='本文件、首push真实回执及控制增量只做一次普通收尾提交，最终远端tip在回返消息提供，主控可直接从Git对象核对该tip的父提交和tree。为避免自指，不在文件中填入包含本文件最终内容的commit/hash，也不再为最终tip追加第三次提交。此控制记录例外不扩张为遗漏其它未忽略文件。必要用户操作无；请主控读取本结果并维护唯一状态及CHG。\n'
p.write_text(text,encoding='utf-8')
print('report saved',d['commit'],d['tree'],'budget',elapsed,flush=True)
