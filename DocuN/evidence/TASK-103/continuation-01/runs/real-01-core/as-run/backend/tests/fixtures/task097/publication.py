"""一次发布的不可变观察记录；计数读者不与Windows文件替换竞争。"""
import json, os, secrets
from pathlib import Path

def publish_once(root,name,value):
    root=Path(root);target=root/name
    temp=root/(name+'.'+secrets.token_hex(8)+'.tmp')
    temp.write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf-8')
    # Windows rename拒绝覆盖已存在目标；发布后从不更新，读者无需共享删除权限。
    os.rename(temp,target)
    return target
