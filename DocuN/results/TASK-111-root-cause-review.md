# TASK-111 / R-105 编排根因复盘与继续条件

2026-10-10，Codex 编排 Agent。按用户“从头找原因，核对方案变化，确认可执行性后再编排”的最新要求完成。范围为108的设计前提、109的实际失败、110的采用变化、111的实现与续作控制。不是独立终审，不接管产品修复，不追加运行许可。

## 结论

反复停线有三类原因叠加，不能再统称为容器打不开、资源不够或纯环境问题。

第一，108采用了没有已知完整实现锚的强导航承诺，109最终拿到真实反证。110改为有限数据与固定程序有依据且已由用户明确采用，当前不建议第三次换引擎或恢复自由模型脚本。

第二，111存在本轮新定位的确定产品缺陷DEF-027。宿主把固定脚本作为JavaScript字符串替换模板，脚本里的美元符加单引号被解释成HTML模板尾部，提前插入script结束标签。v2-01、v2-02、v2-03三个构建上下文均有同一缺陷；两次实际启动对应v2-02/03。当前仅增加等待的候选仍有此缺陷，继续原样构建会保留确定失败条件。

第三，验证顺序、夹具完整性和资源预算没有作为一套可执行方案检查。我此前把过多准备放到首次正常预览之前，又用实施分类硬截止和多个互不匹配的次数上限切断修复；执行侧还有可避免的CLI、权限、元数据、进程身份与夹具错误。后来的续作虽然修了一部分控制问题，仍没有先核对最终页面组装，且正常预览尚未成立就消耗完镜像与主浏览器额度。编排对此负有责任。

本次没有声称修复完成或后续绝不会失败。已经把“Runtime可能加载慢”的猜测推进到一个能直接定位、无需新容器即可证明的必败代码路径；修后真实ready、ACK、PNG与停止仍须由执行层取得。

## 读入身份与实际操作

当前111结果为75828字节，SHA256为31a88d3f1ca1b724225eaafa33ca685a2eb526a88cb9082cd1b1b8692b32476c，与执行者交付收据一致。该收据覆盖的66项当前源逐项匹配；七项V4.0/CHG-0003规则指纹匹配。这里的66项不冒充全仓复核或完整安全审计。

本轮读取原合同、裁定、结果、必要源和原始失败文件；按ECMAScript与HTML/CSP规范核对字符串字节，计算哈希；只对一个精确PG与两个本卡preview读取Docker停止元数据。没有执行产品Python/JavaScript、compile、unittest、build、SQL、浏览器、容器启动或业务请求，没有修改产品、旧任务卡或执行者结果。

详细核证保存在[review-evidence.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-111/orchestration-review-03/review-evidence.json)。[trace_review.py](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-111/orchestration-review-03/trace_review.py)只读取文件、推导字符串与查询精确容器元数据，exit=0。该静态推导是B类，不标为新的浏览器A类测试。

## 从108到111实际发生了什么

### 108与109，未证前提与过长的诊断准备

108在10月8日晚的A3已经明示，sandbox不能阻止frame导航自身，Playwright网络route也不是全部导航的同步否决入口。它仍把所有URL变化、同文档fragment、新frame/target均在发生前拒绝作为待实现的NavigationGate。这个具体承诺比最终需求的抽象安全目标更强，用户随后采用了具体包，因此不能事后擅自删除。

不合理之处是，关键机制尚未找到，就把它写进了一个完整交付合同。109设置H0并在反证时冻结业务是正确的保护，但H0前耗在大量准备错误上。原记录依次有Docker查询2秒超时、FROM裸digest解析错误、OCI成功后日志误判、Crashpad目录组合、getBrowserCommandLine缺enable-automation、观察主体与预算不匹配。它们大多是实施或诊断控制错误，不是同一个浏览器安全问题反复失败。

109最终在固定浏览器中，实际可信点击造成about:srcdoc#H0_SAME_DOCUMENT_COMMITTED提交，独立document、target和导航事件一致。旧8/8入口封存，停止旧路线合理；无需重复该反例。原件见[109最终报告](D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-109-result.md)及其中navigation-hash-counterexample.json。

### 110，方向调整合理，但文档可行不等于运行已证

110有限比较了原生候选，没有冒称CEF/Qt能完整满足全部同步拦截。采用包把模型输出从自由HTML/JS改为有限描述，由固定项目程序计算和绘图；同步改变输入协议、产物类型和信任边界。用户于10月10日明确确认，见[110采用决定](D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-110-work-decision.md)。这是公开说明并批准的能力收缩，不是暗中删掉失败用例。

提高pids到256、内存与swap到1GiB有旧观察接近128任务和768MiB的依据，不等于证明新场景资源必足。停止证明改为受限private PID namespace/init结束的完整组合，也有机制出处与明确前提；它不能简化成只看Pid=0。目前没有证据要求因本次脚本拼接错误再改这两项。

110明确没有运行。它支持选定实现方向，不支持“拿这个合同直接全链一次成功”。本应尽早验证的决定性问题已从任意脚本导航拦截，变成固定renderer最终页面能否加载、计算、回ACK并生成真实画面。

### 111，实施和预算循环放大了缺陷定位成本

初轮先后撞上父检索词数限制、inspect格式错误、夹具给旧受保护域多授DML、SELECT FOR UPDATE与只读权限不符，最后Docker不接受--pid private。四次原生生成已经成功，但renderer实际start仍为0。一个3600秒根在已知失败后继续等待，finally又被同一过期闸挡住清场。独立清场随后完成，原失败不能改写。

C01把完整控制、全部故障准备与实施离线压进3600秒分类门；实际7530.953秒后才发现超限。这个预算与前置顺序由编排设置，不适配工作量；执行侧未及时监测且尚有Path拼接、清场依赖业务门和故障占位等错误。C02取消分类门并改成先正常再故障是正确纠正，但仍保留了不够用的其它硬限。

C02执行又自行加了work-intent的300秒新鲜度退出，使PG在允许普通修正期间提前停止；这是执行控制偏差，并非产品安全要求。用户在执行窗口批准同一PG再启动一次，追加权限只覆盖该精确动作，不能解释为全部额度刷新。

随后v2-02主UI复验使用已有预览预算的旧部署活动。新image/load改变config hash，持久预算拒绝不一致配置，尚未create；这一拒绝没有证明renderer失败。再用合格未预览活动与独立诊断产物实际启动两次renderer，才暴露trusted_frame中的Runtime未定义。增加错误阶段是必要诊断，但第三个镜像额度此时已经用尽。

## DEF-027，固定脚本被字符串替换语义截断

严重度P1，开放。位置为[renderer-host.cjs](D:/shspic/project_NO3_RetroLume-agent/deploy/preview/renderer-host.cjs:49)的compiledHTML，以及[runtime.cjs](D:/shspic/project_NO3_RetroLume-agent/deploy/preview/runtime.cjs:51)。

宿主使用以下替换形式。

~~~javascript
.replace('__SCRIPT__', script)
~~~

固定脚本第51行的正则构造包含以下相邻字符。

~~~javascript
new RegExp('^'+prefixes.get(kind)+'[A-Za-z0-9_]{1,24}$')
~~~

这里的美元符和紧随其后的单引号，正是字符串replacement的特殊序列。ECMAScript规定它替换为原字符串中匹配项后面的全部内容。本模板中该尾部是script/body/html三个结束标签和换行。脚本第51行因而被插入HTML结束标签，原本在第206行注册的RetroLumeRuntime不会成为完整脚本的执行结果。

[ECMAScript GetSubstitution](https://tc39.es/ecma262/multipage/text-processing.html#sec-getsubstitution)定义该替换；[HTML脚本结束标签解析](https://html.spec.whatwg.org/multipage/parsing.html#script-data-end-tag-name-state)说明该结束标签会终止脚本文本；[CSP内联哈希算法](https://www.w3.org/TR/CSP3/#match-element-to-source-list)对实际脚本文本计算哈希，而非原磁盘文件。

本轮对三个实际构建上下文逐字节核对。原runtime为15586字节、SHA256 8daa3bbf979102436116074e0f240cb4e832abef43334e58b301a972a9fa3b8e；按规范推导，第一个script内只剩3352字节，已与CSP允许的完整脚本哈希不符。输入是实际构建文件，不是假造模型页面；三个上下文的四项相关文件均与各自load-manifest匹配。文件没有CR换行，已排除本次由CRLF规范化造成哈希差异的猜测。

v2-03现成A类stderr记录的是trusted_frame与Cannot read properties of undefined (reading 'start')。本轮B类证明已足以确定该宿主必定损坏脚本；不能伪称旧日志已记录CSP拒绝详情，或排除异步加载可能同时存在。现有waitForFunction候选仍保留同一字符串替换，因此即便等满3秒也没有消除这个确定阻断。

最小修复方向是字面插入固定内容，例如函数replacement返回script；需要同时检查style等相邻替换，不改CSP、安全域或模型输入。验收必须调用实际宿主组装函数，核对提取的script/style与固定源字节、CSP哈希及Python生成的compiled_html一致，不能复制另一份测试算法自证。之后才验证真实浏览器ready和后续功能。

## 为什么已有离线通过没有抓到它

[Python离线入口](D:/shspic/project_NO3_RetroLume-agent/backend/tests/fixtures/task111/offline.py)验证descriptor、Python编译包和部分旧合同；[Node离线入口](D:/shspic/project_NO3_RetroLume-agent/frontend/tests/task111/offline.cjs)直接require runtime检查计算和数据拒绝。

两者都绕过了renderer-host的实际HTML组装。Python str.replace是字面替换，产物正确不能证明JavaScript String.replace相同。三个镜像都以正确的磁盘脚本hash声明CSP，却在运行拼接时改变了脚本。语法通过、数字58.8或0.375通过、manifest匹配分别是真实子事实，均不覆盖这一跨语言边界。这不是需要更大量测试，而是漏了一个直接决定可运行性的检查。

## 其它必须一起纠正的继续条件

第一，当前正常活动与最终部署的绑定未安排好。[host_policy.py](D:/shspic/project_NO3_RetroLume-agent/backend/app/preview/host_policy.py:57)将image/load纳入config，[012迁移](D:/shspic/project_NO3_RetroLume-agent/backend/migrations/012_html_explanations.sql:278)对已有活动预算拒绝不同config。这符合当前失败关闭实现，不能为通过测试改旧行、重置次数或关闭身份校验。应先冻结最终镜像，再准备正确绑定的合成活动；旧生成证据可分段继承，若宣称同一对象的完整Native到UI链，则必须给真正需要的新合成生成与Windows会话预留额度。跨部署继续旧活动的产品兼容策略尚不能据本轮宣称解决，不顺手修改持久模型。

第二，[c02_faults.py](D:/shspic/project_NO3_RetroLume-agent/backend/tests/fixtures/task111/c02_faults.py:48)现在只处理normal_http，其余直接抛complete fault scenarios not yet prepared。这是已知未完成范围，不能再写“只差运行”。先正常的小循环合理，但完整剩余矩阵的实际入口、独立触发、期望和对象数量必须在触发相应故障前补齐。主控不把这份文件名视为覆盖证明。

第三，资源账在算术上不能支持旧续作计划。已用真实根8/9、镜像3/3、主browser3/3、PG start7/7、preview create4/14、start2/14、合成发送6/6、Windows6/8。执行者当前剩余计划为两个正常生命周期加十个独立故障，至少12个新preview，对比只余10个；还没包含修复余量。最后一个真实根和剩余真实秒数不能抵消这些硬限。必须重新做整套预算与实际用例映射，不能只补眼前缺的一项。

第四，不再把所有低风险准备、离线检查和普通修复绑定成必须回用户的新卡。下一合同需要一个完整工作目标、一份现行权限与余额、一套明确安全退出条件；旧卡和失败作为只读历史引用。普通有据修正在同卡内连续完成，只有根因再次推翻、越权、资源未知或整体上限达到才交回。产品3次/180秒、reserve30—60、ready8、D-10、外部停止和无真实付费等安全约束不因工程预算调整而放宽。

## 保留的有效成果与尚未证明的内容

保留两项最终模板生成、既有离线数值、app/denied DML拒绝、真实hook异常同事务回滚和UNKNOWN无artifact等原件。升级证据仅签真实范围，old数据/字段和旧主体权限不变、新NOLOGIN HTML owner增加九项SELECT；raw ACL并非字节相等。upgrade使用从本卡main导出的限定010/011 schema重建前提，不能冒称001—012在该库逐条原迁移均重新运行通过。

两次renderer启动失败后的精确对象结束有原件，但没有ready后的完整工作树与故障矩阵，不冒停止全合同通过。新读取的PG、preview-03、preview-14均Exited、Running=false、Pid=0、restart_count=0，见[resource-metadata.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-111/orchestration-review-03/resource-metadata.json)。本轮没有启动或停止它们，没有删除旧对象。

真实正常ready、远端ACK、PNG、完整交互和剩余故障仍未通过；合法输入后的CSP/加载时序、8秒内全启动与稳定图形需实际验证。没有依据保证修掉DEF-027后所有其它缺陷都不存在。只承诺不再拿已知必败版本投入完整组合，不以新等待或更大预算掩盖根因。

## 编排裁定与下一次工作的顺序

本次收回111为已返回、部分成果有效、完整验收不通过，DEF-027开放。按用户要求先完成复盘，本轮不追加任何运行额度，不发送新执行卡，不恢复109或其它旧runner；已完成的G3—G10和充分未变证据保持。

后续继续沿TASK111/R105，不另拆修复编号。真正出卡前，将已知阻断、剩余矩阵、最终对象绑定、合成资源与修正余量写成一份自洽现行合同。若当前窗口已混淆旧许可，应交同等能力的新A+工程窗口，以当前合同和已证事实恢复，不能靠换窗清失败或额度。必需独立终审仍在完整候选稳定后集中一次。

卡内的正确顺序已经明确。

1. 定向修DEF-027并核实际页面组装、脚本字节与CSP绑定。等待只解决确有依据的加载时序，不替代字节正确。
2. 最终镜像冻结后，在精确隔离与预算下先取得一个最小真实计算、ACK、PNG和停止闭环。该步骤先证明新renderer可用，不先启动主UI或重复模型生成来定位它。
3. 复用同一最终镜像，处理正确的活动config与已有artifact绑定，再完成两项完整正常UI、事务/权限/竞争和剩余真实故障。充分未变原件直接继承，普通修正在卡内完成。
4. 完整候选达到合同后才交集中独立终审。没有正常闭环时不再宣称进入收尾或保证“一次做完”。

以上是本次有证据的根因裁定和重新编排依据，不是新的实际运行授权，也不是让用户重复批准已经采用的110方案。
