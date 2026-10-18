from control import ROOT,event
path=ROOT/'frontend/src/main.tsx';raw=path.read_text(encoding='utf-8')
old='<ActivityWorkspace key={view} token={session?.token ?? ""} variant={view === "interview" ? "interview" : "learning"}/>'
new='<ActivityWorkspace key={view} token={session?.token ?? ""} variant={view === "interview" ? "interview" : "learning"} scopeDraft={scopeDraft}/>'
if raw.count(old)!=1:raise RuntimeError('expected_single_mount')
path.write_text(raw.replace(old,new),encoding='utf-8',newline='\n');event('material_scope_draft_wired')
