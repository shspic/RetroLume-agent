import ast,hashlib,json
from pathlib import Path
E=Path(__file__).absolute().parent;R=E.parents[4]
p=E/'run-six.py';s=p.read_text(encoding='utf-8')
s=s.replace('E.parent / "orchestration-20261023/permit.json"','E.parents[1] / "orchestration-continuation01-20261023/permit.json"')
a=s.index('        if self.path.exists():');b=s.index('        self.redactions,',a)
s=s[:a]+'''        if self.path.exists():self.state = json.loads(self.path.read_bytes())
        else:
            self.state = json.loads((E.parent / "checkpoint.json").read_bytes())
            self.state["previous_checks"] = self.state["checks"]
            self.state["checks"] = {}
        require(self.state["entries"] < 7, "combined_entry_cap")
        self.state["entries"] += 1
        self.entry = self.state["entries"]
        self.entry_clock = time.monotonic()
        self.preparation_conservative_seconds = 7800
        self.run = E / ("entry-" + str(self.entry).zfill(2))
        self.run.mkdir(exist_ok=False)
'''+s[b:]
a=s.index('        manifest =',s.index('    def freeze'));b=s.index('    def guard',a)
s=s[:a]+'''        inputs = json.loads((E / "final-run-inputs.json").read_bytes())
        for row in inputs:
            require(digest(Path(row["path"]).read_bytes()) == row["sha256"], "frozen_input_drift")
        self.evidence("as-run.json", {"helpers": rows, "inputs": inputs, "observed": utc()})

'''+s[b:]
s=s.replace('(4 if slot == "source" else 2)','(5 if slot == "source" else 2)')
s=s.replace('"task128-" + name','"task128-c01-" + name').replace('"task128-wrong-"','"task128-c01-wrong-"')
a=s.index('    def run_all(self):');b=s.index('\n\ndef main():',a)
s=s[:a]+'''    def run_all(self):
        thread = threading.Thread(target=self.memory_watch, daemon=True); thread.start()
        def stage(key, action):
            if self.state["checks"].get(key, {}).get("status") == "passed":return True
            self.state["checks"][key] = {"status":"started", "utc":utc()};self.save()
            try:
                action()
                self.state["checks"][key] = {"status":"passed", "utc":utc()};self.save();return True
            except BaseException as error:
                self.state["checks"][key] = {"status":"failed", "error_type":type(error).__name__, "reason":str(error) if isinstance(error, RuntimeError) else "redacted_nonruntime", "utc":utc()}
                self.evidence("stage-"+key+"-failure.json",self.state["checks"][key]);self.save();return False
        def initial_preflight():
            spec = importlib.util.spec_from_file_location("real_c01_install",ROOT / "deploy/initialize_normal.py")
            install = importlib.util.module_from_spec(spec);spec.loader.exec_module(install)
            config=json.loads((PRIVATE / "source/config/install.json").read_bytes())
            with install.connect(config,self.secrets_for("source")) as connection:
                observed=install.preflight(connection,config)
            self.evidence("correct-empty-preflight.json",{"passed":True,"observed":observed})
        try:
            self.guard()
            for slot in self.state["slots"]:
                self.configure_slot(slot)
                projected=self.inspect(slot)
                require(not projected["state"]["Running"], "preexisting_running_resource")
                require(projected["created"]==self.state["slots"][slot]["created_projection"]["created"],"creation_changed")
                require(projected["mounts"]==self.state["slots"][slot]["created_projection"]["mounts"] and projected["limits"]==self.state["slots"][slot]["created_projection"]["limits"],"limits_or_mount_changed")
                require([WIN.file_identity(Path(r["path"])) for r in self.state["slots"][slot]["roots"]]==self.state["slots"][slot]["roots"],"root_entity_changed")
                for kind,identity,expected,keys in (("volume",SLOTS[slot]["volume"],self.state["slots"][slot]["volume"],("Name","CreatedAt","Driver","Labels")),("network",self.state["slots"][slot]["network_id"],self.state["slots"][slot]["network"],("Name","Id","Created","Driver","Labels"))):
                    actual=self.docker_json([kind,"inspect",identity])[0]
                    require(all(actual.get(k)==expected.get(k) for k in keys),"volume_or_network_changed")
                self.evidence(slot+"-pre-reuse-identity.json",projected)
            # A：正确预检、四拒绝、成功安装、角色、首API，同一源启动。
            self.start_pg("source")
            okay=stage("preflight",initial_preflight)
            for key,action in (("1",self.check1),("2",self.check2),("3",self.check3),("api1",lambda:self.api_once(1))):
                if okay:okay=stage(key,action)
            if okay:
                self.state["source_after_A"]={"database":self.database_facts("source"),"identity":self.state["slots"]["source"]["database_identity"],"control_id":self.state["slots"]["source"].get("control_id")};self.save()
            self.stop_pg("source")
            # B：独立唯一注入；A的失败不伪造此项结果。
            stage("5",self.check5)
            if self.state["slots"]["interrupted"].get("holding"):self.stop_pg("interrupted")
            # C：真实PG重开后第二API及只读verify；成功安装不重放。
            if okay:
                self.start_pg("source")
                require(self.database_facts("source")==self.state["source_after_A"]["database"],"source_changed_across_pg_restart")
                if stage("api2",lambda:self.api_once(2)):
                    self.state["checks"]["4"]={"status":"passed","utc":utc(),"two_api_cycles_across_pg_restart":True};self.save()
                stage("6",self.check6)
        finally:
            self.done.set()
            for slot in self.state["slots"]:
                try:self.stop_pg(slot)
                except Exception as error:self.state["stop_unknown"] = type(error).__name__
            thread.join(timeout=5)
            self.state["last_entry"].update(status="returned",finished=utc(),controller_wall_seconds=time.monotonic()-self.entry_clock)
            self.save()
'''+s[b:]
ast.parse(s);p.write_text(s,encoding='utf-8')
obs=E/'install-observer.py';s=obs.read_text(encoding='utf-8')
s=s.replace('        inner_cursor = self.inner.execute(statement, params, **kwargs)', '''        try:
            inner_cursor = self.inner.execute(statement, params, **kwargs)
        except BaseException as error:
            values=[v for k,v in os.environ.items() if k.startswith("RETROLUME_NORMAL_")]
            self.observer.event("real_execute_failed",stage=stage,**safe_diagnostic(error,values))
            raise''')
ast.parse(s);obs.write_text(s,encoding='utf-8')
pre=json.loads((E/'pre-snapshot.json').read_bytes())['inputs'];rows=[]
allowed={str(R/'deploy/initialize_normal.py'),str(R/'backend/tests/test_normal_install.py')}
for row in pre:
    path=Path(row['path']);value=hashlib.sha256(path.read_bytes()).hexdigest()
    assert str(path) in allowed or value==row['sha256'],str(path)
    rows.append({'path':str(path),'sha256':value,'baseline_sha256':row['sha256'],'allowed_changed':str(path) in allowed})
with (E/'final-run-inputs.json').open('x',encoding='utf-8') as out:json.dump(rows,out,indent=2)
for path in (E/'run-six.py',E/'install-observer.py',E/'win-support.py'):ast.parse(path.read_bytes())
print(json.dumps({'frozen_inputs':len(rows),'three_stages':'A source4 / B interrupted2 / C source5','source_cap':5,'entry_cap':7,'new_resources':0}))
