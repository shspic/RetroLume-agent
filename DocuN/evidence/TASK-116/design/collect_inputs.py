"""TASK116 pure file metadata collector; no product import, execution, git or services."""
import ast
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import time

DESIGN = Path(__file__).resolve().parent
ROOT = DESIGN.parents[3]


def digest(path):
    raw = path.read_bytes()
    return len(raw), hashlib.sha256(raw).hexdigest()


def main():
    records = [json.loads(line) for line in (DESIGN / 'reads.jsonl').read_text(encoding='utf-8').splitlines()]
    grouped = {}
    for item in records:
        key = item['path']
        entry = grouped.setdefault(key, {'path': key, 'reads': []})
        entry['reads'].append({field: item.get(field) for field in ('utc', 'mono_ns', 'mode', 'match', 'ranges', 'purpose')})
        entry['read_sha256'] = item['sha256']
    supplementary = {
        'AGENTS.md': '入口全文已读；用户当前入口及锁定规则；不维护共享文档',
        'DocuS/最终需求文档.MD': '当前v1.2及第3—13节全文；Must/字面语义重新定位',
        'DocuS/架构动态文档.MD': 'v1.32当前头/采用边界/相关历史接口定向段；非全文重审',
        'DocuS/执行动态文档.MD': 'v2.56顶部当前状态及原STEP018—020定向段；历史计数继承',
        'DocuN/results/TASK-116-work-decision.md': '现行设计授权全文',
        'DocuN/evidence/TASK-116/orchestration-20261014/input-manifest.json': '主控243登记/三旧移除输出导航；仅起点不重hash全集',
        'DocuN/results/TASK-114-result.md': '同窗终稿闭包/失败/有限层继承，只读；不是本次运行',
        'DocuN/results/TASK-115-result.md': '有限STEP017终审头/关闭与限制，当前有效记录',
        'DocuN/results/TASK-111-result.md': '续作07前70行定向读取，输出截断部分不冒全文读；image/load/HostPolicy明确身份',
        'README.md': '本机/学习/记忆/退出相关段与标题定向读取，未全文重审',
        'deploy/start_local.py': '公开脚本完整读取，私配内容/环境值未读',
        'deploy/start-backend.ps1': '当前本机启动接口公开正文读取',
        'deploy/compose.local.yml': '完整公开Compose；PG/renderer-build而非常驻宿主',
        'deploy/preview/README.md': '正式配置/加载/许可入口定向读取，旧候选不得推翻当前裁定',
        'deploy/preview/load-manifest.json': '正式manifest元数据读取；曾整行输出截断，不重hash所有vendor',
        'config/activity.example.json': '公开示例全文；teaching缺项及默认零门',
        'config/preview.example.json': '公开签票配置全文；未读ticket/key/私密文件',
        'config/data-exit.example.json': '公开factory/R01配置全文',
        'backend/requirements.txt': '现有公开依赖声明全文',
        'backend/requirements.lock': '现有核心锁全文；未安装/联网',
        'frontend/package.json': '公开scripts/依赖全文',
        'frontend/package-lock.json': '锁定依赖元数据身份，沿同窗不变认知；不是新许可全仓审计',
        'backend/app/main.py': '路由/装配/配置/生命周期全文；文首docstring历史不代替代码',
        'backend/app/runtime.py': 'Windows Selector loop公开代码全文',
        'backend/app/service_config.py': '配置层/profile/限额公开代码定向读取；不读本地配置',
        'backend/app/preview/generation.py': '实际HtmlGenerationService.generate完整读取',
        'backend/app/data_exit/contracts.py': '前45行PROFILE/TABLES/Limits',
        'backend/app/data_exit/config.py': 'DataRuntime定义与方法名定位；实现按原114闭包继承，未全文重读',
        'backend/app/data_exit/api.py': '实际公开入口/method及只读装配按旧C03认知继承，未全文重读',
        'backend/migrations/002_activities.sql': 'scope/operation字段/约束定向匹配',
        'backend/migrations/007_activity_operation_results.sql': '结果原子承载/容量约束定向匹配',
        'backend/migrations/013_data_exit.sql': 'schema_profile/控制/角色/trigger及关键函数定向匹配；旧实际ACL证据继承',
        'frontend/src/activities/ActivityWorkspace.tsx': '创建/范围/goal seed/意图/导航与domain关键段',
        'frontend/src/activities/InterviewWorkspace.tsx': '实际goal/submit/reconcile/反馈/历史关键段与方法匹配',
        'frontend/src/activities/MemoryWorkspace.tsx': '公开记忆入口方法定位与原104采用认知继承',
        'backend/tests/test_teaching_policy.py': '明确test方法标识定位，旧方法复用不是本卡测试',
        'backend/tests/test_teaching_recovery.py': '四种恢复test方法标识',
        'backend/tests/test_task103_memory.py': '记忆容量/数值/不确定方法标识',
        'backend/tests/test_interview_contracts.py': 'probe/profile互斥与绑定方法标识',
        'backend/tests/test_data_exit_c03.py': '三C03方法标识；旧证据限定层保留',
    }
    for relative, scope in supplementary.items():
        entry = grouped.setdefault(relative, {'path': relative, 'reads': []})
        entry['supplementary_scope'] = scope
        entry['scope_recorded_after_read_not_retrospective_clock'] = True
    for relative, entry in grouped.items():
        size, sha = digest(ROOT / relative)
        entry['bytes'] = size
        entry['sha256'] = sha
        entry['same_as_recorded_read'] = entry.get('read_sha256', sha) == sha
    manifest = json.loads((ROOT / 'DocuN/evidence/TASK-116/orchestration-20261014/input-manifest.json').read_text(encoding='utf-8-sig'))
    def manifests(value):
        found = {}
        if isinstance(value, dict):
            if 'sha256' in value:
                name = value.get('relative_path') or value.get('path') or value.get('relative')
                if isinstance(name, str):
                    name = name.replace('\\', '/')
                    prefix = ROOT.as_posix().rstrip('/') + '/'
                    if name.startswith(prefix): name = name[len(prefix):]
                    found[name] = value['sha256']
            for child in value.values(): found.update(manifests(child))
        elif isinstance(value, list):
            for child in value: found.update(manifests(child))
        return found
    expected = manifests(manifest)
    for relative, entry in grouped.items():
        entry['manifest_expected_sha256'] = expected.get(relative)
        entry['same_as_manifest_when_present'] = None if relative not in expected else entry['sha256'] == expected[relative]
    result = {'schema': 'TASK116.used-source-identities.v1', 'utc': datetime.now(timezone.utc).isoformat(),
              'mono_ns': time.monotonic_ns(), 'all_registered_243_rehashed': False,
              'count': len(grouped), 'records': list(grouped.values()),
              'private_values_product_import_services_tests_network_git_writes': 0}
    (DESIGN / 'source-identities.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    samples = json.loads((DESIGN / 'sample-inputs.json').read_text(encoding='utf-8'))
    sample_meta = {'schema': 'TASK116.frozen-sample-identities.v1', 'scenario_count': len(samples['scenarios']), 'sources': []}
    for item in samples['sources']:
        raw = item['text'].encode('utf-8')
        sample_meta['sources'].append({'alias': item['alias'], 'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest(),
                                      'lines': len(item['text'].split('\n')), 'expected_lines': item['expected_lines']})
    (DESIGN / 'sample-identities.json').write_text(json.dumps(sample_meta, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'used_source_count': len(grouped), 'changes_since_read': [k for k, v in grouped.items() if not v['same_as_recorded_read']],
                      'manifest_mismatches': [k for k, v in grouped.items() if v['same_as_manifest_when_present'] is False],
                      'scenario_count': len(samples['scenarios']), 'actual_runtime': 0}, ensure_ascii=False))


if __name__ == '__main__': main()
