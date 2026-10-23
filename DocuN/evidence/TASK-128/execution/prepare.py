import ast, datetime, hashlib, json
from pathlib import Path
E=Path(__file__).absolute().parent
R=E.parents[3]
sha=lambda b:hashlib.sha256(b).hexdigest()
m=json.loads((E.parent/'orchestration-20261023/input-manifest.json').read_bytes())
def rows(x):
    if isinstance(x,dict):
        if 'sha256' in x and ('absolute_path' in x or 'path' in x):yield x
        for v in x.values():yield from rows(v)
    elif isinstance(x,list):
        for v in x:yield from rows(v)
checks=[]
for v in rows(m):
    p=Path(v.get('absolute_path',v.get('path')))
    if not p.is_absolute():p=R/p
    assert p.is_file(),str(p)
    checks.append({'path':str(p),'sha256':sha(p.read_bytes()),'match':sha(p.read_bytes())==v['sha256']})
assert all(v['match'] for v in checks)
for name in ('deploy/initialize_normal.py','backend/tests/test_normal_install.py','README.md','deploy/normal-install.md'):
    p=E/'pre'/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((R/name).read_bytes())
(E/'pre-snapshot.json').write_text(json.dumps({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'inputs':checks},indent=2),encoding='utf-8')
s=(E/'run-six.py').read_text(encoding='utf-8')
s=s.replace('"TASK": "TASK-127", "R": "R-121", "entries": 1','"TASK": "TASK-128", "R": "R-122", "entries": 3')
a=s.index('        self.state = json.loads(');b=s.index('        self.entry =',a)
s=s[:a]+'''        if self.path.exists():self.state = json.loads(self.path.read_bytes())
        else:
            self.state = json.loads((ROOT / "DocuN/evidence/TASK-127/execution/final-checkpoint.json").read_bytes())
            self.state.update(TASK="TASK-128", R="R-122", inherited_checks=self.state["checks"], checks={})
            for slot in self.state["slots"].values():slot["install_attempted"] = False
        require(self.state["entries"] < 6, "combined_entry_cap")
        self.state["entries"] += 1
'''+s[b:]
s=s.replace('4200','4800').replace('< 9900','< 9900')
s=s.replace('for row in manifest["sources"]:', 'for row in manifest["product_baseline"]:')
s=s.replace('len(manifest["sources"])','len(manifest["product_baseline"])')
# Creation is structurally unavailable in this card.
a=s.index('        definition = SLOTS[slot]',s.index('    def configure_slot'));b=s.index('    def pg_kwargs',a)
s=s[:a]+'        raise RuntimeError("TASK128_creation_prohibited")\n\n'+s[b:]
s=s.replace('                if number == 5:', '                if number == 5:')
s=s.replace('            self.api_once(index)\n            self.stop_pg("source")','            self.api_once(index)\n        self.stop_pg("source")')
# Fresh receipt names stay in the same approved private roots and never overwrite 127.
s=s.replace('(name + ".jsonl")','("task128-" + name + ".jsonl")')
s=s.replace('("wrong-" + key + ".json")','("task128-wrong-" + key + ".json")')
(E/'run-six.py').write_text(s,encoding='utf-8')
for name in ('run-six.py','install-observer.py','win-support.py'):ast.parse((E/name).read_bytes())
print(json.dumps({'input_count':len(checks),'all_match':True,'controller_prepared':True}))
