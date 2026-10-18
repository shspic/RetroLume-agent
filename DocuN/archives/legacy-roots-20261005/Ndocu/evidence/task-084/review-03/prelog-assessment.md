# TASK-084 review-03 日志前独立初判

输入顺序：已复读review-02、核 focused-repair-03/pre 字节副本和pre-hashes、incremental.diff、final-hashes及七份当前源码；尚未读本轮05-diagnostic/unit-final/stop-analysis/manifest/static/official-facts或083本轮陈述。七份最终文件及repository/005独立SHA256全部匹配，详见hashes.txt。session实质主要是SessionOutcome诊断/manager身份字段与计时观测，旧预扣/退款路径未变。

D1：新固定base Python SUP模块、悬停进程精确句柄、随机命名映射双槽有界帧、SUP确切退出后读结果，已消去旧Process.start/Pipe.recv/send用户态阻塞路径；父子共享monotonic管理deadline，CreateProcess及Win32内核无限挂起不作硬实时承诺。无SUP结果一律unknown账字段/cleanup_incomplete；进程退出本身不证明业务Job树空。若父方期限结束后terminate未证exit，当前close丢弃精确句柄，仍为未知且须停批；不能算整树安全。映射用默认DACL，DSN在受信本地共享页，跨同权限恶意代码未认证；按既定受信本地模型暂列条件风险。新路径尚无真实Win32验证。

D4：Start事件碰撞 helper 现先拒183/失败并仅关闭本次返回句柄，且不触发外来事件，前轮碰撞缺陷静态关闭。另发现04旧控制链的可运行性竞态：job_control.py中Start SetEvent后在子进程确认OpenEvent前立刻CloseHandle；若子进程尚未打开，命名对象消失，子端失败。须保留Start句柄直到悬停身份回执或明确子进程退出。此缺陷不等于外来事件被触发。

最终focused_unit的deadline-before-resume测试静态上计数不对：launcher有三次run_deadline正值检查才Resume，测试给(5,5,5,0,0)令第三次仍为5，必进入Resume；最小修正把第三次设0，并断言无Resume/无DB claim、清理未知且精确进程终止。现有失败日志待核，不改生产截止逻辑以迁就测试。

05只增加sleep前后单调读数、导入hash及SessionOutcome诊断字段，FakeJob sleep(0.002)与session C公式未变；本次PASS即使出现也不能自动说明上次FAIL原因。D3旧恢复仍失败关闭；新official-facts尚未读，不先评两列方案。Job/PG未运行，运行门不自行解除。
