from pathlib import Path
import json
HERE=Path(__file__).resolve().parent
body=(HERE/'final-stop-check.py').read_text(encoding='utf-8').replace("'final-stop-proof.json'","'entry-root18-stop.json'")
exec(compile(body,str(HERE/'final-stop-check.py'),'exec'),{'__file__':str(HERE/'final-stop-check.py'),'__name__':'__main__'})
from tests.fixtures.task120 import resources as r
print(json.dumps({'available_memory_bytes':r.available_memory(),'min_start_bytes':512*1024**2}))
