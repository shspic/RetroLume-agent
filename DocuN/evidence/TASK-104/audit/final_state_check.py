from metadata import *
import subprocess
# 最后仅做元数据状态与字节检查，运行许可不恢复。
index=load(ROOT/'DocuN/evidence/TASK-104/orchestration-setup-20261007/audit-input.json')
checks=[]
postroot=ROOT/'DocuN/evidence/TASK-103/continuation-02/final/post'
for rel,expected in index['current_files'].items():
    current=sha(ROOT/rel);old=sha(postroot/rel)
    checks.append({'path':rel,'sha256':current,'expected':expected,'post_sha256':old,'match':current==expected==old})
for group in ('protected_files','rules_and_contracts','goal_contracts'):
    for item in index[group]:
        path=Path(item['path']);path=path if path.is_absolute() else ROOT/path
        checks.append({'path':str(path),'sha256':sha(path),'expected':item['sha256'],'match':sha(path)==item['sha256']})
assert len(checks)==325 and all(x['match'] for x in checks)
save('final-identity-check.json',{'at':stamp(),'rows':325,'match':325,'checks':checks,'product_changed_by_audit':False})
ids=['4889202d9a58c622fb7cd2bd3087e5bceb7ad20a049c6550f4bd3588ff66ac11','f96ac8dcb64648c76a2bc70f3f8b75969ada0ea0ea69b5896fe5ecb71affab85','4b813f9e4317aef9c613eb140fcb2d40c55a6bd98ee5d79807ea5851975d7f68']
containers=[]
for cid in ids:
    value=json.loads(subprocess.run(['docker','inspect',cid],capture_output=True,text=True,encoding='utf-8',timeout=15,check=True).stdout)[0]
    containers.append({'cid':value['Id'],'name':value['Name'],'running':value['State']['Running'],'pid':value['State']['Pid'],'exit_code':value['State']['ExitCode'],'image':value['Image'],'mounts':[{'Type':x['Type'],'Name':x.get('Name'),'Destination':x['Destination']} for x in value['Mounts']]})
assert all(not x['running'] and x['pid']==0 for x in containers)
script="$taskLive=@(Get-CimInstance Win32_Process | Where-Object { ($_.Name -eq 'python.exe' -or $_.Name -eq 'node.exe' -or $_.Name -eq 'chrome.exe') -and ($_.CommandLine -like '*-m tests.fixtures.task104*' -or $_.CommandLine -like '*task104-citation-audit.cjs*' -or $_.CommandLine -like '*TASK-104*browser-profile*') }); @($taskLive | ForEach-Object {[pscustomobject]@{pid=$_.ProcessId;created=$_.CreationDate.ToUniversalTime().ToString('o');command=$_.CommandLine}})|ConvertTo-Json -Compress"
stdout=subprocess.run(['powershell.exe','-NoProfile','-Command',script],capture_output=True,text=True,encoding='utf-8',timeout=15,check=True).stdout.strip()
alive=json.loads(stdout) if stdout else []
assert not alive
import socket
ports={}
for port in (18103,18104,55443,55444,55445):
    with socket.socket() as connection:ports[str(port)]=connection.connect_ex(('127.0.0.1',port))!=0
assert all(ports.values())
save('final-readonly-resource-state.json',{'at':stamp(),'containers':containers,'owned_processes_alive':alive,'ports_available':ports,'inspection_only':True,'did_not_connect_pg2_pg3':True,'preserved_all_container_volume_database_role_profile_data':True})
finish('final-byte-and-owned-resource-state',{'identity_matches':325,'complete_posts':291,'containers_stopped':3,'alive_owned_processes':0,'ports_available':ports,'new_run':False})
