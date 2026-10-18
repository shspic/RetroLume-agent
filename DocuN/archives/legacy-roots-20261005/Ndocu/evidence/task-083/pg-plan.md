# TASK-083 后续专用 PG 验证准备（not_run）

本卡不运行迁移、不连接数据库。下一卡只在全新合成库与专用测试 DSN 上执行；专用 DSN 缺失明确 skip，不回退用户或应用 DSN。

| ID | 最小场景 | 必须观察的事实 |
| --- | --- | --- |
| PG-01 | 001—004 建表后 activities 空表执行 005 | 唯一新增列 `dispatch_closed BOOLEAN NOT NULL DEFAULT FALSE`；同事务提交；001—004 hash 未变。 |
| PG-02 | 有一条活动时在副本事务执行 005 | 异常且整个事务回滚；列不存在；该活动及其他表均不变。 |
| PG-03 | claim 成功、折叠耗尽、cancel、settle | 仅 claim 新代次开门；其余路径关门；create 默认 false 不授予执行资格。 |
| PG-04 | 两连接按来源→活动锁顺序并发 close/admit/mark | close 提交后新 admit/mark 均拒绝；先已 mark 的调用按原记录结果规则收敛；无死锁。 |
| PG-05 | 同一代次首次 settle 关门前/后；随后同 G/C 重试；再 claim 新代次后旧 G/C 重试 | 关门前拒绝不写；关门后退款；旧幂等不改新代次的门、R/S/G；冲突 C 拒绝。 |
| PG-06 | 关门后 record RECEIVED/UNKNOWN、取消、过期恢复 | 合法旧结果仍可记录；未知按原纪律；取消与残留折叠不退款，不被新门阻断。 |

受影响既有用例定位：`test_activity_time_budget.py` 的 settle 正常/重复/旧代次分支需使用适配 helper；`test_activity_ledger.py` 的准入、mark、cancel 路径及 `test_activity_recovery.py` 的结果恢复路径需按行为选择，保留原业务断言。新增 PG 用例应独立覆盖 PG-01—06，不能把离线替身或 079 旧账本通过结果称为新行为通过。真实运行标识、命令与预算须在下一卡授权后冻结。
