import importlib.util,json
from pathlib import Path
E=Path(__file__).absolute().parent
s=importlib.util.spec_from_file_location('stop128',E/'win-support.py');w=importlib.util.module_from_spec(s);s.loader.exec_module(w)
state=json.loads((E/'checkpoint.json').read_bytes());interval=state['api_intervals'][-1]
rows=[]
for old in interval.get('processes',[]):
    try:
        current=w.ProcessRef(old['pid'])
        rows.append({'pid':old['pid'],'expected_birth':old['birth'],'current_birth':current.birth,'same_birth':current.birth==old['birth'],'alive':current.alive()})
        current.close()
    except OSError as error:rows.append({'pid':old['pid'],'expected_birth':old['birth'],'open_error_code':error.errno,'already_absent':error.errno==87})
record={'recorded_interval':interval,'current_process_observations':rows,'port_owners':w.port_owners({state['api_port']}),'no_stop_or_restart_performed':True}
with (E/'api-stop-diagnosis.json').open('x',encoding='utf-8') as out:json.dump(record,out,indent=2)
print(json.dumps(record))
