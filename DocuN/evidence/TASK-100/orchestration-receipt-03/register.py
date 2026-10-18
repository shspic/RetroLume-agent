"""串行登记回收与独立审计卡；无产品或测试执行。"""
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import sys

sys.stdout.reconfigure(encoding='utf-8')
ROOT = Path('D:/shspic/project_NO3_RetroLume-agent')
OUT = Path(__file__).parent
BASE = ROOT / 'DocuN/evidence/TASK-100/continuation-02'
AUDIT = ROOT / 'DocuN/evidence/TASK-101'
STATE = ROOT / 'DocuS/执行动态文档.MD'
ARCH = ROOT / 'DocuS/架构动态文档.MD'
LOG = ROOT / 'DocuS/文档变更记录.MD'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def stamp():
    return datetime.now(timezone(timedelta(hours=8))).isoformat()


def load(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def prepend(path, text):
    before = path.read_bytes()
    backup = OUT / 'before' / path.relative_to(ROOT)
    backup.parent.mkdir(parents=True, exist_ok=True)
    if backup.exists():
        raise RuntimeError('已有维护前副本，不重复写共享文档')
    backup.write_bytes(before)
    if path.read_bytes() != before:
        raise RuntimeError('并行变化：' + str(path))
    path.write_bytes(text.encode('utf-8') + before)


def register():
    if (ROOT / 'DocuN/tasks/TASK-101.md').exists() or (ROOT / 'DocuN/results/TASK-101-result.md').exists():
        raise RuntimeError('101已占用，停止重复出卡')
    receipt = load(OUT / 'receipt.json')
    if any(item['sha256'] != item['expected_sha256'] for name in ('sources', 'evidence', 'rules') for item in receipt[name]):
        raise RuntimeError('当前对象身份不匹配')
    if not all(item['ok_found'] for item in receipt['raw_methods']):
        raise RuntimeError('方法原始通过记录有缺口')
    for item in receipt['sources']:
        if sha(ROOT / item['path']) != item['sha256']:
            raise RuntimeError('产品或夹具在回收后发生变化：' + item['path'])
    if '文档 v2.03' not in STATE.read_text(encoding='utf-8-sig')[:150]:
        raise RuntimeError('唯一共享状态不是预期v2.03')
    old_card = ROOT / 'DocuN/tasks/TASK-100.md'
    snapshot_card = OUT / 'TASK-100-card-as-returned.md'
    snapshot_card.write_bytes(old_card.read_bytes())
    limits = receipt['limits']
    counts = receipt['counts']
    guide = """# TASK-100 / R-094 续作02回收裁定（2026-10-05，当前）

调度已返回；本轮编排验收部分通过，接受最终候选、逐项有限运行证据与资源收尾，不签G8或完整父STEP。执行者原结果和六个原批FAIL全部保留。不是独立审计结论。

112项源码/夹具/dist当前hash与最终身份一致；657证据逐文件匹配；七锁定规则一致。原始stderr可找到29个不同PG方法、4个HTTP方法的OK，最终离线原日志为58项/0skip/OK。原生页面/截图/收据五项hash一致；构建与四个dist绑定在最终身份。接收的是这些事实，不据文件名或汇总表声称整链总批PASS。

六入口包括一次只读预检拒绝，原失败保留。执行者登记三项追加许可，批准前旧账hash相符，中文原文可读；具体授权时序、各进入口及主动尾段不确定性由101控制轴独立核证。最终账entry6/6、container-start5/5、app3/3、SUP21/24、browser3/3、driver3/3、build1/1，离线42.750/真实261.211/收尾33.313秒；主动13643.959秒是分段账口径，不抹去旧尾段未知、初轮至少9入口及漏5.940秒、续作01的4入口与旧投入。

本轮只读精确Docker State显示Running=false/Pid=0；18100/55442无监听，未发现task100运行进程。该事实是检查时点，不代替执行者各批树与Job原件。库、角色、卷、合成行和旧证据保留，编排没有启停/连接数据库或执行测试。

DEF003—007按原归属登记候选修正，正式关闭待101集中审计。修后task100-browser.cjs及两份辅助夹具未真实整批重跑；原DOM/截图/收据与源码一致性可作限定补证，是否充足由101独立决定。逐进程as-loaded与Chromium后代出生时间未采，不虚构；不自动把不同证据粒度变成新规格。

下一101/R095为G8稳定完整成果一次集中独立审计，独立于100实现窗口，代码/证据/控制三个轴同卡完成。默认只读，必要时最多一次仅最终bundle的合成浏览器显示补证，PG/DDL/Docker启停/产品服务/Windows业务/SUP/模型/工具/build全部0，不借用100剩余SUP或旧许可。无需再跑main-combo或已验17窗。

101未收到原生转交或开始事实前仅待转交。完整G8、真实provider质量、全部STEP009—012、M-1、部署与项目仍未通过；其他Must及Compose/Linux/Nginx/Git计划保持。

## 以下为旧裁定历史

"""
    prepend(ROOT / 'DocuN/results/TASK-100-work-decision.md', guide)
    prepend(old_card, """# TASK-100 / R-094 已返回冻结通知（2026-10-05，当前）

续作02已真实回传并完成编排普通核证；候选与有限证据部分通过，集中独立审计待101。原三许可、追加许可及其额度终点保留在下方和原账，禁止再启动main-combo或借用名义剩余SUP。产品、009、夹具与旧原件冻结，独立审计只有其新卡指定写权。原完整合同原字节快照见 DocuN/evidence/TASK-100/orchestration-receipt-03/TASK-100-card-as-returned.md。

这不是G8、父STEP或项目放行。下方仍为原执行合同及全部历史。

""")
    protected = []
    identity = load(BASE / 'final-file-identity.json')
    for item in identity['protected_checks']:
        rel = item['path']
        if rel.startswith(('DocuS/', 'DocuN/')) or rel == 'AGENTS.md':
            continue
        path = ROOT / rel
        if path.is_file():
            protected.append({'path': rel, 'sha256': sha(path)})
    deferred = ('verification-index', 'final-file-identity', 'evidence-inventory', 'browser-final-artifact-verification',
                'result-prefix', 'result-before', 'remaining-controls-proposal', 'remaining-controls-entry-proposal')
    raw_files = [{'path': item['path'], 'sha256': item['sha256'], 'bytes': item['bytes'],
                  'read_policy': '只核身份，不读实现自评；需定位原件时先记录自身初判' if Path(item['path']).name.startswith(deferred)
                                 else '原始运行/输入/快照/预算证据，可按任务范围读取'}
                 for item in receipt['evidence']]
    inputs = {
        'schema': 'task101.independent-audit-input.v1', 'at': stamp(), 'project_root': str(ROOT),
        'task': 'TASK-101', 'round': 'R-095', 'rule_version': 'V4.0/CHG-0003',
        'contracts': [
            {'path': 'DocuN/results/TASK-099-result.md', 'sha256': sha(ROOT / 'DocuN/results/TASK-099-result.md'), 'read': '第3—8节批准业务合同、V01—V20/H1—H4；跳过设计自评'},
            {'path': snapshot_card.relative_to(ROOT).as_posix(), 'sha256': sha(snapshot_card), 'read': '原始目标/边界/各期许可；不以其中普通核证线索代替独立判断'},
            {'path': 'DocuS/最终需求文档.MD', 'sha256': sha(ROOT / 'DocuS/最终需求文档.MD'), 'read': '仅相关Must、数据/安全/限制'}],
        'source_files': [{'path': item['path'], 'sha256': item['sha256'],
                          'role': '文档，不参与运行代码资格' if item['path'] == 'README.md' else '最终产品/测试/夹具/构建对象'}
                         for item in receipt['sources']],
        'protected_product_files': protected, 'rule_files': receipt['rules'], 'raw_files': raw_files,
        'excluded_inputs': ['DocuN/results/TASK-100-result.md', 'DocuN/results/TASK-100-work-decision.md',
                            'DocuN/evidence/TASK-100/orchestration-receipt-03/receipt.json',
                            '实现聊天/推理/客户端记忆', '编排或实现者的预填验收意见'],
        'prior_budget_reference': {
            'path': 'DocuN/evidence/TASK-100/continuation-02/attempt-ledger.json', 'sha256': sha(BASE / 'attempt-ledger.json'),
            'limits': limits, 'counts': counts,
            'policy': '已结束许可及旧未知不清零；101没有旧PG/Job运行额度'},
        'raw_locator_note': 'hash清单只证明身份，不预填审计通过；原批FAIL须独立保留与分级',
    }
    AUDIT.mkdir(parents=True, exist_ok=True)
    save(AUDIT / 'input-snapshot.json', inputs)
    arch_header = """# 架构动态文档

文档 v0.82，2026-10-05，Asia/Shanghai。需求v1.1不变，唯一执行动态v2.04。G8最终候选与有限验证已返回，完整成果集中独立审计待执行。下面v0.81及全部历史原字节保留。

## G8真实候选与有限证据边界

实际实现候选由009的teaching_records/commands/head、teaching_repository的意图/资格/原子结果及一致读面、teaching_contracts/adapter/service/api/policy/progress/views和教学前端组成。records在INSERT前形成最终事实，原007正文/终态与教学效果同短事务；版本、暴露、纠错/推进、UNKNOWN和pending资格沿099原合同，不更换原监督停止或四账权威。

当前逐项证据含最终58离线、29不同PG、4HTTP、009六场景/非空旧行兼容、原17窗及4重开窗、三题型和10浏览器控制。最终112源码/夹具/dist当前匹配，657原件完整。它们是限定已验证事实，不代表任何main-combo总批成功；六原批FAIL和修后脚本未真实重跑保留。服务端/持久事实与显示替身分开，实际脚本中的纠错字段检查失败不能被改写成历史PASS。

010—012等父STEP还需完整自身门槛。101集中审代码、证据、控制并决定现有逐项证据可采范围；必要单次显示补证不运行PG/Job或真实provider，不代实现修码。逐进程as-loaded与浏览器后代粒度由审计按实际风险评估，不用事后虚构身份。

原G3/G4/D3/G5/G6/G7未变部分和旧限定验收继续有效，099批准模型和公开接口不变。V19真实provider质量未授权/未验证；完整G8/M-1/部署/项目不放行。归档路径、Compose/Linux/Nginx/Git与其他Must安排保持。

## 以下为v0.81及更早历史

"""
    prepend(ARCH, arch_header)
    state_header = """# 执行动态文档

文档 v2.04，2026-10-05，Asia/Shanghai。唯一总状态账；需求v1.1不变，架构v0.82，task_model/阶段07。下面v2.03及全部历史原字节保留。

## TASK100续作02已返回；TASK101集中独立审计

100/R094调度已返回，编排普通核证部分通过：最终候选和逐项有限验证已回收，不自签完整G8。112对象/657证据/七规则匹配，原日志29PG/4HTTP和58离线OK可定位。六原入口没有整批PASS，修后浏览器整脚本未运行，旧FAIL/投入/未知原文保留。DEF003—007仅候选修正待101独立裁判，不以结果自评关闭。

原许可及追加账已结束：entry6/6、start5/5、app3/3、SUP21/24、browser3/3、driver3/3、build1/1；新增段离线42.750/真实261.211/收尾33.313秒及主动13643.959口径已存原账。旧至少9入口、漏5.940秒、主动尾段及旧不确定性/续01的4入口不清零。三追加登记与批准前hash可读可追；101另核控制时序，不追认旧投入。原100剩余SUP不借出，原卡已冻结。

本轮只读精确容器Running=false/Pid=0，18100/55442无监听、无task100运行进程；这是编排检查时点。001—008、监督主体及用户原始需求未由编排修改，库/卷/行保留，没有业务运行或资源变更。100结果原文未动，归档当前映射沿v2.03有效。

先占101/R095：G8完整成果集中独立审计，A+增强执行，全新隔离审计窗口，不能使用100实现窗口或其推理记忆；真实型号如实登记。当前调度已登记，卡待完整保存核证后标待转交。完整代码/009与原子语义、V01—V20/H1—H4原件及版本、六入口和资源/许可三个轴同卡；不拆成逐缺陷审计或默认重跑原主链。

101新许可为主动14400秒、元数据/自有辅助离线600秒，默认只读。必要显示补证最多1合并入口/1driver/1browser/1静态服务，单调180秒和独立120秒收尾；仅最终bundle+合成只读GET显示，不启动真实产品后端/PG/Docker/Job，不发业务POST、不运行模型/工具，不重构dist。任何失败或BLOCKED计入口，用完即停；旧100总账另列，不能据新许可把旧失败改PASS。

审计不修产品/旧夹具/原证据/共享状态；补证只允许自身指定新fixture和证据。初判后按实际必要性启用单次probe，已有证明够用直接复核采纳。未获转交/开始事实不写已派发。101结果回来后编排裁定G8，下一102/R096仅计划不占号；STEP009—012仍部分验证，V19/其余Must/整体验收/部署未完成。

本批文档变化与下一CHG在完整卡保存后登记；TASK/R/预算不因归档或新窗口重置。

## 以下为v2.03及更早历史

"""
    prepend(STATE, state_header)
    save(OUT / 'registration.json', {'at': stamp(), 'task': 'TASK-101', 'round': 'R-095', 'schedule': '已登记',
                                    'source_round_returned': 'TASK-100/R-094', 'input_snapshot_sha256': sha(AUDIT / 'input-snapshot.json')})
    print(json.dumps({'phase': 'register', 'task': 'TASK-101', 'schedule': '已登记', 'input_objects': len(inputs['source_files']),
                      'raw_evidence_objects': len(inputs['raw_files'])}, ensure_ascii=False))


def finish():
    card = ROOT / 'DocuN/tasks/TASK-101.md'
    text = card.read_text(encoding='utf-8')
    for heading in ('目标与交付', '项目、规则与接收安排', '背景与最小充分上下文', '执行边界与资源',
                    '验证、证据与审计关系', '停止与回传', '必要人工与待同步信息'):
        if '## ' + heading not in text:
            raise RuntimeError('任务模板缺节：' + heading)
    if '<' in text or '〈' in text or '**' in text:
        raise RuntimeError('卡面残留占位或不合新文档规则')
    input_path = AUDIT / 'input-snapshot.json'
    inputs = load(input_path)
    for item in inputs['source_files']:
        if sha(ROOT / item['path']) != item['sha256']:
            raise RuntimeError('出卡时被审快照已变：' + item['path'])
    for item in inputs['contracts']:
        if sha(ROOT / item['path']) != item['sha256']:
            raise RuntimeError('原合同已变')
    data = STATE.read_bytes()
    old = '当前调度已登记，卡待完整保存核证后标待转交。'
    new = '完整101卡与独立输入已保存并核可读，调度待转交；尚无实际转交、接收或开始证据。'
    if data.count(old.encode()) != 1:
        raise RuntimeError('占号状态不唯一')
    STATE.write_bytes(data.replace(old.encode(), new.encode()))
    paths = [
        ('DocuN/evidence/TASK-100/orchestration-receipt-03/receive.py', '回收元数据原件，不运行业务；初版文档字符串换行解析已定界修正，原检查副本保留'),
        ('DocuN/evidence/TASK-100/orchestration-receipt-03/receipt.json', '112对象/657原件/七规则匹配，29PG/4HTTP/58离线原始OK定位；非独立审计'),
        ('DocuN/evidence/TASK-100/orchestration-receipt-03/evidence-identity.json', '保存657原始证据身份，不改执行者原件'),
        ('DocuN/evidence/TASK-100/orchestration-receipt-03/live-ports-processes.json', '只读精确资源已停、端口/进程时点核证；无启动或数据库连接'),
        ('DocuN/evidence/TASK-100/orchestration-receipt-03/TASK-100-card-as-returned.md', '保存100真实回传时原完整合同原字节供独立审计'),
        ('DocuN/results/TASK-100-work-decision.md', '置顶续作02部分通过、限度和集中审计安排；历史裁定保留'),
        ('DocuN/tasks/TASK-100.md', '置顶已返回/旧许可结束/产品冻结通知，原执行合同保留'),
        ('DocuN/evidence/TASK-101/input-snapshot.json', '中性独立审计合同/当前身份/原件入口，不夹入实现自评'),
        ('DocuS/架构动态文档.MD', 'v0.82同步真实候选和有限证明，009/受控权威与旧限制保持'),
        ('DocuS/执行动态文档.MD', 'v2.04先占101/R095后改待转交；旧计数未知/FAIL与单次显示补证新许可分列'),
        ('DocuN/tasks/TASK-101.md', '保存完整A+新隔离集中审计卡；三个轴和必要单次显示补证同卡'),
        ('DocuN/evidence/TASK-101/delivery-proof.json', '记录全文保存、模板/路径/快照核证，未声称派发或审计完成'),
    ]
    before_log = LOG.read_bytes()
    if 'CHG-0845' in before_log.decode('utf-8-sig'):
        raise RuntimeError('CHG0845已占用')
    backup = OUT / 'before' / 'DocuS/文档变更记录.MD'
    backup.parent.mkdir(parents=True, exist_ok=True)
    backup.write_bytes(before_log)
    last = 844 + len(paths)
    old_state = '本批文档变化与下一CHG在完整卡保存后登记；TASK/R/预算不因归档或新窗口重置。'
    new_state = f'本批CHG0845—{last:04d}，下一CHG{last+1:04d}；TASK/R/预算不因归档或新窗口重置。'
    data = STATE.read_bytes()
    if data.count(old_state.encode()) != 1:
        raise RuntimeError('文档编号状态不唯一')
    STATE.write_bytes(data.replace(old_state.encode(), new_state.encode()))
    at = stamp()
    lines = [f'- CHG-{i:04d}，{at}，Codex编排Agent，{path}。{reason}。' for i, (path, reason) in enumerate(paths, 845)]
    LOG.write_bytes(before_log + ('\n\n' + '\n\n'.join(lines) + '\n').encode('utf-8'))
    proof = {'at': stamp(), 'task': 'TASK-101/R-095', 'schedule': '待转交', 'card_path': str(card),
             'card_sha256': sha(card), 'card_bytes': card.stat().st_size, 'full_card_readback': True,
             'required_template_sections_present': True, 'input_sha256': sha(input_path),
             'sources_rechecked': len(inputs['source_files']), 'parent_contracts_rechecked': len(inputs['contracts']),
             'no_dispatch_or_audit_claim': True, 'next_chg': f'CHG-{last+1:04d}',
             'versions': {'architecture': '0.82', 'state': '2.04'}}
    save(AUDIT / 'delivery-proof.json', proof)
    print(json.dumps(proof, ensure_ascii=False))


if __name__ == '__main__':
    {'register': register, 'finish': finish}[sys.argv[1]]()
