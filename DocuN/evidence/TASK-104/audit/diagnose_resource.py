from metadata import *
import subprocess
ids=['4889202d9a58c622fb7cd2bd3087e5bceb7ad20a049c6550f4bd3588ff66ac11','f96ac8dcb64648c76a2bc70f3f8b75969ada0ea0ea69b5896fe5ecb71affab85','4b813f9e4317aef9c613eb140fcb2d40c55a6bd98ee5d79807ea5851975d7f68']
items=[]
for cid in ids:
    result=subprocess.run(['docker','inspect',cid],capture_output=True,text=True,encoding='utf-8',timeout=15)
    assert result.returncode==0
    v=json.loads(result.stdout)[0]
    items.append({'cid':v['Id'],'name':v['Name'],'image':v['Image'],'state':{k:v['State'][k] for k in ('Running','Pid','ExitCode')},'labels':v['Config'].get('Labels'),'mounts':v['Mounts'],'limits':{k:v['HostConfig'].get(k) for k in ('NanoCpus','Memory','PidsLimit','Privileged','Binds','RestartPolicy','PortBindings')}})
save('root-01-resource-diagnostic.json',{'at':stamp(),'containers':items,'whole_env_not_printed_or_saved':True,'root1_attempt_retained':True})
for v in items:print(json.dumps(v,ensure_ascii=False))
finish('root01-failed-resource-predicate-diagnosis',{'inspection_only':True,'new_starts':0})
