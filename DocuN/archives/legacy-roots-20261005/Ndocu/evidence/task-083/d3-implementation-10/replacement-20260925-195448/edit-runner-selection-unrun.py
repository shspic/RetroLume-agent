from pathlib import Path
p=Path("Ndocu/evidence/task-083/d3-implementation-10/runner_replacement.py")
s=p.read_text(encoding="utf-8")
a='("migration","ledger","windows","migration,ledger","ledger,windows","migration,windows")'
b='("migration","ledger","windows","migration,ledger","ledger,windows","migration,windows","migration,ledger,windows")'
if s.count(a)!=1: raise RuntimeError(s.count(a))
p.write_text(s.replace(a,b,1),encoding="utf-8")
