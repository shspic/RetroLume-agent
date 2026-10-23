"""主控仅登记任务和维护文档，不导入或运行产品。"""
from pathlib import Path
from datetime import datetime, timedelta, timezone
import hashlib
import json
import re

ROOT = Path('D:/shspic/project_NO3_RetroLume-agent').resolve()
HERE = ROOT / 'DocuN/evidence/TASK-125/orchestration-20261022'
TZ = timezone(timedelta(hours=8))


def digest(data):
    return hashlib.sha256(data).hexdigest()


def path(relative):
    target = (ROOT / relative).resolve()
    target.relative_to(ROOT)
    return target


def write(relative, content):
    target = path(relative)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(content.encode('utf-8') if isinstance(content, str) else content)
    return target


def dump(relative, value):
    return write(relative, json.dumps(value, ensure_ascii=False, indent=2) + '\n')


CARD = r'''# TASK-125 / R-119 正常首次部署安装工具链与关闭配置完整工程

## 目标与交付

你担任本卡工程执行者。连续完成一个可验收成果，将当前仅支持001的旧首次初始化入口补足为支持已采用001—015原始迁移链的正式安装工具、默认关闭的配置准备和准确运行说明，完成相应离线验证及范围内修复后统一回传。

本卡是新的部署工程单元，不重做TASK122/123计量资料研究，不重新开发已验收的业务功能。可交付可供后续精确正常部署卡调用的产品工具，但本卡不执行安装器apply，不创建正常实例、不连接数据库、不启动服务、不启用真实调用。外部账号和计量缺口继续只阻塞实际启用。

必须交付以下完整部分。

- 正式入口D:/shspic/project_NO3_RetroLume-agent/deploy/initialize_normal.py。至少提供可安全运行的帮助和无数据库plan模式，以及仅供后续另行精确授权时使用的首次空库apply路径。默认绝不实施。实际参数和用法以最终源码和真实帮助输出为准，不只写一个不可运行草案。
- 正式固定迁移清单D:/shspic/project_NO3_RetroLume-agent/deploy/normal_install_manifest.json，逐项锁定现有001—015的顺序、原始字节hash、目标profile与所需角色分工。它是安装工具元数据，不是新的Q授权协议或业务账本。
- 默认关闭且没有真实身份或凭据的D:/shspic/project_NO3_RetroLume-agent/config/normal-install.example.json，以及D:/shspic/project_NO3_RetroLume-agent/deploy/normal-install.md和README最小必要更新。
- D:/shspic/project_NO3_RetroLume-agent/backend/tests/test_normal_install.py，验证本卡实际新增行为；必要纯函数可在上述正式入口内组织，不扩建通用安装平台。
- 全部pre副本、统一diff、post和实际被测hash、命令/退出/失败/用时/继承说明，保存至D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-125/execution/；统一结果保存至D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-125-result.md。

成功标准为正式工具和默认关闭配置已实现，离线验收覆盖下述真实新行为，未改变现有安全合同，并准确列明将来运行所需输入和仍未发生的动态验证。不将离线通过写成001—015已在新正常库成功安装。

## 项目、规则与接收安排

项目根D:/shspic/project_NO3_RetroLume-agent，入口D:/shspic/project_NO3_RetroLume-agent/AGENTS.md。模式task_model，V4.0，公共AGENTS修订CHG-0003。公共根为D:/spiritice/AA文件/MS_spi knowledge libraay/obsidian_1/&职业相关/项目流程/项目开发提示词V4。

读取公共DocuS/AGENTS.MD，以及DocuS/WORK.MD第2节task_model、第6节结果合同、第8节接续和第9节状态。锁定指纹采用项目DocuN/evidence/v4-migration-20260930/rules-snapshot.json，不采用后来修订；同窗已读且hash不变的规则直接复用。

任务类型为实现、离线测试及范围内普通修复，父STEP-018，关联STEP-020部署交接、NFR-004、CON-002、DR-002、SEC-001/002/003、FLOW-007及已关闭TASK120—124。需求v1.4，发卡后架构v1.65、执行动态v2.93。原始需求仅用户维护。

接收资源A+增强执行，优先继续原TASK123工程/核查窗口，复用已有部署缺口与关闭交接上下文。此为安装迁移及角色隔离工程，复杂度C2、风险R3、不确定性U2，采用增强资源直接完成；不要求常规先失败。真实客户端/模型由接收者如实登记，未知不捏造。原窗不可用时用同等胜任的新工程窗口，仍沿TASK125/R119，不分两条工程线。不得使用原TASK124独审窗口实现本卡。

授权依据为用户持续推进项目的既有开发授权，以及本轮明确要求提供接续提示词。授权终点仅上述本地可逆工程和离线验证。新卡不授予数据库/角色/容器/卷/服务/外发实际操作权，也不改变已批准的100次/25元条件总额及48/28/24固定分额。

本卡调度为待人工转交，未发生接收或启动事实。无并行工程或审计写入。执行者独占本卡允许文件，主控只维护共享状态，禁止彼此混写。

## 断点与最小充分上下文

按以下顺序读取，同窗不变材料复用，不通读历次巨量聊天或全部历史文档。

1. 根入口、锁定规则、唯一总账DocuS/执行动态文档.MD置顶当前段与本卡登记。TASK123有限工程和F124-01均已关闭，原13方法与独审原件有效，不重新开案。
2. 本卡配套DocuN/evidence/TASK-125/orchestration-20261022/input-manifest.json、permit.json及已有Git差异路径记录。确认当前允许修改对象与冻结对象，没有真实在途工作后再实施。已存在改动均视为应保留成果，不reset、不checkout覆盖、不混入本卡diff。
3. DocuN/evidence/TASK-123/execution/correction-01/deployment-handoff.md及finite-inputs.json。这是唯一当前有效关闭交接，原execution同名文件只作历史。读TASK123主控裁定置顶和DocuN/evidence/TASK-123/orchestration-closure-20261022/closure-receipt.json；不要重跑原13方法。
4. DocuN/evidence/TASK-122/preparation/operation-runbook.md第2、4节，以及deployment-package.draft.json、readiness-plan.json中部署配置相关条目。它们均非执行许可，不直接当产品配置。计量/账号既有缺口只引用，不重新联网搜索。
5. DocuS/最终需求文档.MD中部署、安全及当前Q采用边界；DocuS/架构动态文档.MD的正常部署、DATA/FLOW-007、R01/R02/R03职责，仅按相关定位读取。根README、deploy/start_local.py、deploy/initialize-materials.py、deploy/compose.local.yml及config/local.env.example、data-exit.example.json和现有关闭配置示例。
6. backend/migrations/001_materials.sql至015_activity_scope_delete_permission.sql原文，backend/app/data_exit/schema_profiles.py、schema_checks.py、q_roles.py、config.py、files.py及确有需要的直接依赖。以当前采用的data_exit.v1.r03为目标，读取实际字段、角色、ACL、函数及原profile核验接口，不从文件名猜版本。
7. 仅作已实现顺序参考读取backend/tests/fixtures/task120/setup.py的_migrate_legacy及必要直接依赖。其TESTONLY专库、合成凭据、角色复用、正则改写CREATE ROLE、替换010/011碰撞guard、源注入和旧续作许可全部不能移入正常产品。正式工具不能import tests、DocuN或旧runner，也不能调用其migrate函数。

历史事实继承如下。TASK120根/PG64/64、149失败和旧TASK117的81失败不清零。TASK123保守3710.557411/7200、三测试批3/3已封存；TASK124已结束，其未用预算不恢复。它们不是本卡额度。本卡此前没有运行尝试，不把旧失败写为零；新尝试单列并链接旧账，不重建第二份总状态账。

## 实施合同

### A 安装清单和无副作用计划

只支持未来获准的独立新集群中已明确创建的全新空数据库首次安装。现有正常库、用户库、旧TESTONLY库、恢复副本或共享集群的就地升级均不属于本工具本次能力。工具不承担创建/启动容器、数据库或卷，不调用Docker、Compose、start_local或应用。

清单使用当前实际15份SQL的固定白名单及原始字节hash，不glob任意未来SQL自动执行，不修改内容、换行或编码来通过既有source/profile检查，不删除或跳过角色碰撞guard。若源码自带BOM等需正常解码执行，明确区分原件hash与执行解码，保持SQL语义原样。

plan模式仅读取用户明确提供的非敏感安装参数及项目内固定SQL/产品配置结构，校验路径、清单完整性/顺序/hash、标识符、目标profile和关闭状态，给可判读的计划及实际缺口。未知CID、数据库OID、system_identifier、SID、dataset/instance/root身份不造值，不把未观察身份写成匹配，不签installed/verified或可外发结论。示例占位不能生成可执行通过结论。

help、默认路径、坏参数和plan不连接数据库、不读真实环境中的DSN/密钥、不装载应用、不构造ControlHub/QAuthority、不调用现capabilities，也不扫描私有配置。先完成本地参数/固定清单核验，再允许未来apply进入有副作用阶段。

### B 首次安装实现与权限隔离

apply必须是显式单独动作，接收将来受信操作人给出的精确目标身份和安全注入的安装连接。它在任何DDL/DCL或数据写之前，用只读查询核真实服务器/数据库与计划身份相符、目标确为空、必要前置版本适用、所需全局角色不存在。不得凭名字前缀、连上成功或旧TESTONLY身份推定正常目标。不匹配立即失败且零写入。

安装管理员连接只在短时安装路径使用。业务与快照采用分离的非超级登录身份，通过现已采用的NOLOGIN职责组获得必要权限；不得让业务身份获得superuser、CREATEROLE/CREATEDB/BYPASSRLS、对象owner或可经SET/INHERIT/ADMIN链取得的管理能力。现有q_roles/schema_checks的真实职责和拒绝语义必须复用，不能用只检查直接membership替代。不得为了通过检查扩大PUBLIC或任意owner授权。

全局角色已存在，即使名称相同或表面标志一样，本次首次安装也拒绝；不DROP/ALTER/重置旧角色、不照抄旧共享集群的替换/跳过SQL逻辑。本卡不设计通用多库角色复用方案。

完整执行001—015既有采用链，正常控制行及必要身份按真实依赖顺序建立，不遗漏data_control、maintenance摘要、当前profile和原业务/快照权限。只实现既有模型所需安装数据，绝不创建业务活动、模型结果、预扣、grant、operator批准、源清单或T0。任何必须写入的标识只在将来实际apply时按明确输入/生成过程记录；示例和本卡计划不预签真实身份。

各SQL有自身事务边界，必须尊重原BEGIN/COMMIT；不把15个文件谎称整包一个原子事务。安装元数据仅保存非敏感的固定文件hash、目标身份、已确认阶段和提交未知事实，不新建业务迁移账表或授权平台。途中失败保留已提交阶段；响应丢失按提交未知停止，禁止按无副作用自动重试、重建或清空。重复apply不得重放DDL。已完整成功对象只有与原收据和现有schema/角色实际一致时才能作只读复核，部分/未知状态只交回精确事实，不实现自动修复或续迁移。

凭据只通过明确的安全进程环境或输入通道注入，参数只放环境变量名或受忽略配置路径，不在argv/例子/输出/日志/安装收据回显密码、DSN、维护密钥及其hash。本卡不读取任何实际凭据，不重置账号密码。SQL对象名用现有psycopg安全标识符能力，不用字符串拼接用户输入。错误只返回稳定非敏感原因和确认到的阶段，不输出驱动原异常中的连接详情。

### C 关闭配置、启动衔接和交付说明

新示例是安装工具自己的明确输入，不能冒称现有loader支持的新schema。活动、integration、q-approval和预览仍使用已有原生结构且关闭；缺外部计量/账号/审计/首次启用事实时不得填写verified=true，不生成可用grant/manifest/operator票据。各独立data/backup/control/restore根只在将来受信部署时绑定；本卡不创建私有运行根或伪造ACL/file-id。

不改start_local的公开签名或重开语义，不让启动自动迁移。说明中清楚区分旧001入口、现在新增的完整首次安装入口、将来的只读核验及原正常启动。给最终实际可用参数、预期关闭结果、失败后保留数据和后续精确许可所需最少输入；不要再写不存在的--profile/--initialize/--migrate。

未来资源候选可引用原runbook的独立normal名称/卷/端口，但只作为未创建候选，不现在固定成已存在CID或调用权。本卡不签未来正常实例配置可用、真实loader已装载、Q首次启用或STEP完成。正常部署和外部门实际满足后，由主控另行冻结精确资源与运行合同。

## 允许、禁止与保护范围

允许新增仅deploy/initialize_normal.py、deploy/normal_install_manifest.json、deploy/normal-install.md、config/normal-install.example.json、backend/tests/test_normal_install.py；允许最小修改README.md。若文件接收时已出现，先核归属，不覆盖未知变化。可在指定execution目录写scratch测试数据、pre副本、普通证据、统一diff和结果。

禁止修改001—015、原start_local/initialize-materials/compose行为、backend/app任何文件、业务API/认证/时钟/费用/Grant/worker/恢复/profile/ACL校验、前端/dist、依赖与锁、真实配置、旧证据和归档、公共库、DocuS及主控orchestration文件。不得Git add/commit/push，不安装或联网，不创建后台进程。发现必须扩大文件/语义范围，先完成不受阻部分，再集中给具体最小diff提案，不自行扩大。

允许的代码实现是未来apply路径，不是本卡执行apply的权限。真实PG连接/查询/DDL/DCL、Docker/Compose/容器/卷、API/HTTP服务、浏览器/Job/renderer、模型/Embedding/计量服务、账号后台、用户资料/用户库、真实费用和真实远程写入全部上限0。不要inspect、探端口或读取旧.runtime来“补环境检查”。

本卡不变100/25和固定学习/面试/补证分额、两家provider、28Must/89动作/24片6索引。F124理由修正沿既有evaluate→progress事实，不再加中性备注接口或重开旧纠错逻辑。

## 离线验证与证据

先保存本次允许文件的原字节及hash。所有既有Git改动保留，diff以本卡pre为准；新文件标不存在，不把整库既有差异算本卡成果。真实测试字节和最终冻结字节须一致；修后只补受影响验证，不反复跑旧回归。

使用现有backend/.venv/Scripts/python.exe，-B避免pyc，按产品现有组织执行新增定向用例。仅标准库和项目已安装依赖，不安装新包。测试进程只传必要系统变量与合成占位，不继承两个provider key、真实DSN、私配路径、TESTONLY注入、sitecustomize或旧PYTHONPATH；不要读取它们的值再脱敏。

本批验证的必要观察如下，可在一个集中批内完成。

- 默认/help/plan/坏参数零连接、零子进程、零应用或授权构造，重复plan不写入安装结果或生成身份。
- 缺SQL、额外/重排/原件hash漂移、目标profile不符、目录越界/junction和已存在输出冲突按实际入口拒绝；没有对任意未来SQL的自动执行路径。
- 显式apply边界及只读预检优先，身份不符、非空库、角色碰撞时没有写请求；未知提交和部分阶段不进入自动重放/清理分支。可用最小执行记录器观察调用边界，不把它冒称真实PG事务、ACL或迁移验证。
- 使用现有纯角色校验函数的必要样本，确保安装说明/角色方案不允许业务或snapshot取得管理或跨职责权限；只证明输入方案与现有校验一致，不宣称实际角色已经建立。
- 示例保持关闭，不能产出启用回执；日志和错误中无测试哨兵凭据/DSN，产品源码没有对tests/DocuN/个人绝对路径/公共提示词库的运行依赖。
- README和新说明中的命令对应最终真实帮助/函数参数，旧正常启动与001入口未被暗改。

测试替身只能证明所观察的本地控制流，不能冒充SQL真实执行、回滚、profile匹配或正常首次安装成功。真实PG安装/权限与正常启动组合验证保留在未来精确运行卡，不在此卡偷偷追加。

复用TASK123原13方法和TASK124独审通过范围、TASK120/121原迁移/profile/权限既有证据，按对象与适用范围引用，不运行旧055/074/079/120等。不要为复用证据再造SQL字符串断言。

## 预算、停止与审计门

本卡新增工具wall上限10800秒，包含900秒保存/收尾；日历自permit签发起24小时。先到为门，等待用户转卡也不能越过许可截止。每条通常60秒，集中定向离线批最多600秒；初次一批，有明确修正依据最多两批复检，每批可合并全部受影响方法，不按子测试消耗根额度。无需为用完预算多做检查；全部通过即交付。

记录每次工具/测试实际退出、时长、对象hash和失败。不把回传等待计为工具实测，无法准确计时就标unknown并给不超过许可的保守包络。账户Sol/其它模型用量中断不等于产品预算重置；同卡恢复先核最后操作是否完成，只补缺失，不重复已成证据。

同一根因两次有依据修正仍失败、关键方案推翻、必须改原SQL/授权/数据模型/原运行入口、需要真资源或任何计量外发、范围/预算到门时，停止受影响部分并交具体差异。不要因外部计量仍缺就把本卡安装工具全部留成设计。

安装器涉及将来迁移和角色权限。稳定代码及原始离线证据保留给一次独立审查，在将来首次真实apply前完成该风险门，可与正常部署准备的集中审查合并。此卡普通自查不冒充独审；不按每个函数/文件再派审计，也不重审已验收的未变业务。当前只交工程候选，不自行执行高风险安装、签动态验收、Q启用、STEP018/019/020、M1或项目通过。

## 回传与最少人工

卡内连续完成实现、定向验证与普通修复，完成或达到停止门后一次交回。统一结果先写实际完成范围、未完成/未验证、真实文件差异和作用、命令/退出/耗时/原始证据导航，再写输入/规则hash、继承边界、失败账、预算、偏差、风险、需主控同步的文档变化和下一步。原失败及后续补证按轮次保留，不覆盖历史。

本卡不需要用户提供key、账单、释放内存或开服务。账号/分词外部材料保持原精确未决项，不发重复提问或供应商消息。唯一人工操作是用户转交本卡，完成后带回结果路径；无新资源需要用户手动清理。

保存并复读D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-125-result.md，只回复一句话结论与可点击完整绝对路径。共享状态、CHG和最终裁定由主控串行维护。
'''


def main():
    state_path = path('DocuS/执行动态文档.MD')
    arch_path = path('DocuS/架构动态文档.MD')
    change_path = path('DocuS/文档变更记录.MD')
    originals = {p: p.read_bytes() for p in (state_path, arch_path, change_path)}
    state = originals[state_path].decode('utf-8-sig')
    arch = originals[arch_path].decode('utf-8-sig')
    changes = originals[change_path].decode('utf-8-sig')
    assert '文档v2.92' in state[:120]
    assert '文档v1.64' in arch[:120]
    assert max(map(int, re.findall(r'CHG-(\d+)', changes))) == 1628
    assert not path('DocuN/tasks/TASK-125.md').exists()
    assert not path('DocuN/results/TASK-125-result.md').exists()
    rules = json.loads(path('DocuN/evidence/v4-migration-20260930/rules-snapshot.json').read_text(encoding='utf-8-sig'))
    for item in rules:
        actual = digest(Path(item['absolute_path']).read_bytes())
        assert actual == item['sha256'], item['relative_path']
    immutable = {
        'DocuN/evidence/TASK-123/execution/correction-01/finite-inputs.json': '79e843d4ccad235c85d24e01cd508160597cb0196baa56e686f9f96d8da0b1e5',
        'DocuN/evidence/TASK-123/execution/correction-01/deployment-handoff.md': '8ece65467fbc9c1ec59b0878c8dbf9564a9605324920c140d19c8879979e5f79',
        'DocuN/results/TASK-124-result.md': '60c7394a8315739e6468e6fc4ebd586300155edb7179555152c3efbea0e05661',
    }
    for relative, expected in immutable.items():
        assert digest(path(relative).read_bytes()) == expected, relative
    for relative in ('deploy/initialize_normal.py', 'deploy/normal_install_manifest.json', 'deploy/normal-install.md',
                     'config/normal-install.example.json', 'backend/tests/test_normal_install.py'):
        assert not path(relative).exists(), relative
    for original, content in originals.items():
        write('DocuN/evidence/TASK-125/orchestration-20261022/before/' + original.name, content)
    now = datetime.now(TZ)
    issued = now.isoformat()
    registered = f'''# 执行动态文档

文档v2.93，2026-10-22，Asia/Shanghai。唯一总状态账；需求v1.4、架构v1.65、task_model/07。以下v2.92原字节保留。

## TASK125/R119正常首次安装工具工程已登记

{issued}。用户明确要求继续给提示词，主控在已授权开发内选择可独立完成的部署工具工程，接续TASK123已明确的001入口不足。新增成果不再处理相同计量搜索，不恢复旧卡预算或创建资源。完整卡尚在保存核读，调度已登记，验收留空。

'''
    write('DocuS/执行动态文档.MD', registered.encode('utf-8') + originals[state_path])
    card = write('DocuN/tasks/TASK-125.md', CARD)
    assert card.read_text(encoding='utf-8') == CARD
    current = f'''# 执行动态文档

文档v2.93，2026-10-22，Asia/Shanghai。唯一总状态账；需求v1.4、架构v1.65、task_model/07。以下v2.92原字节保留。

## TASK125/R119正常首次安装工具链工程待人工转交，真实Q仍冻结

{issued}。用户明确要求提供接续提示词，主控登记TASK125/R119，完整卡DocuN/tasks/TASK-125.md已保存核读，状态待转交，验收留空。接收A+，优先原TASK123工程窗口复用部署交接；原124独审窗口不得承担实现。未发生转交、接收、开始或在途执行事实。

本卡是原部署缺口中可独立推进的本地工程，目标为正式首次空库安装器、固定001—015清单、关闭配置及用户说明，并完成定向离线验证。只允许新增指定deploy/config/test五文件及README最小更新。将来apply路径可以实现，本卡实际apply/PG/角色/数据库/容器/服务/浏览器/模型/联网/费用/Git全部0，不创建normal、grant、T0、实际loader或首次回执。安装器不能复制旧TESTONLY共享角色改写、凭据和注入；角色/权限及真实安装门留待稳定候选独审与后续精确资源许可。现阶段没有把工程已登记写成已实现或已验证。

新增工具wall10800秒含900收尾，日历24h；初次集中离线批及最多两批有据复检、每批至多600秒，无按子测试拆根额度。原TASK123的3710.557411/7200及三批3/3、124结束账、120根/PG64/64与149/旧117的81失败全部照留；新预算仅对应新部署代码，不恢复旧运行许可。

TASK123/F124-01有限收口不重开，13方法与原独审按范围继承；有效输入仍为correction-01两文件，外部计量/版本模板/Embedding容量和本人账号事实没有新增，Q继续冻结。只是不依赖这些材料的安装工具离线实现前移；实际正常实例初始化/角色写入/真实loader/绑定/首次启用仍须对应外部前置、独审及精确运行卡齐备。不得派相同搜索/设计/试跑绕启用门。

STEP018仍进行中/部分验证，019/020/M1/项目/发布未验；100次25元和固定分额、28Must/89动作/24片6批不变。主控本轮只核文件与只读Git差异、保存卡及共享文档，未运行产品或实时资源探针。基线与许可在DocuN/evidence/TASK-125/orchestration-20261022，CHG1629—1632，下一1633。

## 以下为v2.92及更早历史

'''
    write('DocuS/执行动态文档.MD', current.encode('utf-8') + originals[state_path])
    architecture = f'''# 架构动态文档

文档v1.65，2026-10-22，Asia/Shanghai。需求v1.4、执行动态v2.93、task_model/07。以下v1.64原字节保留。

## 正常首次安装工具进入离线工程，原业务与Q门保持

{issued}。TASK125/R119承接已确认的首次初始化只覆盖001的缺口，计划实现deploy/initialize_normal.py、固定001—015原件清单、关闭的安装参数示例与说明/测试。现仅待转交，均未实现或验证。本次不改变持久模型、业务API、角色职责、既有迁移、Grant或计费协议。

新工具仅面向未来精确获准的独立新集群空库首次安装，启动入口仍不自动迁移；只读plan与显式apply分开。SQL原文及现data_exit.v1.r03/角色能力核验保持，拒绝旧共享角色复用/修改guard与安装中断自动重放。安装代码的离线候选可在外部计量等待期间独立开发；实际PG/DDL/DCL、normal、启动和任何Q仍不授权。安装器权限/迁移风险在稳定后、首次实际apply前集中独审，不能由离线替身验证冒充真实PG成功。

TASK123/124不变readiness和准确理由读回结论继承，不重开旧实现；真实理由/恢复、真实Must语义和计量/本人账号缺口照留。100/25及固定分额、两provider与原28Must不变，不新增平台或部署服务。

## 以下为v1.64及更早历史

'''
    write('DocuS/架构动态文档.MD', architecture.encode('utf-8') + originals[arch_path])
    entries = f'''

- CHG-1629，{issued}，Codex编排Agent，DocuN/tasks/TASK-125.md。新建R119完整正常首次安装工具链离线工程卡，登记后核读为待转交，不含真实apply或Q。

- CHG-1630，{issued}，Codex编排Agent，DocuS/架构动态文档.MD。v1.65只登记新安装工具计划与固定既有模型/角色/真实运行门，未记为实现或验证。

- CHG-1631，{issued}，Codex编排Agent，DocuS/执行动态文档.MD。v2.93登记新单元、A+原窗、10800秒工具/24h离线边界和原账继承；旧关闭、外部门与Q冻结保持。

- CHG-1632，{issued}，Codex编排Agent，DocuN/evidence/TASK-125/orchestration-20261022。保存规则/输入及既有差异身份、旧共享原件、新合同许可和读回证明；主控无产品运行。
'''
    write('DocuS/文档变更记录.MD', originals[change_path] + entries.encode('utf-8'))
    sources = [
        'AGENTS.md', 'DocuS/最终需求文档.MD', 'DocuS/架构动态文档.MD', 'DocuS/执行动态文档.MD',
        'DocuS/文档变更记录.MD', 'README.md', '.gitignore',
        'DocuN/evidence/v4-migration-20260930/rules-snapshot.json',
        'DocuN/evidence/TASK-123/execution/correction-01/finite-inputs.json',
        'DocuN/evidence/TASK-123/execution/correction-01/deployment-handoff.md',
        'DocuN/evidence/TASK-123/orchestration-closure-20261022/closure-receipt.json',
        'DocuN/results/TASK-123-work-decision.md', 'DocuN/results/TASK-124-work-decision.md',
        'DocuN/results/TASK-124-result.md',
        'DocuN/evidence/TASK-122/preparation/operation-runbook.md',
        'DocuN/evidence/TASK-122/preparation/deployment-package.draft.json',
        'DocuN/evidence/TASK-122/preparation/readiness-plan.json',
        'deploy/start_local.py', 'deploy/initialize-materials.py', 'deploy/compose.local.yml',
        'config/local.env.example', 'config/data-exit.example.json', 'config/activity.example.json',
        'config/integration.example.json', 'backend/requirements.lock', 'frontend/package-lock.json',
        'backend/app/data_exit/schema_profiles.py', 'backend/app/data_exit/schema_checks.py',
        'backend/app/data_exit/q_roles.py', 'backend/app/data_exit/config.py', 'backend/app/data_exit/files.py',
        'backend/tests/fixtures/task120/setup.py', 'backend/tests/fixtures/task120/audit07_setup.py',
        'backend/app/main.py', 'backend/app/q_readiness.py', 'backend/app/activities/api.py',
        'backend/tests/test_q_readiness.py', 'backend/app/activities/teaching_repository.py',
        'backend/app/learning/teaching_progress.py',
    ]
    migration_names = [
        '001_materials.sql', '002_activities.sql', '003_pdf_review.sql', '004_activities_time_budget.sql',
        '005_activities_dispatch_closed.sql', '006_activities_running_owner_session.sql',
        '007_activity_operation_results.sql', '008_activity_tool_budget.sql', '009_teaching.sql',
        '010_learning_memory.sql', '011_text_interview.sql', '012_html_explanations.sql',
        '013_data_exit.sql', '014_step018_retrieval.sql', '015_activity_scope_delete_permission.sql',
    ]
    sources += ['backend/migrations/' + n for n in migration_names]
    identities = []
    for relative in sources:
        source = path(relative)
        raw = source.read_bytes()
        identities.append({'path': relative, 'absolute_path': str(source), 'bytes': len(raw),
                           'sha256': digest(raw), 'write_allowed': relative == 'README.md'})
    for rule in rules:
        raw = Path(rule['absolute_path']).read_bytes()
        identities.append({'path': rule['relative_path'], 'absolute_path': rule['absolute_path'],
                           'bytes': len(raw), 'sha256': digest(raw), 'write_allowed': False, 'public_readonly': True})
    manifest = dump('DocuN/evidence/TASK-125/orchestration-20261022/input-manifest.json', {
        'TASK': 'TASK-125', 'R': 'R-119', 'issued_at': issued, 'source_count': len(identities),
        'sources': identities, 'new_product_paths': [
            'deploy/initialize_normal.py', 'deploy/normal_install_manifest.json', 'deploy/normal-install.md',
            'config/normal-install.example.json', 'backend/tests/test_normal_install.py'],
        'git_status_readonly_observed': {
            'purpose': '现有差异不归本卡；主控未回滚或混入',
            'command': 'git status --short --untracked-files=no', 'exit_code': 0,
            'tracked_modified_paths': [
                'DocuN/evidence/TASK-120/execution/budget.json', 'DocuN/evidence/TASK-120/execution/case-index.json',
                'DocuN/evidence/TASK-120/execution/command_control.py', 'DocuN/evidence/TASK-120/execution/events.jsonl',
                'DocuN/evidence/TASK-120/execution/runtime_control.py', 'DocuN/tasks/TASK-120.md',
                'DocuS/执行动态文档.MD', 'DocuS/文档变更记录.MD', 'DocuS/架构动态文档.MD', 'README.md',
                'backend/app/activities/api.py', 'backend/app/activities/interview_repository.py',
                'backend/app/activities/repository.py', 'backend/app/activities/teaching_repository.py',
                'backend/app/capabilities/embedding.py', 'backend/app/capabilities/gateway.py',
                'backend/app/capabilities/q_context.py', 'backend/app/capabilities/q_gateway.py',
                'backend/app/capabilities/q_protocol.py', 'backend/app/data_exit/control.py',
                'backend/app/data_exit/deletions.py', 'backend/app/data_exit/maintenance.py',
                'backend/app/data_exit/packages.py', 'backend/app/data_exit/q_store.py',
                'backend/app/data_exit/schema_checks.py', 'backend/app/data_exit/schema_profiles.py',
                'backend/app/data_exit/snapshot.py', 'backend/app/interview/api.py',
                'backend/app/interview/policy.py', 'backend/app/learning/teaching_service.py',
                'backend/app/main.py', 'backend/app/memory/api.py', 'backend/app/memory/repository.py',
                'backend/app/memory/service.py', 'backend/app/operator/q_request.py', 'backend/app/preview/api.py',
                'backend/app/retrieval/service.py', 'backend/app/worker/launcher.py',
                'backend/tests/fixtures/task120/offline.py', 'backend/tests/fixtures/task120/resources.py',
                'backend/tests/fixtures/task120/run.py', 'backend/tests/fixtures/task120/setup.py',
                'backend/tests/fixtures/task120/transport.py', 'backend/tests/test_task120_outbound_approvals.py',
                'frontend/src/activities/ActivityWorkspace.tsx', 'frontend/src/activities/InterviewWorkspace.tsx',
                'frontend/src/activities/TeachingWorkspace.tsx', 'frontend/src/data/context.tsx'],
            'untracked_files_enumerated': False,
        },
    })
    permit = dump('DocuN/evidence/TASK-125/orchestration-20261022/permit.json', {
        'schema': 'retrolume.task-scope.v1', 'TASK': 'TASK-125', 'R': 'R-119',
        'execution_class': 'OFFLINE_FIRST_INSTALL_ENGINEERING_NO_Q',
        'issued_at': issued, 'deadline': (now + timedelta(hours=24)).isoformat(),
        'contract_sha256': digest(card.read_bytes()), 'input_manifest_sha256': digest(manifest.read_bytes()),
        'dispatch_status': '待人工转交', 'acceptance': None, 'recipient': 'A+原TASK123工程窗口优先',
        'tool_wall_cap_seconds': 10800, 'reserved_close_seconds': 900,
        'offline_test_batch_cap': 3, 'offline_test_batch_seconds': 600,
        'calendar_hours': 24, 'historical_budgets_reopened': False,
        'real_caps': {name: 0 for name in ('installer_apply', 'pg_connection', 'docker', 'container', 'volume',
            'database', 'role_mutation', 'api_service', 'browser', 'windows_job', 'preview', 'provider',
            'embedding', 'metering_api', 'network', 'fee_cny', 'git_write', 'delegation')},
        'Q': 'FROZEN', 'T0': None, 'normal_instance_created': False,
        'independent_review': '稳定候选后首次真实apply前，集中审查安装迁移/角色风险；不以本卡离线验证替代',
    })
    for row in identities:
        assert digest(Path(row['absolute_path']).read_bytes()) == row['sha256'], row['path']
    assert state_path.read_bytes().endswith(originals[state_path])
    assert arch_path.read_bytes().endswith(originals[arch_path])
    assert change_path.read_bytes().startswith(originals[change_path])
    assert '*' not in CARD and '〈' not in CARD and '| ---' not in CARD
    assert 'DocuN/evidence/TASK-125/execution/' in CARD
    assert not path('DocuN/results/TASK-125-result.md').exists()
    assert not path('deploy/initialize_normal.py').exists()
    proof = {
        'TASK': 'TASK-125', 'R': 'R-119', 'created_at': issued, 'checked_at': datetime.now(TZ).isoformat(),
        'status': '待人工转交', 'accepted': None, 'source_identities_checked': len(identities), 'drift': 0,
        'rules_match': 7, 'card_bytes': card.stat().st_size, 'card_sha256': digest(card.read_bytes()),
        'permit_sha256': digest(permit.read_bytes()), 'input_manifest_sha256': digest(manifest.read_bytes()),
        'shared_state_version': '2.93', 'architecture_version': '1.65', 'next_CHG': 1633,
        'historical_shared_bytes_preserved': True, 'new_product_files_created_by_orchestrator': False,
        'product_run': 0, 'Q': 'FROZEN', 'T0': None,
    }
    dump('DocuN/evidence/TASK-125/orchestration-20261022/save-proof.json', proof)
    print(json.dumps({key: proof[key] for key in ('TASK', 'R', 'status', 'source_identities_checked', 'drift',
          'card_bytes', 'shared_state_version', 'next_CHG', 'product_run', 'Q')}, ensure_ascii=False))


if __name__ == '__main__':
    main()
