# TASK-083 验证12 预检BLOCKED诊断记录（2026-09-26，执行窗 GLM-5.3-Flash 补充证据）

本文件为 runner BLOCKED 后执行窗补充的只读诊断证据，不含任何凭据/Env。runner 本体输出见同目录 state.json 与三个 as-run 快照。

## runner 事实

- 唯一一次启动命令（工作目录项目根）：`backend/.venv/Scripts/python.exe -B Ndocu/evidence/task-083/d3-repair-11/runner.py --authorized-reuse --total-seconds 900`
- runner hash 26ECB423DF5524EC834FFB96366ECC599F62764D648EDA63F30FB6EC73D3F731（与卡冻结一致，运行后未变）
- 进程起 2026-09-26T06:47:44Z 止 06:47:48.736Z（UTC），墙钟约4.4秒；stdout/stderr 均为空（runner 不写控制台）
- state.json：verdict=BLOCKED、attempts=[]、cleanup_incomplete=false、container_stopped=false、error="RuntimeError: inspect exit=1"
- 失败点：main() 首步 `before=inspect(...)`（touched 置位之前）→ 容器未启动/未认证/未轮换/无批次；finally 的 stop 分支因 touched=false 未执行（无可停对象，容器保持既有停止态）

## 根因探针（全部只读，docker inspect --format 不改状态）

宿主：Docker server 29.7.2；守护进程可达。

| # | 模板 | 对象 | 结果 |
| --- | --- | --- | --- |
| 预1 | `{{.Id}}\|{{.State.Running}}\|{{.State.Status}}`（简化） | 85242648 | 85242648…\|false\|exited，exit0 |
| 预2 | 卡面完整14字段（首次复现） | 85242648 | **exit1**：template parsing error: :1:305 executing at <.HostConfig.Mounts>: map has no entry for key "Mounts" |
| 预3 | `{{json .HostConfig.Mounts}}`（单字段） | 85242648 | null，exit0 |
| 预4 | `{{json .HostConfig.Binds}}`（单字段） | 85242648 | null，exit0 |
| 预5 | HostConfig 顶层键清单（{{json .HostConfig}} → python 解析） | 85242648 | Mounts 不存在（False）、Binds 存在（True）；相关键=[Binds, CpuCount, PortBindings] |
| A | `{{json .HostConfig.Binds}}\|{{json .HostConfig.Mounts}}` | 85242648 | null\|null，exit0 |
| B | `{{.Id}}\|{{json .HostConfig.Mounts}}` | 85242648 | **exit1**（同错误） |
| C | `{{json .HostConfig.Mounts}}\|{{json .HostConfig.Mounts}}` | 85242648 | null\|null，exit0 |
| D | 14字段去掉第14字段（含 .Id，共13字段） | 85242648 | 13字段齐全，exit0 |
| E | 完整14字段 | 1086a37d（首容器） | **exit1**（跨容器通用） |
| F | `{{.Id}}\|{{json .HostConfig.Binds}}` | 85242648 | id\|null，exit0 |
| G | `{{json .Config.Labels}}\|{{json .HostConfig.Mounts}}` | 85242648 | labels\|null，exit0 |
| H | `{{.State.Running}}\|{{json .HostConfig.Mounts}}` | 85242648 | false\|null，exit0 |
| I | `{{json .HostConfig.Mounts}}\|{{.Id}}` | 85242648 | **exit1**（.Id 在任意位置即触发） |
| J | `{{.HostConfig.RestartPolicy.Name}}\|{{.HostConfig.NetworkMode}}` | 85242648 | no\|bridge，exit0 |
| K | `{{.Name}}\|{{json .HostConfig.Mounts}}` | 85242648 | name\|null，exit0 |
| L | 13字段+第14字段改顶层 `{{json .Mounts}}`（含 .Id） | 85242648 | **14字段 exit0**；顶层 Mounts 数据=同一匿名卷（11140b6c…，/var/lib/postgresql/data） |

经验规则（CLI 内部机制未查源码定论，以探针为准）：模板引用 `{{.Id}}` 时，本机 docker CLI 29.7.2 对 inspect 结果走通用 map 渲染且 missingkey=error；该路径下容器 HostConfig JSON 有 Binds 键、无 Mounts 键（omitempty）→ `.HostConfig.Mounts` 必错。模板不含 `.Id` 时走类型化结构体路径，Mounts 为结构体字段（nil→null）成功。runner 投影首字段即 `{{.Id}}`，故其14字段投影在本机恒定失败。首次复现即确定性复现，排除"守护进程冷启动/资源省电"类瞬时假设。

为何此前未暴露：implementation-10 runner 用全量 `docker inspect` JSON+python 字段选取（runner_replacement.py:62 `hc=obj["HostConfig"]`），2026-09-25 同机实测通过；repair-11 改为 --format 投影以排除 Config.Env，review-08 为纯静态审计（动态额度0），该投影直至本卡首跑才首次执行。

## 运行后资源与零写入核准

- `docker ps -a --filter label=retrolume-task=083`：9容器全部 Exited(0)（85242648/1086a37d/47da46df/f868e4f2/6e5ee099/f7356959/b8b7982f/10faef60/8b2b6349），无活动 083 容器。
- 目标容器13字段只读快照（原样，无Env）：85242648b70dc11839a93de29a51bc7e492390d8ad479036c141f37b26f4f6a7|/retrolume-task-083-d3-20260925-195448|sha256:cf134a767f474095eeba57e0117be8e568e0117be8e568e011a63f33fbf252f14c9b760f8e6f|{"phase":"d3-10","retrolume-task":"083","run":"20260925-195448"}|false|[{"Destination":"/var/lib/postgresql/data","Driver":"local","Mode":"","Name":"11140b6c41401e2cef58ef2743357938db543c5891a3a8d68fce87a60cb85e07",...,"Type":"volume"}]|1000000000|536870912|128|no|bridge|{"5432/tcp":[{"HostIp":"127.0.0.1","HostPort":"55439"}]}|null —— 与卡面精确资源许可逐项一致。
- 端口 55439：托管 python socket bind 测试空闲（与 runner 同口径）。
- 13项冻结hash（8 REPAIR11+5 UNCHANGED_REVIEW07）：运行前、运行后各复算一次，13/13 ALL MATCH，零漂移、零写入。
- 预算：0批/0 PG进程/0 Windows场景/0次启动认证轮换；剩余2批/2PG/12Windows、容器总数2不变；另记墙钟约4.4秒（无资源接触，是否并入30分钟总账由编排裁定）。
