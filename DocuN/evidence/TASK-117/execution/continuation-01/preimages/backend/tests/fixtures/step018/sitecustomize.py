"""只有本卡显式合成env才加载有限传输，产品默认路径不会包含此目录。"""
import os
if os.environ.get('RETROLUME_TASK117_SYNTHETIC')=='TASK-117-STEP018-INTEGRATION-S01-20261014':
    from runtime_fixture import install
    install()
