"""只有本卡显式合成env才加载有限传输，产品默认路径不会包含此目录。"""
import os,sys
if (os.environ.get('RETROLUME_TASK117_SYNTHETIC') in ('TASK-117-STEP018-INTEGRATION-S01-20261014','TASK-117-STEP018-INTEGRATION-S02-20261015','TASK-117-STEP018-INTEGRATION-S03-20261015','TASK-117-STEP018-INTEGRATION-S04-20261016','TASK-117-STEP018-INTEGRATION-S05-20261016')
        and 'app.pdf_import.worker' not in sys.orig_argv):
    from runtime_fixture import install
    install()
