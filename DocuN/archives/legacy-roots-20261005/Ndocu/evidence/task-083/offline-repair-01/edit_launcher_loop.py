"""Use the repository's Windows psycopg event-loop factory in the dedicated SUP."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
path = ROOT / "backend/app/worker/launcher.py"
data = path.read_text(encoding="utf-8")
old_import = "from app.activities import PostgresAdmissionLedger\n"
new_import = "from app.activities import PostgresAdmissionLedger\nfrom app.runtime import psycopg_compatible_loop_factory\n"
assert data.count(old_import) == 1
data = data.replace(old_import, new_import)
old = '''        outcome = asyncio.run(SingleWindowSupervisor(ledger, config).run_once(
            activity_id, executor_id, command,
            run_tag=run_tag, manager_deadline_ns=deadline_ns,
        ))
'''
new = '''        with asyncio.Runner(loop_factory=psycopg_compatible_loop_factory) as runner:
            outcome = runner.run(SingleWindowSupervisor(ledger, config).run_once(
                activity_id, executor_id, command,
                run_tag=run_tag, manager_deadline_ns=deadline_ns,
            ))
'''
assert data.count(old) == 1
path.write_text(data.replace(old, new), encoding="utf-8", newline="")
