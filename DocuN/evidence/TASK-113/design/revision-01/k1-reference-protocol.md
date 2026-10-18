# K1 原件发布、引用与清理统一协议

本文件是当前完整合同的设计证据，不是生产代码/测试。主控静态反例成立于首轮候选DELETE设计，当前产品没有资料DELETE，不是已发生事故。实读OriginalStore.put、materials.upload、PostgresMaterials.save/create_pdf_candidate/confirm_pdf_candidate及原主控design-gap-facts，旧正文和hash不改。

拟新增OriginalReferenceCoordinator，单Windows部署、一个源业务库与一个原件根绑定一个originals_root_id。根重定位、同根多库、多主写者、外部绕过生产接口的文件操作不在此切片内；绑定不符拒绝启用清理。不得用内存RLock代替跨进程协议。

OS层RootLease为固定、不会被替换的控制文件同一字节范围的LockFileEx共享/排他锁。每个线程任务单独非继承句柄，不把同句柄可重叠锁用作升级；捕获文件对象身份，禁止unlink/replace锁文件。共享用于完整引用建立和快照copy；排他用于逻辑删除及物理最后判据/unlink。实际成功获取为资格，超时/未知/进程退出不靠墙钟或PID推断自动取得锁。Windows锁随句柄关闭/进程终结由OS释放但可能延迟，未实取排他不能清理。依据[LockFileEx官方定义](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-lockfileex)，未运行API探针。

PG层统一根键的事务级advisory shared/exclusive fence覆盖所有原件元数据新引用。根键由受信绑定ID确定，不由请求或包给。引用事务先shared，清理事务先exclusive，再按源→记忆→活动既有顺序锁业务行。它用来等待已进入DB的事务结束，不代替OS文件锁。事务级advisory锁结束时释放，依据[PostgreSQL锁说明](https://www.postgresql.org/docs/16/explicit-locking.html)，本次未连接DB。

来源PG拟data_control增加originals_root_id/reference_epoch。拟data_operation_jobs中record_class=reference_fence是源侧引用准入事实，不是长期数据job进度权威。它含prepared source/version/candidate ID、sha/size、root_id/epoch、state=open/committed/rejected/ambiguous/cancelled和私有pin_nonce_sha256；私有owner/nonce不出包，公开仅历史安全投影。创建票据的固定函数只有受信协调器可调用，不由客户端文档字段或任意SET自称。材料元数据INSERT/指针激活的新增guard校验已绑定票据，不能直接SQL绕开。原九个隔离加载INSERT分支和两教学FK另行保留；这是K1新增引用围栏，不替换它们。

正常引用顺序

1. 请求有界接收/验证后，服务端prepare_reference生成原件hash及预分配source/version/candidate ID，取得RootLease shared并检查控制选择代次没有维护fence。
2. 短事务登记匹配root/epoch和随机私有nonce的open票据，确认其COMMIT。失败或未知不发布/复用原件。
3. 在同一live ReferencePin中调用OriginalStore.put/verify，包括FileExistsError幂等命中，核实际hash/size；PDF解析失败可以留孤儿，但不能提交新保留引用。
4. save/create_pdf_candidate/confirm_pdf_candidate以reference_pin和prepared IDs为必填内部参数。引用事务先PG shared，再核票据nonce/epoch/state及已取OS pin，然后业务行锁、INSERT引用、在同COMMIT把票据改committed。API只返回普通业务收据，不返回pin/nonce/锁键。
5. 至少确认该事务COMMIT或用预分配ID读取核实结果后才正常释放shared。明确rollback/rejected保旧成功项，已发布无引用文件仍可留，不自动GC。COMMIT丢回包保ambiguous，有限核对期间持pin；无法核清可终止本请求、留下持久票据并拒清理，不能标not_committed。

进程死亡或shared已放而DB仍可能延迟提交时，不用一次SELECT没行证明没有引用。清理必须取得OS排他，再取得PG exclusive等待在途引用事务；随后在单独短事务取消所有旧未决引用票据并推进reference_epoch，确认该取消COMMIT。排他OS仍持有。旧排队SQL即使稍后获PG shared也因旧epoch/已取消票据拒绝INSERT。该取消结果未知就不unlink；不得把取消与物理unlink放在一个可能rollback的事务中，使票据又恢复open。

确认取消后，在第二个READ COMMITTED短事务再次取得PG exclusive，取得锁之后才用新语句查询全部保留引用。查询保留所有未墓碑来源的全部material_versions，包括历史、current_version=NULL的待PDF及候选；共享hash任何一条保留引用成立都保文件。核本删除manifest及源修订、普通文件身份/hash/size后，在同一OS排他+PG排他期间做唯一准确unlink，再写清理结果。检查到unlink之间不放锁、不释放epoch围栏，不在这段等网络、模型、渲染或用户。单键5MiB/有限时间，失败记pending/physical_result_unknown；若结果COMMIT丢失只核单键/旧收据，不再盲unlink。源DB或票据资格未知一律不删。

删除墓碑提交和之后精确文件清理是两个阶段，各自重新取排他；中间允许新的成功导入，由后段最后引用查询保护。快照持shared直到复制完成，使清理只能在T文件闭包结束后进入排他。文件入库的无引用孤儿不是自动清理授权。

必要入口

- materials.upload的新TXT/MD、替换、PDF候选，pin在put之前取得并跨run_in_threadpool保持，直到save/candidate的持久结果核清。
- PostgresMaterials.save/create_pdf_candidate不得在013启用后无pin直接造版本；预分配ID用于未知COMMIT核对。
- confirm_pdf_candidate激活指针同样校验pin/票据/墓碑；旧候选的已有保留引用仍纳入最后判据。skip不解除所有历史保留引用，不凭current_version=NULL视作可删。
- 其他直接元数据入口必须经协调器和新增guard；活动/记忆/HTML只允许引用仍保留且未删除的版本，不能靠激活已墓碑源重新保留已删键。
- 恢复工厂在独立target原件根建立target RootLease，发布文件及metadata加载全段持shared，使用绑定的loading身份。target没有在线GC，加载失败只封存；包不能选择源根或取消源票据。

锁序为控制选择读取→MutationPermit→OS RootLease→PG根advisory→引用票据→源/记忆/活动锁。控制journal锁只短时读/追加，不能持它等待RootLease/PG；清理不能在source行锁内反向取RootLease。模式fence发起先拒新permit、允许已登记收尾，之后才等排他。丢失pin/连接/模式代次拒绝继续新引用，不做自动锁升级。

修正前D已查A外无引用，B无共同锁复用F/提交vB，D unlink F，B缺原件。修正后若B先得shared，D的排他等待B COMMIT，最后查询发现vB保留F；若D先得排他，B在put之前等待，D精确删后B重新发布F再提交。B死亡或提交未知时，D需PG等待/持久取消旧epoch及第二次最新查询，不能利用OS句柄已释放直接删。全部为手工推演，无真实竞态运行。
