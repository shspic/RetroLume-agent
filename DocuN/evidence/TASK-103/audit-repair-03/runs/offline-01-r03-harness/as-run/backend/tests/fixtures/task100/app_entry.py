"""实际应用的本卡专用启动器；产品 app/main/监督入口原样使用。"""
from .fixture_runtime import INSTALLED
if not INSTALLED: raise SystemExit('TASK-100 fixture not installed')
import uvicorn
uvicorn.run('app.main:create_app',factory=True,host='127.0.0.1',port=18100,
            loop='app.runtime:psycopg_compatible_loop_factory',log_level='info')
