"""冻结合成输入的真实HTTP适配；不替换服务端响应，不自动重交已COMMIT动作。"""
from pathlib import Path
import sys,json,hashlib,time
from uuid import uuid4
C01=Path(__file__).resolve().parent;EXEC=C01.parent;ROOT=EXEC.parents[3]
sys.path.insert(0,str(EXEC))
import control as c
import httpx
SAMPLES=json.loads((ROOT/'DocuN/evidence/TASK-116/design/sample-inputs.json').read_text(encoding='utf-8'))


def two_page_pdf():
    texts=[SAMPLES['pdf_definition'][k] for k in ('page1_text','page2_text')]
    objects=[b'<< /Type /Catalog /Pages 2 0 R >>',b'<< /Type /Pages /Kids [3 0 R 5 0 R] /Count 2 >>']
    for i,text in enumerate(texts):
        objects.append(f'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 7 0 R >> >> /Contents {4+2*i} 0 R >>'.encode())
        stream=('BT /F1 12 Tf 50 700 Td ('+text.replace('\\','\\\\').replace('(','\\(').replace(')','\\)')+') Tj ET').encode('ascii')
        objects.append(f'<< /Length {len(stream)} >>\nstream\n'.encode()+stream+b'\nendstream')
    objects.append(b'<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>')
    data=bytearray(b'%PDF-1.4\n');offsets=[0]
    for i,obj in enumerate(objects,1):offsets.append(len(data));data.extend(f'{i} 0 obj\n'.encode()+obj+b'\nendobj\n')
    xref=len(data);data.extend(f'xref\n0 {len(objects)+1}\n0000000000 65535 f \n'.encode())
    for n in offsets[1:]:data.extend(f'{n:010d} 00000 n \n'.encode())
    data.extend(f'trailer\n<< /Size {len(objects)+1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n'.encode())
    return bytes(data)


class FrozenFlow:
    def __init__(self,label):
        self.label=label;self.folder=C01/label;self.folder.mkdir(exist_ok=True)
        if (self.folder/'proof.json').exists():
            (self.folder/('proof-before-'+str(time.time_ns())+'.json')).write_bytes((self.folder/'proof.json').read_bytes())
        self.client=httpx.Client(base_url='http://127.0.0.1:18118',timeout=105,trust_env=False)
        self.proof={'schema':'TASK117.S02.http.v1','label':label,'commands':[],'checks':[],'real_provider_calls':0,'actual_fee':0,'Q':'NOT_ENABLED'}
        session=self.call('GET','/api/session');self.client.headers['X-RetroLume-Session']=session['token']
        self.client.headers['X-RetroLume-Data-Context']=json.dumps(session['data_context'],ensure_ascii=False,sort_keys=True,separators=(',',':'))
    def save(self):c.write(self.folder/'proof.json',self.proof)
    def close(self):self.save();self.client.close()
    def call(self,method,path,body=None,*,expected=200,native=0,content=None):
        c.guard();c.count('http')
        if native:c.count('native_windows',native)
        r=self.client.request(method,path,json=body) if content is None else self.client.request(method,path,content=content)
        try:value=r.json()
        except ValueError:value={'bytes':len(r.content),'sha256':c.sha(r.content)}
        logged_body={**body,'input_owner_key':'<ephemeral-not-persisted>'} if isinstance(body,dict) and 'input_owner_key' in body else body
        if path!='/api/session':c.write(self.folder/(str(time.time_ns())+'.json'),{'method':method,'path':path,'request':logged_body,'content_sha256':c.sha(content) if content is not None else None,'status':r.status_code,'response':value})
        if r.status_code!=expected:raise RuntimeError(f'HTTP_{r.status_code}:{path}:{str(value)[:250]}')
        return value
    def prepare(self,*,pdf=False):
        identities=[{'alias':s['alias'],'filename':s['filename'],'bytes':len(s['text'].encode()),'sha256':c.sha(s['text'].encode())} for s in SAMPLES['sources']]
        raw=two_page_pdf();(self.folder/'PDF-2.pdf').write_bytes(raw)
        identities.append({'alias':'PDF-2','filename':SAMPLES['pdf_definition']['filename'],'bytes':len(raw),'sha256':c.sha(raw)})
        identity_file=self.folder/'inputs-before-upload.json'
        if identity_file.exists():assert json.loads(identity_file.read_text())['inputs']==identities
        else:c.write(identity_file,{'sample':c.sample(),'inputs':identities})
        rows=self.call('GET','/api/materials')['items'];mapping={}
        from urllib.parse import quote
        for source,identity in zip(SAMPLES['sources'],identities):
            existing=next((r for r in rows if r['sha256']==identity['sha256'] and r['title']==source['filename']),None)
            mapping[source['alias']]=existing or self.call('POST','/api/materials?filename='+quote(source['filename']),content=source['text'].encode())['material']
        prior_invalid=any(json.loads(p.read_text()).get('path')=='/api/materials?filename=invalid-utf8.md' and json.loads(p.read_text()).get('status')==422 for p in self.folder.glob('*.json') if p.name not in ('proof.json','inputs-before-upload.json'))
        if not prior_invalid:self.call('POST','/api/materials?filename=invalid-utf8.md',content=b'\xff\xfe',expected=422)
        if pdf:
            c.count('native_windows')
            candidate=self.call('POST','/api/materials?filename='+quote(SAMPLES['pdf_definition']['filename']),content=raw)['candidate']
            cid=candidate['candidate_id'];vid=candidate['version_id']
            self.call('POST',f'/api/pdf-candidates/{cid}/confirm',{'version_id':vid,'pages':[{'physical_page':1,'reviewed':True},{'physical_page':2,'reviewed':False}]},expected=422)
            mapping['PDF-2']=self.call('POST',f'/api/pdf-candidates/{cid}/confirm',{'version_id':vid,'pages':[{'physical_page':1,'reviewed':True},{'physical_page':2,'reviewed':True,'supplement':'用户独立补充：本页分钟须换秒，不代替原页。'}]})['material']
        else:self.proof['checks'].append({'case':'X01/PDF-2','status':'UNRESOLVED','reason':'两次真实HTTP解析失败保留；当前补充不修复/不重试PDF，独立MD继续'})
        self.proof['sources']=mapping;c.write(C01/'frozen-source-bindings.json',mapping)
        if (C01/'frozen-memory-binding.json').exists():return mapping,self.call('GET','/api/memories/'+json.loads((C01/'frozen-memory-binding.json').read_text())['memory_id'])
        mid=str(uuid4());key=str(uuid4())
        self.call('POST','/api/memories/commands',{'business_key':key,'memory_id':mid,'expected_revision':0,'action':'save','body':{'kind':'preference','title':'S02偏好','text':SAMPLES['inputs']['memory_body']}})
        memory=self.call('GET','/api/memories/'+mid)
        self.proof['memory']=memory;c.write(C01/'frozen-memory-binding.json',memory);self.save()
        return mapping,memory
    def create(self,sources,memory=None):
        body={'activity_id':str(uuid4()),'source_ids':[r['id'] for r in sources],'expected_sources':[{'source_id':r['id'],'version_id':r['version_id'],'revision':r['revision']} for r in sources]}
        if memory:body['memory_selection']={'confirmed':True,'entries':[{k:memory[k] for k in ('memory_id','version','revision','body_sha256')}]}
        self.call('POST','/api/activities',body);return body['activity_id']
    def index(self,aid):
        status=self.call('GET',f'/api/activities/{aid}/retrieval/status')
        if not status.get('ready'):
            receipt=self.call('POST',f'/api/activities/{aid}/retrieval/commands',{'business_key':str(uuid4()),'action':'source_index','expected_scope_revision':status['scope_revision'],'expected_domain_revision':status['domain_revision'],'confirmed':True},native=status['index_batches'])
            assert receipt['terminal_disposition'] in ('received','cache_ready'),receipt
    def query(self,aid,head,query):
        value=self.call('POST',f'/api/activities/{aid}/retrieval/commands',{'business_key':str(uuid4()),'action':'query','expected_scope_revision':head.get('scope_revision',1),'expected_domain_revision':head['revision'],'query':query,'confirmed':True},native=1)
        assert value.get('current') and value['terminal_disposition']=='received',value
        return value['retrieval_ref']
    def teaching(self,aid,action,body,*,query='平均速度 分钟换秒 米每秒'):
        workspace=self.call('GET',f'/api/activities/{aid}/teaching/workspace');h=workspace['head']
        scope=self.call('GET',f'/api/activities/{aid}')['activity']['scope_revision'];h={**h,'scope_revision':scope}
        command={'business_key':str(uuid4()),'expected_revision':h['revision'],'expected_goal_version':h['goal_version'],'expected_scope_revision':scope,'action':action,'body':body}
        if action in ('plan','exercise','evaluate'):command['retrieval_ref']=self.query(aid,h,query)
        receipt=self.call('POST',f'/api/activities/{aid}/teaching/commands',command,native=int(action in ('plan','exercise','evaluate','calculate')))
        self.proof['commands'].append({'activity_id':aid,'domain':'teaching','command':command,'receipt':receipt});self.save()
        assert receipt['status']=='committed',receipt
        return self.call('GET',f'/api/activities/{aid}/teaching/workspace')
    def interview(self,aid,action,body):
        workspace=self.call('GET',f'/api/activities/{aid}/interview/workspace');h=workspace.get('head') or {}
        command={'schema':'interview.command.v2','business_key':str(uuid4()),'expected_head_revision':h.get('revision',0),'expected_goal_version':h.get('goal_version',0),'expected_scope_revision':h.get('scope_revision',1),'action':action,'body':body,'retrieval_ref':None}
        if action in ('ask','review'):command['retrieval_ref']=self.query(aid,h,'虚构接口 缓存路径 个人分工 合成测量 耗时')
        receipt=self.call('POST',f'/api/activities/{aid}/interview/commands',command,native=int(action in ('ask','review')))
        self.proof['commands'].append({'activity_id':aid,'domain':'interview','command':command,'receipt':receipt});self.save()
        assert receipt['status']=='committed',receipt
        return self.call('GET',f'/api/activities/{aid}/interview/workspace')
