# R03最小修复与一根组合验证

固定首读11:59:39Z另扣60秒，10800秒截止。297基线匹配，改前MemoryWorkspace／memoryIntents及全部原dist已存pre；旧42根／C02三项与104其他已核范围不重跑。只有本轮两个前端文件改动，其余禁止域冻结。

execute捕获生命周期、owner、完整绑定和读／写epoch；每次await返回后核授权，再select／清草稿／notice。refresh接收同一授权谓词，晚结果及错误不污染新编辑身份；select不同ID清旧notice。草稿删除在IDB get回调内重核同一编辑epoch，后续新编辑事务不会被旧删除吞掉。自身合法select改变read序号后没有额外编辑副作用，finally只释放所属实例busy。

一根主验证，预计记忆POST6—8／上限12，无活动／教学／SUP。创建专用A/B用户记忆，核旧activity_memory_choices引用0，避免修改当前引用上游。正常保存及修订核确认版本、清对应旧draft，IDB／owner／完整绑定都按公开DOM和真实数据库。

- 准确P1：A修改POST真COMMIT暂停；输入增加edit epoch；交付POST后捕获其列表refresh GET真响应并暂停。此时才点击B，明确载入无草稿B并核干净完整身份。释放旧列表GET，B不被抢回；编辑B新草稿仍是B，A原收据及一次effect成立。控制器分开保存两个响应时间点。旧源码在该回执后GETawait结束无guard时会select A，干净B使旧select不会被dirty挡住。
- 卸载：同样POST确认后的列表GET挂起，导航离开活动面板，再释放，重开后无旧选择／notice／草稿污染；不重新发送原键。
- 受影响旧窗：真实POST还未交付时明确切B并输入，交付后保持B；未切换正常修订仍加载新版本且只清原draft。仅本轮新合成ID，旧C02所有副作用只读。
- 引用：旧target先当前真实GET200；界面用section.library/default列表及cursor匹配实际activity详情确认，必要加载更多。真实citation GET200挂交付，导航卸载面板再重开另一明确身份；尝试释放，允许实际Abort，不复活旧原文／位置，引用阶段POST0。PG业务快照／四账一致。

每个POST先走r03 bridge按key/ID登记并计次数，非save/revise拒绝、revise只允许本轮登记ID。Native /api/session GET无不支持Origin，业务请求保持真实session／同源；不写认证头。named卷按Mounts严格判别，完整HostConfig/Binds兼容固定命名卷；没有LIKE百分号查询。r03 bootstrap许可日期明确20261007，ROOT parents[5]、backend cwd、Selector循环及非交互finally一次核。

先一次新fixture前置及node语法检查，一次源改变后的正常构建；不改源不重build。每根硬300／总真实1200，资源按精确PID／出生／命令、CID收尾，保留所有已COMMIT／profile。若失败只修明确不同直接原因后复验未过部分，不重提交旧效果；同因两修仍败停止。
