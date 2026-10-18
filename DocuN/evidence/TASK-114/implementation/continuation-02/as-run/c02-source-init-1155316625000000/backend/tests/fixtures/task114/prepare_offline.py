"""创建本卡固定工作根和保存早期工具观察，不占用真实容器。"""
import json
import os
from pathlib import Path
import sys
from budget import Budget,ROOT,CONTROL


def main():
    budget=Budget()
    early=CONTROL/'early-observations.json'
    if not early.exists():
        observations={'说明':'早期未逐进程计时，按工具总等待上界保守计入离线；原错误不丢弃',
                      'offline_conservative_seconds':15,'failures':['生成器正则量词错误，已改为完整类型匹配','CRLF 定向匹配未命中，已仅规范生成器输入换行','restore profile 条件缺括号，已修正','cmd 以斜杠相对路径不能启动，改用 node 直接执行项目内编译器'],
                      'real_resources_before_this_step':0}
        early.write_text(json.dumps(observations,ensure_ascii=False,indent=2),encoding='utf-8')
        value=budget.load();value['offline_seconds']+=15;budget.save(value)
    parent=ROOT/'DocuN/evidence/TASK-114/synthetic'
    for name in ('source-root','backup-root','restore-root','control-root','scratch','sentinel-root'):
        root=parent/name
        if not root.exists():
            budget.reserve('real_roots');root.mkdir(parents=True)
            (root/'.task114-root.json').write_text(json.dumps({'TASK':'TASK-114','purpose':name},ensure_ascii=False),encoding='utf-8')
    # 离线日志为额外实际控制根，先占次数，测试原件不删除。
    if not (parent/'scratch/offline-control').exists():budget.reserve('real_roots')
    os.environ['RETROLUME_TASK114_SCRATCH']=str(parent/'scratch')
    return budget.offline('offline-boundaries-01',[str(ROOT/'backend/.venv/Scripts/python.exe'),'-X','utf8',str(ROOT/'backend/tests/test_data_exit_offline.py')])


if __name__=='__main__':raise SystemExit(main())
