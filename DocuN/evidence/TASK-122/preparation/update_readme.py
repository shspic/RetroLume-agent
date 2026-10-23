"""只改本卡允许的README段落，保留其余原字节并保存差异。"""
from pathlib import Path
import difflib
import hashlib
import json

ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).resolve().parent
before=(OUT/'README.before.bin').read_bytes()
target=ROOT/'README.md'
if target.read_bytes()!=before:
    raise SystemExit('README在本卡备份后已变化，停止覆盖')
changes=[
('本目录为 RetroLume 本地工程，提供资料、学习、文字面试、低信任记忆和隔离只读恢复入口。STEP018 的混合检索集成仍在 TASK117 合成候选收口中；实际验收状态以 [执行动态文档](DocuS/执行动态文档.MD) 为准。合成传输与真实供应商语义分别验证。',
 '本目录为 RetroLume 本地工程，提供资料、学习、文字面试、低信任记忆和隔离只读恢复入口。STEP018 的 Q v2 有限工程切片已验收关闭，真实供应商语义仍待前置核齐后的有限验证；实际验收状态以 [执行动态文档](DocuS/执行动态文档.MD) 为准。'),
('TASK117 S08已形成四项缺陷修正的合成工程候选，正式bundle8完成八项定向浏览器检查；等待原TASK118增量独审，Q继续冻结。已有PG、恢复、PDF和固定预览证据按原版本继承，本轮未重跑这些业务链，也未启用真实供应商或费用。',
 '2026-10-21，主控已关闭 TASK120 有限工程交付并接受 TASK121 review02 的五项关闭结论；历史执行控制不通过保留。Q 从未正式启用，T0/72小时尚未开始，真实调用与费用仍为0。TASK122只整理启用前置和操作包，账号、计量及正常部署门未核齐时继续关闭。下列TASK117/S06说明保留其历史适用范围。'),
('grant 的 `source_manifest_sha256` 绑定 `retrolume.outbound-sources.v1` 规范JSON摘要，清单另保留冻结设计样本摘要；',
 '当前Q v2的grant以 `source_manifest_sha256` 绑定 `retrolume.outbound-sources.v2` 规范JSON摘要；旧v1清单只在其原兼容边界适用。清单另保留冻结设计样本摘要；'),
('当前TASK117的Q未启用。', '当前Q仍未启用。后续S08的 `model_requests` 说明属于v1历史边界；当前v2使用本机逐请求精确批准。')]
after=before
for old,new in changes:
    old_bytes=old.encode('utf-8')
    if after.count(old_bytes)!=1:raise SystemExit('README目标段落不是唯一匹配，停止覆盖')
    after=after.replace(old_bytes,new.encode('utf-8'),1)
newline=b'\r\n' if b'\r\n' in before else b'\n'
extra='''

真实启用须先核当前官方能力、账号适用含税价、token/framing/额外计费上界、严格返回身份、正常服务器非敏感readiness及新normal绑定，再由主控保存首次启用回执。两个provider共用唯一100次/25元条件额度，三个固定活动分额48/28/24次及12/7/6元；示例配置、密钥存在、TESTONLY通过和本地批准都不代替该回执。

正常operator使用同一受信本机身份，先inspect本次完整请求与实际字节，再交互输入精确APPROVE摘要，返回原页面GET核对并明确继续原键。已claim、可能已发或UNKNOWN只读对账；不得换key、重新批准重发或清空预算。部署配置与两个provider密钥只经正常服务器安全环境注入，不发送到聊天或浏览器。

当前准备成果、正常配置字段、已知readiness缺口、默认关闭草案及一次后续操作包见 [TASK122前置结果](D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-122-result.md) 与 [后续操作包](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-122/preparation/operation-runbook.md)。这些文档不创建资源、不启用Q；旧TESTONLY库、runner和运行许可继续封存。
'''
after+=extra.strip('\n').replace('\n',newline.decode()).encode('utf-8').join([newline+newline,b''])
target.write_bytes(after)
diff=''.join(difflib.unified_diff(before.decode('utf-8-sig').splitlines(keepends=True),after.decode('utf-8-sig').splitlines(keepends=True),fromfile='README.before',tofile='README.after'))
(OUT/'README.diff').write_text(diff,encoding='utf-8')
record={'before_sha256':hashlib.sha256(before).hexdigest(),'after_sha256':hashlib.sha256(after).hexdigest(),
    'before_bytes':len(before),'after_bytes':len(after),'replacement_count':len(changes),'other_original_bytes_preserved':True}
(OUT/'README-change.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(record,ensure_ascii=False,indent=2))
