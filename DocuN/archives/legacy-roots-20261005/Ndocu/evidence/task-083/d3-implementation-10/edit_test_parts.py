from pathlib import Path
p=Path("backend/tests/fixtures/task083/d3_pg_windows.py"); s=p.read_text(encoding="utf-8")
a='def main():\n    migration_cases()\n    ledger_cases()\n    windows_case()\n    emit({"phase":"complete","all_pass":True})'
b='def main():\n    parts=set(os.environ.get("D3_PARTS","migration,ledger,windows").split(","))\n    if not parts or not parts <= {"migration","ledger","windows"}:\n        raise ValueError("invalid D3 part selection")\n    if "migration" in parts: migration_cases()\n    if "ledger" in parts: ledger_cases()\n    if "windows" in parts: windows_case()\n    emit({"phase":"complete","all_pass":True,"parts":sorted(parts)})'
if s.count(a)!=1: raise RuntimeError(s.count(a))
p.write_text(s.replace(a,b,1),encoding="utf-8")
