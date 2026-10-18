# TASK-083 / R-077 — inspect兼容修复与真实验证接续13
接收原083执行窗口，继续原增强任务所需能力，实际模型如实登记，不因12已完成的结果或标签重做工作；原窗不可用才等价接续。STEP008局部，父082，关联084/R078、NFR002/003、SEC002、FLOW005、DATA007。
根D:/shspic/project_NO3_RetroLume-agent；需求v1.1、架构v0.45、执行状态v1.64；Git基础45951501d2741630a229762d6b2d3f4b34d7f702及全部差异保留。本卡待转交。

## 当前断点与一次授权成果
验证12唯一runner启动在首inspect字段投影报错，尚未触发start/认证/轮换和测试进程；8场景not_run。13项冻结未变，review08关闭的产品/控制问题仍有效。这里只证明本机模板缺键失败，不把未核实的Docker内部机制写成事实。
编排授权一次最小inspect缺键兼容修正、一次定向准备检查，通过后直接续原精确容器的完整真实验证，不再先交084审一行模板。最终由084只核新增投影差异和动态证据，独立审计保留。授权不包含削弱身份条件、读取全量Env、改变controller/contracts或扩大产品模型；出现这种需要才停。
修复与执行在同一卡连续交付，不因普通已明确步骤再请求许可；不重跑12探针矩阵、不重新研究Docker。

## 规则与最小上下文
入口D:/shspic/project_NO3_RetroLume-agent/AGENTS.md；
公共D:/spiritice/AA文件/MS_spi knowledge libraay/obsidian_1/&职业相关/项目流程/项目开发提示词V3/docu/AGENTS.MD，已读未变复用。
读083结果置顶12、Ndocu/evidence/task-083/d3-repair-11/continuation-20260926-064735-85cbc7d0/preflight-blocked-diagnostics.md与state.json；
review08有效结论/证据分级、d3-repair-11/{runner.py,contracts.py,controlled_child.py,runner-walkthrough.md,final-hashes.txt}，既有D3批准合同复用。原12完整授权历史存本卡归档，无须复制全部历史结果。
冻结以review08/hashes.txt十三项为准。runner修前=26ECB423DF5524EC834FFB96366ECC599F62764D648EDA63F30FB6EC73D3F731；controller=14E20FCB63DB913E22FF05F4C8286C0A3D56FEE946A06DBB17E044635CF0E401；contracts=A344AC5FBDF7C838C08C18FC1816D5D8E823C3FF67B1A98976CF11129257CBCD；fixture=A1E419F34C6464FC588B5812A9AE95545E4074C8732130CC85D2251AF57CE3A1。保存runner修前原字节/hash、限定diff与新hash，其他被审文件应不变，未知漂移不覆盖。

## inspect修复合同（不放宽检查）
只改runner.inspect的第14字段访问及确有必要的对应解析，优先使用完整含Id模板中的缺键安全映射读取，例如 {{json (index .HostConfig "Mounts")}}。此具体写法尚未在本机实测，须以下一次实际完整投影检查确认，不宣称已验证。
缺失或JSON null映射为configured_mounts=None；真实空列表按原契约允许；非空列表必须传递并被原valid_identity拒绝。字段解析失败/类型异常/输出基数不等于14均失败关闭，不用catch-all伪造None。valid_identity中binds/configured_mounts及精确顶层mounts检查全部保持，资源限制和标签一项不删。
不采用“删第14字段后固定None”，也不把顶层Mounts冒充配置Mounts；两者语义不同。禁止回退完整inspect JSON读取Config.Env。正常资源状态、stop/kill收尾均复用同一修正后的inspect，不分叉两套读取。
允许一次≤60秒定向检查批：现有venv -B，内存compile改动runner；只调用目标CID完整14字段只读投影一次，记录exit/14字段脱敏输出及真实valid_identity判定；纯合成输入验证缺失/null/空列表通过适用解析、非空configured_mounts拒绝，其他13字段和验证器不弱化。不得在该检查启动容器/PG/Job/受测进程。一次失败只读定位留证，不再追加探针或循环改模板，交回具体差异。没有必要复跑整套离线。
检查通过、有限diff确认无控制/授权变化后轮换本卡runner冻结，直接使用修正版执行下述流程。所有旧continuation/as-run/原始日志和final-hashes文件原样保留；新hash记录独立文件，不倒改历史。

## 唯一精确资源与启用
CID 85242648b70dc11839a93de29a51bc7e492390d8ad479036c141f37b26f4f6a7；
name retrolume-task-083-d3-20260925-195448；
labels retrolume-task=083 / phase=d3-10 / run=20260925-195448；
image sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f；
唯一volume 11140b6c41401e2cef58ef2743357938db543c5891a3a8d68fce87a60cb85e07 → /var/lib/postgresql/data；
1CPU/512MiB/pids128/restart=no/bridge、无host bind、仅127.0.0.1:55439→5432；
db retrolume_task083_d3，role task083_d3。
诊断抄写的镜像行含重复片段，不能用于身份匹配；以上固定完整hash及原runner常量为准，运行时按真实投影核对。截图/摘要的Exited仅日志时点事实，启动前仍按runner核当前停止/身份/无其他083活动任务/端口空闲；不满足就停，不清端口、不停止别的资源。
编排继续授权同CID一次start→既定容器OS postgres的本地socket指定DB角色认证→stdin轮换内存新随机测试口令→loopback核库/用户/容器内5432→余下测试→精确stop保留。认证/改密仍未知，失败同CID收尾，不读旧secret、不改认证、不升权换角色、不建第三容器，不启Docker Desktop或拉镜像。
项目根启用一次：
backend/.venv/Scripts/python.exe -B Ndocu/evidence/task-083/d3-repair-11/runner.py --authorized-reuse --total-seconds 600
前述定向检查已通过及本卡就是旗标的授权依据。不得额外启动旧runner或裸fixture绕控制；tool yield保留原session读结果，不重启命令。单runner持新凭据直到完成/受限复验，口令/DSN仅内存与子环境，不日志/argv/文件。停止后不另开runner重领凭据。旧首容器及所有其他资源不触碰。

## 八场景与一次连续结果
首次parts=migration,ledger,windows，contracts固定顺序：
migration_empty（NULL/0/上界合法、负/超界拒绝）、migration_old（旧行NULL）、migration_rollback（失败无部分DDL）；
ledger_active_lease_rejected（有效旧租约不抢占）、ledger_new_g（同SID0全折/新G、独立pending上界、旧G/C实际重试分支不污染新窗）、ledger_exhausted（None提交关闭）、ledger_lock_barrier（真实锁等待早于deadline/lease边界，锁后判定有辨别力）；
windows_recovery（真实旧Job精确PID/创建时间/SID、树空close/Open2、生产固定SUP新G与真实PG结算、外层树零/句柄收尾）。
逐项唯一start/result、完整parts/all_pass/exit/cleanup共同判，未达场景记not_run。PG失败不进入Windows；成功路径不升级为所有崩溃分支实测。旧Job07/PG08/09不重跑。

## 预算账与允许的定向修正
12的“额度零消耗”只限新容器/启动/PG测试进程/场景计数，不包括时间与诊断命令。约4.4秒首跑和12探针+5预检全部登记，不认可资源操作零时间；跨首容器只读探针范围偏差保留，不能据只读追认任意扩查。已发生事实保留，不重跑凑完美记录。
原30分钟总资源账：既往10轮保守占900秒不变；原12和其后诊断时间缺完整计量，暂从原余900中保守占240秒（非实测认定）；本卡定向检查≤60秒、runner≤600秒，合计仍≤1800秒。若现存证据证明12含诊断实际超240秒，必须先据实扣减并缩短本600秒参数；不能因占账不足隐瞒耗时。参数低于runner最小120或无余量则停，不改runner下限。不为补齐精确计时另跑探针。无迹象超240时按此保守额度执行，原始未知照录。
原已用1真实批/1PG/0Windows，13仍最多再2批/2PG，原3批/3PG/12Windows不重置；两容器上限不变。每场景主动30秒、测试命令60秒含收尾、每批600秒含60秒预留，最早期限优先，本轮600包含认证、等待修正及finally。
第一批若尚未开始Windows且PG普通夹具根因明确、精确树零/句柄完成，允许一次有据夹具修正（如慢环境锁观察窗），不削弱正证/断言、不改产品或控制器、系统/DB时钟。同runner存活且余量足时写本continuation的唯一attempt-02.go，选择失败part及未运行后继：migration失败通常migration,ledger,windows；ledger失败ledger,windows。已过part不机械重跑；整个part不可细分的重复如实记。第二批后即停无第三批，结果合并必须八场景覆盖，不把部分parts PASS当全链PASS。
Windows一旦开始后失败/超时、任何身份/树/清理unknown立即FAILED_STOP，不复验。需要改runner控制/产品语义或扩大权限时停止，不拿新的投影兼容授权扩成全面修正。修正版runner再次启动后前置失败即收尾交回，不再开第二runner。本卡无新增通用单元或其他探针预算。

## 收尾、写入与回传
沿已审controller精确句柄/PID+创建时间及自有外层Job收束、树0正证；Assign前猝死残留悬停不算清理完整，只有确认归属才精确清理，不裸PID/名称/端口杀。unknown停止后继并如实报告，不为PASS扩大清理。
容器finally核CID/标签→stop，失败同CID一次kill→inspect停止；共享总deadline，错误与cleanup分开；不删除容器/卷/旧新schema，不DROP。runner已退且cleanup未知，只在本卡余时内精确补收尾，不再测试。
允许写runner.py限上述inspect兼容差异；pre/diff/新hash及定向检查证据写Ndocu/evidence/task-083/d3-inspect-continuation-13/；runner新运行仍用其自建d3-repair-11/continuation-新tag/；有限夹具修正按上述授权；TASK-083-result.md置顶13保留历史。禁止修改产品/迁移/controller/contracts、正式docu/公共库/记忆/旧证据/依赖、用户库或配置、模型外发、Git提交推送。
统一回传投影实际修法/真实完整字段与拒绝验证、runner新hash和未变13项范围、八场景实况/所有原始命令和计时/累计预算/资源终态、实际普通夹具修正及复用、未验证。没有真实证据不签D3动态/M-1/STEP008/one_call；末次原084仅审本次实际差异和新证据，不重新全量审查。不自行填编排最终验收。保存可读后只回复一句结论与绝对路径。