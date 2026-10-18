"""S07到限封存，只写证据、原累计账和结果，不执行产品或验证。"""
from pathlib import Path
from datetime import datetime, timezone
import difflib
import hashlib
import json
import time

N = Path(__file__).resolve().parent
E = N.parent
ROOT = E.parents[3]
PERMIT = 'TASK-117-STEP018-AUDIT-REPAIR-S07-20261017'


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def stamp():
    return {'utc': datetime.now(timezone.utc).isoformat(), 'mono_ns': time.monotonic_ns()}


def main():
    assert not (N / 'final-binding.json').exists(), '本次封存已完成，不重复追加'
    receipt = json.loads((N / 'receipt.json').read_text(encoding='utf-8'))
    before = json.loads((N / 'before-budget.json').read_text(encoding='utf-8'))
    b = json.loads((E / 'budget.json').read_text(encoding='utf-8'))
    assert b['active_segment'] == PERMIT and b['active_root'] is None
    s = next(row for row in b['segments'] if row['permit'] == PERMIT)
    now = stamp()
    elapsed_utc = (datetime.fromisoformat(now['utc']) - datetime.fromisoformat(s['start_utc'])).total_seconds()
    discontinuity = now['mono_ns'] < s['start_mono_ns']
    assert elapsed_utc > s['activity_cap_seconds'], '此脚本只用于已确认到限保存'
    assert not s['suspensions'] and s['paused_seconds'] == 0
    assert b['counts'] == receipt['baseline_counts'], '出现未知新增运行计数，须保留并核对'
    assert b['roots'] == before['roots'] and b['runtime_intervals'] == before['runtime_intervals']
    assert b['failures'][:len(before['failures'])] == before['failures']
    assert (E / 'events.jsonl').read_bytes().startswith((N / 'before-events.jsonl').read_bytes())

    changes = json.loads((N / 'changes.json').read_text(encoding='utf-8'))
    rows, delta = [], []
    for relative, pre in changes.items():
        path = ROOT / relative
        raw = path.read_bytes() if path.exists() else b''
        old = (ROOT / pre['backup']).read_bytes() if pre['exists'] else b''
        assert not pre['exists'] or digest(old) == pre['sha256']
        changed = path.exists() != pre['exists'] or raw != old
        rows.append({'path': relative, 'D': pre['D'], 'pre': pre,
                     'post': {'exists': path.exists(), 'bytes': len(raw), 'sha256': digest(raw) if path.exists() else None},
                     'changed': changed, 'tested_current_bytes': False})
        if changed:
            delta.extend(difflib.unified_diff(old.decode('utf-8-sig').splitlines(True), raw.decode('utf-8-sig').splitlines(True),
                                            fromfile='pre/' + relative, tofile='post/' + relative))
    (N / 'S07-product.diff').write_text(''.join(delta), encoding='utf-8')
    save(N / 'post-source-manifest.json', {'sample': now, 'files': rows,
          'changed_files': [row['path'] for row in rows if row['changed']], 'validation': 'NOT_RUN'})
    bundle = json.loads((N / 'bundle-7-before.json').read_text(encoding='utf-8'))
    bundle_rows = []
    for row in bundle['files']:
        current = (ROOT / row['source']).read_bytes()
        backup = Path(row['backup']).read_bytes()
        bundle_rows.append({**row, 'current_sha256': digest(current), 'backup_sha256': digest(backup),
                            'current_and_backup_unchanged': digest(current) == digest(backup) == row['sha256']})
    assert all(row['current_and_backup_unchanged'] for row in bundle_rows)
    save(N / 'bundle-7-post.json', {'sample': now, 'files': bundle_rows,
          'S07_build_executed': False, 'S07_source_is_not_in_this_bundle': True})

    save(N / 'final-stop-observation.json', {
        'sample': {'utc': '2026-10-17T09:35:07.8034845Z', 'qpc': 233691202879, 'frequency': 10000000},
        'S07_registered_processes': [], 'S07_runtime_started': False, 'active_root': None,
        'observed_node_chrome_python_firefox_msedge_processes': [],
        'process_observation_method': 'PowerShell Get-Process names, Id/StartTime/Path; no matching processes returned',
        'loopback_port': '127.0.0.1:18119', 'netstat_tcp_18119_rows': [], 'listener_observed': False,
        'actions_to_stop_processes': [], 'CIM_attempt': 'Win32_Process read unavailable; safer Get-Process/netstat observation used, no escalation',
        'old_PG_or_product_runtime_resampled': False,
        'old_stop_reference_only': 'continuation-05/final-resource-stop-binding.json at 2026-10-16T15:45:05.045131Z',
        'scope': 'Only S07 and specified port observed; no claim of live original PG state'})
    timing = {'sample': now, 'first_tool': receipt['first_tool'], 'start_mono_ns': s['start_mono_ns'],
              'observed_utc_elapsed_seconds': elapsed_utc, 'paused_seconds': 0,
              'activity_charged_conservatively_seconds': elapsed_utc,
              'activity_cap_seconds': 21600, 'save_only_after_seconds': 20400,
              'over_activity_cap_seconds': elapsed_utc - 21600,
              'monotonic_discontinuity_observed': discontinuity,
              'clock_domain_identity': 'UNKNOWN; current monotonic is lower than saved start',
              'interruption_pause_reconstructed': False,
              'policy': 'No refund for interruption or clock-domain change; UTC conservatively retained; no further implementation/tests',
              'runtime_holding_seconds_delta': 0,
              'controlled_validation_process_seconds': s['offline_process_run_seconds'],
              'metadata_command_process_wall_complete': False,
              'metadata_wall_note': '历史工具读写未逐项登记到offline子账，原始回执保留；不将0称全部离线进程零耗时，不追认控制通过'}
    save(N / 'final-timing.json', timing)
    cases = {
        'D01': {'status': 'INITIAL_CODE_UNVERIFIED', 'remaining': '三条foreign写入口反例、SnapshotTests和合法取消对照均未运行'},
        'D02': {'status': 'INITIAL_CODE_UNVERIFIED', 'remaining': '实际网关正反例、await变化、旧embedding/wire回归及说明尚未完成'},
        'D03': {'status': 'INITIAL_CODE_UNVERIFIED', 'remaining': '正式bundle、IDB晚到owner/view/head三反例和恰一次POST、原键草稿未验证'},
        'D04': {'status': 'NOT_IMPLEMENTED', 'remaining': '受信provider/model告知与缺字段门尚未实现，三处正式浏览器验证未执行'}}
    as_run = {'sample': now, 'permit': PERMIT, 'Q': 'FROZEN',
              'runtime_root_opened': False, 'backend_tests': 'NOT_RUN', 'typecheck': 'NOT_RUN',
              'compile': 'NOT_RUN', 'build': 'NOT_RUN', 'browser': 'NOT_RUN', 'fixture_server': 'NOT_RUN',
              'controller_boundary_selfcheck': 'NOT_RUN', 'runtime_watchdog_implementation': 'NOT_COMPLETED',
              'test_exit_codes': None, 'http_delta': 0, 'provider_call_delta': 0, 'actual_fee_delta': 0,
              'inheritance': 'Only prior frozen evidence for its original bytes/layers; no S07 repair is passed',
              'cases': cases}
    save(N / 'as-run.json', as_run)
    failures = [
        ('S07_resume_CIM_read_unavailable', '只读Win32_Process查询CIM资源不可访问，命令退出1；改用Get-Process/netstat，无运行资源需停止'),
        ('S07_clock_domain_discontinuity', '恢复采样单调钟低于原起点，时钟域连续性未知；未追造暂停，按UTC保守计活动'),
        ('S07_activity_limit_return_incomplete', '首次工具至恢复采样超过21600秒且无预记pause；只封存，四项不标通过')]
    for label, reason in failures:
        row = {'label': label, 'reason': reason, **now, 'segment': PERMIT}
        b['failures'].append(row)
        with (E / 'events.jsonl').open('a', encoding='utf-8') as stream:
            stream.write(json.dumps({'kind': 'failure', **row}, ensure_ascii=False) + '\n')
    s.update(status='returned_incomplete_activity_limit', final_sample=now,
             activity_used_seconds=elapsed_utc, activity_overrun_seconds=elapsed_utc - 21600,
             clock_domain_discontinuity=discontinuity, paused_seconds=0,
             final_timing_evidence=str(N / 'final-timing.json'), validation_status='NOT_RUN')
    b['phase'] = 'S07_returned_incomplete_activity_limit'
    save(E / 'budget.json', b)
    index = json.loads((E / 'case-index.json').read_text(encoding='utf-8'))
    index['S07'] = {'sample': now, 'permit': PERMIT, 'status': 'REPAIRS_INCOMPLETE_NO_VALIDATION', 'Q': 'FROZEN',
                    'supersedes_current_candidate_status_for_changed_source': True,
                    'old_cases_retained_as_historical_evidence': True, 'cases': cases}
    save(E / 'case-index.json', index)
    save(N / 'final-budget-observed.json', b)
    changed = [row['path'] for row in rows if row['changed']]
    first = datetime.fromisoformat(s['start_utc']).astimezone(timezone.utc)
    old_report = (N / 'before-result.md').read_bytes()
    assert len(old_report) == 79709 and digest(old_report) == receipt['old_report_sha256']
    result = ROOT / 'DocuN/results/TASK-117-result.md'
    assert result.read_bytes() == old_report, '已有他人新报告时不覆盖'
    text = f'''# TASK-117 / R-111 S07 到限封存，四项修复未完成

本轮未完成四项缺陷合并修正：D01、D02、D03已保存初版源码但未经验证，D04尚未实施；活动硬门已到，停止继续修改及测试，Q保持冻结。此结果不是工程稳定候选，不提交缺陷关闭或项目验收。

## 接续与真实停止原因

沿用原TASK-117工程窗口，许可{PERMIT}，task_model/V4.0、CHG-0003。接收时核对30项必要输入，原规则与冻结原件身份一致；原TASK118独审结论继续有效。A+为资源标签，实际环境为Codex desktop / GPT-6，具体服务端变体未披露。

首次工具UTC为{first.isoformat()}，本次封存采样为{now['utc']}。两者相差{elapsed_utc:.6f}秒，卡内活动上限21600秒，20400秒起只允许清场保存。账中没有预记暂停，不能因平台中断事后扣时，保守活动超额{elapsed_utc-21600:.6f}秒保持记录。本次只做断点读取、资源观察及封存，没有开启新修正、验证族或运行根。日历48小时尚未耗尽，不代表活动额度仍可使用。

恢复时宿主单调计数低于保存的起点，时钟域连续性未知；未推断具体重启原因。原S07控制器只写出初版，有限边界自检尚未执行；其仅用原单调差值的门不能作为本次剩余额度证明。此次采用UTC保守计时，不重置起点或补造pause，不追认控制合格。metadata子进程未完整逐项纳入offline子账的缺口也保持，受控测试子账0秒不能解释为所有读写进程零耗时。详情见final-timing.json。

## 四项实际源码与未验证边界

1. D01：backend/app/data_exit/control.py抽取真实锁内_validated_locked，commit、create_or_get_job、change_job与读快照共享完整当前字节、文件身份、首hub身份及残尾判断，继续在同一排他锁内replay/CAS/append。缓存增加内部事件序列，公开状态仍返回副本。初版已落盘。卡面三条foreign有效日志替换、same-key/foreign job拒绝、原SnapshotTests及合法peer取消对照未补齐或运行，不能声称写入口修复通过。

2. D02：embedding.py新增严格的有限model_requests审批对，绑定完整payload摘要及完整typed request摘要；旧清单缺少模型审批时模型路径失败关闭，空新增字段设计为保持旧embedding清单hash。gateway.py捕获请求/配置副本和序列化发送字节，准入前、await准入后及dispatch前复核原始范围与受信审批；发送对象由同一冻结字节重新解码。设计上dispatch阶段发现变化保持已预扣并记录NOT_SENT，不退款或重试。上述均只有初版源码，没有运行实际gateway最低transport的批准一次send、各类不批准零send、await变化或旧wire/embedding用例；兼容性未验证。

   本地manifest增加model_requests，每项payload_sha256和request_sha256均为64位小写hex，最多128项；非空字段进入新manifest hash，必须与既有grant绑定及私有传递保持一致。批准来源必须是operator预先审核的完整固定合成请求，连同动态ID、scope/记忆版本及派生消息计算摘要，再显式更新同一批准清单及其grant绑定；不得在收到任意正文后自动加白。没有生成正式Q配置、签票或启用文件。实际loader传播、README/样例说明与完整可执行正反例仍待补齐，不把全部模型拒绝当完成。

3. D03：TeachingWorkspace.tsx初版捕获原activity、owner、view_token、head revision、scope、DataContext/namespace，并在build、保存完整IndexedDB草稿、摘要持久化后及POST前复核。postTeachingCommand增加发送前同步guard；teachingIntents.ts在会话owner变化时使原lease失效，保留原链不自动改绑。domain_sent标记移至发起POST之后，允许原页面只读刷新以观察晚到身份变化。真实正式bundle尚未构建；query后IDB完成窗口内同activity owner、view及head/scope变化、正常恰一次POST、原键GET和完整草稿留存均未动态验证。

4. D04：尚未实施。RetrievalPanel和retrieval-api仍为原字节，ActivityWorkspace、InterviewWorkspace与retrieval/service.py也未修改。三处确认前实际provider/model、用途及预算告知和缺字段阻断仍待完成；不能把既有泛化文案或只读接口已有字段作为修复通过证据。

本次实际变更{len(changed)}个产品文件：{'; '.join(changed)}。测试文件、README与config样例未改变。没有修改001—014、持久模型、公开写合同、依赖锁、Git、DocuS、任务卡或主控/独审原件。

## 证据与继承

证据根为D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-117/execution/continuation-06/。receipt.json记录接收原件；changes.json与preimages保存每个拟改文件的原字节；post-source-manifest.json给出实际pre/post/hash和D归属；S07-product.diff为有限统一diff；as-run.json明确所有新验证均未运行，没有伪造退出码、HTTP时间线、截图或pass。

bundle-7-before完整保存4项原构建字节，bundle-7-post.json复读确认当前dist与备份仍逐项相同。JS为index-BgdcRLRN.js，SHA256 58a87abf5ff4b02b33aab5dc3735507f4f097791e021aeb4ddfbf0b62ac115e8。该bundle不包含本轮教学源码变化；没有S07页面实际fetch，不能称最终bundle通过。

原PDF/Job、固定预览、两域业务、恢复与只读重开等证据继续只对原冻结字节和原验证层有效，本轮不重跑，也不据此推导D01—D04已过。TASK118四项缺陷保持开放，历史控制不通过不赦免。真实PG roster SUM/两provider持久预扣组合、真实外网、未来Q及独立验收均未新增取证。

## 运行停止、失败与累计账

S07未创建运行根、合成HTTP服务器、浏览器profile、PG/卷/产品API或preview，无本轮PID+birth需要停止。2026-10-17T09:35:07.8034845Z只读Get-Process未返回node/chrome/python/firefox/msedge，netstat TCP中18119无记录；final-stop-observation.json留存观察范围。CIM的Win32_Process读取返回资源不可访问，未升权或绕过，改用上述只读观察，不据此断言其它所有进程状态。没有杀用户进程，没有启动Docker求证。

原六PG/CID、selector和原业务运行状态不重采；只引用continuation-05/final-resource-stop-binding.json的2026-10-16T15:45:05.045131Z历史停止证明，不称其为当前现场。source frozen及永久readonly selector继续作为授权边界。

本段新增root、Browser、build、fixture_server、HTTP、provider及费用均0；原累计roots24，Browser16，build7，fixture_server0，HTTP2324；PG创建尝试/对象/卷各6、PGstart46、产品API33、Native140、preview创建/启动各2、provider和费用0全部保持。runtime持有delta0，受控验证进程子账0；未完整计入的metadata wall已明确unknown，不追记为已通过控制。保守活动计{elapsed_utc:.6f}秒，无预记暂停。

原63条失败完整保留，追加CIM读取不可用、恢复单调时钟域不连续、活动到限交回三条事实，累计{len(b['failures'])}条。原S01/S03投入/持有超额、S04/S05离线超额、漏采和unknown均不改写。before-budget/events/case-index保留原字节，唯一累计账仅追加S07；case-index保留旧用例，并增加当前源码修复未完成的S07覆盖说明。

## 待主控同步与下一步

建议状态为到限交回、修复未完成、四缺陷开放；Q冻结。DocuS/总状态/新额度由主控维护，工程窗未自行维护第二份总进度，也未向审计窗发送消息。

后续需要新的明确续作许可，保留当前6个源码改动、全部preimage、失败、超额与累计账。先处理跨宿主时钟域的控制器门并做离线有限边界核对，再完成D04与D01/D02定向测试、既有用例必要适配；全部修改收齐后集中一次后端/typecheck，成功后正式build，再按原合同补D03/D04最小合成浏览器场景。不得整批重跑或把原根数清零。只有完整稳定后才适合交原TASK118增量独审，本次不提交修复通过候选。

以下保留S06及更早报告原79709字节，SHA256 b596ab87ae3facc605dab65acbf9c708c784c11b1f8581b75ddc6611ad802ac9；该历史段不是本轮通过声明。

---

'''
    assert '*' not in text
    result.write_bytes(text.encode('utf-8') + old_report)
    reread = result.read_bytes()
    assert reread.endswith(old_report) and reread[:len(text.encode('utf-8'))].decode('utf-8') == text
    binding = {'sample': stamp(), 'result': str(result), 'bytes': len(reread), 'sha256': digest(reread),
               'S07_prefix_bytes': len(text.encode('utf-8')), 'old_suffix_bytes': len(old_report),
               'old_suffix_sha256': digest(reread[-len(old_report):]), 'full_byte_reread': True,
               'status': 'INCOMPLETE_ACTIVITY_LIMIT', 'Q': 'FROZEN',
               'evidence': []}
    for filename in ('post-source-manifest.json', 'S07-product.diff', 'bundle-7-post.json', 'as-run.json',
                     'final-timing.json', 'final-stop-observation.json', 'final-budget-observed.json'):
        raw = (N / filename).read_bytes()
        binding['evidence'].append({'path': str(N / filename), 'bytes': len(raw), 'sha256': digest(raw)})
    save(N / 'final-binding.json', binding)
    with (E / 'events.jsonl').open('a', encoding='utf-8') as stream:
        stream.write(json.dumps({'kind': 'S07_returned_incomplete_activity_limit', **binding['sample'],
                                 'result_sha256': binding['sha256'], 'old_suffix_sha256': digest(old_report),
                                 'Q': 'FROZEN', 'new_runtime': False, 'new_validation': False}, ensure_ascii=False) + '\n')
    print(json.dumps({key: value for key, value in binding.items() if key != 'evidence'}, ensure_ascii=False))


if __name__ == '__main__':
    main()
