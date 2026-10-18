# TASK-087 / R-081 — 业务结果原子提交与恢复读取实施合同（修正轮01置顶）

日期：2026-09-28。执行窗口：TASK-085/087 原最强实现窗口续用（同窗连续推进，实际模型 GLM-5.3-Flash，如实登记）。基线：需求 v1.1、架构 v0.51、执行状态 v1.71；Git 首提交 45951501d2741630a229762d6b2d3f4b34d7f702，既有未提交成果保留。
本卡为只读设计：未改源码/测试/DDL/正式 docu/公共库/旧证据，未运行 import/compile/unittest/PG/Windows Job/Docker/应用/模型，运行预算 0 消耗，未 Git 提交。仅写本结果与 Ndocu/evidence/task-087/revision-01/。
本文按修正轮01任务卡六项要求（K1—K6）一次重写完整推荐合同 A—D；首轮全文原样保留在文末"首轮原结果（历史保留）"，冲突以本文为准。

## 0.1 修正轮结论

唯一推荐事务方向与首轮一致并保留：**在存活 worker 的 `record_outcome` 既有短事务内，原子提交正文行与 received 终态**；不由退出后的旧 G 回执授予新写权。本轮修正的是合同的持久事实语义（K1）、读取失效抑制（K2）、关门门禁与幂等双路径（K3）、规范化与字节边界（K4）、协议逐跳与文件清单（K5）、验收矩阵补齐（K6）。

一句话语义（修正版）：**`ModelCallResult.status == SUCCEEDED` 收紧为"模型返回成功且正文行已与 received 同事务提交、且 `record_outcome` 已向 gateway 返回 `RecordOutcome.RECORDED/ALREADY_PRESENT` 确认"**；提交确认缺失时 gateway 不得声称 committed。回执协议 3 的 `business_commit` 为三值（`committed` / `not_committed` / `unconfirmed`），其中 `unconfirmed` 明确表示"提交结果未确认"，不得写成"未提交"。

可批准实施范围（供编排裁定，未获批不得实施）：1 个新迁移（007 草案）+ 7 个产品文件精确增量 + 2 个只读读取接口 + 跳2 协议升 3 + N1 早拒绝；验证为离线契约 + 真实合成 PG 定向（含提交前回滚/提交后响应丢失两类原子性证明）+ 最少 1 例 Windows 接线；实施后一次独立代码审计。

## 0.2 K1—K6 对照表

| 项 | 修正卡要求（摘要） | 首轮缺陷 | 本轮修正位置 | 遗留 |
| --- | --- | --- | --- | --- |
| K1 | 持久事实不由响应推断；业务/时间状态分开；回滚与提交-响应-丢失区分；DB 不可读按持久事实恢复；UNKNOWN 后正常退出走正常结算 | B4 把"record 报错"一律写成"事务回滚、dispatched、无正文、终局丢失"并标 received_without_committed_payload；UNKNOWN 全额预扣表述过宽 | B2（record 异常三分类）、B4（完整组合矩阵）、B5、C2（三值回执）、D3 T13/T20a/T20b、D4 轨2/轨3 | 无 |
| K2 | 失效隐藏由读取接口落实；read/list 一致；历史事实与使用资格分开；来源/scope 绑定失败关闭；SQL 形状/分页/字节边界 | C1 只返回 payload+sources_current advisory，把隐藏责任留给消费方；无分页/字节边界设计 | C1 全节重写（SQL CASE 投影、状态枚举、EXISTS、游标分页、payload_integrity 与状态区分） | 无 |
| K3 | 正文新写显式查 dispatch_closed；关门后新写与无写幂等确认分两条路径；旧 received 无正文不得补写；权力边界不写零；持久保证限定真实仓储 | 声称复用 _operation_is_current 已含关门检查（不实）；"新增权力边界=零"不准确；record_outcome 返回 None 无确认语义 | B2（分支序与 dispatch_closed 显式检查）、B3（权力边界改写）、A4.8（RecordOutcome 枚举）、D6 | 无 |
| K4 | 规范化定义明确（字节等值 vs 语义等值）；bounded 不能当重复键检测；64KiB→128KiB 扩张不承诺恒不触限；helper 落点不倒置依赖；DDL/应用侧各自承诺 | "封套仅多固定短前缀恒不触限"错误；json.dumps 未 sort_keys 的等值语义未定义；依赖落点未指定 | A4.1—A4.5、A4.8、C2（回执去正文副本）、D3 T01/T17 | 无 |
| K5 | 逐跳协议版本明确；N1 与 D1 对齐；完整文件清单与 FK 清理链；007 首次/重复执行分开定义；无性能承诺 | "请求/回执同步3"与"session.py/launcher 不变"矛盾；"4个文件"与实际清单不符；007 幂等性凭 CREATE TABLE 声称；"3秒绰绰有余"无依据 | C2（跳1 保2/跳2 升3 逐跳表）、D1（9 文件+测试+FK 清理链）、D2（首次/重复定义）、B2（删性能承诺）、D5（N1 落 session.run_once） | 无 |
| K6 | 补提交前回滚/提交后响应丢失/两个先后次序/结算失败恢复读取/scope 失效/关门后首提交/伪 hash 与配对反例；推演不硬编码"异常=回滚" | T 矩阵缺上述各项；B4 推演未区分回滚与未知 | D3（T11b/T13b/T16b/T20a—T20d）、D4（轨2/轨3 重写） | 无 |

**未解决的最少关键决定（交编排）**：① 主要持久模型变更（新表 `activity_operation_results`、SUCCEEDED 语义事务化收紧、回执协议 3 去正文副本、`record_outcome` 返回枚举的接口签名变化）须按既有授权流程批准后方可实施——本卡只形成可审方案，D6 列明边界；② `unconfirmed` 状态的受限幂等重放接口已定义（B4），但其调用方（未来 G4 接线/对账工具）不在本切片，属既有登记缺口，不阻塞实施。除此之外无须用户回答的技术细节。

## 1. A — 唯一推荐范围和数据合同

### A1 本切片提交什么（同首轮，口径修正）

| 概念 | 内容 | 是否持久 |
| --- | --- | --- |
| 原始模型结果 | 供应商完整 HTTP 响应体 | 否。仅既有元数据列（response_bytes/usage/returned_model/finish_reason/remote_request_id） |
| 经过验证内容 | `_parse_success` 校验通过的 `text` 或 `json_object`（finish_reason=stop、非空、JSON 深度≤12/节点≤2000、无截断、有限数） | **是——本切片持久化的业务正文** |
| 业务产物封套 | `{"format":"text"|"json","value":<content>}` 规范化字节 + 身份/来源关联列 | 是；正文列存封套整体规范化字节（A4.1） |

- 成功定义（修正）：仅 `status=SUCCEEDED` 且 `record_outcome` 返回 `RECORDED/ALREADY_PRESENT` 构成有效业务成果；TOOL_PLAN/FAILED/UNKNOWN/NOT_SENT/REJECTED 一律无正文行。`SUCCEEDED ⇒ 本地存在提交事实`成立（拟收紧语义）；反向 `DB 已提交 ⇒ 调用方必收到 SUCCEEDED` **不成立**（commit 响应丢失时调用方收到 UNKNOWN/unconfirmed，B4 组合 5）。
- 可读取者：与活动同信任域的可信内部组件；本卡不新增对外 HTTP。
- 范围：仅现有 one_call 一个最小成果；不建全领域表、不做通用事件平台、不做"全历史完美回放"。

### A2 DDL 草案（仅本文提出，不创建正式迁移）

```sql
-- TASK-087 修正轮01 候选迁移 007：业务成果正文（G3 切片）。本卡只写不执行。
-- 首次执行前置：002 已建（activity_operations 存在）；不要求 activities 为空。
-- 重复执行：不支持（CREATE TABLE 无 IF NOT EXISTS，重复执行报 duplicate table 并整体回滚），
--           不凭 CREATE TABLE 声称幂等——与 004/005 的"仅空库 ALTER"是两种不同约定（D2）。
BEGIN;
CREATE TABLE activity_operation_results (
    activity_id UUID NOT NULL,
    operation_id VARCHAR(128) NOT NULL,
    admission_id UUID NOT NULL,
    execution_generation INTEGER NOT NULL CHECK (execution_generation >= 0),
    scope_revision INTEGER NOT NULL CHECK (scope_revision > 0),
    payload_format TEXT NOT NULL CHECK (payload_format IN ('text', 'json')),
    payload TEXT NOT NULL CHECK (octet_length(payload) BETWEEN 1 AND 131072),
    payload_sha256 TEXT NOT NULL CHECK (payload_sha256 ~ '^[0-9a-f]{64}$'),
    committed_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (activity_id, operation_id),
    FOREIGN KEY (activity_id, operation_id)
        REFERENCES activity_operations(activity_id, operation_id)
);
COMMIT;
```

- 必要索引：无新增（PK 前缀 activity_id 支持按活动列出；被引用表 PK 已存在）。
- 列级/表级与应用侧承诺的准确边界（K4）：DDL CHECK 只保证格式域（枚举、字节长度区间、hash 形状、非负整数）；**`payload_sha256` 与 `payload` 实际字节的匹配、封套规范形态、超限拒绝、幂等/冲突规则均由应用侧构建与读取复算保证**（A4、C1），64 位 regex 不能证明正文匹配。冗余 `admission_id/execution_generation/scope_revision` 由锁内 `activity_operations` 行取值（B2 步骤⑦），不接受调用者伪造。
- 正文上限 131072 = one_call `MAX_DATA_BYTES`；one_call 生产配置 `max_request_bytes/max_response_bytes ≤ 65536` 下封套编码后**仍可能**超限（JSON 转义/元数据扩张，K4），故按实际编码后字节显式拒绝（A4.5），不承诺恒不触限；更大响应配置被 `payload_limit` 拒绝是显式边界。
- 无新增依赖/PG 扩展/平台。

### A3 为何现有字段不够（同首轮结论，读取行修正）

| 需求 | 现有承载 | 不足 | 结论 |
| --- | --- | --- | --- |
| 业务正文（≤128KiB） | disposition/error_code/response_bytes 等 | 无可容纳列 | 新表新列 |
| "已提交"标记 | state CHECK 仅 5 枚举 | 扩枚举破坏既有语义 | 不加状态：行存在=已提交 |
| 幂等与冲突判定 | 操作 PK+admission UNIQUE | 不保证正文一致 | 同 PK + 规范字节 hash 等值（A4.4） |
| 来源失效可见性 | `_lock_sources` 仅写路径 | 读路径无法反映 | **读取接口默认抑制失效正文（C1），不是 advisory 旗标** |

### A4 身份冲突、hash/规范化、重复提交规则（K4 修正）

1. **规范化定义 = 规范字节等值（canonical byte equality）**，非 JSON 语义等值：封套字节 = `json.dumps({"format": F, "value": V}, ensure_ascii=False, separators=(",", ":"), allow_nan=False).encode("utf-8")`。键序按解析对象插入序（不 sort_keys）；数字按 Python `json.dumps` 输出（int 原样、float repr）；控制字符与引号按 JSON 转义（`\n`→`\\n`）；非 ASCII 不转义。幂等比较 = 存储行 `(payload_format, payload_sha256)` 与新提交计算值按字节等值。**明确不承诺语义等值**：同一逻辑 JSON 不同键序/数字字面量重放属异文冲突，不做跨形态规范化；同对象重放（唯一实际路径：同一 worker 进程内存中的同一 result 对象，或持有原参数的受限重放方）字节稳定。测试 hash 稳定性按本定义（T01）。
2. **重复键**：正文来自 `_safe_json_loads` 解析后的 dict，Python `json` 语义下重复键在解析时坍缩（后值覆盖）；本合同**不检测、不拒绝重复键**，hash 绑定坍缩后字节。`one_call.bounded` 返回原对象、非序列化字节，也不能充当重复键检测（K4），不用于本路径。
3. **helper 落点与依赖方向**：新增纯函数 `canonical_payload_bytes(envelope) -> bytes` 与 `payload_digest(envelope) -> str` 放 `app/capabilities/contracts.py`（gateway/repository/one_call 共享，capabilities ← worker 现有方向不倒置）；`one_call.bounded` 服务 IPC 帧界校验，保留不动，不复用为正文规范函数。
4. **提交资格**：与 record_outcome 同源（`_operation_is_current` + payload 路径额外显式 `dispatch_closed` 检查，B2）。
5. **超限/非法拒绝先于写行**：封套编码后 `len(bytes) > 131072` → `ResponseValidationError("payload_limit")` → FAILED(received) 无正文（先拒后写，不写坏行再靠读取发现）；hash 必须由 helper 对实际字节计算，伪 hash/格式不符在 `_outcome_values` 校验拒绝。
6. **重复提交（幂等）**：终态上重放相同 outcome+相同 (format, sha256) → `ALREADY_PRESENT` 零改写；**旧 received 无正文不得由重放补成"已提交"**（无正文终态是已完成的事实——FAILED/TOOL_PLAN 或旧合同历史），带 payload 的重放对无正文终态一律 `AdmissionDenied`（B2 步骤③）。
7. **异文冲突**：同键不同 (format, sha256) → `AdmissionDenied("payload_conflict")` 整体回滚，先到先得不可覆盖。
8. **record_outcome 返回值（K3）**：`AdmissionLedger.record_outcome` 返回类型由 `None` 改为枚举 `RecordOutcome`（`RECORDED` / `ALREADY_PRESENT`）。SUCCEEDED 持久保证**仅由符合本合同的 PostgresAdmissionLedger 提供**（单事务 ACID + 枚举确认）；gateway 校验返回值必须是枚举成员，替身返回 None/其他值视为合同违反 → UNKNOWN（`record_unconfirmed`）。`RejectingAdmissionLedger` 保持抛 `AdmissionUnavailable`（失败关闭）。无异常本身不构成任何实现的持久证据。
9. **并发**：同一操作并发 record 在 `activity_operations` 行 FOR UPDATE 上串行，锁内先查后插，无并发插入窗口。

### A5 预算、UNKNOWN、幂等边界（K1 修正）

- 次数/费用：admit 预留零变化；成功提交不退预留（既有行为）。时间账 M/R/S、预扣、关门、结算零变化；正文不占时间账。
- record 异常三分类（修正核心，详见 B2/B4）：`AdmissionDenied/ActivityLedgerConflict`（事务内确定性抛出）= 确定回滚未提交；`AdmissionUnavailable`（psycopg.Error，含 commit 响应丢失/连接断/超时）= **提交状态未知**；正常返回枚举 = 确定提交。
- 不隐式重发、不生成新 operation 蒙混重试；重试必须走新操作并重查额度。本地仅承诺提交/读取幂等；不承诺远端 exactly-once。供应商已收费但本地丢失正文 = 业务终局丢失，只能新操作重试（ADR-005 既有代价，如实声明）。
- **gateway 返回 UNKNOWN 后 worker 正常写回执并 exit 0 → SUP 按既有关闭/结算正常走（S+=C），不是全额预扣**；仅 worker/SUP 被硬杀或未结算时才按原残留规则保守收场（B4 组合 5/6、D4 轨2）。

## 2. B — 时序、所有者与事务

### B1 真实函数级调用链（[G3]=本切片增量）

```text
launcher.run_supervised_window(...)                        # 不变（跳1 协议 2 保留）
└─ supervisor_main.main → _validated_request（协议2）      # 不变
   └─ SingleWindowSupervisor.run_once(...)
      ├─ [G3] one_call 分支入口：config.request_timeout_seconds > 120 → ValueError
      │    （N1 早拒绝，位于 claim/预扣之前；idle 分支不校验，保留 idle 可用域）
      ├─ inspect_window → claim_lease(G+1, R=W_eff)        # 不变
      ├─ NamedMapping.create + worker_request（[G3] 跳2 协议 3）
      ├─ spawn_suspended(worker_main one_call) → resume
      │    └─ worker: execute_one_call(value)
      │         ├─ decode_worker_request（[G3] 校验协议 3）
      │         ├─ gateway.call → admit / mark_dispatch_started（不变）
      │         ├─ transport.send（无事务；网络不进 DB 事务，不变）
      │         ├─ _parse_success → SUCCEEDED(text|json)
      │         ├─ [G3] envelope → canonical_payload_bytes → 超限→FAILED(payload_limit)；
      │         │    hash = payload_digest(envelope)
      │         └─ _finish: record_outcome(permit, outcome+payload 三元组)
      │              BEGIN（锁序来源→活动→操作，不变；3s 语句/2s 锁/5s idle 上限保持，
      │                    不加性能承诺——128KiB 写入耗时由未来定向验证确认）
      │                ① 终态幂等分支（先于 current，见 B2）
      │                ② _operation_is_current 校验
      │                ③ [G3] payload 新写分支：显式 dispatch_closed=False 检查
      │                ④ UPDATE activity_operations（received+元数据，原语句）
      │                ⑤ [G3] INSERT activity_operation_results（锁内行取值）
      │              COMMIT → 返回 RecordOutcome.RECORDED/ALREADY_PRESENT
      │         └─ [G3] 回执（跳2 协议3：business_commit 三值，result 去正文副本+payload_sha256）
      ├─ wait_empty_until → C=ceil(elapsed)                 # 不变
      ├─ decode_receipt（[G3] 协议3 配对校验；失配→failed_closed）
      ├─ job.close → begin_window_close（仅置 dispatch_closed=TRUE，**不递增 G**）
      └─ settle_execution_window（S+=C、R-=W、**G+1 在此发生**）
```

恢复/重启读取（[G3] 新增，只读）：`read_committed_result` / `list_committed_results`（C1）。

### B2 record_outcome 扩展（单事务；分支序与既有完全兼容）

```python
async def record_outcome(permit, outcome) -> RecordOutcome:
    values = self._outcome_values(outcome)   # [G3] 扩展：payload 三字段同存同缺、format 枚举、
                                             # octet_length∈[1,131072]、sha256 regex；payload 仅随
                                             # RECEIVED 且 state∈dispatched 的新写或终态等值重放
    async with tx:                           # 超时参数不变
        activity, call, sources_valid = await self._locked_operation(permit)  # 锁序不变
        if call["state"] in {"not_sent", "received", "unknown"}:   # ③ 终态幂等分支（先于 current，
            stored = self._stored_outcome(call)                    #    与既有顺序一致）
            stored_payload = await self._stored_payload_row(connection, call)  # (format,sha256)|None
            if stored == values_meta:
                if outcome 带 payload:
                    if stored_payload == (fmt, sha256): return RecordOutcome.ALREADY_PRESENT  # 无写确认
                    raise AdmissionDenied("已终结无正文状态不能补写正文")   # 旧 received 无正文/unknown/not_sent
                return RecordOutcome.ALREADY_PRESENT
            raise AdmissionDenied("已终结调用不能覆盖为不同结果")          # 含异文 payload_conflict
        current = self._operation_is_current(activity, call, sources_valid)  # 不查 dispatch_closed（实读事实）
        if not current and disposition is not UNKNOWN:
            raise AdmissionDenied("失效或过期执行只能登记 unknown 诊断")     # 原行为
        if call["state"] == "reserved" and disposition is not UNKNOWN:
            raise AdmissionDenied("尚未越过发送边界的调用不能登记该结果")     # 原行为
        if outcome 带 payload:                                        # [G3] 新写分支
            if activity["dispatch_closed"]:
                raise AdmissionDenied("关闭门后不接受正文新写")            # K3 显式检查，独立于 current
            UPDATE activity_operations ...（received+元数据，原语句不变）
            INSERT INTO activity_operation_results(...)                  # admission/G/scope/executor
              SELECT 自锁内 call 行取值，不接受调用者声称                  # K4
        else:
            UPDATE activity_operations ...（原语句不变）                   # 原非正文诊断/UNKNOWN 路径不改
    return RecordOutcome.RECORDED
```

- 关键事实（实读源码，K3）：`_operation_is_current`（repository.py:913-925）校验 sources/status/executor/G/scope/租约/截止，**不含 dispatch_closed**；`begin_window_close`（465-498）仅置 `dispatch_closed=TRUE` 不递增 G；`settle_execution_window`（571-584）才 G+1。故正文新写分支必须显式检查 dispatch_closed，不能声称复用 current 已含该检查。
- **关门后两条路径（K3）**：a) 关门后**新写**正文（INSERT/首次 received）→ 被 dispatch_closed 检查拒绝（回滚，无行）；b) 关门/settle 后**相同已提交事实的无写确认**（终态分支，元数据+payload 逐元组相等）→ `ALREADY_PRESENT`，零改写、无需 current、无需门开。两路径分开定义，不存在"一处关闭后全拒另一处又允许幂等"的矛盾。G 关闭（settle 完成、活动 pending）后旧 G 首次插入正文的通道为零（current 校验：executor 已 NULL/G 不等必拒）。
- 失败回滚后的持久事实（K1 修正）：事务回滚 ⇒ UPDATE 与 INSERT 同生共死，两表无半写；操作行保持 `dispatched`（**不是 received**），读取分类 `unresolved_or_unknown`，由既有 `recover_unknown/recover_obsolete_operations` 收敛 unknown——**不是 received_without_committed_payload**（后者仅描述终态 received 且无正文行的正常 FAILED/TOOL_PLAN 或旧历史）。

### B3 与"085 结束后 G 已推进"问题的解决及权力边界（K3 修正）

- 提交发生于 worker 存活、G 当前、租约有效、门未关之时（record_outcome 原有时点）；关门/结算只使 G 前移，不能追溯取消已提交正文。回执不携带任何可执行权力。
- **权力边界（修正措辞，K3）**：worker 原有 DSN 上的写权限于操作元数据列；本合同在同一连接、同一锁序内**扩展出"持久化业务正文"的新写权力**（新表、新列、SUCCEEDED 语义收紧），复用同一 DSN 不等于权力边界为零——这是须编排/用户批准的实质持久模型扩展（D6）。SUP 退款/预算权力（claim/settle/cancel 算术与语义）本合同零改动。
- 被杀关系：record 事务提交后被杀 → 正文已持久（COMMIT 已返回）→ 任意后续结局只是时间账问题；事务中被杀 → 连带回滚、两表无半写。

### B4 响应/持久状态完整组合矩阵（K1）

| # | record 路径 | gateway 返回（=回执 status/error_code） | business_commit | activity_operations 行 | results 行 | 读取/恢复 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | SUCCEEDED+payload，事务正常返回 RECORDED/ALREADY_PRESENT | SUCCEEDED | committed | received（disposition=received） | 有 | committed（C1 快照按失效规则细分） |
| 2 | FAILED/TOOL_PLAN，事务正常返回 | FAILED / TOOL_PLAN | not_committed | received | 无 | terminal_without_payload（正常终态，无正文是事实而非异常） |
| 3 | record 抛 AdmissionDenied（资格失效/冲突/终态异文，确定性回滚） | UNKNOWN / record_denied | not_committed | **dispatched（未终结）** | 无 | unresolved_or_unknown → 既有 recover 收敛 unknown |
| 4 | record 抛 AdmissionUnavailable（连接断/超时/commit 响应丢失） | UNKNOWN / record_unconfirmed | **unconfirmed（提交结果未确认，不得写成未提交）** | dispatched 或 received（不可知） | 无或有（不可知） | **不重新出站**；恢复后先查 `read_committed_result`（同 activity/operation/permit 身份）或以原 permit+outcome+payload 做受限幂等重放：命中终态等值 → ALREADY_PRESENT（确已提交）；行仍 dispatched 且 current 仍真 → 本次真正写入（补记账，非重发）；已失效 → AdmissionDenied → 保守收敛。重放需持有原 permit+完整 outcome+原 payload；不能取得正文（如 worker 已死、内存丢失）→ 无法重放，操作由 recover 收敛 unknown，正文业务性丢失=ADR-005 既有代价，只能新操作重试 |
| 5 | 组合1/4发生后 worker 正常写回执 exit 0 | — | — | — | — | SUP 树零 → 关门 → settle S+=C 正常结算，**不是全额预扣** |
| 6 | record 提交后 worker 被硬杀（回执丢失） | 无回执 | — | received | 有 | stop_ns 后 terminate → stopped_at_deadline → R 残留全额保守折叠；正文行幸存，read=committed |
| 7 | transport 层未知（超时/断连），record(UNKNOWN) 正常返回 | UNKNOWN / delivery_unknown 等 | not_committed | unknown 终态 | 无 | unresolved_or_unknown（发送未知，无正文是事实） |
| 8 | admit 拒绝 | REJECTED | not_committed | 无操作行 | 无 | not_found |

- 时间结算与业务提交分离重申：业务已提交但结算失败/响应丢失 → 既存事实按 B4 组合 1/4 读取，时间账按既有保守规则（新 claim 折叠 R→S）；时间已结算但正文未提交（组合 2/3/7）→ 不得谎称业务完成，读取如实呈现。不退款、不延时、不绕关闭门、不改 D3 信任范围。

### B5 竞争冲突统一机制（同首轮，关门行按函数级事实改写）

| 竞争 | 串行化点 | 先后次序与边界 |
| --- | --- | --- |
| 提交 vs 取消 | activities 行锁 | 取消先 → record 非 UNKNOWN 拒（回滚无行）→ dispatched 残留 → recover unknown；提交先 → 正文保留，取消照常（R→S 全额），读取按 C1（cancelled 活动的已提交成果正文可读+标注，不构成新写/发送授权） |
| 提交 vs 来源撤销/替换 | material_sources 行锁 | 撤销先 → sources_valid=false → 非 UNKNOWN 拒，无正文；提交先 → 正文保留，读取 INVALIDATED_SOURCE 抑制正文 |
| 提交 vs scope_revision 变化 | activities 行锁+等值 | 变化先 → 等值失败拒；提交先 → 行内 scope 快照固化，读取时 activity.scope_revision≠行内 → INVALIDATED_SCOPE_CHANGED 抑制正文（失败关闭，不具历史绑定证据即不展示） |
| 提交 vs 关门 | activities 行锁 | 关门先 → 新写被 dispatch_closed 检查拒；已提交事实的等值重放 → ALREADY_PRESENT（两路径，B2） |
| 提交 vs 租约过期/新 G | activities 行锁 + current | 过期/新 G 后晚到 → 仅 UNKNOWN 诊断，无正文通道 |
| 并发重复提交 | 操作行锁+PK+hash | 首个 RECORDED；相同 → ALREADY_PRESENT；异文 → payload_conflict 回滚 |

### B6 G4 缺口声明（同首轮，不变）

本设计验证的来源权威 = `material_sources.current_version/revision` 与 `activity.scope_revision` 等值。不假设调用者可信维护 revision：`CallContext.scope_revision` 由调用方声明、admit/record 只做等值兜底；谁在来源变化时递增活动 revision、谁下发新范围（G4 真实范围修改入口）仍未接线，属既有登记缺口，本合同不解决、不掩盖；读取侧对无法证明绑定当前 scope 的历史成果失败关闭（C1）。

## 3. C — 读取和可见性（K2 全节重写）

### C1 读取接口（内部合同，不新增 HTTP；失效隐藏由接口落实）

```python
class ResultReadStatus(StrEnum):
    COMMITTED_CURRENT = "committed_current"                    # 有效，含正文
    COMMITTED_HISTORY_CANCELLED = "committed_history_cancelled"  # 活动已取消，正文可读+标注，无任何写/发送授权
    INVALIDATED_SOURCE = "invalidated_source"                 # 来源失效：仅标识/元数据，无正文
    INVALIDATED_SCOPE_CHANGED = "invalidated_scope_changed"   # scope 不符：同上
    NO_OPERATION = "no_operation"                             # 无操作行
    UNRESOLVED = "unresolved"                                 # state∈reserved/dispatched/unknown
    TERMINAL_WITHOUT_PAYLOAD = "terminal_without_payload"    # 终态 received 无正文行（正常 FAILED/TOOL_PLAN 或旧历史）

@dataclass(frozen=True)
class CommittedResultSnapshot:
    activity_id: str; operation_id: str; admission_id: str
    execution_generation: int; scope_revision: int            # 行内快照（提交时锁内取值）
    provider: str; configured_model: str
    finish_reason: str | None; returned_model: str | None; remote_request_id: str | None
    prompt_tokens: int | None; completion_tokens: int | None; response_bytes: int | None
    payload_format: str | None
    payload: str | None = field(default=None, repr=False)      # 敏感正文默认 repr 隐藏（K2）
    payload_sha256: str | None = field(default=None, repr=False)
    committed_at: datetime | None
    activity_status_now: str | None; activity_scope_revision_now: int | None
    read_status: ResultReadStatus

async def read_committed_result(activity_id, operation_id) -> CommittedResultSnapshot
async def list_committed_results(activity_id, *, limit<=200, after_operation_id) -> tuple[CommittedResultSnapshot, ...]
```

**失效隐藏规则（read/list 一致执行，调用者无法选择忽略）**：
1. 抑制条件恰好两种（K2）：来源失效（activity_scope_sources 任一来源在 material_sources 的 current_version/revision 与快照不符或已无 current_version）；结果行 scope_revision ≠ 当前 activity.scope_revision。命中任一 → SQL 投影 `payload=NULL`，返回状态+标识+必要元数据（operation_id/admission_id/committed_at/payload_sha256/payload_format/G/scope 快照），**不返回正文与任何可用引用**。
2. 取消后的已提交成果：正文可读（无删除发生，DR-002 保留至用户删除），但 `read_status=COMMITTED_HISTORY_CANCELLED` + `activity_status_now=cancelled` 显式标注；区分"历史提交事实"与"当前可使用资格"，历史存在不构成新写/发送授权。
3. 历史绑定规则：结果行携带提交时锁内取的 scope_revision/G 快照；未来 activity_scope_sources 变化时不把新范围当旧成果的来源快照；不具历史绑定证据（revision 不等）即失败关闭。不假定未实现的 G4 已解决。
4. 快照边界（K2）：判定与投影在**一个语句快照**内完成（下述单条 SQL），无 FOR UPDATE、不参与锁序竞争；本切片不宣称撤回已返回字节；未来 HTTP/模型消费边界仍须实时权威校验，快照资格不授予无限期使用权（G4/接线缺口如实登记）。
5. `unconfirmed`（B4 组合4）恢复后的读取：直接走本接口按持久事实定界（有行=committed），无需先重放。

**SQL 形状（K2：EXISTS 避免多来源 JOIN 重复）**：

```sql
SELECT o.state, o.disposition, o.admission_id, o.execution_generation AS op_generation,
       o.scope_revision AS op_scope, o.provider, o.configured_model,
       o.finish_reason, o.returned_model, o.remote_request_id,
       o.prompt_tokens, o.completion_tokens, o.response_bytes,
       r.payload_format, r.payload_sha256, r.committed_at,
       a.status AS activity_status_now, a.scope_revision AS activity_scope_revision_now,
       CASE WHEN a.scope_revision = r.scope_revision
             AND NOT EXISTS (SELECT 1 FROM activity_scope_sources s
                             JOIN material_sources m ON m.id = s.source_id
                             WHERE s.activity_id = %(activity_id)s
                               AND (m.current_version IS NULL
                                    OR m.current_version::text <> s.version_id::text
                                    OR m.revision <> s.source_revision))
            THEN r.payload ELSE NULL END AS payload          -- 失效正文不出进程（K2）
  FROM activity_operations o
  LEFT JOIN activity_operation_results r
         ON r.activity_id = o.activity_id AND r.operation_id = o.operation_id
  JOIN activities a ON a.id = o.activity_id
 WHERE o.activity_id = %(activity_id)s AND o.operation_id = %(operation_id)s
```

- list 变体：同判定列（CASE → 有效性布尔）、`operation_id` 升序游标（`after_operation_id` keyset）、`LIMIT %s`（1..200）；**轻量投影不取 payload 列**，页返回字节天然有界（无正文，每行数百字节 × ≤200）；正文获取必须走 read 单条（≤131072 字节）。read/list 的失效抑制规则完全一致。
- **hash 复算只在有效分支**（payload 非 NULL 时 `payload_digest` 复算）：不符 → 抛 `payload_integrity` 完整性错误，不冒充读取状态、不返回正文；失效分支不复算（正文从未出进程）。**状态与完整性错误区分**：状态枚举是正常业务状态；`payload_integrity` 是错误（异常），两者不混用。
- 参数校验同 `list_unresolved_operations` 口径（UUID/受限字符集/limit 域）；授权由调用方层负责（可信内部组件），投影不得直接暴露 HTTP/工具/模型（R-064 口径）。新方法零日志；业务正文不进诊断日志。无用户批准的新历史正文导出接口，不存在绕过抑制的开关。

### C2 回执演进（K1/K4/K5：跳1 保 2、跳2 升 3、三值、去正文副本）

**逐跳协议版本（K5）**：

| 跳 | 通道 | 现状 | 本合同 | 说明 |
| --- | --- | --- | --- | --- |
| 跳1 | launcher `_request`/`_decode_outcome` ↔ supervisor_main `_validated_request`/`write_result` | 硬编码 2（launcher.py:192/208；supervisor_main.py:27/83） | **保留 2** | 该跳不携带业务提交语义、无字段变化；升版无信息增益、徒增差异面 |
| 跳2a | `worker_request`（SUP→worker） | 硬编码 2（one_call.py:90/97） | **升 3** | 与回执同版防混：`decode_worker_request` 校验 `protocol==3`，≠3 拒绝 |
| 跳2b | `receipt`/`decode_receipt`（worker→SUP） | 硬编码 2 + business_commit 字面量 "not_committed"（one_call.py:117-118/128-129） | **升 3** | session.py:311 与 launcher.py:294 消费 `decode_receipt` 自动获得新校验（两文件零改动）；嵌套 `model_receipt` 在跳1 帧（协议2）内由 decode_receipt 校验协议3，两层版本各自独立校验 |

idle 兼容：idle worker `argv==["idle"]` 直返 0，不经 decode_worker_request；SUP idle 分支 exchange=None——跳2 升版不影响 idle。混版拒绝：任一跳版本不符即 ValueError/ManagerControlError。生产/测试同仓库同版本发布，无跨版本混跑；085 夹具中写死跳2 协议 2 的用例在实施卡一并更新（D1）。

**business_commit 三值与配对规则**：

| status | business_commit 允许值 | payload_sha256 | 持久含义 |
| --- | --- | --- | --- |
| succeeded | **仅 committed** | 必为 64hex | 正文行已随 received 同事务提交且 record 已返回确认（B4 组合1） |
| unknown | not_committed \| **unconfirmed** | None | not_committed=确定无正文行（record 确定性回滚/发送未知/UNKNOWN 终态）；unconfirmed=正文行存在性未知（record 以 AdmissionUnavailable 结束，error_code=record_unconfirmed） |
| rejected / not_sent / failed / tool_plan | **仅 not_committed** | None | 无正文路径 |

反例一律 ValueError 拒绝：succeeded+not_committed、succeeded+unconfirmed、unknown+committed、failed+committed、committed 而无 hash、not_committed 而有 hash。worker 侧 `receipt()` 推导：succeeded→committed（缺 hash 属内部错误即拒）；unknown→error_code=="record_unconfirmed" 时 unconfirmed 否则 not_committed；其余→not_committed。

**回执 result 去正文副本（K4）**：协议3 回执的 `result` 中 `text`/`json_object` 恒置 None，新增 `payload_sha256` 摘要（gateway 在 record 确认后填入 `ModelCallResult`，见 D1）。理由：① 64KiB 响应经解码/封套再编码可能超 128KiB IPC 限（扩张不承诺恒不触限），正文副本使回执在临界样本必然超限；② 回执不携带可被误用的正文，DB 为唯一权威。`decode_receipt` 的 succeeded 分支校验相应改为：text/json_object 均 None 且 payload_sha256 为 64hex。`ModelCallResult`（进程内返回值）保留 text/json_object 不变——去副本仅限 IPC 回执投影。

**不能把所有 model SUCCEEDED 无条件包装为业务已提交**：由"SUCCEEDED ⇔ record 确认返回"的事务化定义 + 配对规则共同消除；回执字段仅是进程内通知快照，**任何使用资格判定以 DB 读取为准**，回执声明不作为持久事实凭据（K1：not_committed 亦不可用来断言 DB 一定无行——持久事实以 read 为权威）。

## 4. D — 最小落地差异、验收与升级点

### D1 精确文件清单（实施卡执行范围；K5 完整版）

| # | 文件 | 动作 | 函数/签名/返回变化 |
| --- | --- | --- | --- |
| 1 | `backend/migrations/007_activity_operation_results.sql` | 新增 | A2 DDL 原文 |
| 2 | `backend/app/capabilities/contracts.py` | 修改 | `LedgerOutcome` 增 `payload_format/payload/payload_sha256`（默认 None）；新增 `RecordOutcome` 枚举（RECORDED/ALREADY_PRESENT）；`AdmissionLedger.record_outcome` 返回类型 `None→RecordOutcome`（协议签名变化）；`RejectingAdmissionLedger` 同步（保持抛错）；新增纯函数 `canonical_payload_bytes`/`payload_digest`；`ModelCallResult` 增 `payload_sha256: str\|None = field(default=None, repr=False)` |
| 3 | `backend/app/capabilities/gateway.py` | 修改 | `_handle_response`：SUCCEEDED 路径构建封套+超限拒绝（payload_limit→FAILED(received) 无正文）+hash 计算；`_finish`：三分类（返回值非枚举或 AdmissionUnavailable→UNKNOWN("record_unconfirmed")；AdmissionDenied→UNKNOWN("record_denied")；正常→原 status+payload_sha256 填充） |
| 4 | `backend/app/activities/repository.py` | 修改 | `_outcome_values` 扩展校验；新增 `_stored_payload_row`；`record_outcome` 按 B2 分支序重写并返回 RecordOutcome；新增 `read_committed_result`/`list_committed_results`/`CommittedResultSnapshot`/`ResultReadStatus` |
| 5 | `backend/app/activities/__init__.py` | 修改 | 导出新类型 |
| 6 | `backend/app/worker/one_call.py` | 修改 | `worker_request`/`decode_worker_request` 协议3；`receipt`（business_commit 三值推导+result 去正文副本+payload_sha256）；`decode_receipt`（协议3+配对校验+去正文校验）；`bounded`/`OneCallInput` 不动 |
| 7 | `backend/app/worker/worker_main.py` | 修改 | `execute_one_call`/docstring 口径（"SUCCEEDED 即已原子提交"） |
| 8 | `backend/app/worker/session.py` | 修改 | `run_once` one_call 分支入口 N1 早拒绝（`config.request_timeout_seconds > 120 → ValueError`，claim 前）；其余不变（decode_receipt 消费经 one_call 模块自动获得协议3） |
| — | 不变 | — | `launcher.py`/`supervisor_main.py`/`gate.py`/`windows_job.py`/`supervisor_ipc.py`/002—006/admit/claim/close/settle/cancel/recover 全部签名与语义；跳1 协议 2 |

**直接受影响测试/夹具（K5）**：`backend/tests/test_worker_one_call.py`（:171 business_commit 断言改三值；:129 跳1 协议2 断言不变；:248 跳1 往返不变）；`backend/tests/fixtures/task085/real_cases.py`（:82 business_commit 透传，枚举字符串兼容）；**FK 清理链适配**——007 FK 后删除顺序必须 results→operations→activities，须在 `test_activity_ledger.py:47`、`test_activity_recovery.py:73`、`test_activity_time_budget.py:61`、`fixtures/task083/pg_migration.py:73` 的清理 SQL 前各加一行 `DELETE FROM activity_operation_results`（或等效 WHERE 收窄），一并纳入实施卡，不等 PG 运行再发现。

### D2 迁移与旧数据策略

- 007 首次执行：前置仅 002 已建；**不要求 activities 空表**（纯新增 CREATE TABLE，无 ALTER、无回填，对含既有数据的获批合成库安全——与 004/005 的仅空库约定不同，如实区分）；仅授权在获批合成库执行；用户库迁移/回填未授权。
- 重复执行：不支持，报 duplicate table 整体回滚；不宣称幂等。
- 旧数据：已存在 received/unknown 操作不回填正文；读取如实呈现 terminal_without_payload / unresolved（区分于首轮误写：record 回滚残留是 dispatched→unresolved，不是 received_without_payload）。
- 事务失败回滚：007 单事务 DDL；应用侧 record 回滚后两表无半写（T20a 证明）。

### D3 测试矩阵（K6 补齐；可直接写入实施卡）

离线（无 PG，替身/纯函数）：
- T01 封套规范化与 hash 稳定性：同对象两次编码字节相等（text/json、Unicode、转义扩张样本）；**近 64KiB 含转义响应 → 封套超 128KiB 拒绝**（K4 扩张反例）。
- T02 payload 非法：编码后超限、format 非枚举、三字段同存同缺、伪 hash（regex 合法但与字节不符）→ 应用侧构建保证 + 读取复算拒绝（T10/T16 动态覆盖复算侧）。
- T03 LedgerOutcome 扩展校验（payload 仅随 RECEIVED 等）。
- T04 协议3配对正反例：合法对全表（C2）；反例：succeeded+not_committed、succeeded+unconfirmed、unknown+committed、failed+committed、committed 无 hash、not_committed 有 hash → 全部 ValueError。
- T05 读取状态推导：COMMITTED_CURRENT / COMMITTED_HISTORY_CANCELLED / INVALIDATED_SOURCE / INVALIDATED_SCOPE_CHANGED / NO_OPERATION / UNRESOLVED / TERMINAL_WITHOUT_PAYLOAD 逐状态；payload_integrity 错误与状态区分。
- T06 N1：`SessionConfig(request_timeout_seconds=121)` + one_call → `run_once` 入口 ValueError、无 claim 无预扣（claim_attempted=False 可断言）；同 config idle 正常（不收紧）。
- T06b 回执推导：record_unconfirmed → unconfirmed；record_denied → not_committed。

真实合成 PG（定向，非全套复跑；**不用 mock 冒充事务**）：
- T10 正常链：record(正文) 与 received 同事务落库，返回 RECORDED → settle → read=COMMITTED_CURRENT；次数/费用/时间账逐值核对；回执 committed 且 payload_sha256=DB 行 hash。
- T11 幂等重放（同 outcome+payload，窗口内）→ ALREADY_PRESENT 零改写。
- T11b（K3/K6）关门后与 settle 后（活动 pending、G+1、executor NULL）同值重放 → ALREADY_PRESENT 无写确认；两路径与"关门后新写拒绝"并存不矛盾。
- T12 异文冲突（同键异 hash）→ AdmissionDenied，既存行逐字节不变。
- T13 取消竞争（取消先，两连接屏障）→ record 抛 **AdmissionDenied（确定回滚，断言异常类型）** → 操作残留 dispatched → recover_unknown → unknown；无正文；**两表无半写**。
- T13b（K6）提交先+取消后：正文行幸存；read=COMMITTED_HISTORY_CANCELLED（正文可读+cancelled 标注）；DB 行字节不变；不构成新授权。
- T14 租约过期/旧 G 晚到 → 仅 UNKNOWN 诊断、无正文。
- T15 record 成功后不结算 → 新 claim 折叠 R→S 全额 → read 仍 COMMITTED。
- T16 来源替换后 read=INVALIDATED_SOURCE：无正文、hash/committed_at 元数据返回；读后 DB 行 payload 字节逐字节不变。
- T16b（K6）scope 失效：模拟 `UPDATE activities SET scope_revision=scope_revision+1` → read=INVALIDATED_SCOPE_CHANGED 无正文。
- T17 封套编码后超限 → FAILED(received, payload_limit)、无正文行。
- T18 007 迁移：空前置库执行成功；含 received 无正文行旧数据的库执行成功且不回填；**重复执行报错回滚（验证非幂等声明）**；FK 清理链正序删除成功。
- T19 并发屏障：两连接同时 record 同操作 → 行锁串行 → 一 RECORDED 一 ALREADY_PRESENT（真实 PG 事务）。
- T20a（K6）提交前回滚：屏障注入事务内失败（锁超时/约束违规）→ **断言 activity_operations 无变化 AND results 无行（两表无半写）**；gateway UNKNOWN 按 record_denied/record_unconfirmed 分类。
- T20b（K6）提交后响应丢失：子类化 PostgresAdmissionLedger，`record_outcome` 先 `await super().record_outcome(...)` **成功返回后**再抛 AdmissionUnavailable（真实 PG 已 COMMIT、行已在库，调用侧异常注入）→ gateway UNKNOWN(record_unconfirmed) → `read_committed_result`=COMMITTED_CURRENT（正文在）→ 同参数幂等重放 ALREADY_PRESENT 不改写 → **断言 transport 恰发送一次，无重发**。
- T20c（K6）正文已提交后结算失败/响应丢失：settle 注入失败 → R 残留 → 新 claim 折叠 S+=W → read=COMMITTED（正文幸存、时间保守）。
- T20d（K6）关门后首次提交：begin_window_close 后 record(SUCCEEDED+payload) → AdmissionDenied（dispatch_closed 显式检查）无行；此前已提交操作的等值重放 → ALREADY_PRESENT。

Windows 接线（最少）：T21 一例真实 SUP→worker→合成 PG happy path：exit0、跳2 回执 protocol3+committed+无正文副本+hash 与 DB 一致、settle 后行存在。可选 T22：record 后杀 worker → stopped_at_deadline 全额 → 行幸存（B4 组合6）。不默认复跑 D3/085 全套。

### D4 手工状态轨迹（推演非测试，K1 修正版；每条与 A—C、接口状态、DDL 一致，算术可核）

基线数值同首轮：M=600、来源 v1r0、W=90、C=3、S 起 0。

| # | 轨迹 | G | 操作状态 | 成果行 | 时间账 R→S | 回执与结论 |
| --- | --- | --- | --- | --- | --- | --- |
| 轨1 正常全链 | claim(W=90)→admit op1→dispatch→模型成功→record 正文 h1 返回 RECORDED→树零 C=3→关门（仅置旗）→settle | 0→1→2（settle 时） | reserved→dispatched→received | h1 | 90→0；S=0→3 | 回执 succeeded/committed/hash=h1；worker exit0 正常结算；read=COMMITTED_CURRENT；requests_reserved=1 恒留 |
| 轨2a 提交后响应丢失 | 同轨1 至 record 的 COMMIT 已到达服务器，连接断 → record 抛 AdmissionUnavailable | 1→2（settle 时） | **received（DB 事实）** | h1（DB 事实） | 90→0；S=0→3 | gateway UNKNOWN(record_unconfirmed) → 回执 unknown/unconfirmed → **worker 正常写回执 exit0 → SUP 正常关门结算（非全额预扣）**；恢复：read=COMMITTED_CURRENT 或幂等重放 ALREADY_PRESENT；无重发 |
| 轨2b 提交后 worker 被硬杀 | 同轨1 至 record COMMIT 返回，回执写出前 terminate | 1；R 残留 | received | h1 | R=90 残留；下次 claim 折叠 S+=90、G→2 | 无回执；stopped_at_deadline 全额保守；正文行幸存 read=COMMITTED |
| 轨3 提交前确定回滚 | dispatch→模型成功；cancel 先获活动锁（cancelled、R→S=90、G→2）→ record 抛 AdmissionDenied（回滚） | 1→2 | dispatched→（recover_unknown）→unknown | 无 | R=90→S=90 | gateway UNKNOWN(record_denied)→回执 unknown/not_committed；worker exit0 → SUP 正常结算 S+=C；**两表无半写**；read=UNRESOLVED；**异常类型=AdmissionDenied=确定回滚，不得按轨2a 的未知处理** |
| 轨4 幂等/冲突/失效/关门 | 轨1 完成后：a) 同值重放（settle 后、活动 pending）→ ALREADY_PRESENT；b) 异文 h2 → payload_conflict 回滚；c) 来源替换 v2r1 → read=INVALIDATED_SOURCE（无正文、h1 可复算于 DB）；d) 关门后再提交新正文 → AdmissionDenied | 2 | received | h1 不变 | S=3、R=0 不变 | a 无写确认；b 行不变；c 正文抑制+元数据可读；d 无行 |

### D5 N1/N2 处理（K5 对齐）

- N1：早期校验落点 = `session.run_once` one_call 分支入口（D1#8），`config.request_timeout_seconds > 120 → ValueError`，位于 claim/预扣前；idle 分支不校验（保留 idle 可用域）；不在 SessionConfig.__post_init__ 全局收紧。配套离线反例 T06。本卡不修，实施卡完成。
- N2：不改限额/帧边界行为，不触发定向覆盖；不为已通过的 085 补全套。

### D6 授权边界汇总

- **已获授权的原行为（不变）**：admit/mark/record 元数据语义、UNKNOWN 保守预留、次数/费用预留不退、时间预扣/关门/结算算术（关门仅置旗、settle 才 G+1 的函数级事实）、取消折叠、恢复收敛、跳1 协议边界、服务 64KiB/封套 128KiB/映射 1MiB、单机单会话 D3 信任边界、UNKNOWN 后 worker 正常退出的正常结算路径。
- **拟改变的持久模型/提交语义（本卡裁定物，须批准）**：新表 `activity_operation_results`（含 FK）；SUCCEEDED ⇔ 正文同事务提交且 record 确认返回；`AdmissionLedger.record_outcome` 返回 `RecordOutcome` 枚举（协议签名变化）；worker 在既有连接上扩展业务正文持久写权（复用 DSN ≠ 权力边界为零，B3）；回执协议3（跳2 升版、business_commit 三值、result 去正文副本、`ModelCallResult` 增 payload_sha256 字段）；两个只读读取接口及失效抑制；N1 早拒绝（session.py）。不改 SUP 退款/预算权力。
- **必须编排/用户决定项**：仅一项实质决定——批准上述持久模型/提交语义变更包（D1#1—#8）后出实施卡；若不批准读取失效抑制或回执去正文副本的某一部分，其余组件的依赖关系已在 D1 标明，可拆分裁定。无须用户回答的技术细节问题。

### D7 可裁决结论

- **实施范围**：D1 清单全部；以本合同 A/B/C 为实现规范；实施卡须含 T06/T06b（N1）。
- **验证范围**：D3 矩阵 T01—T21（T22 可选）；T10—T20 必须真实 PG 事务；通过判定为逐例断言 + 迁移前后旧行为不回填 + T20a/T20b 原子性证明。
- **必需独立审计**：是。新持久模型 + 提交语义变化 + 接口签名变化属主要模型变更。审计最小范围：record_outcome 原子性/锁序/dispatch_closed 检查与双路径幂等、payload 校验完备（含规范化定义与扩张拒绝）、读取只读性与失效抑制无绕过（含 SQL 投影）、协议3 配对无绕过、007 迁移前置与 FK 清理链、回执/状态机无"SUCCEEDED 未提交"残留路径、N1 校验位置在 claim 前。

## 5. 未验证/未决与风险

- 本卡未运行任何验证（静态正确 ≠ 真实通过）；DDL 为草案。所有 K1—K6 修正基于 2026-09-28 对当前源码的实读（revision-01 hash 清单），其中 `_operation_is_current` 不查 dispatch_closed、begin_window_close 不递增 G、record_outcome 返回 None、双跳协议硬编码 2、`_handle_response` 在 record 非 UNKNOWN 时返回含正文 result 仅 del parsed——六项函数级事实均经实读确认。
- 输入基线差异登记：产品源码 14 项（repository/contracts/gateway/one_call/worker_main/session/gate/launcher/activities__init__/002/004/005/006 + gate）与首轮 hash 逐一相同；三个 docu 文档（085-086 验收/架构/执行状态）与首轮 hash 不同，原因是对齐修正轮基线 v0.51/v1.71 及验收文件函数级勘误追加（编排合法更新，非漂移）；supervisor_main.py 与 6 个测试/夹具文件为本轮新增读入（K5 协议与 FK 清理链核对）。详见 `Ndocu/evidence/task-087/revision-01/input-hashes-r01.json`。
- 未决（非本卡）：G4 revision 权威接线、unconfirmed 恢复重放的实际调用方、UI/HTTP 暴露、TOOL_PLAN 正文（G5）、真实供应商连通、用户库迁移授权。
- 风险：① record 以 AdmissionUnavailable 结束时正文存在性未知是协议内在属性，本合同以 unconfirmed 状态+受限幂等重放+DB 权威读取收敛，不假装消除；② 读取失效抑制以单语句快照为界，快照后的来源/scope 变化不回溯已返回字节（未来接线方须实时校验，G4 缺口）；③ 64KiB→128KiB 扩张在临界样本会拒绝接近上限的有效成果（显式边界，payload_limit，非缺陷）；④ 回执去正文副本后 SUP 诊断只见摘要，正文核查必须走 DB 读取（可接受，DB 为唯一权威）。
- 轨迹为推演，不构成测试证据；实际结果以实施卡运行证据为准。

## 6. 实施与审计建议

实施卡沿用本窗续接（不换窗、不重做 085）；按 D1 顺序实现（迁移→contracts→repository→gateway→one_call→session→测试/夹具适配）；实施完成后按 D7 范围出一次独立代码审计卡（只审增量）。资源建议：合成 PG 容器 1 个（对齐 085 口径）；Windows 接线 T21 一次。007 与既有测试 FK 清理链适配必须在实施卡内同步完成，不留到运行时发现。

---

# 首轮原结果（历史保留；冲突以上方修正轮01为准）

日期：2026-09-28。执行窗口：TASK-085 原最强实现窗口续用（同窗连续推进，实际模型 GLM-5.3-Flash，如实登记）。需求 v1.1、架构 v0.50、执行状态 v1.70；Git 首提交 45951501d2741630a229762d6b2d3f4b34d7f702，既有未提交成果保留。
本卡为只读设计：未改源码/测试/DDL/正式 docu/公共库/旧证据，未运行 import/compile/unittest/PG/Windows Job/Docker/应用/模型，运行预算 0 消耗，未 Git 提交。仅写入本结果与 Ndocu/evidence/task-087/。

## 0. 结论与可批准范围（推荐合同）

**唯一推荐方案：把"有效业务成果的原子持久提交"合并进既有 `record_outcome` 的同一短事务**——gateway 在成功解析路径构建正文封套，随 `LedgerOutcome` 传入 `record_outcome`；在同一事务（既有锁序：来源→活动→操作）内完成"当前代次资格校验 + `activity_operations` 终态写入 + 新表 `activity_operation_results` 正文行插入"。提交者是存活 worker，提交时点在树零/关门/结算之前、G 仍当前之时；不存在任何事后凭旧回执写库的权力，"先校验再另事务落正文"的拆分被结构消除。

语义变化一句话：**`ModelCallResult.status == SUCCEEDED` 从"模型返回成功"收紧为"模型返回成功且业务正文已与 received 状态同事务原子持久提交"**；回执演进为协议 3，`business_commit` 与 status 强配对。其余全部既有批准行为不变：次数/费用预留、UNKNOWN 保守纪律、时间预扣/关门/结算、取消、D3 单机信任边界、002—006 迁移。

可据此批准并一次完成的实施范围：1 个新迁移（007，仅草案在本文）+ 4 个产品文件的精确增量 + 1 个只读读取接口 + 回执协议 3；验证为"离线契约 + 合成 PG 定向 + 最少 1 例 Windows 接线"；实施后需一次独立代码审计（见 D7）。

## 1. 实际读入与证据

全部读入文件的 SHA-256 记录于 `Ndocu/evidence/task-087/input-hashes.json`（17 项，2026-09-28 时点）。关键定位（行号均为当前读入版本）：

| 文件（hash 前缀） | 关键定位 |
| --- | --- |
| repository.py（bca82833…） | `_transaction` 139-168（3s 语句/2s 锁/5s idle 超时）；`claim_lease` 315-435（预扣 W_eff）；`begin_window_close` 465-498；`settle_execution_window` 500-587（G+1/pending/受限幂等）；`cancel_activity` 589-621；`recover_unknown` 623-659；`recover_obsolete_operations` 708-767；`admit` 821-878；`_locked_operation` 880-911（锁序来源→活动→操作）；`_operation_is_current` 913-925；`_outcome_values` 944-977；`_stored_outcome` 979-993；`record_outcome` 995-1019 |
| contracts.py（bca21efd…） | `LedgerOutcome` 171-181；`CallStatus` 221-227；`ModelCallResult` 244-257；`AdmissionPermit` 157-163 |
| gateway.py（f57e3fe3…） | `call` 96-162（admit→mark→transport→_handle_response）；`_handle_response` 216-265；`_parse_success` 267-373；`_finish` 375-393（record 失败→UNKNOWN "ledger_record_failed"，正文丢弃）；`_record_unknown_best_effort` 395-402 |
| one_call.py（2c3465bc…） | `MAX_BODY_BYTES=65536`/`MAX_DATA_BYTES=131072` 16-17；`bounded` 22-29（规范化 JSON 字节）；`receipt` 116-118（硬编码 "not_committed"）；`decode_receipt` 121-165（129 行强校验 not_committed）；`run_one_call` 168-183 |
| worker_main.py（afcb69b7…） | `execute_one_call` 53-62；`main` 65-87（回执不落盘，仅 NamedMapping） |
| session.py（7d7fa5e3…） | claim 233-241；spawn/Resume 268-285；树零等待 287；回执读取+decode 305-316；先关 Job 句柄 319；关门 321；settle+响应丢失重试 323-333；`SessionOutcome` 389-399（`model_receipt` 仅进程内返回，不持久） |
| gate.py / launcher.py | 发送门不回开；launcher 委派 SUP，本合同不改 |
| 002_activities.sql（3a9c5855…） | `activity_operations` 52-82：state CHECK 65、PK(activity_id,operation_id) 77、response_bytes≤64MiB 73 |
| 004/005/006 | 五列时间账本（004 20-30）；`dispatch_closed`（005）；`running_owner_session_id`（006，旧行 NULL 不获恢复权） |
| 085-086 验收（fa01159f…） | "回执 business_commit=not_committed……关闭门推进 G，不能凭回执向业务表晚写"（13 行）；N1（22-23 行）；N2（24 行） |

问题入口核对（与卡面一致，均经实读源码证实）：`gateway._finish` 成功正文在 record 后即丢弃（gateway.py:261-265）；`record_outcome` 只写元数据、无正文列（repository.py:1009-1017）；数据库无业务正文存储（002 全表）；SUP 在树零后才关门/结算，settle 即 G+1（repository.py:571-585），此后任何旧 G 写入必被 `_operation_is_current` 拒绝——085 的"不能凭回执晚写"由此成立。

## 2. A — 唯一推荐范围和数据合同

### A1 本切片到底提交什么

三个概念严格区分：

| 概念 | 内容 | 本切片是否持久 |
| --- | --- | --- |
| 原始模型结果 | 供应商完整 HTTP 响应体（choices/usage 包装） | 否。只保留既有元数据（response_bytes/usage/returned_model/finish_reason/remote_request_id，已在 `activity_operations`） |
| 经过验证内容 | gateway `_parse_success` 校验通过后的 `text` 或 `json_object`（finish_reason=stop、非空、JSON 深度≤12/节点≤2000、无截断） | **是——这就是本切片持久化的业务正文** |
| 业务产物封套 | 经过验证内容 + 身份/来源关联（activity_id、operation_id、admission_id、G、scope_revision、payload_format、payload_sha256、committed_at） | 是；封套即新表一行 |

- **成功定义**：仅 `status=SUCCEEDED`（text 或 json 二选一，无 tool_plans）构成有效业务成果。`TOOL_PLAN/FAILED/UNKNOWN/NOT_SENT/REJECTED` 一律不产生正文行（tool 执行不在本切片，G5 未接线）。
- **"有效"的边界**：等于 gateway 既有成功解析不变式；不含未来教育域语义校验（意图/证据引用/教学正确性均属 G4/后续角色，本合同不引入）。
- **可读取者**：与活动同信任域的可信内部组件（未来 002/003 模块的接线方）；本卡不新增对外 HTTP，不暴露给工具/模型（同 R-064 对 `UnresolvedOperation` 投影的限制口径）。
- **来源与活动关联**：复用既有 `activity_operations`（操作身份/代次/范围）与 `activity_scope_sources`（来源版本快照）+ `material_sources`（当前权威版本），不复制、不冗余存储来源正文。
- **范围**：只覆盖现有 one_call 一个最小成果；不建学习/面试全领域表、不做通用事件平台、不做"全历史完美回放"。

### A2 DDL 草案（仅本文提出，不创建正式迁移）

```sql
-- TASK-087 候选迁移 007：业务成果正文（G3 切片）。本卡只写不执行。
BEGIN;
CREATE TABLE activity_operation_results (
    activity_id UUID NOT NULL,
    operation_id VARCHAR(128) NOT NULL,
    admission_id UUID NOT NULL,
    execution_generation INTEGER NOT NULL CHECK (execution_generation >= 0),
    scope_revision INTEGER NOT NULL CHECK (scope_revision > 0),
    payload_format TEXT NOT NULL CHECK (payload_format IN ('text', 'json')),
    payload TEXT NOT NULL CHECK (octet_length(payload) BETWEEN 1 AND 131072),
    payload_sha256 TEXT NOT NULL CHECK (payload_sha256 ~ '^[0-9a-f]{64}$'),
    committed_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (activity_id, operation_id),
    FOREIGN KEY (activity_id, operation_id)
        REFERENCES activity_operations(activity_id, operation_id)
);
COMMIT;
```

- **必要索引：无新增**。主键前缀 `(activity_id)` 即支持"按活动列出已提交成果"；FK 引用的 `activity_operations` PK 已存在（002:77）。不建 payload 全文/向量索引（那是 DATA-003 检索层的事）。
- `payload_format/payload/payload_sha256` 三者恒同时存在（应用层校验，见 A4）；元数据（usage/returned_model 等）不复制，读取时 JOIN `activity_operations`，避免双写漂移。
- 正文大小上限 `131072`（= one_call `MAX_DATA_BYTES`，one_call.py:17）；one_call 配置 `max_response_bytes ≤ 65536`（one_call.py:57-58）且封套仅比解析后正文多固定短前缀，故 one_call 路径恒不触限；更大响应配置（`ModelServiceConfig` 允许至 4MiB）将被 `payload_limit` 拒绝——这是本切片的显式边界，不是缺陷。

### A3 为何现有字段不够（逐项）

| 需求 | 现有承载 | 不足 | 结论 |
| --- | --- | --- | --- |
| 业务正文（≤128KiB text/json） | `disposition(≤10枚举)/error_code(64)/response_bytes(计数)` | 无任何可容纳 128KiB 已验证正文的列；塞入即破坏既有语义与 CHECK | 新表新列 |
| "已提交"标记 | `state` CHECK 仅 5 枚举（002:65） | 扩枚举要改 CHECK 且把"有正文"误当状态机节点 | **不加新状态**：正文行存在=已提交，行不存在=未提交。状态机零变更，最小且可回溯 |
| 幂等与冲突判定 | PK(activity_id,operation_id)+admission_id UNIQUE | 只保证操作唯一，不保证正文一致 | 正文行同 PK + sha256 等值规则（A4） |
| 来源失效可见性 | `_lock_sources` 比对 `material_sources.current_version/revision` | 仅写路径使用，读路径无法反映 | 读接口带 `sources_current` 快照旗标（C1），不持久化失效状态 |

### A4 身份冲突、hash/规范化、重复提交与异文冲突的确定规则

1. **正文规范化**：封套恒为 `{"format":"text"|"json","value":<content>}`，字节 = `json.dumps(envelope, ensure_ascii=False, separators=(",", ":"), allow_nan=False).encode("utf-8")`——与 one_call `bounded()`（one_call.py:22-29）同一规范化函数，复用其 NaN/类型/递归防护。`payload` 列存该规范化字节的 UTF-8 文本；`payload_sha256` 为其 SHA-256 小写 hex。
2. **提交资格**：与 `record_outcome` 完全同源——`_operation_is_current`（repository.py:913-925：sources_valid ∧ running ∧ executor ∧ G 相等 ∧ scope_revision 相等 ∧ 租约未过期 ∧ 截止未过）。不新设资格、不持久化资格、不发放可延迟使用的凭证。
3. **重复提交（幂等）**：终态 `received` 上重放相同 outcome（含相同 payload_format+sha256）→ 幂等返回、零改写（既有 `_stored_outcome` 相等分支扩展，比较元组增加 payload 两个分量；结果行存在且 hash 相同即满足）。
4. **异文冲突**：同操作键再提交且 sha256 或 format 不同 → `AdmissionDenied("payload_conflict")`，整个事务回滚，既存行原样。先到先得，后到不得覆盖——正文与 received 状态一样是不可覆写终态。
5. **操作身份冲突**：正文行以 `(activity_id, operation_id)` 为 PK 且 FK 到 `activity_operations` 同键——不存在无操作行的正文、不存在一正文挂两操作。`admission_id` 冗余存储仅作审计对账，不做幂等键。
6. **并发**：对同一操作的并发 `record_outcome` 在 `activity_operations` 行排他锁上串行化（`_locked_operation` FOR UPDATE，repository.py:899-902）；获得操作锁后先查后插正文行，无并发插入窗口。取消/关门在活动行锁上与之串行（B5）。
7. **冲突异常族**：全部沿 `AdmissionDenied`（gateway 已把它映射为 REJECTED/UNKNOWN 语义，不改异常类型族，不新增异常类）。

### A5 预算、UNKNOWN、幂等边界

- 次数/费用：`admit` 预留语义零变化；成功提交**不退预留**（既有批准行为：预留只在取消/未知时保守保留，成功亦不回退——002 无回退路径，repository 无任何 UPDATE 预留的语句除 admit 增量外）。本合同不新增任何费用/次数写点。
- 时间预算：M/R/S 五列、预扣、关门、结算零变化；正文提交不占时间账、不因正文存在而改变 C/W 算术（B4）。
- UNKNOWN 纪律：record 失败（DB 不可用/锁超时/冲突回滚）→ gateway 返回 `UNKNOWN("ledger_record_failed")`（既有 gateway.py:384-385，正文随之丢弃）→ 操作行留在 `dispatched` → 由既有 `recover_unknown`/`recover_obsolete_operations` 收敛为 unknown。**不隐式重发、不生成新 operation 蒙混重试**——重试必须走新操作并重查额度（FLOW-005 既有文本）。
- 重启读取零副作用：读取方法只读、无行锁、无出站、无计数。本地承诺仅"提交/读取幂等"；**不承诺远端 exactly-once**（供应商已收费但本地丢失正文 = 该操作业务终局丢失，只能以新操作重试，计入预算——ADR-005 既有代价，如实声明）。

## 3. B — 时序、所有者与事务

### B1 真实函数级调用链（增量以 [G3] 标注）

```text
launcher.run_supervised_window(...)                       # 不变
└─ SingleWindowSupervisor.run_once(...)                   # 不变（085 已验收范围）
   ├─ ledger.inspect_window → ledger.claim_lease(G+1, R=W)         # 不变
   ├─ NamedJob.create + spawn_suspended(worker_main one_call)      # 不变
   │    └─ worker: execute_one_call(value)                         # 不变
   │         ├─ decode_worker_request                              # 不变
   │         ├─ gateway.call(context, request)
   │         │    ├─ ledger.admit（预扣次数/费用，短事务）           # 不变
   │         │    ├─ ledger.mark_dispatch_started（出站边界）        # 不变
   │         │    ├─ transport.send（无事务；网络不得进 DB 事务）     # 不变
   │         │    ├─ _parse_success → result(SUCCEEDED, content)
   │         │    ├─ [G3] envelope=canonical({"format",value}); 超限
   │         │    │      → ResponseValidationError("payload_limit")
   │         │    │        → FAILED(received) 无正文
   │         │    └─ _finish: ledger.record_outcome(permit, outcome+payload)
   │         │         BEGIN（锁序：来源 FOR UPDATE → 活动 FOR UPDATE → 操作 FOR UPDATE）
   │         │           ① _operation_is_current 校验（失败且非 UNKNOWN → 拒绝回滚）
   │         │           ② UPDATE activity_operations（state='received'+元数据）   # 原 UPDATE 不变
   │         │           ③ [G3] 查/插 activity_operation_results（同 PK；
   │         │                 已存在且 hash/format 相同→幂等；不同→payload_conflict 回滚）
   │         │         COMMIT   —— 正文行与 received 状态同生共死
   │         └─ [G3] receipt(...)（协议3：SUCCEEDED ⇔ business_commit="committed"）
   ├─ wait_empty_until(stop_ns) → t1 → C=ceil(elapsed)              # 不变
   ├─ decode_receipt（[G3] 增加配对校验；失配 → failed_closed 全额）   # 配对规则新增
   ├─ job.close → begin_window_close(G)（dispatch_closed=TRUE）      # 不变
   └─ settle_execution_window(G, W, C)（S+=C, R-=W, G+1）            # 不变

恢复/重启读取（[G3] 新增，只读）:
   ledger.read_committed_result(activity_id, operation_id)
   ledger.list_committed_results(activity_id, limit, after)         # C1
```

### B2 record_outcome 扩展伪代码（单事务，短事务约束不变）

```python
async def record_outcome(permit, outcome):
    values = _outcome_values(outcome)      # [G3] 扩展：payload 三元组校验
    async with tx:                          # statement_timeout 3s / lock_timeout 2s / idle 5s 不变
        activity, call, sources_ok = _locked_operation(permit)   # 来源→活动→操作，不变
        if call.state in {not_sent, received, unknown}:          # 终态幂等分支
            stored = _stored_outcome(call) + _stored_payload(op) # [G3] 补查 results 行
            if stored == values: return                          # 幂等零改写
            raise AdmissionDenied("已终结调用不能覆盖为不同结果")   # 含 payload_conflict
        if not current and outcome.disposition is not UNKNOWN:
            raise AdmissionDenied(...)                            # 不变
        if call.state == reserved and disposition is not UNKNOWN:
            raise AdmissionDenied(...)                            # 不变
        UPDATE activity_operations ...                            # 原 UPDATE 原样
        if payload present:                                       # [G3]
            row = SELECT ... FROM activity_operation_results WHERE PK
            if row: (sha256/format 相同 → 跳过；否则 raise payload_conflict)
            else: INSERT INTO activity_operation_results(...)
    COMMIT
```

- 网络调用不进事务：`payload` 在 `_parse_success`（transport 返回之后）内存中构建完毕才进入事务；事务内只有 3-4 条本地 SQL，128KiB 单行写入在既有 3s 语句超时内绰绰有余。
- `_outcome_values` 扩展校验：payload 三字段同存同缺；`payload_format ∈ {text,json}`；`octet_length(payload) ∈ [1,131072]`；sha256 匹配 `^[0-9a-f]{64}$`；payload 存在时 `disposition` 必为 RECEIVED 且仅在 `dispatched→received` 的新写路径允许（reserved/UNKNOWN/NOT_SENT 路径携带 payload 一律拒绝）。
- **失败回滚后的持久事实**：事务回滚 ⇒ 操作行保持 `dispatched`、无正文行、无部分写入（单事务原子性）；上层 gateway 得 UNKNOWN，worker 回执 not_committed，全额预扣按既有 failed_closed/stopped 语义保守处理。

### B3 与"085 结束后 G 已推进"问题的解决

- 提交发生于 worker 进程存活、`dispatch_closed=FALSE`、G 当前、租约有效之时——即 `record_outcome` 原有时点。树零、关门、结算全部发生在其后，只能使 G 前移而**不能追溯取消已提交正文**（正文行不携带任何未来写权）。
- 不存在"拿旧回执伪造提交权"的通道：回执只是通知，不携带任何可执行权力；关门/结算后所有写路径（含 payload）都会被 `_operation_is_current` 拒绝。
- 不存在"先校验再另事务落正文"的拆分：校验与落正文是同一事务内相邻语句，其间无释放锁的边界。
- 与随后事件的关系：树零 → 关门 → 结算照旧执行；正文提交不改变它们的任何判定输入（settle 检查 status/executor/G/R/dispatch_closed，不查正文）。
- 与"被杀"的关系：worker 在 record 事务提交后被杀 → 正文已持久（COMMIT 已返回），后续任意结局（ stopped_at_deadline 全额、SUP 死亡、租约折叠）都只是时间账问题；worker 在事务中被杀 → 连带回滚，`dispatched` 残留交由既有恢复收敛。两个方向都无中间态。
- 新增权力边界 = 零：worker 原本就持有 ledger DSN 并执行 admit/mark/record（worker_main.py:55-56），本次仅在同一对象上多走一条同锁序方法；无新凭据、无新进程权、无 SUP 职责变化（不预设也不需要修改 SUP 结算职责）。

### B4 "持久业务提交"与"时间结算成功"分离矩阵

| 情形 | 业务正文 | 时间账 | 读取结论 |
| --- | --- | --- | --- |
| record 成功 → 树零 → 关门 → settle 成功 | 已提交 | S+=C、R=0、G+1 | committed |
| record 成功 → worker/SUP 死亡，settle 未发生 | **已提交（幸存）** | R=W 残留，下次 claim 保守折叠 S+=W（或 cancelled 全额折叠） | committed；时间保守、无退款 |
| record 失败（回滚）→ 树零 exit0 → settle 成功 | 无（该操作业务终局丢失） | S+=C 正常 | received_without_committed_payload |
| record 成功 → settle 响应丢失 → 同 G/W/C 重试 ALREADY_SETTLED | 已提交 | 结算幂等确认（repository.py:557-561） | committed |
| 时间已结算但正文从未提交 | 无 | 已结算 | 读取方不得声称业务完成；重试=新操作 |
| 取消后 record 晚到 | 无（资格失效） | 取消时 R→S 全额 | unresolved→unknown |

原则重申：不得为了持久结果退款、延时、绕过关闭门或改变 D3 信任范围——本合同在所有分支都没有触碰这四项。

### B5 竞争冲突统一机制（同一锁序内串行化）

| 竞争 | 串行化点 | 先到者 | 后到者 |
| --- | --- | --- | --- |
| 提交 vs 取消 | activities 行锁（双方都先锁来源再锁活动） | 若取消先：record 仅允许 UNKNOWN，无正文；若提交先：正文保留，取消照常（不删正文），activity_status=cancelled 下读取仍 committed（历史事实） | 见左 |
| 提交 vs 来源撤销/版本替换 | material_sources 行锁（`_lock_sources` FOR UPDATE） | 撤销先 → sources_valid=false → 非 UNKNOWN 拒绝，无正文；提交先 → 正文保留，此后读取 sources_current=false | 见左 |
| 提交 vs scope_revision 变化 | activities 行锁 + 等值检查 | revision 先变 → 等值失败拒绝；提交先 → 行内 scope_revision 快照已固化 | 见左 |
| 提交 vs 租约过期/新 G | activities 行锁 + `_operation_is_current` | 过期/新 G 后晚到 → 只能 UNKNOWN；晚到正文无通道 | 见左 |
| 并发重复提交 | activity_operations 行锁 + PK + hash 等值 | 首个 commit 胜出；第二个相同→幂等，不同→payload_conflict | 见左 |

每类冲突的允许/拒绝/返回既存边界：**拒绝**（取消/失效/过期/异文）时无任何持久写入；**允许**时正文与 received 同事务落库；**返回既存**仅在完全相等的幂等重放。

### B6 G4 缺口声明（本设计验证什么、不假设什么）

- 本设计验证的来源权威 = `material_sources.current_version/revision`（既有 `_lock_sources`）与 `activity.scope_revision` 等值——两者都是提交资格的必要条件。
- **不假设调用者可信维护 revision**：`CallContext.scope_revision` 目前由调用方声明，admit/record 只做等值兜底；谁在来源变化时递增活动 scope_revision、谁把新范围下发调用者（G4 真实范围修改入口）仍未接线，属既有登记缺口，本合同不解决、不掩盖。

## 4. C — 读取和可见性

### C1 读取接口（内部合同，不新增 HTTP）

```python
@dataclass(frozen=True)
class CommittedResultSnapshot:
    activity_id: str; operation_id: str; admission_id: str
    execution_generation: int; scope_revision: int
    provider: str; configured_model: str
    payload_format: str; payload: str; payload_sha256: str   # 读取时复算 hash 自检
    finish_reason/returned_model/remote_request_id/prompt_tokens/completion_tokens/response_bytes  # JOIN operations
    committed_at: datetime
    activity_status_now: str            # pending | running | cancelled
    activity_scope_revision_now: int
    sources_current: bool               # 快照期判定，无锁、advisory

async def read_committed_result(activity_id, operation_id) -> CommittedResultSnapshot | ReadMiss
async def list_committed_results(activity_id, *, limit<=200, after_operation_id) -> tuple[...]   # 有界，仿 list_unresolved_operations
```

派生状态（读取方按字段推导，不持久化新状态）：

| 状态 | 条件 | 消费语义 |
| --- | --- | --- |
| not_found | 无该操作行 | — |
| unresolved_or_unknown | state ∈ reserved/dispatched/not_sent/unknown | 不可当业务成果 |
| received_without_committed_payload | disposition=received 且无正文行 | FAILED/TOOL_PLAN（finish_reason 可区分 tool_calls）或 record 回滚遗留；诊断可用，业务不可用 |
| committed_current | 有正文行 ∧ sources_current | 可作为当前范围业务成果使用 |
| committed_invalidated | 有正文行 ∧ ¬sources_current | **历史存在 ≠ 允许作为当前依据展示/引用**（FLOW-005 补充：被删正文/引用必须隐藏或不可用）；消费方门禁，正文字节不删不改（保留至用户删除，DR-002 既有规则，不新增永久保留策略） |

- 授权/范围来源：调用者层负责（内部可信组件）；ledger 只做参数校验（activity_id UUID、operation_id 受限字符集，同 `list_unresolved_operations`）。投影含可复算 permit 信息，同 R-064 口径**不得直接暴露 HTTP/工具/模型**。
- 读取实现：单条 LEFT JOIN SQL（operations × results × activities × scope_sources × material_sources）在一个语句快照内完成，无 FOR UPDATE、不参与锁序竞争；hash 复算不符 → 明确错误（payload_integrity），不静默返回。
- **业务正文不进诊断日志**：新方法零日志；gateway 既有脱敏规则不变；`SessionOutcome.model_receipt` 已是 `repr=False`。

### C2 回执演进 protocol 3（字段/枚举差异明确列出）

| 项 | 协议 2（现状） | 协议 3（本合同） |
| --- | --- | --- |
| `protocol` | 2 | 3（请求/回执同步升版，防混版本） |
| `business_commit` | 字面量 `"not_committed"`（one_call.py:118,129） | `result.status==SUCCEEDED ⇔ "committed"`，否则 `"not_committed"`；decode 强制配对（失配→ValueError→SUP failed_closed 全额，安全网） |
| 其余字段 | 不变 | 不变（`result` 仍携带正文副本供 SUP 进程内诊断，**不作为业务凭证**，DB 为唯一权威） |
| 兼容性 | — | 生产/测试同仓库同版本发布；085 夹具/测试中写死协议 2 的用例在实施卡内一并更新（测试文件变更，非产品兼容负担） |
| 提交失败回传 | — | 无新错误通道：record 失败 ⇒ gateway 返回 UNKNOWN ⇒ 回执恒 "not_committed"；持久事实由"无正文行 + 操作状态"表达（B4） |

不能把所有 model SUCCEEDED 无条件包装为业务已提交的旧问题，由配对规则 + "SUCCEEDED 已被事务化定义"共同消除：现在回执声称 committed 当且仅当 DB 事务已提交。

## 5. D — 最小落地差异、验收与升级点

### D1 精确文件清单（实施卡执行范围）

| 文件 | 动作 | 内容 |
| --- | --- | --- |
| `backend/migrations/007_activity_operation_results.sql` | 新增 | A2 DDL 原文 |
| `backend/app/capabilities/contracts.py` | 修改 | `LedgerOutcome` 增 `payload_format/payload/payload_sha256`（默认 None）；常量 `BUSINESS_PAYLOAD_MAX_BYTES=131072` |
| `backend/app/capabilities/gateway.py` | 修改 | 成功路径构建 envelope+hash；超限 → `ResponseValidationError("payload_limit")` → FAILED(received) 无正文；`_handle_response` 把 payload 附入 outcome |
| `backend/app/activities/repository.py` | 修改 | `_outcome_values` 扩展校验；`_stored_outcome`/幂等分支纳入 payload；record_outcome 事务内查/插正文行；新增 `read_committed_result`/`list_committed_results` 与 `CommittedResultSnapshot` |
| `backend/app/activities/__init__.py` | 修改 | 导出新类型 |
| `backend/app/worker/one_call.py` | 修改 | receipt/decode_receipt 升协议 3 + 配对校验 |
| `backend/app/worker/worker_main.py` | 修改 | 仅模块 docstring 口径（"回执不提交业务成果"→"SUCCEEDED 即已原子提交"） |
| 不变 | — | session.py / launcher.py / gate.py / windows_job.py / supervisor_ipc.py / 002—006 / admit/claim/close/settle/cancel/recover 全部方法签名与语义 |

### D2 迁移与旧数据策略

- 007 为**纯增量 CREATE TABLE，不做空表限定**（与 004/005 的 ALTER 加列不同，对含既有 activities 数据的合成库安全）；执行顺序在 006 之后，前置依赖仅 002 的两张表。仅授权在获批合成库执行；**用户库迁移/回填未授权**。
- 旧数据处理：已存在 `received/unknown` 操作**不回填正文**——读取如实呈现 received_without_committed_payload / unresolved_or_unknown；不以"看起来成功"回填历史（防止把未验证历史冒充已提交）。
- 事务失败回滚要求：007 单事务，失败整体回滚；应用侧 record 事务失败回滚后无部分事实（B2）。

### D3 测试矩阵（可直接写入下一实施卡）

离线（无 PG，替身/纯函数）：T01 envelope 规范化与 hash 稳定性（text/json、Unicode、重复键、NaN 拒绝）；T02 payload 超限/非法 sha256/format 拒绝；T03 LedgerOutcome 三字段同存同缺校验；T04 协议 3 配对正反例（SUCCEEDED+not_committed 拒绝、FAILED+committed 拒绝）；T05 读取派生状态推导（含 sources_current 计算）；T06 **N1 早拒绝**：`SessionConfig(request_timeout_seconds=121)` + one_call → SUP 入口 ValueError、无 claim 无预扣（仅收紧 one_call 分支，idle 不变）。

真实合成 PG（定向，非全套复跑）：
T10 正常链：record(正文) 与 operations 同事务落库 → settle → read=committed_current，次数/费用/时间账逐值核对；
T11 幂等重放（同 outcome+同正文）→ 零改写；
T12 异文冲突（同键异 hash）→ AdmissionDenied，既存行逐字节不变；
T13 取消竞争屏障（两连接：cancel 先 → record 拒绝、操作残留 dispatched → recover_unknown → unknown、无正文）；
T14 租约过期/旧 G 晚到 record → 仅 UNKNOWN、无正文；
T15 record 成功后不结算 → 新 claim 折叠 R→S 全额 → read 仍 committed（业务幸存/时间保守）；
T16 来源替换后 read=committed_invalidated，payload 字节+hash 不变；
T17 payload 超限 → FAILED(received, payload_limit)、无正文行；
T18 007 迁移：空库执行成功；含 received 无正文行的库执行成功且旧行不回填；
T19 并发屏障：两连接同时 record 同操作 → 行锁串行 → 一 committed 一幂等（PG 真实事务，不用 mock 冒充）。

Windows 接线（最少）：T20 一例真实 SUP→worker→合成 PG happy path：exit0、回执 committed、settle 后行存在、hash 与回执一致。可选 T21（预算允许时）：record 后杀 worker → stopped_at_deadline 全额 → 行幸存。不默认复跑 D3/085 全套；mock 不得用于事务保证路径（T10-T19 必须真实 PG）。

### D4 手工状态轨迹（推演非测试，G/操作状态/成果状态/R-S/返回逐项可核）

| # | 节点 | 活动 G | 操作状态 | 成果行 | 时间账 R→S | 返回/结论 |
| --- | --- | --- | --- | --- | --- | --- |
| 轨1 正常 | create(M=600,src v1r0)→claim(W=90)→admit op1→dispatch→模型成功→record(正文h1)→树零C=3→关门→settle | 0→1→2 | reserved→dispatched→received | h1 | 90→0；S=0→3 | 回执 committed；read=committed_current；requests_reserved=1 恒留（既有不退） |
| 轨2 提交后被杀 | 同轨1至 record 成功；stop_ns 到，terminate，state=stopped_at_deadline，不关门不结算 | 1 | received | h1 幸存 | R=90 残留；下次 claim 折叠 S+=90、G→2 | 回执丢失不影响正文；read=committed；时间全额保守、无退款 |
| 轨3 取消竞争 | claim→admit→dispatch→模型成功；cancel 先获活动锁（cancelled、R→S=90、G→2）；record 晚到 | 1→2 | dispatched→(recover_unknown)→unknown | 无 | R=90→S=90 | record 整体拒绝回滚；gateway UNKNOWN；read=unresolved_or_unknown |
| 轨4 幂等/冲突/失效 | 正常提交 h1 后：a) 同 outcome 重放；b) 异文 h2；c) 来源替换 v2r1 | 2 | received | h1 | S=3、R=0 不变 | a 幂等零改写；b payload_conflict 回滚、行不变；c read=committed_invalidated、h1 可复算 |

### D5 N1/N2 处理

- **N1**：按验收文件要求（22-23 行），本合同把"一处早期校验"定为：`run_once` 的 one_call 分支增加 `config.request_timeout_seconds > 120 → ValueError`（idle 会话不收紧）；配套离线反例 T06。本卡不修，实施卡内完成。
- **N2**：本合同不改限额/帧边界行为，不触发定向覆盖；不为已通过的 085 补跑全套。

### D6 授权边界汇总

- **已获授权的原行为（不变）**：admit/mark/record 元数据语义、UNKNOWN 保守预留、次数/费用预留不退、时间预扣/关门/结算算术、取消折叠、恢复收敛、协议边界（服务 64KiB/封套 128KiB/映射 1MiB）、单机单会话 D3 信任边界。
- **拟改变的持久模型/提交语义（本卡裁定物）**：新表 `activity_operation_results`；SUCCEEDED ⇔ 正文同事务已提交；回执协议 3；两个只读读取方法。
- **必须编排/用户决定项（仅列原要求决定不了的关键问题）**：无。推荐方案为单一方案；唯一必要替代及其代价：SUP 在树零后、关门前的独立事务提交正文（worker/gateway/contracts 零改动）——代价是 record 与正文之间保留死亡窗口（received-no-payload 歧义不可消除）、SUP 承担正文校验与提交、管理窗内多一次往返；语义严格弱于推荐方案，故不推荐。

### D7 可裁决结论

- **实施范围**：D1 清单全部；以本合同 A/B/C 为实现规范；实施卡须含 T06/N1 早拒绝。
- **验证范围**：D3 矩阵 T01-T20（T21 可选）；PG 用例必须真实事务；通过判定为逐例断言 + 迁移前后旧行为不回填。
- **必需独立审计**：**是**。理由：新持久模型 + 提交语义变化属主要模型变更（架构第 11 节口径）。审计最小范围：record_outcome 原子性与锁序未破坏、payload 校验完备、读取只读性（无锁/无副作用）、协议 3 配对无绕过、迁移幂等与 FK 正确、回执/状态机无"SUCCEEDED 未提交"残留路径。

## 6. 未验证/未决与风险

- 本卡未运行任何验证（静态正确 ≠ 真实通过）；DDL 为草案，未创建迁移文件。
- 未决（非本卡）：G4 revision 权威接线、UI/HTTP 暴露读取接口、TOOL_PLAN 正文与工具执行（G5）、真实供应商连通、用户库迁移授权。
- 风险：record 失败导致成功正文业务性丢失（只能新操作重试，计入预算）——ADR-005 既有代价，本合同未消除也未扩大；读取 `sources_current` 为快照期 advisory 旗标，不构成并发强保证（消费方门禁语义已声明）。
- 轨迹为推演，不构成测试证据；测试矩阵的实际结果以实施卡运行证据为准。

## 7. 实施与审计建议

实施卡沿用本窗续接即可（不换窗、不重做 085）；建议按 D1 顺序实现（迁移→contracts→repository→gateway→one_call→测试），实施完成后按 D7 范围出一次独立代码审计卡（只审增量），PG/Windows 验证与审计可同卡或分卡由编排裁定。资源建议：合成 PG 容器 1 个（对齐 085 口径），离线+PG 用例预算按 T01-T19 实际条目另卡登记。
