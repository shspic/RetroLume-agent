from pathlib import Path
p=Path("backend/tests/fixtures/task083/d3_pg_windows.py")
s=p.read_text(encoding="utf-8")
a="except psycopg.CheckViolation:"
b="except psycopg.errors.CheckViolation:"
if s.count(a)!=1: raise RuntimeError(s.count(a))
p.write_text(s.replace(a,b,1),encoding="utf-8")
