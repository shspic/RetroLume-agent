# TASK-109 / R-103 续作01 — 离线基础输入与一次真实最小证伪

## 目标与交付

你继续担任原109执行者，本轮只完成一个有决定价值的断点成果：修正离线构建输入，实际加载固定非root/sandbox浏览器，取得B-01及自身导航的最小真实反例或准确环境阻断，并精确收尾。当前host和counter没有生产NavigationGate，即使反例未触发也只得NOT_FULL_H0，因此本轮不进入四表/PG/profile/模型/API/UI业务接线，不把诊断PASS_SUBFACT当完整H0。

仍TASK109/R103，结果置顶 D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-109-result.md，标题续作01；原15176字节/SHA 76b6a8ee174a9651c6544341c4d9dc549060653b4d1f4eba4feb9edd910eb55a完整保作新前缀后原字节历史。新原件在 DocuN/evidence/TASK-109/execution/continuation-01/，不能覆盖R01/R02/session/日志/旧源码快照或清空计数。

交付包括实际构建路径/基础与派生身份、最小观测与辨别力、准确not_run边界、当前源码/as-run/失败与预算、资源状态、是否存在真实导航反证及下一最低必要改变。充分即停，不把未实现整包再派泛读审计或完整测试套件。

## 项目、规则与接收安排

根 D:/shspic/project_NO3_RetroLume-agent，入口同根AGENTS.md。task_model/V4.0/公共AGENTS CHG-0003，需求v1.1、架构v1.03、唯一执行动态v2.25，阶段07。公共根 D:/spiritice/AA文件/MS_spi knowledge libraay/obsidian_1/&职业相关/项目流程/项目开发提示词V4；同窗已读规则未变复用，补本卡/当前工作裁定。七项锁定指纹仍DocuN/evidence/v4-migration-20260930/rules-snapshot.json，不读取其他模式或新版。

接收A+，沿实际完成109的原业务窗口，未换实现者或模型返额；107仍独立，不参与修复。G11-P已批准，不再询问普通FROM/构建方法修正。这里只是原同边界未验收任务的明确限额修订，不增加原生引擎、页面权限、真实账户/费用/下载/删除/Git权。主控不代执行。新增文稿/注释简体中文、不用星号/表格，旧格式原字节保持。

原H0根2/2均FAIL、imagebuild1/2、preview/controller/PG/模型均0，真实72入口非72次成功，real27.219秒含build24.579秒、syntax0.344、active/metadata各2700.7保守重叠及H0研究1535.6/1800、官方4/4与SSL失败保留。原阶段已停止，其他名义余量不自动执行。本轮补充许可TASK-109-G11-C01-20261009，仍计原总root8/build2/preview16等累计，最多补一个H0真实根；新增一次不重置旧两次。

原固定总起点774301594189000和截止795901594189000保持。新阶段首读固定不超过3600秒的子截止，实际不得越原总截止；主控本轮仅给该新增一个根的授权，不追认已结束根存活。若转卡时旧截止已过，先完成不受阻准备/保存事实、不得运行，交真实缺口，不改旧时间。

## 背景与最小充分上下文

读原109报告的两根原件、当前Dockerfile/root/supervisor/reaper/host/counter及本轮输入包。当前491对象中原363零变化、阶段一新增128均匹配，业务无实现，任务容器/端口均空。具体断点快照在 DocuN/evidence/TASK-109/orchestration-continuation-01-20261009/continuation-input.json；同窗未改111包/规则/108合同和官方源事实直接复用。

两次失败均早于browser：R01的2秒metadata期限误判，8秒版本在R02子检查成功；R02裸FROM sha256 ID被BuildKit当docker.io仓库，尝试auth.docker.io token而失败。正确repo digest只改源未build，不保证解析不联网；network=none只约束RUN。保留外部解析尝试偏差，不宣旧网络0或镜像已生成。

主控只读核现Docker client/server29.7.2、desktop-linux/docker driver、BuildKitv0.32.2及containerd snapshotter。没有改store/daemon/builder设置。buildx inspect没有--format的主控metadata错误已披露，plain输出已核；不复制错误flag。

本轮唯一推荐是本地OCI基础命名上下文，不再让FROM走registry解析；不切legacy builder、不改镜像store/重启daemon、不创建另一个builder、不尝试若干FROM引用。[Docker官方buildx文档](https://docs.docker.com/reference/cli/docker/buildx/build/)明确本地OCI layout可用作命名build-context并由FROM名字引用。这是方法依据，本机Windows路径/内容传递与真实构建仍必须本轮一次验证；不冒官方说明等于已在本机通过。

## 执行边界与资源

仅修改原已允许阶段一的Dockerfile/白名单上下文、必要正式离线构建助手，以及host/counter、h0-root/监督/救援中本次有据控制/观测修正；默认seccomp、资源权限、固定Node/Browser版本和111包不变。允许新增本轮独立fixture/control，不运行已触顶的旧h0-root入口。业务层/012/PG/API/frontend/profile/gateway/原账本/旧域/依赖锁/正式DocuS/其他结果只读。旧128源码/as-run/hash保留，新最小diff另存。

离线构建准备一次合并完成：

1 精确确认缓存基础ID c091b21d9fae78c76e85cd4356431e9b018402f172a214fc7d7a5e9a7e29d8ac及所有需要层在本地；从该ID只做本地image save/内容导出，不拉取。构建素材置正式deploy/preview下本卡独占cache目录，证据只索引/哈希；不把大基础归档塞进主COPY上下文，不依赖DocuN实验实现。

2 验证导出归档结构与完整字节，绑定config digest等于上述基础ID、层顺序/rootfs diff IDs/manifest和descriptor摘要。若有合格OCI layout直接复用；只有Docker归档时允许标准库按已知schema流式整理为OCI layout，保原config/layer内容、不执行层、不修改基础字节。不盲extractall、跟随symlink/路径穿越或写workspace外，不删旧文件，不安装转换工具；缺层/不识别结构停止，不伪造OCI成功。

3 Dockerfile引用唯一名字task109_cached_base，build命令以本地oci-layout命名上下文及明确manifest digest绑定它；严格核本机CLI实际URI路径语法，不拿真实build穷举Windows路径。没有外部syntax frontend、remote cache/HTTP/Git来源，所有其余COPY仍117文件白名单和输入hash；RUN只有原可信useradd，无包安装或HTML执行。networknone/pullfalse仍保留，但零任务registry解析还必须检查实际源/日志，不能只引用这两个flag。

4 仅现有desktop-linux/docker builder，派生镜像tag为retrolume-task-109-g11-h0:c01，实际immutable ID/load metadata最终读取。原基础不tag覆盖/不修改镜像store，不能默认iidfile等于loaded image ID；实际源/基础/最终config及用户/entrypoint分别核。若本地OCI方式不被本机支持、仍尝试registry或任一关键输入未知，停本轮真实链，不fallback联网/旧builder/commit或再build。

所有上述导出/建构计同一新增真实根H0-R03预检后的时间和attempt，即使先失败也不返。最多一次image save/一次build，build≤600秒；累计imagebuild2/2。新Root≤1200秒，real新增≤1200、独立cleanup≤300；只读准备metadata≤600、自有修正syntax/内存compile同一offline批≤60，总首读子窗≤3600并不得越原6小时截止。stage官方研究新额度0，主控给出primary依据，同窗其他源已读复用，不另开系列网页研究。

本轮最多创建/启动一个preview，使用原名retrolume-task-109-g11-preview-01（当前不存在），runtime≤60秒/诊断≤15，Reaper/controller≤1且绝对截止固定。资源label保原TASK109/原permit归属，新增action-permit=本C01许可，nonce随机，create第一时点冻结CID/image/label/params；原inspect_owned的身份语义保持。全部原UID10001/networknone/read-only/capdrop/no-new-privileges/seccomp/privateIPC/1CPU768MiBpids128/有限tmpfs/无mountsocket端口/真sandbox保持，不能为启动加root/no-sandbox或增资源。

新增PG/卷/SQL/app/API/main-browser/native-model/provider/付费均0。business继续冻结，不因局部popupPASS或探针没看到改变解冻。旧106/103/100/088不启；新旧原件、OCI缓存/镜像/容器停后保留，无rm/prune/DROP/DELETE/系统时钟/安装/Git。

## 验证、证据与审计关系

首build前一次静态核清当前同链准备/观测缺口，一起修到自己的stage一控制源，不在每个首失败再申请根：metadata/create/inspect不一律2秒，元数据8秒、create15秒、身份检查8秒有界且受根/实际60秒deadline限制；明确Tmpfs与真实inspect Mounts表示法，不能把允许的有限tmpfs误认host bind；无未声明mount仍拒绝。stdout/manifest/协议/类路径/Node UID/当前包/binary/ROOT/许可/计数要对应。超时create的唯一name/nonce在原create额度内找回实际已创建CID，未确认不能start/重复create。

所有输入/目标/frame观察窗口按原合同足够2秒，不用原250ms签无新目标。每个restricted动作除真实鼠标命令与位置外，保存受控固定页的实际handler/gesture辅助及引擎事件；form被禁止submit与popup sandbox拒绝分层，不把未触发当通过。受限data/blob/hash/child遇首个创建/提交反证即停后续，不为了跑齐矩阵重载各样本。

保当前counter性质为诊断器。新页无害正对照→受限新页→自身data/blob最小证伪真实加载；browser/Node/argv/sandbox实际身份先看，加载环境错误与权限反证分开。入口终态只有明确FAIL/ERROR/NOT_FULL_H0/具体PASS_SUBFACT，不能人为添加PASS_FULL_H0；即便全部最小探针没变，也没有完整生产NavigationGate与其他H0证明，仍不得进入业务。

真实触发前就开启page/target/frame观察，记录loader/document/URL与独特哨兵，frames初始合法拓扑和新目标分开；可信手势有效正对照是必要依据，marker未找到/observer丢失/包和实际browser不符为未确认。source/fixture/OCI层/配置hash/build实际输入/最终image及同轮加载绑定，JS语法和source修正不签动态。

补一次有界根是为取得决定路线的证据，不自动续其余methods。不再跑旧node-check/原G10/旧四容器；只有实际本轮代码修正需要新的syntax，单批就够。结果若是实际导航/创建反证，给准确原生欠缺与最低必要方案差异/成本；仅环境不足则给完整原始错误/构建阶段/实际限制，不从一个错误推断所有引擎都不可能。

本轮不安排110独立终审或把普通源码核称审计。未来确有完整host候选与足够动态原件再集中独立审计；原109/G11依然未验收，旧原子/Job有限结论不会替新容器证明。

## 停止与回传

原许可/根/官方页/投入继续保留；独立本轮action许可新账只记新增，根H0-R03=累计第73入口，原R01/R02不能改色或重计免费。第一次root预检就计数，次入口/次build/次preview0，不因工程错误再试。新source只修改本轮允许stage一，旧session/报告/原源码字节只读，不能改旧len>=2 guard骗第三根。

任何本轮build/启动/协议/环境失败、首个关键反证、未知归属/资源/时间或上限到达即收尾，不换方式续根；普通准备差异在真正开始前完成，实际停止后不暗复检。原总期限若已过，不启动，把明确条件交回。

仅停止精确CID/image/nonce/labels和已登记PID/出生/命令的本轮root/attach/events/reaper。停止命令回包、Running/Pid/重启策略、attach闭合/事件/PIDnamespace依据与现场事实分开；没有可靠完整物理证明写unknown，不能用Exited字段直接改真。新OCI cache/镜像/容器/所有原件保留，不stopdaemon或杀其他进程。实际根已退出的conhost不再机械kill；原未确认和补证各自保留。

报告先一个准确结论和真实阶段、build/加载/反例及剩余条件，随后主要修正/完整diff/prepost/hash、实际命令/原FAIL/原新时间计数/registry解析范围、原件与物理收尾、对完整G11后续的具体影响。不把“准备失败”写“关口安全失败”，也不把局部未反证写可交付；不得自行关闭B-01/SEC003/STEP015016/M-1或项目。

保存109结果置顶保原15176字节历史，回读且可访问后一句真实结论+原绝对结果路径供用户带回；不逐步骤回传，不修改DocuS/共享预算或其他任务结果。

## 必要人工与待同步信息

用户只需转本卡当前前缀给原109 A+业务窗口，带回同一109结果。原G11-P仍有效，普通离线构建修正无需再问采用；新原生组件/新权限仍必须准确差异另裁。共享状态/原72+新根真实数/预算/失败与最终裁定由编排维护，当前仍待转交，无实际开始。
