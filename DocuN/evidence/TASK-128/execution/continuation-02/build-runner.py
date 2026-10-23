import ast
from pathlib import Path
E=Path(__file__).absolute().parent
p=E/'run-six.py';s=p.read_text(encoding='utf-8')
s=s.replace('orchestration-continuation01-20261023','orchestration-continuation02-20261023')
s=s.replace('(E.parent / "checkpoint.json")','(E.parent / "continuation-01/checkpoint.json")')
s=s.replace('            self.state["checks"] = {}','            self.state["checks"] = dict(self.state["checks"])')
s=s.replace('self.state["entries"] < 7','self.state["entries"] < 8')
s=s.replace('self.preparation_conservative_seconds = 7800','self.preparation_conservative_seconds = 8700')
s=s.replace('(5 if slot == "source" else 2)','(7 if slot == "source" else 3)')
s=s.replace('"task128-c01-" + name','"task128-c02-" + name')
s=s.replace('    def guard(self, *, startup=False):','    def guard(self, *, startup=False, purpose="resource"):\n        if startup:self.wait_capacity(purpose)\n')
s=s.replace('            require(WIN.available_mib() >= 512, "startup_memory_below512")','            require(WIN.available_mib() >= 512, "startup_memory_changed_after_wait")')
a=s.index('    def command(self,')
s=s[:a]+'''    def wait_capacity(self, purpose):
        self.state["capacity_checks"] = self.state.get("capacity_checks",0)+1
        number=self.state["capacity_checks"]
        started=time.monotonic();samples=[]
        while True:
            self.guard()
            value=WIN.available_mib();elapsed=time.monotonic()-started
            samples.append({"utc":utc(),"available_mib":value,"elapsed_seconds":elapsed})
            if value>=512:
                self.evidence("capacity-"+str(number)+".json",{"purpose":purpose,"ready":True,"samples":samples});return
            if elapsed>=90:
                self.evidence("capacity-"+str(number)+".json",{"purpose":purpose,"ready":False,"samples":samples})
                raise RuntimeError("capacity_below512_after90_seconds")
            self.done.wait(min(2,90-elapsed))

'''+s[a:]
s=s.replace('self.guard(startup=True)\n        require(not any','self.guard(startup=True, purpose="PG:"+slot)\n        require(not any')
s=s.replace('self.guard(startup=True)\n        require(self.state["api_starts"]','self.guard(startup=True, purpose="API")\n        require(self.state["api_starts"]')
s=s.replace('        self.guard()\n        home = PRIVATE / slot\n        config = config or', '        self.guard()\n        require(slot != "source" or action == "verify", "source_apply_forbidden")\n        home = PRIVATE / slot\n        config = config or')
# verify and first API share one PG lifecycle.
a=s.index('    def check6(self):');b=s.index('    def run_all(self):',a)
part=s[a:b].replace('        self.stop_pg("source")\n','')
s=s[:a]+part+s[b:]
# Capture actual descendants even when no successful session could be read.
s=s.replace('        finally:\n            if process.poll() is None:', '''        finally:
            if process.poll() is None:
                seen={ref.pid for ref in self.api_refs}
                for pid in WIN.descendants(process.pid):
                    if pid not in seen:
                        try:self.api_refs.append(WIN.ProcessRef(pid))
                        except OSError:pass
            if process.poll() is None:''')
# Preflight the real interrupted target before the unique planned injection.
s=s.replace('        require(not self.state["slots"]["interrupted"].get("install_attempted"), "interrupted_injection_no_replay")', '''        require(not self.state["slots"]["interrupted"].get("install_attempted"), "interrupted_injection_no_replay")
        spec=importlib.util.spec_from_file_location("c02_actual_install",ROOT / "deploy/initialize_normal.py")
        install=importlib.util.module_from_spec(spec);spec.loader.exec_module(install)
        config=json.loads((PRIVATE / "interrupted/config/install.json").read_bytes())
        with install.connect(config,self.secrets_for("interrupted")) as connection:
            observed=install.preflight(connection,config)
        self.evidence("interrupted-correct-empty-preflight.json",{"passed":True,"observed":observed})''')
a=s.index('    def run_all(self):');b=s.index('\n\ndef main():',a)
s=s[:a]+'''    def run_all(self):
        thread=threading.Thread(target=self.memory_watch,daemon=True);thread.start()
        def stage(key,action):
            if self.state["checks"].get(key,{}).get("status")=="passed":return True
            self.state["checks"][key]={"status":"started","utc":utc()};self.save()
            try:
                action();self.state["checks"][key]={"status":"passed","utc":utc()};self.save();return True
            except BaseException as error:
                self.state["checks"][key]={"status":"failed","error_type":type(error).__name__,"reason":str(error) if isinstance(error,RuntimeError) else "redacted_nonruntime","utc":utc()}
                self.evidence("stage-"+key+"-failure.json",self.state["checks"][key]);self.save();return False
        try:
            self.guard()
            for slot in self.state["slots"]:
                self.configure_slot(slot);projection=self.inspect(slot);target=self.state["slots"][slot]
                require(not projection["state"]["Running"],"preexisting_running_resource")
                require(projection["created"]==target["created_projection"]["created"] and projection["mounts"]==target["created_projection"]["mounts"] and projection["limits"]==target["created_projection"]["limits"],"created_identity_or_limits_changed")
                require([WIN.file_identity(Path(row["path"])) for row in target["roots"]]==target["roots"],"root_entity_changed")
                for kind,identity,expected,keys in (("volume",SLOTS[slot]["volume"],target["volume"],("Name","CreatedAt","Driver","Labels")),("network",target["network_id"],target["network"],("Name","Id","Created","Driver","Labels"))):
                    actual=self.docker_json([kind,"inspect",identity])[0]
                    require(all(actual.get(k)==expected.get(k) for k in keys),"volume_or_network_changed")
                self.evidence(slot+"-pre-reuse-identity.json",projection)
            receipt=Path(self.state["slots"]["source"]["successful_receipt"])
            require(digest(receipt.read_bytes())=="a2211aa56f0497ef55e2ff42f4ea2e6b3b50bb3049cca62cbd5ef06844df6f06","source_receipt_drift")
            # Fifth item is independent and remains unique even on a resumed entry.
            stage("5",self.check5)
            if self.state["slots"]["interrupted"].get("holding"):self.stop_pg("interrupted")
            self.start_pg("source")
            stage("6",self.check6)
            if stage("api1",lambda:self.api_once(1)):
                self.state["source_after_first_api"]={"facts":self.database_facts("source"),"control_id":self.state["slots"]["source"]["control_id"]};self.save()
                self.stop_pg("source")
                self.start_pg("source")
                require(self.database_facts("source")==self.state["source_after_first_api"]["facts"],"source_data_changed_across_pg_restart")
                if stage("api2",lambda:self.api_once(2)):
                    self.state["checks"]["4"]={"status":"passed","utc":utc(),"actual_pg_stop_and_restart":True};self.save()
        finally:
            self.done.set()
            for slot in self.state["slots"]:
                try:self.stop_pg(slot)
                except Exception as error:self.state["stop_unknown"]=type(error).__name__
            thread.join(timeout=5)
            self.state["last_entry"].update(status="returned",finished=utc(),controller_wall_seconds=time.monotonic()-self.entry_clock);self.save()
'''+s[b:]
ast.parse(s);p.write_text(s,encoding='utf-8')
obs=E/'install-observer.py';s=obs.read_text(encoding='utf-8');s=s.replace('    args = parser.parse_args()','    args = parser.parse_args()\n    if args.slot == "source" and args.action != "verify":raise SystemExit("source_apply_forbidden")');ast.parse(s);obs.write_text(s,encoding='utf-8')
for path in (E/'run-six.py',obs,E/'win-support.py'):ast.parse(path.read_bytes())
print('Prepared: inherited checks1/2/3; interrupted unique apply; source verify only; two API cycles across PG stop/start; 90s unchanged memory gate.')
