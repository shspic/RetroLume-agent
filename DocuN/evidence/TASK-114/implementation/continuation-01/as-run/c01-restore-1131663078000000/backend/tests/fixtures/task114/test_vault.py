"""真实 DPAPI 往返与控制文件权限设置，仅用随机合成值。"""
import json,secrets,sys
from budget import ROOT,CONTROL
sys.path.insert(0,str(ROOT/'backend'))
from app.data_exit.control import ControlHub,CredentialVault
from app.data_exit.files import private_file
hub=ControlHub(ROOT/'DocuN/evidence/TASK-114/synthetic/control-root')
vault=CredentialVault(hub)
marker=secrets.token_urlsafe(32)
reference=vault.save({'synthetic_marker':marker})
assert vault.read(reference)=={'synthetic_marker':marker}
data=hub.read_artifact('credentials',reference['id'],reference['sha256'])
assert marker.encode() not in data
private_file(hub.path)
result={'roundtrip':True,'plaintext_absent':True,'private_acl_applied':True,'credential_ref':reference}
(CONTROL/'dpapi-result.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k!='credential_ref'}))
