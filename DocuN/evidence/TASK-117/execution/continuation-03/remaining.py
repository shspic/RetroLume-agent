"""S04真实只读应用查看；旧mode错误原件保留。"""
def readonly_view(flow):
    session=flow.call('GET','/api/session');assert session['data_context']['current_mode']=='restored_readonly'
    caps=flow.call('GET','/api/data/capabilities');records={}
    for category in ('activities','teaching','interview','learning','memories'):
        records[category]=flow.call('GET','/api/data/saved-records?category='+category)
    refused=[]
    for path,body in (('/api/activities',{}),('/api/materials?filename=forbidden.md',{}),('/api/memories/commands',{})):
        value=flow.call('POST',path,body,expected=409);assert 'data_readonly' in str(value);refused.append({'path':path,'response':value})
    return {'session':{k:v for k,v in session.items() if k!='token'},'caps':caps,'records':records,'writes_refused':refused,'fallback_source':False}
