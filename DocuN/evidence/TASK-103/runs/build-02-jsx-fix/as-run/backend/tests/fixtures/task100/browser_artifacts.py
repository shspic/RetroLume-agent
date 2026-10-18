"""核已保存的原生浏览器末屏；不启动浏览器、HTTP、PG或任何产品进程。"""
from __future__ import annotations
import hashlib
import json
from html.parser import HTMLParser
from .control import EVIDENCE,ROOT,atomic_json,utc

BATCH='2026-10-05T041623.670843-0000-main-combo'

class Document(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True);self.text=[];self.scripts=[]
    def handle_starttag(self,tag,attrs):
        if tag=='script':self.scripts.append(dict(attrs))
    def handle_data(self,data):self.text.append(data)

def main():
    batch=EVIDENCE/BATCH;directory=batch/'browser-controls'
    facts=json.loads((directory/'facts.json').read_text(encoding='utf-8'))
    timeline=json.loads((directory/'timeline.json').read_text(encoding='utf-8'))
    source=EVIDENCE/'post-browser-fix/pre/frontend/tests/task100-browser.cjs'
    asrun=json.loads((batch/'as-run-files.json').read_text(encoding='utf-8'))
    assert hashlib.sha256(source.read_bytes()).hexdigest()==asrun['frontend/tests/task100-browser.cjs']
    assert facts['status']=='fail' and 'remainingControls' in facts['error']
    assert len(facts['controls'])==10 and all(c['status']=='pass' for c in facts['controls'])
    receipt=[r for r in timeline if r.get('kind')=='actual_command_receipt']
    posts=[r for r in timeline if r.get('kind')=='request' and r.get('method')=='POST' and '/teaching/commands' in r['url']]
    assert len(receipt)==len(posts)==1
    receipt=receipt[0];request=receipt['body'];saved=receipt['receipt']
    assert saved['status']=='committed' and saved['action']==request['action']=='correct'
    assert saved['model_called'] is False and saved['tool_called'] is False and saved['operation_id'] is None
    canonical={k:request[k] for k in ('action','expected_revision','expected_goal_version','expected_scope_revision','body')}
    canonical['activity_id']=saved['activity_id']
    digest=hashlib.sha256(json.dumps(canonical,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    assert digest==saved['request_sha256']
    html=(directory/'failure-dom.html').read_text(encoding='utf-8');document=Document();document.feed(html)
    correction=request['body']['text']
    assert correction in ''.join(document.text)
    assert html.count('&lt;script&gt;window.__task100Executed=true&lt;/script&gt;')>=2
    assert document.scripts and all(s.get('src') for s in document.scripts)
    assert not [r for r in timeline if r.get('kind')=='pageerror']
    assert str(saved['applied_revision']) in html and saved['head_revision_now']==saved['applied_revision']
    original=source.read_text(encoding='utf-8')
    assert original.index('assert.deepEqual(corrected.budgets,before.budgets)')<original.index("assert.equal(corrected.reason.text,correction)")
    assert (directory/'failure.png').is_file()
    output={
        'at':utc(),'status':'pass','layer':'saved_actual_browser_DOM_HTTP_receipt_and_source_trace',
        'raw_browser_batch_status_unchanged':'fail','raw_browser_batch':BATCH,
        'actual_controls_passed':facts['controls'],'actual_local_correction_receipt':saved,
        'correction_utf8_bytes':len(correction.encode()),'literal_html_is_text':True,'no_inline_script_element':True,
        'model_actions':0,'tool_actions':0,'new_browser_launches':0,'new_http_requests':0,'new_pg_connections':0,
        'keyboard_and_budget_assertions':'executed before the recorded final field assertion failure',
        'corrected_script_dynamic_rerun':'not_run','window_global_probe':'not_run; saved DOM has literal text and no injected script element',
        'sources':{str(p.relative_to(EVIDENCE)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest()
            for p in (directory/'failure-dom.html',directory/'failure.png',directory/'timeline.json',directory/'facts.json',source)},
    }
    atomic_json(EVIDENCE/'browser-final-artifact-verification.json',output)
    print('PASS: 10 real browser controls + committed zero-fee correction, UTF-8 literal text and saved DOM; original batch FAIL retained')
    return 0

if __name__=='__main__':raise SystemExit(main())
