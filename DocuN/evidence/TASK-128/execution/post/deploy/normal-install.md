# 正常首次安装工具

`initialize_normal.py` 是独立新 PostgreSQL 17 集群中已明确创建的全新空数据库首次安装入口，目标为 `data_exit.v1.r03`。它不创建数据库、容器、卷或服务。原TASK125/126的离线工程及独审范围保留，真实操作须有冻结精确资源的运行许可。

TASK128已在授权隔离库确认并修正空串service连接失败：不再传`service=''`，连接前发现环境中存在`PGSERVICE`或`PGSERVICEFILE`即以`ambient_service_rejected`拒绝，不读取用户service配置、不修改环境；显式host/hostaddr=127.0.0.1及身份核验保留。修后正式只读连接成功，两项定向离线方法通过。当前原身份预检仍拒绝PostgreSQL实际地址文本`172.19.0.2/32`，完整安装、角色权限和正常启动六项尚未通过；不得据连接修复宣称已可完成真实安装。连接增量待独立复核，地址格式问题及后续资源额度待主控处理。

## 本地帮助与计划

从项目根使用已有后端 Python。以下命令不连接数据库、不读取凭据环境值、不启动子进程，也不装载应用、ControlHub 或 QAuthority。

```powershell
& 'D:/shspic/project_NO3_RetroLume-agent/backend/.venv/Scripts/python.exe' -B 'D:/shspic/project_NO3_RetroLume-agent/deploy/initialize_normal.py'
& 'D:/shspic/project_NO3_RetroLume-agent/backend/.venv/Scripts/python.exe' -B 'D:/shspic/project_NO3_RetroLume-agent/deploy/initialize_normal.py' --help
& 'D:/shspic/project_NO3_RetroLume-agent/backend/.venv/Scripts/python.exe' -B 'D:/shspic/project_NO3_RetroLume-agent/deploy/initialize_normal.py' plan --help
& 'D:/shspic/project_NO3_RetroLume-agent/backend/.venv/Scripts/python.exe' -B 'D:/shspic/project_NO3_RetroLume-agent/deploy/initialize_normal.py' plan --config 'D:/shspic/project_NO3_RetroLume-agent/config/normal-install.example.json'
```

无动作时只显示帮助，退出0。plan 成功退出0表示本地输入结构、原件和关闭模板核验完成，输出 `status=plan_only`、`installed=false`、`verified=false`、`database_observed=false`。示例的 `enabled=false`，端口、数据库身份、三个安装 UUID 和两个登录名均为 null，因此 `local_inputs_complete=false` 并列出缺项。未知 CID、system_identifier、OID、快照、安装身份及四个运行根均保持 null。重复 plan 不生成身份或安装收据。

plan 可额外指定 `--output` 绝对路径，只排他新建一个计划 JSON；父目录须已存在，已有文件或不安全路径拒绝。省略时只输出到终端。任何拒绝退出2，只返回固定原因，不回显坏参数、连接串或驱动异常。计划不证明真实目标匹配，不授予运行或外发权。

路径必须绝对、非 UNC、无 `..`，先按原拼写逐级拒绝符号链接及 Windows reparse/junction，再以严格模式解析现存父目录和项目根的实际长路径身份；8.3短别名同样受保护，归一失败即拒绝，末级仍排他新建。输出不得落入源码、部署、配置和 Git 元数据目录；后续打开仍要求父目录受信，不宣称验证了对手并发替换的竞态。工具只枚举项目固定迁移目录以拒绝额外 SQL，再按清单逐项读取，不自动吸纳未来迁移。清单原字节摘要冻结在入口源码；同时校验顺序、数量、每份 SQL 原字节摘要和四份关闭模板摘要。SQL 仅作 utf-8-sig 解码，保留 BOM 后的原换行及全部正文，不删碰撞 guard 或改写 CREATE ROLE。

## 安装输入与关闭配置

`config/normal-install.example.json` 的 schema 为 `retrolume.normal-install.v1`，仅由本安装器读取，不能交给现有应用 loader。它不包含真实连接串、密码、身份、运行根、ACL、grant、源清单、operator 票据或激活回执。

将来受信部署时，在项目外受信私有目录准备自己的副本，并经后续卡冻结绝对路径；不要放入尚未被 Git 忽略的项目配置新路径。需要填写：

- `target`：仅 loopback IPv4，明确映射端口、数据库名、真实集群 `system_identifier`、数据库 OID、PG 主版本17，以及短时安装管理员登录名。数据库不能为 postgres/template0/template1；名称检查不能替代身份观察。
- `identities`：明确登记的非零 dataset_id、instance_id、originals_root_id 三个 UUID。安装器不自动分配身份，originals_root_id 必须来自后续受信部署的根绑定过程；此工具不绑定或创建运行根。
- `roles`：互不相同、区别于管理员及现有职责组的全新 business_login 和 snapshot_login。名称只接受小写字母开头的有限 PostgreSQL 标识符。
- `credential_env`：四个互不相同的 `RETROLUME_NORMAL_...` 环境变量名，分别供安装管理员密码、全新业务密码、全新快照密码、maintenance_key 使用。真实值仅在未来安装进程安全环境中注入，彼此分离，每项16—1024个 UTF-8 字节，不放 argv、JSON、终端记录或收据。维护摘要仅作为现有 data_control 必需值写入数据库，不输出或保存到安装收据。
- `enabled`：仅表示此安装器的本地实施开关。示例关闭；即使将来明确改 true 且本地项齐全，也必须先满足真实运行许可和独审。`runtime_configs` 四项必须始终 null，不接受顺带启用应用能力。

活动仍沿原生 `config/activity.example.json` 的零次数、零费用和零输出占位，不能产生可用活动能力；integration 和 q-approval 原生示例 enabled=false；preview 沿原生结构保留无效镜像、摘要及票据占位，不虚构一个 loader 不支持的 enabled 字段。安装器核这四份固定关闭模板，没有生成可用配置。原生 data-exit.example.json 也保持关闭；reader 示例只适用隔离只读恢复，不作为正常源配置。

四个独立 data/backup/control/restore 根、真实 Windows ACL/file-id、control_id、selection generation 及连接绑定只能在后续正常部署时核定，本卡不创建私有运行根。账号计量、分词、Embedding 容量、当前模板及外部采用缺项沿既有关闭交接保留，不能用安装器成功替代。Q 未启用，T0=null，真实调用和费用仍为0，原100次/25元及48/28/24分额不变。

## 未来显式 apply 与只读 verify

以下仅说明已实现参数。`$normalConfig` 和 `$installReceipt` 必须由未来运行卡给出真实绝对路径，收据父目录须预先存在；当前没有执行。apply 不提供恢复、升级、清空或重试选项。

```powershell
& 'D:/shspic/project_NO3_RetroLume-agent/backend/.venv/Scripts/python.exe' -B 'D:/shspic/project_NO3_RetroLume-agent/deploy/initialize_normal.py' apply --help
& 'D:/shspic/project_NO3_RetroLume-agent/backend/.venv/Scripts/python.exe' -B 'D:/shspic/project_NO3_RetroLume-agent/deploy/initialize_normal.py' verify --help
# 仅在未来精确许可及独审满足后：
& 'D:/shspic/project_NO3_RetroLume-agent/backend/.venv/Scripts/python.exe' -B 'D:/shspic/project_NO3_RetroLume-agent/deploy/initialize_normal.py' apply --config $normalConfig --receipt $installReceipt
# 仅限同一完整成功收据及目标：
& 'D:/shspic/project_NO3_RetroLume-agent/backend/.venv/Scripts/python.exe' -B 'D:/shspic/project_NO3_RetroLume-agent/deploy/initialize_normal.py' verify --config $normalConfig --receipt $installReceipt
```

apply 先核本地全部输入和固定文件，再核现有 profile 原件映射，排他占用新收据，之后才允许管理员连接。数据库已由另行许可创建，安装期间必须独占这个独立集群。短时安装连接同时显式固定 host/hostaddr 为127.0.0.1，并给出精确 port/database/user/password，不接收 DSN，也不通过修改全局环境纠偏。初次 preflight 在 READ ONLY 事务中核：真实集群/数据库/当前及会话角色一致、管理员为 bootstrap superuser、PG17/UTF8；连接端固定为 loopback，服务端实际地址/端口如实记录，支持容器端口映射；没有其他业务数据库或客户端、额外用户 schema/对象/扩展/默认 ACL/大对象/事件触发器等；没有所需全局职责组或目标登录角色；除管理员和 PG 内置角色外没有其他集群角色；PUBLIC 没有 schema/database CREATE；可用 vector 默认版本恰为0.8.6。任一失败在首次 DDL/DCL/数据写之前停止，保留拒绝收据。

预检通过后严格按001—013原 SQL 各自事务执行；013提交后单独事务插入 normal/R01 控制行及明确身份、maintenance 摘要；014推进 R02，015推进 R03。随后单独事务创建两个新非超级登录角色，业务只授 data_app、memory_app、interview_app、html_app、retrieval_app；快照只授 data_snapshot。membership 显式 INHERIT TRUE、SET FALSE、ADMIN FALSE，并仅为两个新登录授目标数据库 CONNECT。不会授 owner、purger、restore_loader 或管理角色，不复用、ALTER、DROP 或重置任何既有角色。

最后在只读事务中复用现有 schema_checks、schema_profiles 和 q_roles，核 R03 固定 shape/函数/ACL、全局 SET/INHERIT/ADMIN 传递能力、精确登录组和 normal 控制身份。该检查发生在未来真实数据库中才有动态效力；本轮执行记录器只证明本地调用顺序及停止分支，不能证明 SQL、事务、权限或启动已在 PG 生效。这里没有替代原有领域全部回归验收。

收据为本地逐行 JSON，只含固定原件 hash、非敏感目标及安装身份、preflight 观察和 submitted/confirmed/complete/stopped 阶段。每次提交请求前先 flush/fsync submitted，确认响应后再 fsync confirmed。15份迁移和两个补充事务各自提交，不构成整包原子事务。进程退出、断线、丢响应或保存失败保留已确认阶段；最后 submitted 未确认按提交未知停止，即使驱动报错也不自动推断整包回滚。不会自动重试、重放、回滚历史提交、清库或清角色。

重复 apply 遇到原收据立即拒绝；换空收据也会被真实非空库或角色预检拒绝。部分、未知、损坏或没有完整成功收据的目标交回精确阶段事实，不提供续迁移。verify 只接受完整阶段序列、同一清单/输入/原身份及成功结尾，再只读核真实目标与原观察、当前 schema/角色/控制行；仅使用管理员密码，不读另三份秘密，不修改收据。收据是安装元数据，不是新的授权协议或业务账本。

## 与现有启动衔接

旧 `deploy/initialize-materials.py` 仅执行001，不能在完整安装后再跑；它不承担完整部署。本安装器的帮助、plan、apply、verify 均不会调用它或 `start_local.py`，应用启动也不会自动调用安装器。

只有未来安装及独立运行核验均满足后，才按原有正常源 loader 和四根绑定准备关闭配置，并使用原 `deploy/start_local.py` 的 `--container`、`--port`、`--shutdown-stdin` 启动。公开参数没有 `--profile`、`--initialize`、`--migrate`。启动会产生 PG/应用/ControlHub 事实，需要另一张精确运行卡；不能由本文件示例直接执行或推断安装成功。首次真实 PG 安装、角色能力、应用读取、同库重开及停止组合验证仍待该运行卡完成。
