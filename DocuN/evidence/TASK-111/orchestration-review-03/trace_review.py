"""编排只读核证。只读文件、字符串字节和精确资源元数据，不导入或运行产品。"""
from pathlib import Path
import base64
import datetime
import hashlib
import json
import re
import shutil
import subprocess

ROOT = Path('D:/shspic/project_NO3_RetroLume-agent')
OUT = Path(__file__).resolve().parent
C02 = ROOT / 'DocuN/evidence/TASK-111/execution/continuation-02'
DELIVERY = C02 / 'PG-increment-01/delivery'

def sha(data):
    return hashlib.sha256(data).hexdigest()

def load(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def save(name, value):
    (OUT/name).write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

def identity(path):
    data = path.read_bytes()
    return {'path':str(path), 'bytes':len(data), 'sha256':sha(data)}

time = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat()
rules = []
for row in load(ROOT/'DocuN/evidence/v4-migration-20260930/rules-snapshot.json'):
    actual = identity(Path(row['absolute_path']))
    rules.append({**actual, 'expected':row['sha256'], 'match':actual['sha256']==row['sha256']})
receipt = load(DELIVERY/'final-delivery-receipt.json')
report = identity(ROOT/'DocuN/results/TASK-111-result.md')
report['receipt_match'] = report['sha256']==receipt['sha256'] and report['bytes']==receipt['bytes']
source_rows = []
for row in load(DELIVERY/'final-source-identity.json'):
    path = ROOT/row['path']
    actual = identity(path)
    source_rows.append({**actual, 'expected':row['sha256'], 'match':actual['sha256']==row['sha256']})

# ECMAScript GetSubstitution 对本例唯一的 $' 作确定字符串推导。
# 没有加载 Node、浏览器、产品 Python 或 JavaScript；这不是运行后 DOM/CSP 证据。
assembly = []
for version in ('v2-01','v2-02','v2-03'):
    context = ROOT/'deploy/preview/build-contexts'/version
    manifest = load(context/'load-manifest.json')
    texts = {n:(context/n).read_bytes().decode('utf-8') for n in ('runtime.cjs','runtime.css','runtime.html','renderer-host.cjs')}
    script, style, template = (texts[n] for n in ('runtime.cjs','runtime.css','runtime.html'))
    tokens = {p:script.count(p) for p in ("$'",'$`','$&','$$')}
    if tokens != {"$'":1,'$`':0,'$&':0,'$$':0}:
        raise ValueError('静态推导的唯一替换符前提发生变化')
    b64 = lambda text:base64.b64encode(hashlib.sha256(text.encode()).digest()).decode()
    policy = "default-src 'none'; script-src 'sha256-"+b64(script)+"'; style-src 'sha256-"+b64(style)+"'; frame-src 'none'; connect-src 'none'; img-src 'none'; font-src 'none'; object-src 'none'; worker-src 'none'; form-action 'none'; base-uri 'none'"
    stage = template.replace('__POLICY__',policy).replace('__STYLE__',style)
    before, after = stage.split('__SCRIPT__')
    broken_script = script.replace("$'", after)
    parsed_first_script = broken_script.split('</script>',1)[0]
    offset = script.index("$'")
    row = {'version':version, 'manifest':identity(context/'load-manifest.json'),
           'source_files':[dict(identity(context/n), declared=manifest['files'][n], match=sha((context/n).read_bytes())==manifest['files'][n]) for n in texts],
           'host_uses_string_replacement':".replace('__SCRIPT__',script)" in texts['renderer-host.cjs'],
           'replacement_tokens':tokens, 'trigger_line':script[:offset].count('\n')+1,
           'trigger_character_offset':offset, 'replacement_tail':after,
           'runtime_bytes':len(script.encode()), 'first_script_bytes_after_HTML_end_tag':len(parsed_first_script.encode()),
           'expected_inline_sha256':sha(script.encode()), 'derived_first_script_sha256':sha(parsed_first_script.encode()),
           'expected_CSP_base64':b64(script), 'derived_first_script_CSP_base64':b64(parsed_first_script),
           'CSP_hash_match':b64(script)==b64(parsed_first_script),
           'first_runtime_truncation_excerpt':broken_script[offset-65:offset+len(after)+65],
           'literal_full_HTML_sha256':sha((before+script+after).encode()),
           'JS_string_replacement_HTML_sha256':sha((before+broken_script+after).encode()),
           'raw_CR_count':script.count('\r'),
           'evidence_level':'B 源字节、规范和确定字符串推导；未运行产品或浏览器'}
    assembly.append(row)
current_host = (ROOT/'deploy/preview/renderer-host.cjs').read_text(encoding='utf-8')
current_bug = ".replace('__SCRIPT__',script)" in current_host
current_wait = 'frame.waitForFunction' in current_host

raw_error = ROOT/'DocuN/evidence/TASK-111/execution/synthetic/http-control/bf1d042c-5ba4-4a35-a62d-e408402e166b/container-stderr.bin'
linked_paths = [
    'DocuN/results/TASK-108-result.md','DocuN/results/TASK-109-result.md',
    'DocuN/results/TASK-110-result.md','DocuN/results/TASK-110-work-decision.md',
    'DocuN/tasks/TASK-111.md','backend/app/preview/compiler.py',
    'backend/app/preview/host_policy.py','backend/migrations/012_html_explanations.sql',
    'backend/tests/fixtures/task111/offline.py','frontend/tests/task111/offline.cjs',
    'backend/tests/fixtures/task111/c02_faults.py','backend/tests/fixtures/task111/c02_coordinator.py',
    'DocuN/evidence/TASK-111/execution/continuation-02/root-08/production-build.json',
    'DocuN/evidence/TASK-111/execution/continuation-02/root-08/attempt-15/production-build.json',
    'DocuN/evidence/TASK-111/execution/continuation-02/root-08/attempt-17/hook-result.json',
    'DocuN/evidence/TASK-111/execution/continuation-02/root-08/attempt-19/upgrade-result.json',
    'DocuN/evidence/TASK-111/execution/continuation-02/root-08/attempt-19/fault-result.json',
    'DocuN/evidence/TASK-111/execution/continuation-02/PG-increment-01/authority-receipt.json',
    'DocuN/evidence/TASK-111/execution/continuation-02/PG-increment-01/remaining-hard-cap-conflict.json',
]
findings = {'at':time, 'scope':'编排复盘；不是执行层测试、独立审计或G11验收',
            'report':report, 'rules':rules, 'returned_source_count':len(source_rows),
            'returned_sources':source_rows, 'linked_facts':[identity(ROOT/p) for p in linked_paths],
            'assembly_derivations':assembly, 'current_host':identity(ROOT/'deploy/preview/renderer-host.cjs'),
            'current_has_same_defect':current_bug, 'current_has_unbuilt_wait_candidate':current_wait,
            'as_run_error_file':identity(raw_error), 'as_run_error':raw_error.read_text(encoding='utf-8'),
            'standards':[
              'https://tc39.es/ecma262/multipage/text-processing.html#sec-getsubstitution',
              'https://html.spec.whatwg.org/multipage/parsing.html#script-data-end-tag-name-state',
              'https://www.w3.org/TR/CSP3/#match-element-to-source-list'],
            'product_commands_executed':0, 'product_files_written':0,
            'runtime_claim':'现成A类日志为undefined；B类证明宿主必定损坏脚本。不宣称已采得当次浏览器CSP拒绝日志或修后PASS。'}
save('review-evidence.json', findings)

# 只对精确归属对象读取停止元数据；不启动、不停止、不恢复任何对象，不输出 Env。
docker = shutil.which('docker')
resources=[]
names=['1791a2d086228c618bf043b0565e215828ff0ccfe5a858486488f1329a16ef51',
       'retrolume-task-111-g11-preview-03','retrolume-task-111-g11-preview-14']
for name in names:
    try:
        p=subprocess.run([docker,'container','inspect',name],capture_output=True,timeout=10,
                         creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
        if p.returncode:
            resources.append({'object':name,'returncode':p.returncode,'state':'未核实，不根据错误推断已停'})
            continue
        item=json.loads(p.stdout)[0]; st=item['State']
        resources.append({'object':name,'id':item['Id'],'name':item['Name'],'image':item['Image'],
                          'running':st['Running'],'pid':st['Pid'],'status':st['Status'],
                          'restarting':st['Restarting'],'restart_count':item['RestartCount']})
    except Exception as error:
        resources.append({'object':name,'error_type':type(error).__name__,'state':'未核实'})
save('resource-metadata.json',{'at':time,'read_only':True,'objects':resources,
                              'limit':'当前停止元数据，不是完整renderer工作树停止或退款证明'})
print(json.dumps({'report_match':report['receipt_match'],'rule_matches':sum(r['match'] for r in rules),
                  'source_matches':sum(r['match'] for r in source_rows),'source_total':len(source_rows),
                  'defect_in_versions':[r['version'] for r in assembly if r['host_uses_string_replacement']],
                  'script_bytes':[assembly[0]['runtime_bytes'],assembly[0]['first_script_bytes_after_HTML_end_tag']],
                  'current_bug':current_bug,'resources':resources},ensure_ascii=False))
