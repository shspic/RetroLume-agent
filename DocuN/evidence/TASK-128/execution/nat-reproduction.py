"""回放刚读出的真实身份行，仅证明当前guard拒绝原因；不连接PG。"""
import importlib.util,ipaddress,json
from pathlib import Path
E=Path(__file__).absolute().parent;R=E.parents[3]
s=importlib.util.spec_from_file_location('actual_identity_guard',R/'deploy/initialize_normal.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
row=json.loads((E/'entry-05-ready/fixed-formal-connection.json').read_bytes())['identity']
cfg=json.loads((R/'.runtime/normal-first-install/source/config/install.json').read_bytes())
class ActualReadRow:
    def execute(self,statement):assert statement==m.IDENTITY_QUERY;return self
    def fetchone(self):return row
try:m.observe_identity(ActualReadRow(),cfg);raise AssertionError('expected guard rejection missing')
except m.InstallError as e:assert e.args[0]=='target_identity_mismatch'
try:ipaddress.ip_address(row['server_address']);raise AssertionError('expected parser error missing')
except ValueError:pass
actual=ipaddress.ip_interface(row['server_address'])
record={'actual_read_row_source':'entry-05-ready/fixed-formal-connection.json','expected_fields_equal':{k:row[k]==cfg['target'][k] for k in ('database','database_oid','system_identifier','installer_login')},'actual_server_text':row['server_address'],'actual_is_host_prefix':actual.network.prefixlen==actual.max_prefixlen,'ip_address_rejects_actual_text':True,'original_observe_identity_rejection':'target_identity_mismatch','product_guard_modified':False,'replay_only_no_connection':True}
with (E/'nat-reproduction.json').open('x',encoding='utf-8') as out:json.dump(record,out,indent=2)
print(json.dumps(record))
