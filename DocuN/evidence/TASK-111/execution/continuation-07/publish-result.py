"""保存续作07完整结果前缀，原146608字节全文作为原字节后缀保留。"""
import hashlib,json,os,time
from datetime import datetime,timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[5]
OUT=Path(__file__).resolve().parent
FINAL=OUT/'final'
def load(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def link(label,p):return '['+label+']('+str(Path(p).resolve()).replace('\\','/')+')'

def main():
    budget=load(FINAL/'budget-final.json');summary=load(FINAL/'candidate-summary.json');built=load(OUT/'active-build.json');timing=load(OUT/'timing.json')
    target=(ROOT/'DocuN/results/TASK-111-result.md').resolve();assert target.is_relative_to(ROOT.resolve())
    original=(OUT/'pre/DocuN__results__TASK-111-result.md').read_bytes()
    assert len(original)==146608 and hashlib.sha256(original).hexdigest()=='fcee65ac816c59e364f26c23d0feaec023b28a97b170e78785d16af19d4be5f4'
    assert target.read_bytes()==original,'仅允许对原完整结果追加本轮前缀一次'
    source=load(FINAL/'source-identity.json')
    for row in source:assert sha(ROOT/row['path'])==row['sha256'],row['path']
    audit=ROOT/'DocuN/results/TASK-112-result.md';assert sha(audit)=='ea51e0f49f556fd6f07aea11741d26099a534550850c0c68dfa49a9ab4c3b522'
    late=load(OUT/'root-19/late_ready/actor-result.json');early=load(OUT/'root-19/late_ready/late-ready-read-complete.json')
    normal=load(OUT/'root-19/normal_bom_header/actor-result.json');ready=load(ROOT/'DocuN/evidence/TASK-111/execution/continuation-04/synthetic/control'/normal['row']['preview_id']/'ready.json')
    stderr=load(OUT/'root-19/stderr_overflow/actor-result.json');unknown=load(OUT/'root-20/stderr_no_eof/actor-result.json');recovered=load(OUT/'root-20/stderr_no_eof/same-root-persistent-recovery.json')
    end=time.monotonic_ns();utc=datetime.now(timezone.utc).isoformat()
    assert end<timing['deadline_ns'] and budget['budget']['active_batch'] is None
    prefix=f'''# TASK-111 / R-105 续作07结果

三项终审缺陷的范围内修正、E112-01一次保守核销和六个定向验证方法已经完成，作为工程候选交回原TASK-112/R-106窗口增量独立复核。本窗口不裁定DEF关闭，不自签G11、SEC003/B01、STEP、M-1、项目验收或发布。原112审计仍是未关闭结论，后续复核尚未运行。

本轮为A+工程角色，Codex desktop，系统身份GPT-6，精确子型号没有可核工具。用户要求接续原111续作06工程窗口；客户端未提供可核窗口ID，因此记录该接续指令及从现行卡、完整旧结果和冻结原件恢复的事实，不冒称工具确认窗口同一性。没有子Agent，没有与112并行写产品或运行资源，没有新TASK/R。

工程许可TASK-111-G11-C07-20261012，基础HostPolicy仍TASK-111-G11-P110-20261010。根D:/shspic/project_NO3_RetroLume-agent，task_model、V4.0/公共AGENTS CHG-0003。正文读取项目入口、公共AGENTS及WORK适用2/6/8章、现行卡、112三缺陷和执行账、现有相关实现；七个锁定规则指纹均实核一致。卡面基线需求v1.2、架构v1.20、执行动态v2.42、阶段07。公共库、DocuS、用户原始需求及旧审计原文未改。

结果保存于{target.as_posix()}。此后所接的旧全文为146608字节，SHA256 fcee65ac816c59e364f26c23d0feaec023b28a97b170e78785d16af19d4be5f4，以原字节后缀保留。新增工程证据位于{OUT.as_posix()}；唯一产品控制registry仍是continuation-04/synthetic/control，新增生命周期运行事实按产品正常路径登记在同根，冻结证据和交接索引在C07，不另建控制根。

## 差异和版本

实际产品只改production_supervisor.py、pipe.py、renderer-protocol.cjs。工程夹具只改control.py、core.py并新增七个c07定向脚本。C06的105项源身份中100项一致、5项对应上述改动，另有必要的新load-manifest及v2-08构建目录。{link('完整源身份',FINAL/'source-identity.json')}、{link('差异索引和旧新hash',FINAL/'change-index.json')}、{link('五个实际修改差异',FINAL/'source-diff')}给出实际路径和指纹。

本轮未改001—012、SQL/ACL/角色域、持久模型、四账/worker、前端产品及既有bundle、四runtime、数学语言或用户配置。HostPolicy的UID10001、network none、read-only、CapDrop ALL、NNP、seccomp、private PID/IPC、init、no restart、1CPU/1GiB/同值swap、pids256、SHM64MiB、128+32MiB安全tmpfs不变。没有安装、联网下载、pull、clone、依赖或许可证扩张，没有Git写入、删除或发布。

新image为{built['image']['id']}，tag {built['tag']}，load SHA256 {built['load_manifest_sha256']}，四runtime集合仍{built['renderer_sha256']}。真实本地OCI缓存build/load一次，651项新load资源逐字节匹配；新宿主及时ready实际绑定Node {ready['node']}、PW {ready['playwright']}、{ready['version']['product']}、原内核及隔离参数，未用v2-07旧load签新代码。{link('真实build/load及镜像投影',OUT/'root-19/build/production-build.json')}和{link('新load完整核对',FINAL/'load-manifest-verification.json')}保留原件。

## DEF-031 / F112-01

完整ready返回后立即保存真实monotonic接收时刻。身份正确的迟到包保留kernel和原packet；收到事实与提交资格分开。实际成功Event.wait之后再核接收时刻、当前时窗和stop标志，范围仍为原min(t0+8秒,D-10)，边界相等关闭。已resume对象仍走started停止，逾期不提交ready，不授输入资格，不退start次数。

离线六样本实际调用产品_read和_wait_ready，覆盖及时、精确边界、迟到成功wait、Event成功后stop、调度延迟当前窗闭以及D-10边界。它们使用确定替身单调时钟和实际本地匿名管道，只算门级离线证据，不冒真实调度频率。{link('六样本及采样含义',OUT/'offline-01/ready/ready-offline-result.json')}。

真实迟到方法延迟同一实际attach stdout的ready body读取，未改本机或DB时钟。原t0 {early['t0_ns']}ns，ready完整接收{late['result']['ready_received_ns']}ns，相对t0 {(late['result']['ready_received_ns']-early['t0_ns'])/1e9:.6f}秒，超过原8秒；ready_accepted_ns为null。实际合法header/body和hash、读入前后时刻、bootstrap及kernel均保存。持久状态没有ready/running，实际输入门拒绝source_invalid、未向管道提交；停止为stopped，elapsed {late['row']['elapsed_seconds']}、reserve60，双EOF、Linux/init/die/wait和两Job完整。{link('迟到真实方法',OUT/'root-19/late_ready')}。

## DEF-032 / F112-03

stdout与stderr分别记录实际空读EOF和读异常，不把线程退出、文件写成或Pid0当EOF。stderr累计超8192立即stop、捕获最多8192，随后仍在原D+15诊断范围排空同一流；异常或未EOF不能结算。私有最终attach和持久结算门再次要求双EOF、无读异常及原完整Linux/kernel/nonce/事件/实例/两Job证明。没有新公开退款/API或持久模型。Python实际read异常以私有PipeReadError保留，后续真实空读也不消除异常事实。

离线九组实际读取及结算门覆盖空流、8192、8193、分块10000、读取异常、线程已退而stderr EOF=false、stdout缺EOF、读异常后EOF和stdout实际读取异常；缺证没有调用结算/退款。此处不是SQL事务证明。{link('九组门级原件',OUT/'offline-01/stderr/stderr-offline-result.json')}。

真实READY对象对准确PID及birth核实后，有限12289字节写入该Node的实际stderr fd，字节进入生产attach stderr流。实际观测{stderr['result']['pipe_observation']['stderr_observed_bytes']}字节，保留{stderr['result']['pipe_observation']['stderr_captured_bytes']}字节，超限stop后排空取得真实stderr和stdout EOF，完整停止及真实PG结算成功，elapsed {stderr['row']['elapsed_seconds']}秒。{link('实际stderr注入、有限保存和双EOF',OUT/'root-19/stderr_overflow')}。

必要真实未EOF方法预先绑定准确对象、birth、原D、kernel和PassiveWitness真实读副本，只持同步进程和读端，不持额外Job/写端，不与存活reader争读。关闭实际stderr读端后对同一读端实际read产生ValueError；原SUP的stderr EOF=false、stdout EOF=true，原停止收据未确认，持久cleanup_unconfirmed、elapsed null、R60保持，新start拒绝。之后原parent真实结束，独立读副本观察真实双EOF，同一registry恢复并全R60结算，没有未知提前退款，也未使用外部kill冒自主成果。成功复验before为{recovered['before']['state']}，after为{recovered['after']['state']}，elapsed {recovered['after']['elapsed_seconds']}。

首个未EOF夹具漏closed接口，真实JobChild.close出现AttributeError，结果文件发布检查失败；失败原件保留，物理已止和真实读副本仍支持同根全R60恢复。只补夹具closed属性，在root20只复验该方法，没有重做已通过五方法或新build。{link('原失败及全R恢复',OUT/'root-19/stderr_no_eof')}、{link('夹具单点修正依据',OUT/'repair-01')}、{link('最终真实未EOF/拒绝退款/同根恢复',OUT/'root-20/stderr_no_eof')}。

## DEF-033 / F112-02

Node实际validateInit集中区分constraints缺省与存在键，存在必须数组，null及其他非数组拒绝。原始JSON入口比较canonical UTF-8与原字节，UTF-8起始BOM不再被TextDecoder消除后混过门，合法字符串内部U+FEFF不删。Python防线、四runtime和SQL期望renderer身份不放宽。

十组Python/Node同域覆盖缺省、空数组、null、字符串、对象、数字、bool、内部U+FEFF，以及正确长度/hash的BOM header/body。Node离线加载实际renderer-host入口及其纯JSON、身份/hash、init、runtime校验链，只把浏览器启动截在固定标志；不把离线host框架当实机浏览器。最初跨realm夹具触发Object.prototype拒绝，原失败保留，改为同realm CJS wrapper后只复验Node方法。{link('Node实际入口十组',OUT/'offline-02-node/node/node-host-result.json')}、{link('Python实际入口十组',OUT/'offline-02-node/node/python-domain-result.json')}。

新加载宿主真实管道中，null init只改wire及正确description/hash，不向DB存非法artifact；实际Node拒绝description_constraints_type，未ready。BOM header/body在合法READY后的固定非法input包中注入，保原kernel/Job，实际protocol_failed停止、无非法input ACK。header方法合法组合了必要正常对照，先及时ready、机械能h=4的远端ACK78.4和实际新PNG，再拒非法BOM header。{link('正常ACK',OUT/'root-19/normal_bom_header/actual-normal-ACK.json')}、{link('实际PNG',OUT/'root-19/normal_bom_header/actual-normal.png')}、{link('null实际wire及拒绝',OUT/'root-19/null_init')}、{link('BOM body实际wire及拒绝',OUT/'root-19/bom_body')}。

这些新真实方法只证明本次变化的相关边界；不冒模型Native质量、公开HTTP、UI、32边界或六停止全套新复测。公开输入旧索引措辞更正为21条记录等于17个远端成功ACK加4个422拒绝，拒绝不叫ACK，旧原件未改。

## E112-01和预算

保全原budget字节后追加唯一E112-01 adjustment。root6结束869276343000000ns到精确PG stop确认871556046000000ns，保守2279.703秒，原14546.863对齐16826.566；历史旧cap16200超626.566仍明确保留，未返counts/time/费用，未用新cap免责。该完整持有至确认是保守核销，物理停机瞬时未采，不冒连续每瞬精确观测。执行账中的adjustment只生效一次，不重新运行旧PG或回写旧日志。{link('唯一账调整和原件/hash/计算',OUT/'E112-01-adjustment.json')}。

C07从首个真实采钟2026-10-11T17:44:05.806977Z / 1012109906000000ns保留记录；首两次只读工具没有同步采首读钟，接收前段未知不填0。总窗在该实采前保守扣300秒，不把扣减冒真实首读；deadline {timing['deadline_ns']}ns、business deadline {timing['business_deadline_ns']}ns，综合14400、末600清场。metadata首次阶段包含初步实施，只有实际phase事件段可精确重建，不把它叫纯metadata。旧首读/分类/失败/offline27缺终点及旧13元等仍保留原报告。{link('真实接收和缺口说明',OUT/'accepted.json')}、{link('本许可及实际phase时序',OUT/'timing.json')}。

新root19用155.328秒、root20用13.329秒，新增real合计168.657小于2400，当前累计16995.223对前向cap20400。build/load、PG持有、方法/等待和PG停止确认全部在各根区间并集中；两根之间PG已精确停止，cleanup在real根内重分类而不双计，没有漏记持有外围。当前前向real余2231.343、累计real余3404.777，但真实根20/20和PG start16/16已到本卡次数上限，不能据秒数余量开启新根或PG。

累计image8/9、preview create52/55/start48/51、PG1/1及卷1/1、PG start16/16、API12/12、主browser11/11、model9/10、Windows OneCall9/10、frontend4/5、HTTP1611/5000、公开PNG182/3000、公开input68/300、internal input30/500、offline分组34、Reaper分组2。新model/OneCall/API/主browser/frontend/公开HTTP均0；新内部input4、新preview尝试7，使用准确名56—62；63—65未用，失败次数不返。原两批事后离线和三笔迟记输入在原事件重算时继承独审依据，不伪造事前reserved。

最终整理脚本第一次重算漏加历史三笔迟记输入，统计断言失败，47对象/源/原件/两Job/端口核证已成功保存；只补统计继承项，无账更改，不重复物理检查。结果保存脚本先对只读句柄fsync遭Windows EBADF，原结果未覆盖，保全失败候选后改为写句柄flush/fsync再原子保存。五处本轮脚本/夹具错误、原例失败与对应修正均保留。{link('完整累计count/time和余额',FINAL/'budget-final.json')}、{link('区间19',OUT/'root-19/interval-accounting.json')}、{link('区间20',OUT/'root-20/interval-accounting.json')}、{link('统计修正原件',OUT/'delivery-repair-01')}、{link('保存同步修正原件',OUT/'delivery/sync-repair.json')}。

## 精确收尾和复用

当前47个已登记Docker对象为旧40加新7，精确id/name/image匹配、全部Stopped/Pid0/restart0。新7行均stopped，其中首未EOF失败与最终未EOF复验都按60结算；其他五行elapsed为9、11、8、6、7。每个新生命周期的DB确认与原receipt canonical一致，Linux/kernel/nonce/die/wait、真实双EOF或触发前被动读副本、两Job、准确拥有实例均有索引。所有本批登记实例结束或为后来的不同birth，global唯一锁可取得；18111与55451无监听，active_batch null。旧25/preview542b0750-6e02-418a-b216-5dfbd3b93047仍cleanup_unconfirmed/R60/count1，旧root blocked不清，库/卷/image/行/旧原件全部保留，没有停止daemon或用户进程。

{link('精确47对象和本批实例',FINAL/'exact-resources-final.json')}、{link('停止/两EOF/Job/DB一致性索引',FINAL/'stop-index.json')}、{link('端口原件',FINAL/'ports-final.json')}、{link('新7行',FINAL/'sessions-final.json')}、{link('旧UNKNOWN原样保持',FINAL/'old-unknown-kept.json')}、{link('六个采用方法和保留失败',FINAL/'case-index.json')}。

四runtime/编译包、原数学/图形、两Native、资格/前端迟到/隐藏/卸载/刷新、原32边界和不同故障的充分部分，按C06字节和112限定结论继承，不重放。新host的真实load及Node ingress、SUP时窗及EOF/结算门由本轮增量补足。BFCache、跨浏览器、真实provider/用户数据、自由脚本、任意导航全路径、cgroup删除或内存全释放、正式部署及完整项目验收不在本轮新增证据范围。

## 交回事项

原TASK112/R106窗口只增量核DEF-031/032/033、E112-01及实际变化传播，重点核成功wait双时刻、stderr真实EOF/异常保R和同根全R恢复、Node真实wire拒绝、651新load、as-run/source/diff、账与精确收尾。原五方法的actor文件只因未EOF私有夹具closed修正而有文件hash变化，该属性仅在stderr_no_eof方法使用；产品源和新image在root19/20间未变，勿机械重跑充分五方法。

主控随后维护DocuS、DEF/CHG及最终裁定，按真实增量复核结论决定G11关闭；本窗口只提交工程候选和实际预算，不派112、不改正式文档、不新建审批或发布权限。建议将架构的ready/EOF/Node数据门和新image/load身份同步，执行动态登记C07已返回待增量审查，历史626.566超限及旧UNKNOWN继续可查，最终需求不降Must。{link('当前候选摘要',FINAL/'candidate-summary.json')}和{link('全证据hash清单',FINAL/'evidence-manifest.json')}是最小交接入口，原112结果保持36048字节/SHA ea51e0f49f556fd6f07aea11741d26099a534550850c0c68dfa49a9ab4c3b522。

保存时间{utc}，单调{end}ns，保守工程窗已过{(end-timing['accepted_ns'])/1e9:.3f}秒。本段结束后为续作06及更早146608字节原全文，不改其历史措辞或结论。

'''
    delivery=OUT/'delivery';delivery.mkdir(exist_ok=True)
    new=prefix.encode('utf-8')+original
    temp=delivery/'result-candidate.bin'
    with temp.open('wb') as stream:stream.write(new);stream.flush();os.fsync(stream.fileno())
    os.replace(temp,target)
    actual=target.read_bytes();assert actual==new and actual[-146608:]==original
    proof=dict(path=str(target),bytes=len(actual),sha256=hashlib.sha256(actual).hexdigest(),prefix_bytes=len(prefix.encode('utf-8')),
        original_suffix_bytes=146608,original_suffix_sha256=hashlib.sha256(actual[-146608:]).hexdigest(),saved_utc=utc,saved_ns=end,
        original_TASK112_unchanged=sha(audit),actual_source_identity_match=True,active_batch=None,no_business_action_during_delivery=True)
    (delivery/'result-delivery-proof.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2),encoding='utf-8')
    entries=[dict(path=str(p.resolve()),bytes=p.stat().st_size,sha256=sha(p)) for p in OUT.rglob('*') if p.is_file() and p!=FINAL/'evidence-manifest.json']
    (FINAL/'evidence-manifest.json').write_text(json.dumps(dict(at_utc=datetime.now(timezone.utc).isoformat(),entries=entries),ensure_ascii=False,sort_keys=True,indent=2),encoding='utf-8')
    assert all(sha(Path(row['path']))==row['sha256'] for row in entries)
    print(json.dumps(proof,ensure_ascii=False))

if __name__=='__main__':main()
