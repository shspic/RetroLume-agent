"""S08只封存已完成证据与候选结果；保留全部历史字节，不再运行产品检查。"""
from pathlib import Path
from datetime import datetime,timezone
from ctypes import wintypes
import difflib
import json
import os
import re
import socket
import ctypes
from control import N,E,ROOT,K,PERMIT,state,segment,guard,write,sha,sample,event,birth,failure

def main():
    assert not (N/'final-binding.json').exists(),'已完成封存，禁止重复记账'
    b=guard();s=segment(b);before=json.loads((N/'before-budget.json').read_text(encoding='utf-8'))
    assert b['active_root'] is None and s['offline_process_run_active'] is None and s['holding_start_mono_ns'] is None
    assert b['segments'][:-1]==before['segments'] and b['roots'][:len(before['roots'])]==before['roots']
    assert b['failures'][:len(before['failures'])]==before['failures']
    assert (E/'events.jsonl').read_bytes().startswith((N/'before-events.jsonl').read_bytes())
    proof_path=N/'root-25/attempt-03/proof.json';proof=json.loads(proof_path.read_text(encoding='utf-8'))
    assert proof['status']=='passed' and len(proof['cases'])==8 and not proof['unknown_routes'] and not proof['external_attempts']
    assert b['counts']['http']-s['baseline_counts']['http']==len(proof['requests'])==162
    old=(N/'before-result.md').read_bytes();result=ROOT/'DocuN/results/TASK-117-result.md'
    assert len(old)==88265 and sha(old)=='fc600e1381e44542fc933bdd294e471e2e1a5d4b70b979a5a2be708878993aab' and result.read_bytes()==old
    assert all(c['post_query_domain_posts']==(1 if c['name']=='D03-same' else 0) for c in proof['cases'][:4])
    fixed=['pg_create_attempts','pg_objects','volumes','pg_starts','api_starts','native_windows','preview_creates','preview_starts','provider_calls','actual_fee_microunits']
    assert all(b['counts'][name]==s['baseline_counts'][name] for name in fixed)
    # 补记先前直接工具的失败；当前采样是补记时点，原始工具回执不改写。
    receipts=json.loads((N/'tool-receipts-at-seal.json').read_text(encoding='utf-8'))
    existing_labels={row['label'] for row in b['failures'] if row.get('segment')==PERMIT}
    supplements=[]
    for row in receipts['commands']:
        if row['label'] in ('root25-same-deadline-cache-fix','final-save','final-port-fallback-read') or 'Get-Content:' in row.get('output','') or re.search(r'rg: .*error',row.get('output','')):
            label='S08_tool_'+row['label']
            if label not in existing_labels:failure(label,'补记直接工具事实，原chunk '+str(row.get('chunk_id'))+'；详见tool-receipts-at-seal.json，不是新增产品缺陷');supplements.append(label)
    event('S08_resume_reason_correction',root=25,attempt=3,
          actual_reason='attempt02已验证sandbox ERR_NETWORK_ACCESS_DENIED；平台require_escalated审核允许同一封闭loopback验证后，在原根原截止恢复',
          historical_message_retained='原same_root_resume辅助器沿用cache说明不精确，保留原事件并在此明确补足；不是审批拒绝后的绕过')
    changes=json.loads((N/'changes.json').read_text(encoding='utf-8'))
    prior=json.loads((E/'continuation-06/changes.json').read_text(encoding='utf-8'))
    manifest=[];delta=[];combined=[]
    for relative,pre in changes.items():
        path=ROOT/relative;raw=path.read_bytes() if path.exists() else b''
        pre_raw=(ROOT/pre['backup']).read_bytes() if pre['exists'] else b''
        assert not pre['exists'] or sha(pre_raw)==pre['sha256']
        audit=prior.get(relative,pre);audit_raw=(ROOT/audit['backup']).read_bytes() if audit['exists'] else b''
        def diff(a,z,first):
            return list(difflib.unified_diff([x+'\n' for x in a.decode('utf-8-sig').splitlines()],[x+'\n' for x in z.decode('utf-8-sig').splitlines()],fromfile=first+'/'+relative,tofile='final/'+relative))
        delta.extend(diff(pre_raw,raw,'S07-initial'));combined.extend(diff(audit_raw,raw,'TASK118-audited'))
        manifest.append({'path':relative,'D':pre['D'],'S08_pre':pre,'TASK118_pre':audit,
          'post':{'exists':path.exists(),'bytes':len(raw),'sha256':sha(raw) if path.exists() else None,
                  'CRLF':raw.count(b'\r\n'),'LF_total':raw.count(b'\n')},
          'changed_in_S08':pre_raw!=raw or pre['exists']!=path.exists(),'changed_from_audit':audit_raw!=raw or audit['exists']!=path.exists()})
    (N/'S08-delta.diff').write_text(''.join(delta),encoding='utf-8')
    (N/'TASK118-four-repairs.diff').write_text(''.join(combined),encoding='utf-8')
    write(N/'post-source-manifest.json',{'sample':sample(),'files':manifest,'diff_policy':'统一diff只规范换行用于审阅；实际pre/post原字节、CRLF计数和SHA权威，未据diff改产品换行'})
    bundle=json.loads((N/'bundle-8.json').read_text(encoding='utf-8'))
    for row in bundle['files']:assert sha((ROOT/row['path']).read_bytes())==row['sha256']
    browser_as_run=json.loads((N/'browser-as-run.json').read_text(encoding='utf-8'))
    assert all(sha((ROOT/row['path']).read_bytes())==row['sha256'] for row in browser_as_run['script_and_source'])
    # 文件锁12方法的ok在第2批后续async环境挂起前已完成；其产品/方法字节未再改变。
    bindings=[('backend-targeted-v2.log','D01'),('backend-no-io.log','D02兼容/loader'),('model-scope-v2.log','D02模型'),('approved-model-final.log','D02批准正例')]
    methods={}
    for filename,layer in bindings:
        text=(N/filename).read_text(encoding='utf-8')
        for line in text.splitlines():
            match=re.match(r'^(test_\w+) \(([^)]+)\) \.\.\. ok$',line)
            if match:methods[match.group(2)+'.'+match.group(1)]={'method':match.group(2)+'.'+match.group(1),'evidence':str(N/filename),'layer':layer}
    assert len(methods)==33,len(methods)
    write(N/'as-run-final.json',{'sample':sample(),'unit_methods':list(methods.values()),'unique_targeted_method_count':len(methods),
        'D01_partial_batch_caveat':'12方法及cleanup均ok；承载批次后续无关async挂起导致命令超时。方法级结果按targeted-as-run.json的原字节复用，不将批次退出码改0',
        'D02_fixture_scope':'真实StoredTeachingDocument与typed网关；memory字段投影覆盖正文/版本，不声称完整v2记忆材料化或PG准入',
        'D02_followup_reason':'仅修typed Message默认tool_calls和JSON tuple/list等价夹具；保留全部原失败，最后仅复检受影响方法',
        'typecheck':{'exit_code':0,'evidence':str(N/'typecheck.log')},'build':bundle,
        'browser':{'exit_code':0,'proof':str(proof_path),'matrix_count':8,'HTTP':162,'synthetic_HTTP':True,'real_PG':False,'real_provider':False},
        'Q':'FROZEN','independent_review':'NOT_SELF_SIGNED'})
    timeline=[]
    for case in proof['cases'][:4]:
        request=next(row for row in proof['requests'] if row['case']==case['name'] and row['method']=='GET' and row['path'].endswith('/'+case['query_key']))
        image=proof_path.parent/(case['name']+'.png')
        timeline.append({'case':case['name'],'request_observed_at':request['at'],'response_observed':case['original_key_GET'],
          'response_completion_window_utc':[request['at'],datetime.fromtimestamp(image.stat().st_mtime,timezone.utc).isoformat()],
          'window_basis':'实际原键GET接收先于返回body及后续截图写入；没有捏造精确响应完成时间'})
    write(N/'network-timeline.json',{'requests':proof['requests'],'actual_asset_responses':proof['assets'],'key_response_windows':timeline,
      'scope':'全部162实际HTTP入站；正式JS/CSS实际浏览器响应体hash；四原键200回执及响应区间。没有全部API正文镜像/每个响应完成精确时刻，不冒真实后端资格'})
    screenshots=[{'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p.read_bytes())} for p in sorted(proof_path.parent.glob('*.png'))]
    write(N/'screenshots.json',{'files':screenshots,'visual_review':['D04-index-teaching-before-confirm.png','D04-changed-interview.png','D04-missing-vector.png'],
      'review':'目标告知文字与禁用资格可见。未覆盖的新建活动quota占位区域出现undefined来自最小fixture，不计作整页产品验收；未为此修改或重跑产品'})
    registered={}
    for p in N.glob('*-pid.json'):
        row=json.loads(p.read_text(encoding='utf-8'));registered[(row['pid'],row['birth_filetime'])]={'pid':row['pid'],'birth_filetime':row['birth_filetime']}
    stops=[]
    for p in (N/'root-25').rglob('stop.json'):
        row=json.loads(p.read_text(encoding='utf-8'));assert not row['same_birth_alive'] and row['18119_no_listener'];stops.append({'path':str(p),'sha256':sha(p.read_bytes()),'stop':row})
        for identity in row['registered_pid_births']:registered[(identity['pid'],identity['birth_filetime'])]=identity
    K.OpenProcess.argtypes=[wintypes.DWORD,wintypes.BOOL,wintypes.DWORD];K.OpenProcess.restype=wintypes.HANDLE
    K.CloseHandle.argtypes=[wintypes.HANDLE]
    K.GetExitCodeProcess.argtypes=[wintypes.HANDLE,ctypes.POINTER(wintypes.DWORD)]
    identities=[]
    for row in registered.values():
        handle=K.OpenProcess(0x1000|0x100000,False,row['pid']);observed={**row,'same_birth_alive':False}
        if handle:
            try:
                actual=birth(handle);exit_code=wintypes.DWORD();assert K.GetExitCodeProcess(handle,ctypes.byref(exit_code))
                observed.update(current_birth_filetime=actual,exit_code=exit_code.value,same_birth_alive=actual==row['birth_filetime'] and exit_code.value==259)
            finally:K.CloseHandle(handle)
        else:
            observed['current_lookup_error']=ctypes.get_last_error()
            if observed['current_lookup_error'] not in (87,):observed['same_birth_alive']=None
        identities.append(observed)
    assert not any(row['same_birth_alive'] for row in identities)
    # 受限sandbox可能直接拒绝connect，故用只读TCP表而非失败的connect推断无监听。
    tcp=ctypes.WinDLL('iphlpapi').GetExtendedTcpTable
    tcp.argtypes=[ctypes.c_void_p,ctypes.POINTER(wintypes.DWORD),wintypes.BOOL,wintypes.ULONG,ctypes.c_int,wintypes.ULONG]
    size=wintypes.DWORD();code=tcp(None,ctypes.byref(size),False,2,3,0);listeners=[];fallback=None
    if code in (0,122):
        buffer=ctypes.create_string_buffer(size.value);code=tcp(buffer,ctypes.byref(size),False,2,3,0);assert code==0,code
        class Row(ctypes.Structure):_fields_=[(name,wintypes.DWORD) for name in ('state','local_addr','local_port','remote_addr','remote_port','pid')]
        length=ctypes.cast(buffer,ctypes.POINTER(wintypes.DWORD)).contents.value
        for ordinal in range(length):
            row=Row.from_buffer_copy(buffer.raw[4+ordinal*ctypes.sizeof(Row):4+(ordinal+1)*ctypes.sizeof(Row)])
            if socket.ntohs(row.local_port&0xffff)==18119:listeners.append({'pid':row.pid,'port':18119})
    else:
        fallback=json.loads((N/'port-observation.json').read_text(encoding='utf-8'))
        assert fallback['netstat_exit']==0 and not fallback['matching_18119']
    assert not listeners
    write(N/'final-resource-stop.json',{'sample':sample(),'owned_pid_births':identities,'same_birth_alive':[],
      'current_lookup_unknown':[row for row in identities if row['same_birth_alive'] is None],
      'TCP_owner_PID_listener_table_return_code':code,'ordinary_netstat_fallback':fallback,'18119_listeners':listeners,'18119_no_listener':True,'attempt_stops':stops,'old_PG_resampled':False,
      'old_stop_reference_only':str(E/'continuation-05/final-resource-stop-binding.json'),'old_stop_reference_utc':'2026-10-16T15:45:05.045131Z'})
    b=state();s=segment(b);now=sample();held=sum(row['seconds'] for row in b['runtime_intervals'] if row.get('segment')==PERMIT)
    external=json.loads((N/'tool-receipts.json').read_text(encoding='utf-8'))['command_wall_upper_seconds']
    upper=(datetime.fromisoformat(now['utc'])-datetime.fromisoformat(s['first_tool_utc'])).total_seconds()
    assert s['offline_process_run_seconds']+external<3600 and held<3600
    delta_counts={name:value-s['baseline_counts'][name] for name,value in b['counts'].items()}
    timing={'sample':now,'first_tool_utc':s['first_tool_utc'],'calendar_deadline_utc':s['calendar_deadline_utc'],
       'UTC_span_upper_seconds':upper,'actual_activity_seconds':'UNKNOWN; 不以跨中断UTC总差作为实际工作或硬门',
       'offline_child_measured_seconds':s['offline_process_run_seconds'],'external_tool_command_wall_upper_seconds':external,
       'conservative_combined_command_wall_seconds':s['offline_process_run_seconds']+external,'command_wall_cap_seconds':3600,
       'runtime_holding_union_upper_seconds':held,'runtime_holding_cap_seconds':3600,
       'timing_basis':'外层工具wall与内部子进程可能重叠，保守相加不退时；首三批10.7秒为有收据的并行上界，不声称精确CPU',
       'clock_anchor':s['clock_anchor'],'last_clock':now,'clock_reanchors':s['clock_reanchors'],
       'old_segments_unchanged':True,'delta_counts':delta_counts,'cumulative_counts':b['counts']}
    write(N/'final-timing.json',timing)
    # 只追加本段，旧case对象/失败/时间不覆盖。
    s.update(status='returned_engineering_candidate',last_clock=now,final_sample=now,
       final_timing=str(N/'final-timing.json'),command_wall_conservative_seconds=s['offline_process_run_seconds']+external,
       UTC_span_upper_seconds=upper,validation_status='FOUR_REPAIRS_TARGETED_SYNTHETIC_VERIFIED_NOT_INDEPENDENT_AUDIT')
    b['phase']='S08_returned_engineering_candidate';write(E/'budget.json',b);write(N/'final-budget-observed.json',b)
    index=json.loads((E/'case-index.json').read_text(encoding='utf-8'))
    index['S08']={'sample':now,'permit':PERMIT,'status':'FOUR_REPAIR_ENGINEERING_CANDIDATE_READY_FOR_TASK118_INCREMENTAL_REVIEW','Q':'FROZEN',
      'D01':'12真实FileLock方法级ok，外来commit/same-key/change零追加，原批次后续环境超时不改写',
      'D02':'完整payload+typed请求范围，批准send1、未批正文/记忆版本零准入、await变更保守、loader/wire兼容',
      'D03':'正式bundle8同activity owner/view/head晚到0POST，正常1POST，原key及完整草稿保留',
      'D04':'索引/教学/面试真实只读字段告知，缺字段关闭，改值对照；合成HTTP层',
      'evidence':str(N/'as-run-final.json'),'historical_cases_and_S07_preserved':True}
    write(E/'case-index.json',index)
    changed_s08=[row['path'] for row in manifest if row['changed_in_S08']]
    changed_all=[row['path'] for row in manifest if row['changed_from_audit']]
    js=next(row for row in bundle['files'] if row['path'].endswith('.js'))
    total_failures=len(b['failures']);new_failures=total_failures-len(before['failures'])
    prefix=f'''# TASK-117 / R-111 S08 四项修正与定向验证工程候选

四项缺陷的必要修正和分层定向验证已完成，正式bundle8的八项合成浏览器场景通过，形成可交原TASK118增量独审的工程候选；Q继续冻结，不自签缺陷关闭、完整S或项目验收。

## 采用与实际范围

沿用原TASK117工程窗口，A+为资源标签，客户端为Codex desktop / GPT-6，具体服务端变体未披露。新许可为{PERMIT}，task_model/V4.0、CHG-0003、阶段07；需求v1.3、架构v1.42、执行动态v2.69。首工具UTC为{s['first_tool_utc']}，本段日历截止{s['calendar_deadline_utc']}。接收核对199项实际输入，六份S07初版与主控采用hash一致，保留其内容，按必要因果增补实现和夹具。未另开窗口、委派、改DocuS/任务卡/独审原件，未安装或联网查供应商。

证据根为{N.as_posix()}/。receipt.json保留真实首点/当前宿主anchor；before-budget/events/case-index及before-result保留接收字节；changes.json与preimages从六份初版起保存本段原件，另引用continuation-06/preimages追溯TASK118所审版本。原88265字节报告保持精确后缀，SHA256 fc600e1381e44542fc933bdd294e471e2e1a5d4b70b979a5a2be708878993aab；旧S07超额、not_run和全部历史判断不改写。

## D01 控制日志所有写入口

保留S07的锁内_validated_locked实现。读快照与commit、create_or_get_job、change_job在各自同一真实文件锁内校验当前完整字节、文件身份、首hub control_id后，才replay/CAS/append；没有在外部先校验再另开写锁。合法完整前缀GET、残尾写拒绝、同size/mtime篡改检测、fsync、取消/fence、容量及公开副本边界继续有效，日志格式没有改变。

本段在准确continuation-07目录构造真实ControlHub/FileLock合成hub。三个格式/hash链完整的外来B日志替换已缓存A后，分别尝试commit、同business_key创建/返回、命中B job的change，均control_corrupt，零追加、零返回外来事实、decide不调用；另核所有写入口对可读残尾均拒绝。合法同字节inode替换、peer取消、revision/clock/deadline/fence与公开副本等共12方法均ok，见backend-targeted-v2.log及targeted-as-run.json。承载该12方法的整批随后在另一async夹具构造时超时，退出码仍为超时；这里仅按未再变化的产品与方法字节继承其已完成结果，没有把命令改成整体成功或重跑其它恢复业务。

## D02 完整受信模型消息范围

采用有限严格model_requests批准对：每项仅payload_sha256与request_sha256，均64位小写hex，最多128项且拒绝重复。完整provider payload及完整typed request同时进入批准范围，包括system/user/history、回答、纠错、选用记忆正文与版本及派生上下文。非空新增字段进入新manifest hash，经实际load_integration_config、grant绑定及私有OneCallInput v4传递；空字段保留旧Embedding清单摘要，但缺少模型批准的旧清单对模型失败关闭。原Embedding/query、旧v3及新v4隔离保留，无grant的本地非外网合成路径仍能完成正常调用。

网关深复制请求与配置，固定序列化发送字节。准入前、await准入后、dispatch前核同一受信范围；原请求、配置或私有intent在await中变化时保守保持已预扣，停止dispatch/send。若mark期间才变化，记录NOT_SENT而不发送、退款或重试。实际最低transport收到由同一冻结JSON字节解码的对象，避免校验一个对象却发送后来的可变对象。

实际TeachingService._stored_document与typed Message装配绑定正常合成正例，网关SUCCEEDED且恰一次替身send；goal、answer、corrections/history、selected-memory text/version六种未批准正文变体均在准入前拒绝，send0；system及完整request格式变体也关闭。准入后的原request/config/private intent变化预留1、mark0/send0；mark期间变化send0、NOT_SENT；grant准入后失效不继续发送。实际本地loader在明确TEST-ONLY目录核新hash与旧hash篡换关闭，并沿私有wire往返；相关既有11方法回归有效。D02共21唯一方法的最终有效结果由backend-no-io.log中3个loader/manifest及11个兼容方法、model-scope-v2.log的6个模型方法、approved-model-final.log的最后一个正例合并，重复同名方法不多计。最终as-run映射见as-run-final.json。

测试的ledger/费用/receipt及transport全为明确test-only，Q样式receipt只在隔离测试目录，不是正式Q启用文件。selected-memory反例覆盖实际背景投影字段的完整消息范围，不冒充完整v2记忆材料化/PG资格链。没有真实供应商或真实持久费用。

operator须在批准前固定有限动作key、活动/记录ID、scope/head、记忆版本和本地事实，用实际装配器生成并审核完整请求/payload后计算摘要，一次采用到受信清单和绑定grant。动态ID及服务生成上下文没有任意值例外，不接收正文后自动加白，不换绑已有活动grant。依赖未知上一轮模型输出的新请求不属于已批准集合；后续有限Q须由主控在不可重绑与持久共享总门合同内另行采用，不把本修复称所有Q动作已可执行。README已给无秘密字段示意，config/integration.example.json继续enabled=false与空路径，不填真实key。

## D03 教学query到domain的原身份

在一次显式意图起点捕获activity、owner、view_token、head revision、scope、DataContext/namespace与原key；build、IndexedDB完整草稿、摘要锁等待等相关await后及最终POST前复核同一身份。摘要锁回调另核原namespace，避免等待锁期间数据切换后写进新摘要库。teachingEditorOwner对已更换的session owner使原lease失效，不自动取得B或改绑；POST helper保留最后同步guard。domain_sent仅在实际发起POST后记，不提前把失效意图标成已交付。完整正文和query事实仍在原命名空间保留，原键GET不触发动作。

真实浏览器实载正式bundle8，在query回执已持久化之后、真实IndexedDB draft事务commit之后、原native oncomplete回调之前暂停；只用原生IDB完成时序形成屏障，没有替换产品guard、组件状态或伪造内部通过。随后驱动同activity正常“刷新教学工作区（只读）”，分别只改session owner A→B、只改view_token、只改head revision；释放回调后domain POST均0，domain_sent仍false，原query key与完整草稿保持。身份不变对照恰一次domain POST、domain_sent=true。四个原key只读GET实际200，原正文逐字保持。

owner场景的准确边界是会话A改B后原A编辑lease失效为只读，未声称同页面成功获得B lease；旧实现忽略该会话更换仍会比较两个A并发送，因此本反例能区分旧风险。head场景满足scope/head或DataContext三者中的head分支，本轮不额外声称覆盖DataContext切换。原键GET取证为真实浏览器显式fetch+封闭HTTP，生产GET实现本身未修改，历史正常只读核对证据按原字节继承，不把此fetch冒充真实后端中间件验收。

## D04 三处服务告知与未知门

从现有retrieval/status与activities/capabilities的受信public字段传入provider/model。索引前显示实际向量身份、用途、单批预留/时间窗口；教学与面试query+model前同时显示向量与聊天身份、用途、两次请求、两笔费用及两个窗口。backend retrieval public身份从service对象投影，配置缺失返回null而非固定身份。前端验证有限字符串与预算资格，缺失/坏格式/未知时相关外发关闭；retrieveForCommand发送前重新读status并核告知，恢复原动作也不能跳过。

正式浏览器覆盖索引确认前、教学query+model确认前、面试确认前的文字。正常向量/聊天为zhipu_embeddings/embedding-3与deepseek_chat_completions/deepseek-chat；改值对照直接显示synthetic_vector_b/s08-vector-model-b与synthetic_chat_b/s08-chat-model-b，证明消费只读fixture字段而非写死服务名，此对照不代表正式支持这些供方。缺向量、教学缺聊天、面试缺聊天三个场景模型按钮均停用、POST0，缺向量索引也停用；本地零费保存按钮资格和只读查看保持，未实际重跑本地保存/取消业务链。

## 正式产物、实际网络与适用层

类型检查exit0，正式Vite build8 exit0，未重跑已完成全业务测试。新主JS {js['path']}，SHA256 {js['sha256']}，{js['bytes']}字节；CSS SHA256 6f02da29293bb8bf41825425f1d9d0c5da950ab02e77dfa4854ed195f49e8b94。浏览器实际JS/CSS response body hash逐项等于磁盘bundle8；bundle7的完整4项旧字节另存本段bundle-7-before，PDF worker字节未改变。未手改dist。

最终{proof_path.as_posix()}记录8个场景全部passed、162个实际HTTP、外网尝试0、未知路由0。固定127.0.0.1:18119只提供正式dist及封闭合成HTTP，所有请求在原根内计入唯一账。请求时间线、正式资源实际响应hash、四个原key 200正文与响应完成区间另在network-timeline.json。区间由实际入站时刻和响应后截图落盘时刻构成，未捏造精确响应完成时间；没有全部API响应正文镜像，不冒充真实后端资格或数据状态。

9张原图及hash在screenshots.json，已人工查看索引/教学告知、改值面试、缺向量三张。目标字段与禁用状态可见；最小fixture未覆盖的新建活动quota区域有undefined占位，不计作整页产品验收，也没有为无关区域扩大修复。D01为实际本地文件锁，D02为实际网关加隔离最低替身，D03/D04为实际浏览器/正式产物加合成HTTP，分别保留验证层限制。

## 原始失败、环境定位与普通修正

原66条失败完整保留，本段新增{new_failures}条记录，累计{total_failures}；详情在唯一budget/events及原工具回执，不清零或把初版not_run当又失败。

本段先出现两次控制检查脚本调用问题：自检读到自身外层active命令、preimage helper被重复包进拒嵌套runner，分别按纯替身基准与直接已计工具入口纠正；控制器未放开并发进程门，19项有限控制自检通过。一次残尾夹具错读回执不公开scope字段，改用合成scope。前两批在首个async测试构造时分别超时120秒，原日志与准确Job清场保留；5秒有界诊断栈明确停于Windows socket.py fallback_socketpair accept，未进入产品协程。无实际I/O的测试改用拒绝fd注册、保留asyncio调度/timeout的闭合loop夹具，不修改系统、事件循环产品实现或网络权限。loader夹具补齐私有wire的65536上限，typed消息摘要补默认空tool_calls，最后仅修JSON tuple/list等价比较并复检单个正例；不降低网关拒绝断言。原schema字段的Pydantic警告保留。

首个浏览器启动尝试因Playwright缓存误指sandbox子目录而未创建浏览器进程，修正为已有1234缓存、不安装/换版本；下一尝试实际启动后固定回环访问被沙箱ERR_NETWORK_ACCESS_DENIED。两次均准确清场，未偷偷换端口或跳过审批。平台require_escalated审核允许这次既有封闭验证后，在原25根原截止内完成最后尝试；原根deadline不延长，三个Browser启动尝试和三次fixture server均逐次计数。辅助器旧resume说明复用cache文字不精确的部分以追加事件明确，未回写历史。直接工具过早读日志/路径问题及根续作旧记录缺attempt_number的KeyError也补记，原回执仍在，不算产品缺陷或伪造已执行。

## S08时间、资源停止与累计

本段不再将跨中断UTC总差作为活动硬门；48小时日历与最后1200秒保存门、真实命令wall3600、runtime持有并集3600、原根1500秒检查/300秒清场分别守门。首点和当前宿主anchor持久化，许可不fallback旧S07；时钟域/mono/UTC倒退、未结束命令、累计次数、持有/子进程/原根到限均有有限反例。自有子进程先挂起加入准确kill-on-close Job再恢复，独立截止、两次低于256MiB压力、stdin EOF与父退出均只关自有子树。无资源和active_root空时才可据同段原日历重锚，本段没有发生重锚，不重置任何旧首点。

封存采样{now['utc']}，首工具至此UTC上界{upper:.6f}秒，不称精确实际工作时长；内部子进程实测{s['offline_process_run_seconds']:.6f}秒，外层工具命令保守上界{external:.7f}秒，相加{timing['conservative_combined_command_wall_seconds']:.7f}秒，嵌套重叠不退时，低于3600。runtime持有并集保守{held:.6f}秒，包含三次driver启动/清场微小余量；关闭资源之间不虚称持有。首三批命令10.7秒来自并行工具收据上界，其余按真实工具wall，CPU/阅读思考/间隙不伪造精确值。旧S07 30294.653691秒及8694.653691超额、metadata unknown原封不动。

本段delta：root1，Browser启动尝试3，build1，fixture server3，HTTP162，provider/费用0；累计roots25、Browser19、build8、fixture server3、HTTP2486。PG创建尝试/对象/卷各6、PGstart46、产品API33、Native140、preview创建/启动各2、provider及费用0全部保持。根25原截止内明确续作，26/27未开；没有再消费剩余预算补无关检查。

最后正常关闭证明为root-25/attempt-03/stop.json，UTC 2026-10-18T01:54:55.272724Z，child exit0、准确PID+birth无存活，18119无监听；final-resource-stop.json在封存时再核全部本段登记的离线子进程及浏览器子树，旧birth存活0，未杀同名用户进程。测试hub句柄随真实teardown或准确Job关闭释放，文件、profile、失败原件保留。原六PG/原owned/preview/selector不启动、修改、清理或实时观察；仅引用2026-10-16T15:45:05.045131Z历史停止原件，不冒当前PG现场状态。

## 精确差异、继承与待主控裁定

本段从S07初版新增/变化{len(changed_s08)}项；从TASK118审计基线累计变化{len(changed_all)}项，均在允许产品/测试/README范围。逐文件D归属与pre/post/raw hash/换行计数见post-source-manifest.json，S08-delta.diff供本次增量审阅，TASK118-four-repairs.diff把S07初版一并纳入四修复最终差异；统一diff仅规整换行展示，实际原字节与hash为准。as-run-final.json及各原as-run说明分段复用、命令退出码和当前源码绑定，final-binding.json绑定结果、最终源与关键原始证据。

旧617行恢复、PDF物理页、固定预览ACK/StopProof、两域持久业务和应用重开证据继续只按各自原字节/层继承，不整批重跑，不据本轮合成结果改成真实PG/供方通过。001—014、持久模型、frozen source/readonly selector、权限/退款/停止语义及依赖锁未动；未git commit/push或改远端，公开候选上传仍未执行。根README已同步S08准确候选状态，配置样例仍关闭。

建议由主控回原TASK118独立上下文一次增量复核四项实际diff、当前源码和必要反例；工程不代发聊天、不自签独审或正式缺陷关闭。工程候选终点已到，不继续优化或增开测试。Q仍需官方当期能力/价格/条款、正常本地secret loader、新normal合成库/控制根、真实PG roster SUM与两provider持久共享预扣组合证、实际受信清单/费率/72h及主控启用回执；原80次20元是未激活条件许可，不重问、不消费，旧账及source冻结不解除。STEP018整体、后续STEP和项目验收仍由主控依有效审计裁定。

以下保留原S07及更早结果88265字节，原SHA256 fc600e1381e44542fc933bdd294e471e2e1a5d4b70b979a5a2be708878993aab，历史结论与本轮工程候选分层阅读。

---

'''
    assert '*' not in prefix
    result.write_bytes(prefix.encode('utf-8')+old)
    raw=result.read_bytes();assert raw[-88265:]==old and raw[:len(prefix.encode('utf-8'))].decode('utf-8')==prefix
    important=['receipt.json','post-source-manifest.json','S08-delta.diff','TASK118-four-repairs.diff','as-run-final.json','network-timeline.json','screenshots.json',
      'control-selfcheck.json','final-timing.json','final-resource-stop.json','final-budget-observed.json','bundle-8.json','browser-as-run.json',
      'backend-targeted.log','backend-targeted-v2.log','async-stack.log','backend-no-io.log','model-scope-v2.log','approved-model-final.log','typecheck.log','build-8.log',
      'root-25/proof.json','root-25/attempt-02/proof.json','root-25/attempt-03/proof.json','root-25/attempt-03/stop.json','tool-receipts-final.json']
    binding={'sample':sample(),'result':str(result),'bytes':len(raw),'sha256':sha(raw),'prefix_bytes':len(prefix.encode('utf-8')),
       'old_suffix_bytes':88265,'old_suffix_sha256':sha(raw[-88265:]),'full_byte_reread':True,'Q':'FROZEN',
       'status':'FOUR_REPAIR_ENGINEERING_CANDIDATE_FOR_TASK118_INCREMENTAL_REVIEW','D01_methods':12,'D02_methods':21,'browser_cases':8,
       'evidence':[{'path':str(N/name),'bytes':(N/name).stat().st_size,'sha256':sha((N/name).read_bytes())} for name in important]}
    binding['evidence'].append({'path':str(N/'tool-receipts-at-seal.json'),'bytes':(N/'tool-receipts-at-seal.json').stat().st_size,'sha256':sha((N/'tool-receipts-at-seal.json').read_bytes())})
    write(N/'final-binding.json',binding)
    event('S08_returned_engineering_candidate',result_sha256=binding['sha256'],old_suffix_sha256=sha(old),Q='FROZEN',independent_review='NOT_SELF_SIGNED')
    print(json.dumps({k:v for k,v in binding.items() if k!='evidence'},ensure_ascii=False))

if __name__=='__main__':main()
