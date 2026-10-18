"""仅持有本卡 scratch 的固定字节锁，通过管道明确释放。"""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT/'backend'))
from app.data_exit.files import RootLease
root=ROOT/'DocuN/evidence/TASK-114/synthetic/scratch'
lock=RootLease(root)
with lock.acquire():
    print('LOCKED',flush=True)
    if sys.stdin.buffer.read(1)!=b'x':raise SystemExit(2)
lock.close()
