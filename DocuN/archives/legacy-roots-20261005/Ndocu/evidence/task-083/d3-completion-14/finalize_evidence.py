"""仅整理现有证据，不启动任何资源或测试。"""
from datetime import datetime,timezone
import difflib
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).parent
RUN=OUT/'continuation-20260927-095506-73c4c3e3'

def read_json(path): return json.loads(path.read_text(encoding='utf-8-sig'))
def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()

records=read_json(OUT/'review08-current-hashes.json')
diff=[]
for record in records:
    path=ROOT/record['path']
    if digest(path).upper()!=record['current_sha256']: raise RuntimeError('post-run drift: '+str(path))
    if record['unchanged']: continue
    before=OUT/'pre'/record['path'].replace('/','__')
    if digest(before).upper()!=record['review08_sha256']: raise RuntimeError('pre drift')
    diff.extend(difflib.unified_diff(before.read_text(encoding='utf-8').splitlines(True),path.read_text(encoding='utf-8').splitlines(True),fromfile='pre/'+record['path'],tofile=record['path']))
(OUT/'incremental.diff').write_text(''.join(diff),encoding='utf-8')

state=read_json(RUN/'state.json')
meta=read_json(RUN/'attempt-01/meta.json')
preflight=read_json(OUT/'preflight.json')
process=read_json(OUT/'runner-process.json')
offline=read_json(OUT/'offline-01.json')
events=[json.loads(line) for line in (RUN/'attempt-01/stdout.log').read_text(encoding='utf-8').splitlines() if line.strip()]
starts={e['scenario']:e for e in events if e['phase']=='scenario_start'}
scenes=[]
for event in events:
    name=event['phase']
    if name not in starts: continue
    scenes.append({'scenario':name,'start_utc':starts[name]['event_utc'],'result_utc':event['event_utc'],
                   'seconds':round(event['event_monotonic']-starts[name]['event_monotonic'],6),
                   'attempt':'attempt-01','exit':meta['exit_code'],'outer_tree_zero':meta['outer_tree_zero'],
                   'handles_closed':meta['handles_closed'],'fixture_sha256':digest(RUN/'attempt-01/as-run.py')})
if len(scenes)!=8 or state['covered_scenarios']!=[x['scenario'] for x in scenes]: raise RuntimeError('coverage mismatch')
if not (state['verdict']=='PASS' and state['container_stopped'] and not state['cleanup_incomplete'] and process['exit']==0): raise RuntimeError('terminal evidence mismatch')
(OUT/'scenario-index.json').write_text(json.dumps(scenes,indent=2),encoding='utf-8')

budget={'historical_conservative_seconds':900,'round12_conservative_seconds':240,
        'round14_preflight_wall_seconds':preflight['seconds'],'round14_runner_internal_wall_seconds':state['resource_wall_seconds'],
        'round14_runner_charged_process_wall_seconds':process['seconds'],
        'round14_resource_charged_seconds':preflight['seconds']+process['seconds'],
        'total_resource_charged_seconds':1140+preflight['seconds']+process['seconds'],
        'remaining_resource_seconds':660-preflight['seconds']-process['seconds'],
        'runner_limit_seconds':600,'cleanup_reserve_inside_runner_seconds':60,
        'batches_historical_used':1,'batches_round14_used':1,'batches_total_used':2,'batches_unused':1,
        'pg_fixture_commands_historical_used':1,'pg_fixture_commands_round14_used':1,'pg_fixture_commands_total_used':2,
        'windows_scenarios_round14_used':1,'windows_scenarios_total_used':1,'windows_original_cap':12,
        'containers_total_used':2,'containers_created_round14':0,'starts_round14':1,'rotations_round14':1,
        'offline_round14_commands':1,'offline_round14_seconds':offline['seconds'],'offline_round14_limit_seconds':600,
        'unused_budget_not_authorization_to_restart':True}
(OUT/'budget-final.json').write_text(json.dumps(budget,indent=2),encoding='utf-8')

rule=Path('D:/spiritice/AA文件/MS_spi knowledge libraay/obsidian_1/&职业相关/项目流程/项目开发提示词V3/docu/AGENTS.MD')
(OUT/'read-index.md').write_text('''# 本窗接续索引

本窗是TASK-083唯一主执行接续窗口，不是编排，也不承担独立审计。父082、关联084/R078、STEP008局部、NFR002/003、SEC002、FLOW005、DATA007；需求v1.1、架构v0.45、执行状态v1.65按卡输入，Git基础45951501d2741630a229762d6b2d3f4b34d7f702现场吻合。

实际模型可确认信息：系统说明为 Codex / GPT-6。没有可调用的客户端模型及推理档切换或核验工具，未冒称具体型号后缀、未声称已在客户端切换到最高档；未改用户配置，未为模型名再开审批。用户在本新窗给出完整14卡，本窗连续完成。未创建第二执行窗口/子代理，未重开TASK或清零预算。

已读最小材料：
- 项目根AGENTS.md及公共docu/AGENTS.MD；未加载WORK及全部阶段提示词。
- TASK-083-D3-work-decision.md批准合同；TASK-083-result.md最新12及11。
- TASK-084-result.md的review08及review07必要定位；review08/hashes.txt、code-prelog-assessment.md与postlog-assessment.md的代码/证据分级。
- repair11/runner-walkthrough.md、final-hashes.txt、12 continuation的state.json及preflight-blocked-diagnostics.md。
- 当前runner、controlled_child、contracts、d3_pg_windows及直接调用方repository/session/launcher/supervisor_main/windows_job/command与迁移接口；无旧十几轮重载。

旧Job07/PG08/09及review08按原适用范围复用；最终哈希绑定的离线结论与中间版结论仍按review08分级。新增一次10项离线检查仅覆盖本卡运行控制增量。记忆快速查询确认既有规划偏好不代替本卡动态验收要求；不修改记忆。

接续核查：inflight-pre.json及inflight-before-start.json均为空；没有13执行产物，文件与review08基线吻合。旧窗口没有在途083 Python/PowerShell运行对象被发现；这不是客户端UI中旧聊天已关闭的证明。当前没有可调用的聊天控制工具，因此没有声称已操作旧聊天。开始前13项哈希中仅本窗修改的3项变化，其余10项吻合；最终再对as-run核对未漂移。公共库只读、正式docu由编排维护。

原准备阶段证据整理命令曾因Windows默认GBK读取UTF-8文件报UnicodeDecodeError（在diff生成阶段）；13项hash已保存且核对完成，运行前并发检查仍执行为空。该错误不在runner/测试/资源路径，未发生额外资源启动。最终整理显式UTF-8补齐diff和本索引；没有覆盖真实运行记录，不把这些文档声称为运行前已完成。

公共规则修改时间UTC：'''+datetime.fromtimestamp(rule.stat().st_mtime,timezone.utc).isoformat()+'\n公共规则SHA256：'+digest(rule)+'\n',encoding='utf-8')

hashes=[]
for record in records:
    hashes.append(digest(ROOT/record['path'])+'  '+record['path'])
for path in sorted((RUN/'attempt-01/sources').iterdir()):
    hashes.append(digest(path)+'  '+str(path.relative_to(ROOT)).replace('\\','/'))
for path in (RUN/'runner-as-run.py',RUN/'controlled_child-as-run.py',RUN/'contracts-as-run.py',RUN/'attempt-01/as-run.py',OUT/'offline_checks.py',OUT/'bounded_check.py',OUT/'resource_preflight.py'):
    hashes.append(digest(path)+'  '+str(path.relative_to(ROOT)).replace('\\','/'))
for name in ('runner','controlled_child','contracts'):
    if digest(RUN/(name+'-as-run.py'))!=digest(ROOT/'Ndocu/evidence/task-083/d3-repair-11'/(name+'.py')): raise RuntimeError('runner as-run drift')
if digest(RUN/'attempt-01/as-run.py')!=digest(ROOT/'backend/tests/fixtures/task083/d3_pg_windows.py'): raise RuntimeError('fixture as-run drift')
(OUT/'final-hashes.txt').write_text('\n'.join(hashes)+'\n',encoding='utf-8')
print(json.dumps({'scenarios':scenes,'budget':budget},ensure_ascii=False,indent=2))
