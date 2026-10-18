"""登记已取得的ROOT01原始工具结果与静态加载身份，不重跑成功检查。"""
import hashlib
from control import ROOT,HERE,write,event,failure,end_root,state,sample

folder=HERE/'root-01'
paths=['backend/tests/test_step018_embedding_contracts.py','backend/app/capabilities/embedding.py',
       'backend/app/capabilities/contracts.py','backend/app/capabilities/gateway.py','backend/app/capabilities/transport.py',
       'backend/app/retrieval/contracts.py','backend/app/worker/one_call.py','backend/app/worker/worker_main.py','backend/app/runtime.py']
identities=[{'path':x,'bytes':(ROOT/x).stat().st_size,'sha256':hashlib.sha256((ROOT/x).read_bytes()).hexdigest()} for x in paths]
write(folder/'unit-result.json',{'entry':'python -X utf8 -m unittest discover -s tests -p test_step018_embedding_contracts.py -v',
      'tool_chunk':'8fc4e4','tool_exit_code':0,'tests':12,'reported_test_seconds':0.064,'reported_result':'OK',
      'layers':['真实产品纯逻辑','明确最低合成传输'],'scope':'typed wire v4/旧v3、float32/007、结构反例、UNKNOWN和record不确定、收费前拒/RRF',
      'not_proved':['真实PG事务/ACL','Windows SUP物理链','UI','真实供应商能力/语义'],
      'actual_provider_calls':0,'actual_fee':0,'as_run_source':identities,'recorded':sample(),
      'reuse':'此源码/方法稳定部分后续引用，不默认重复12方法'})
failure('ROOT01-loopback-platform','已采accept/socket._fallback_socketpair阻塞栈。Selector工厂在沙箱外0.542秒创建关闭，受限环境内挂起；实际平台边界已定位。新测试原默认循环遗漏已改现有Selector工厂。',
        effect='两个受限工具session均已Ctrl-C结束/exit1；沙箱外12方法OK。原90秒失败、缺子PID/输出不改写，不复活旧runner。')
event('root01_confirmed',tool_chunk='8fc4e4',tests=12,diagnostic_outside_chunk='dc3dff',provider_calls=0,fee=0)
end_root(result='12 methods OK after grounded fixture/platform correction; earlier failures retained')
