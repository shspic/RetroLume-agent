"""同源真实HTTP，仅显式POST；响应按业务键保留，GET不触发窗口。"""
import hashlib,json,time
from uuid import uuid4
from control import HERE,ROOT,count,event,write,guard
import httpx

class Flow:
    def __init__(self):
        self.client=httpx.Client(base_url='http://127.0.0.1:18118',timeout=90,trust_env=False)
        self.serial=0;self.proof=json.loads((HERE/'root04-flow-progress.json').read_text()) if (HERE/'root04-flow-progress.json').exists() else {'commands':[],'checks':[]}
        session=self.call('GET','/api/session');self.client.headers['X-RetroLume-Session']=session['token']
        context=session.get('data_context')
        if context:self.client.headers['X-RetroLume-Data-Context']=json.dumps(context,ensure_ascii=False,sort_keys=True,separators=(',',':'))
    def call(self,method,path,body=None,*,expected=200,native=0):
        guard();count('http')
        for _ in range(native):count('native_windows')
        r=self.client.request(method,path,json=body) if body is not None else self.client.request(method,path)
        self.serial+=1
        try:value=r.json()
        except ValueError:value={'bytes':len(r.content),'sha256':hashlib.sha256(r.content).hexdigest()}
        if path!='/api/session':write(HERE/'http'/f'{time.time_ns()}-{self.serial:03d}.json',{'method':method,'path':path,'status':r.status_code,'request':body,'response':value})
        if r.status_code!=expected:raise RuntimeError(f'http_{r.status_code}:{path}:{str(value)[:400]}')
        return value
    def query(self,aid,scope,rev,query):
        for file in sorted((HERE/'http').glob('*.json'),reverse=True):
            prior=json.loads(file.read_text(encoding='utf-8'));body=prior.get('request') or {};response=prior.get('response') or {}
            if prior['path']==f'/api/activities/{aid}/retrieval/commands' and body.get('action')=='query' and body.get('expected_scope_revision')==scope and body.get('expected_domain_revision')==rev and body.get('query')==query and response.get('retrieval_ref'):
                existing=self.call('GET',f"/api/activities/{aid}/retrieval/commands/{body['business_key']}")
                if existing.get('current') and existing.get('terminal_disposition')=='received':return existing['retrieval_ref']
        value=self.call('POST',f'/api/activities/{aid}/retrieval/commands',dict(business_key=str(uuid4()),action='query',expected_scope_revision=scope,expected_domain_revision=rev,query=query,confirmed=True),native=1)
        if value.get('terminal_disposition')!='received' or not value.get('current'):raise RuntimeError('query_not_current:'+str(value.get('error_code')))
        return value['retrieval_ref']
    def teaching(self,aid,action,body):
        w=self.call('GET',f'/api/activities/{aid}/teaching/workspace');h=w['head']
        input=dict(business_key=str(uuid4()),expected_revision=h['revision'],expected_goal_version=h['goal_version'],expected_scope_revision=1,action=action,body=body)
        model=action in ('plan','exercise','evaluate')
        if model:input['retrieval_ref']=self.query(aid,1,h['revision'],'平均速度 分钟换秒 米每秒')
        value=self.call('POST',f'/api/activities/{aid}/teaching/commands',input,native=int(model or action=='calculate'))
        self.proof['commands'].append({'domain':'teaching','activity_id':aid,'action':action,'business_key':input['business_key'],'status':value.get('status')})
        if value.get('status')!='committed':raise RuntimeError('teaching_not_committed:'+str(value))
        write(HERE/'root04-flow-progress.json',self.proof)
        return value,self.call('GET',f'/api/activities/{aid}/teaching/workspace')
    def interview(self,aid,action,body):
        w=self.call('GET',f'/api/activities/{aid}/interview/workspace');h=w.get('head') or {}
        input=dict(schema='interview.command.v2',business_key=str(uuid4()),expected_head_revision=h.get('revision',0),expected_goal_version=h.get('goal_version',0),expected_scope_revision=h.get('scope_revision',1),action=action,body=body,retrieval_ref=None)
        model=action in ('ask','review')
        if model:input['retrieval_ref']=self.query(aid,1,h['revision'],'平均速度 分钟换秒 米每秒')
        value=self.call('POST',f'/api/activities/{aid}/interview/commands',input,native=int(model))
        self.proof['commands'].append({'domain':'interview','activity_id':aid,'action':action,'business_key':input['business_key'],'status':value.get('status')})
        if value.get('status')!='committed':raise RuntimeError('interview_not_committed:'+str(value))
        write(HERE/'root04-flow-progress.json',self.proof)
        return value,self.call('GET',f'/api/activities/{aid}/interview/workspace')
    def run(self):
        (HERE/'http').mkdir(exist_ok=True)
        materials=self.call('GET','/api/materials')['items'];source=next(x for x in materials if x['title']=='速度.md')
        ids=json.loads((HERE/'root04-activity-ids.json').read_text()) if (HERE/'root04-activity-ids.json').exists() else {domain:str(uuid4()) for domain in ('teaching','interview')}
        write(HERE/'root04-activity-ids.json',ids)
        for aid in ids.values():
            facts=self.call('GET','/api/activities')['items']
            if not any(a['activity_id']==aid for a in facts):self.call('POST','/api/activities',{'activity_id':aid,'source_ids':[source['id']],'expected_sources':[{'source_id':source['id'],'version_id':source['version_id'],'revision':source['revision']}]})
            status=self.call('GET',f'/api/activities/{aid}/retrieval/status')
            if not status.get('ready'):
                result=self.call('POST',f'/api/activities/{aid}/retrieval/commands',dict(business_key=str(uuid4()),action='source_index',expected_scope_revision=1,expected_domain_revision=status.get('domain_revision',0),query=None,confirmed=True),native=status.get('index_batches',1))
                if result.get('terminal_disposition') not in ('received','cache_ready'):raise RuntimeError('index_not_ready')
        if not self.proof.get('teaching_final'):
            aid=ids['teaching']
            w=self.call('GET',f'/api/activities/{aid}/teaching/workspace')
            if not w['head']['goal_record_id']:self.teaching(aid,'goal',{'goal':'根据速度.md学习平均速度与分钟换秒，说明单位并独立复测。'})
            _,w=self.teaching(aid,'plan',{'confirmed':True})
            proposal=w['proposal']['record_id']
            _,w=self.teaching(aid,'accept_path',{'proposal_record_id':proposal})
            path=w['head']['path_record_id']
            _,w=self.teaching(aid,'exercise',{'confirmed':True,'path_record_id':path,'node_id':'n1','purpose':'initial'})
            exercise=w['head']['exercise_record_id']
            _,w=self.teaching(aid,'answer',{'exercise_record_id':exercise,'kind':'initial','text':'2分钟是120秒；120米除以120秒为1米每秒。'})
            answer=w['head']['answer_record_id']
            _,w=self.teaching(aid,'evaluate',{'confirmed':True,'exercise_record_id':exercise,'answer_record_id':answer})
            feedback=w['head']['feedback_record_id']
            _,w=self.teaching(aid,'exercise',{'confirmed':True,'path_record_id':path,'node_id':'n1','purpose':'retest','parent_feedback_record_id':feedback})
            exercise=w['head']['exercise_record_id']
            _,w=self.teaching(aid,'answer',{'exercise_record_id':exercise,'kind':'initial','text':'先用2乘60得到120秒，再用120除以120，得到1米每秒。'})
            _,w=self.teaching(aid,'evaluate',{'confirmed':True,'exercise_record_id':exercise,'answer_record_id':w['head']['answer_record_id']})
            self.proof['teaching_final']=w
        aid=ids['interview']
        w=self.call('GET',f'/api/activities/{aid}/interview/workspace')
        if not w.get('head'):self.interview(aid,'start',{'goal':{'target':'解释平均速度与分钟换秒','focus':None,'clarifications':[],'material_roles':[{'source_id':source['id'],'role':'reference'}]}})
        if not w.get('head'):w=self.call('GET',f'/api/activities/{aid}/interview/workspace')
        if w['head']['phase']=='ready':_,w=self.interview(aid,'ask',{'mode':'first','parent_feedback_id':None,'retry_of':None})
        if w['head']['phase']=='question_ready':_,w=self.interview(aid,'answer',{'question_record_id':w['head']['current_question_id'],'text':'2分钟换算成120秒，再计算120/120=1米每秒。'})
        if w['head']['phase']=='answer_ready':_,w=self.interview(aid,'review',{'question_record_id':w['head']['current_question_id'],'answer_record_id':w['head']['current_answer_id'],'retry_of':None})
        if w['head']['phase']=='question_ready':
            _,w=self.interview(aid,'answer',{'question_record_id':w['head']['current_question_id'],'text':'1分钟为60秒，所以2分钟为120秒；没有独立证明的经历仍是自报。'})
            _,w=self.interview(aid,'review',{'question_record_id':w['head']['current_question_id'],'answer_record_id':w['head']['current_answer_id'],'retry_of':None})
        if w['head']['phase']=='feedback_ready':_,w=self.interview(aid,'finish',{})
        if w['head']['phase']!='ended':raise RuntimeError('interview_not_ended')
        self.proof['interview_final']=w;self.proof['semantic_quality']='NOT_RUN_SYNTHETIC_TRANSPORT';write(HERE/'root04-flow-proof.json',self.proof)
        return ids
