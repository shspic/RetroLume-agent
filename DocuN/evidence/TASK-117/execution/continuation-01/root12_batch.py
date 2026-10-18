"""原已提交教学不重放：fixture重型trace对照后的单次未完成步骤复检。"""
from root11_batch import *

if __name__=='__main__':
    try:main(12)
    except BaseException as exc:
        c.failure('S02-ROOT12',type(exc).__name__+':'+str(exc)[:300],effect='保留root11 UNKNOWN及预留；该依赖再未知则不再换键尝试。原有界资源精确清场。')
        (C01/('root12-error-'+str(time.time_ns())+'.txt')).write_text(traceback.format_exc(),encoding='utf-8');raise
