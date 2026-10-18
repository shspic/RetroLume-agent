# TASK113首轮设计定向核证

2026-10-12T14:11:54.045479+08:00，编排只读核证。首轮59137字节/1ca9cda0…，44输入/4补充/七规则/9设计证据匹配，运行0，原3261.109秒与准备unknown保留。当前产品还没有资料DELETE或data_exit模块；以下是未采用候选设计缺口，不称真实数据事故/产品DEF，也不要求运行证明设计文档。

K1：OriginalStore.put在发布/幂等验证原件后返回，PostgresMaterials.save另开事务提交新来源/版本引用，现资料API按此顺序调用，原代码无SourceFileLease。首轮拟租约只明确保护快照copy和清理。删除D取排他/查无他引用后，新来源B不拿该租约就复用同hash并提交引用，D再unlink会使成功B缺原件。A/B为不同来源，锁A不足。必须补所有新增引用与清理最后判据/实际unlink的共同围栏及事务未知/进程边界；不以双查hash省略。

K2：新data_control/data_operation_jobs/data_tombstones三表属提议，source snapshot仅授28表列SELECT的文字不足以支撑同T墓碑/谱系读取。需精确三表纳入/排除、源snapshot只读权限、包/codec载体、target由可信工厂生成的控制身份与受限墓碑加载/只读view。不要通过给snapshot写/删除成员资格补读。

K3：恢复job在原源，目标在新集群且selector换dataset/instance；需给持久控制权威/连接role和切换后by-key/收据/删除索引/最新账旁证路径，不能默认源一直可读。工厂/控制函数签名与受信凭据、停新写围栏和自有停线覆盖、selector半发布/丢响应行为需闭合。永久只读副本是原提议明示范围，并非要求现在改为执行恢复；但不能冒全部持续使用/执行恢复Must已过，采用代价/后续门一致保留。

源码事实依据：backend/app/storage/originals.py put/verify；materials/api.py上传链；materials/repository.py save/create_pdf_candidate；main.py连接/生命周期。已读010最终shape和002/006/012实际约束，未静态发现必须废弃原九加载分支/两FK思路的依据，不重复全仓研究。修正后的权限/格式/关系需整份A—D一致。
