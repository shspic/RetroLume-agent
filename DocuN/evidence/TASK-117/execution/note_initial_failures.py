"""补记已发生且未提前捕获的工程失败；不回填精确未知时刻。"""
from control import failure,event,state,HERE,write,sample

value=state()
if any(x['label']=='initial-fixture-notes' for x in value['failures']):raise SystemExit('记录已存在，不重加')
failure('initial-fixture-notes','两次apply_patch尾行上下文不匹配，未应用目标文件；读实际尾行后更正。最初ROOT01子unittest在90秒超时，父wrapper未捕获输出/子PID；不能追认实际方法数或精确子启动点。当前Get-Process python*未列对象，stdlib超时路径kill/wait已完成。CIM只读资源查询被当前客户端拒绝，改用native内存采样。',
        effect='原失败与方法未验证保留，ROOT01不清零；不更改正确预期，改显式discover路径并直接命令观测')
event('targeted_recheck_basis',root=value['active_root'],reason='backend/tests没有__init__.py，原tests.module定位不可靠；显式discover避免同名包，直连工具stdout避免丢子进程输出',
      original_entry='python -m unittest tests.test_step018_embedding_contracts -v',corrected_entry='python -m unittest discover -s tests -p test_step018_embedding_contracts.py -v')
