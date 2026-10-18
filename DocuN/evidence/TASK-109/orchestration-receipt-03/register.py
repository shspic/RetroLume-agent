"""登记C02环境阻断与C03合并修正验证；不执行原型或重启容器。"""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import hashlib
import json
import time

ROOT=Path(r"D:\shspic\project_NO3_RetroLume-agent")
BASE=ROOT/"DocuN/evidence/TASK-109"
HERE=BASE/"orchestration-receipt-03"
OUT=BASE/"orchestration-continuation-03-20261009"
NOW=datetime.now(timezone(timedelta(hours=8))).isoformat()


def sha(data): return hashlib.sha256(data).hexdigest()
def load(p): return json.loads(p.read_text(encoding="utf-8-sig"))


def save(name,obj):
    p=OUT/name; assert not p.exists(),"先核已有断点，不覆盖"
    p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")


def main():
    receipt=load(HERE/"receipt.json"); current=load(HERE/"current-baseline.json")
    assert len(current)==494 and not OUT.exists()
    for rel,expected in current.items(): assert sha((ROOT/rel).read_bytes())==expected
    report=ROOT/"DocuN/results/TASK-109-result.md"; assert sha(report.read_bytes())==receipt["report_sha256"]
    paths=[ROOT/"DocuS/执行动态文档.MD",ROOT/"DocuS/架构动态文档.MD",ROOT/"DocuS/文档变更记录.MD",ROOT/"DocuN/tasks/TASK-109.md",ROOT/"DocuN/results/TASK-109-work-decision.md"]
    state_path,arch_path,ledger_path,card_path,work_path=paths
    old_state,old_arch,old_ledger,old_card,old_work=[p.read_bytes() for p in paths]
    assert "文档 v2.26".encode("utf-8") in old_state[:500] and "文档 v1.04".encode("utf-8") in old_arch[:500]
    assert b"CHG-1083" in old_ledger and b"CHG-1084" not in old_ledger
    draft=(HERE/"proposed-continuation-03.md").read_bytes(); text=draft.decode("utf-8")
    sections=["目标与交付","项目、规则与接收安排","背景与最小充分上下文","执行边界与资源","验证、证据与审计关系","停止与回传","必要人工与待同步信息"]
    assert all("## "+s in text for s in sections) and "*" not in text and "|" not in text
    OUT.mkdir(parents=True)
    for p,data in zip(paths,[old_state,old_arch,old_ledger,old_card,old_work]):
        dest=OUT/"before"/p.relative_to(ROOT); dest.parent.mkdir(parents=True,exist_ok=True); dest.write_bytes(data)
    budget={"action_permit":"TASK-109-G11-C03-20261009","new_root":1,"new_preview_attempts_max":2,"new_controllers_max":2,
        "second_attempt":"仅首完整错误明确支持的本卡普通环境修正；不自动第二次",
        "seconds":{"active_subwindow":1800,"metadata":500,"real_root":600,"offline":120,"cleanup":300,"preview_each":60,"preview_total":120,"diagnostic_each":15},
        "offline_batches_max":2,"offline_each":60,"original_start_ns":774301594189000,"original_deadline_ns":795901594189000,
        "remaining_original_seconds_at_registration":max(0,(795901594189000-time.monotonic_ns())/1e9),"deadline_extension":False,
        "old_global_roots":74,"old_task_roots":4,"cumulative_root_cap":8,"cumulative_H0_root_cap_amended":5,
        "cumulative_preview_cap":16,"old_preview_used":1,"old_controller_used":1,"cumulative_controller_cap_amended":3,
        "imagebuild_used_limit":"2/2封存，新save/build/load/tag0","new_research_pages":0,
        "no_sandbox_seccomp_resource_relaxation":True,"old_failures_time_fees_not_reset":True,
        "zero_new":["PG","SQL","profile_model","API_UI","image_build","install_new_engine","provider_fee","Git"],"new_used":0}
    save("verification-budget.json",budget)
    image=load(BASE/"orchestration-receipt-02/image-resource-readonly.json")["image"]
    save("continuation-input.json",{"at":NOW,"TASK":"TASK-109","R":"R-103","round":"C03","current_files":current,
        "report_before":{"path":str(report),"bytes":receipt["report_bytes"],"sha256":receipt["report_sha256"]},"immutable_image":image,
        "stopped_C02":load(HERE/"container-readonly.json"),"error_tail_chars":2000,"underlying_directory_or_errno_cause_unconfirmed":True,
        "actual_Node_browser_file":receipt["Chrome_file_actual_sha256"],"debug_and_directory_mechanism_refs":load(HERE/"diagnosis-scope.json"),
        "evidence_index":str(HERE/"evidence-identities.json"),"source_control":str(BASE/"execution/continuation-02/prepared-control.json"),
        "bootstrap_allowed":"固定受信tmpfs初始化+有限stderr+require原镜像counter，源码/argv冻结，不供页面/HTTP任意exec",
        "image_and_inside_JS_mutation":False,"business_frozen":True,"budget":budget})
    save("window-assignment.json",{"TASK":"TASK-109","R":"R-103","round":"C03","resource":"A+强推理","window":"原109业务窗口",
        "dispatch":"待转交","sent":False,"received":False,"started":False,"new_used":0,"independent107":"不实施/不泛审未齐业务"})
    work=f"""# TASK-109 / R-103 C02回收与启动环境合并收口C03

{NOW}，Codex编排Agent。C02报告37685字节/5a82ac39…和原27219后缀/旧sessions一致，原493对象不改、仅新控制入口一项现494。Node24.18.1/包1.62.1/UID10001/Chrome file0b20…/实际pid19已运行，Crashpad database错误在Browser之前，2000字符截断；不能唯一归因HOME/XDG，也不是导航反证。

精确CID5bd9e24d…已kill9/die137/wait137/Pid0/restartno/attach和线程退出，主控只读核仍Stopped。普通接受加载与精确停止子事实，不签Browser/sandbox或平台物理全树验收，namespace推断待审保持。旧rootR04ERROR/计数74、real4.656含stop1.000/window3.047、active958.5/metadata300保守/offline0.015/cleanup30保守、build2/2封存与累计85.797含build27.017旧重叠/13元不返。

同原109/R103续作03合并明确原容量tmpfs的运行home/XDG/uidgid可写目录、完整有界browser stderr与一项有据普通修正，Browser就绪在同容器直接续原探针/收尾，不把环境和page再拆卡。原HOME声明缺/临时目录活权限未观测是需要核证的条件，官方通用文档只是机制指引，不冒151唯一根因。禁止disable Crashpad/sandbox/加cap/改seccomp资源或换engine。

新action许可TASK-109-G11-C03-20261009，只补一个rootR05/实际后累计75。preview02/03最多两个、各一次create/start/60s，第二个仅完整错误给独立证据的本卡目录条件修正且第一确认停；controller最多2，计原root8/preview16，H0累计4→5/controller总cap2→3明确修订，旧1用量不返。active子窗1800/metadata500/rootreal600/offline120（最多2批各60）/cleanup300/每诊断15，原start774301594189000/deadline795901594189000不延；原截止过则不运行，研究新0。

权限不扩大：镜像aa824/confige881及内JS/包/binary/seccomp固定，新save/build/load0；受信bootstrap仅原/tmp128MiB与home32MiB内mkdir/mode/probe和require原counter，采用明确node entrypoint固定源码hash，不接页面/model/HTTP表达式，不提供通用exec。HOME/XDG/tmpfs UID10001/mode0700收紧是普通启动环境，readonly/networknone/capdrop/NNP/privateIPC/768MiB/pids128等保持；DEBUG只browser类别/有限stderr无Env秘密，不改现有安全flags。

根内合并合理有据修复但不盲重复；新kernel/版本/权限/资源条件越域即交具体差异，不解冻PG/profile/model/API/UI。任何probe首次反证仍停，NOT_FULL_H0不能改FullPass；新主要方案/原生组件另裁，原G11-P不重问。旧preview01保留Stopped不复活，原件/cache/image/source旧数据不删不重写。

本卡已完整保存回读待原109A+人工接收，新实际0，无真实开始；原107仍独立、110未占未派。业务和B01/SEC003/STEP/M1/项目仍未通过，主控本次只有普通核证/共享维护，产品/SQL/测试/build/启动0。

## 以下为109首轮及C01/C02原裁定历史

"""
    work_path.write_bytes(work.encode("utf-8")+old_work)
    arch=f"""# 架构动态文档

文档 v1.05，2026-10-09，Asia/Shanghai。需求v1.1、唯一执行动态v2.27。C02真实Node/Chrome spawn与精确停止成立，Crashpad启动错误截断，Browser/权限探针未运行；C03合并环境收口待转交，业务冻结。下面v1.04及历史原字节保留。

## 真实环境阻断与有限普通修正

现image aa824/confige881实际Node24.18.1/Playwright1.62.1/UID10001、binary0b20…加载，Chrome pid19启动但Crashpad报必需database；无Browser/CDP/有效sandbox/page原件，container Seccomp2不能替Browser证明。错误2000字符截断及无stderr导致errno/路径根因未核，不误写HOME为唯一原因或导航已反证。

精确CID外部kill/wait/die/EOF/Pid0与namespace事实分层，Stopped是真实子事实，完整cgroup空仍未直接取证/推断待审保持。image/build/cache与未改G10保护证据继承不重做。

C03在原bounded tmpfs内明确用户home/XDG/所有权和完整stderr，以固定可信bootstrap再进入原image counter；只允许一有据环境修正，Browser ready后同容器直接真实probe与停止。UID/readonly/NNP/seccomp/privateIPC/memPID不松、不禁crash/sandbox/no image变化、业务仍0；诊断器未有完整同步守卫不签放行，任何越域条件或反证交具体最低改变。

## 以下为v1.04及更早历史

"""
    arch_path.write_bytes(arch.encode("utf-8")+old_arch)
    state=f"""# 执行动态文档

文档 v2.27，2026-10-09，Asia/Shanghai。唯一总状态账；需求v1.1、架构v1.05、task_model/阶段07。下面v2.26及全部历史原字节保留。

## C02真实加载但Crashpad阻断；C03合并环境修正与probe待转交

109/R103 C02已实际返回37685字节/5a82ac39…，原27219/15176精确历史与old sessions保持；493不改，仅新16194字节控制入口/420ef45a…共494对象。实际Node24.18.1/PW1.62.1/UID10001/binary0b20…/Chrome spawn19成立，Crashpad --database必需错误截到2000字符且stderr空；未有Browser/CDP/有效sandbox/网页动作，不能签权限反证或根因唯一HOME。

新CID5bd9e24d…/preview01真实create/start且原资源不松，外部kill0/wait137/kill9-die137/attach137和线程闭合，Stopped/Pid0/restartno真实成立，原namespace结束推断/cgroup未直接核验范围保留。主控当前只读核该CID仍Stopped，未启动/exec/测试/build。普通采纳加载/精确停止子事实，R04ERROR不改色，完整H0/B01/SEC003/G11/STEP/M1/项目未过。

累计root74不是74PASS、TASK109roots4/8/H0修订4/4、build2/2封存、preview/controller各1；C02 real4.656含stop1.000/window3.047、active958.5上界/metadata300预留/offline0.015/cleanup30保守，累计real85.797含build27.017子段不再加，所有旧FAIL/ERROR/UNKNOWN/2700.7与1693.1及600metadata/13元保持。旧raw/OCI/image/source及tmpfs现场可观测限制不重置不补造。

现问题为普通启动环境待核，指定home/XDG仍未有活目录UID/mode/可写证据，旧tmpfs没有显式uid/gid；generic Crashpad文档与旧Chromium路径文档只是机制指引，不是固定151因果实证。不能从2k截断选唯一原因，不能禁sandbox或crash reporting绕过。

同109/R103 C03完整七节已保存待人工转交至原A+，新增实际0、未真实接收/开始。一次合并明确原容量home/tmp目录/用户权限及stderr、确有新证据的一次卡内修正，Browser就绪同容器直接续旧固定probe/停止，不再环境返回后另卡页测试。新固定bootstrap仅受信目录初始化/probe+require原counter，argv/sourcehash冻结，不接HTTP/模型/页面cmd；镜像/内JS/包/seccomp冻结，新save/build0。

action许可TASK-109-G11-C03-20261009补root1/R05（实际后累计75）、preview02/03最多各一次create/start/runtime60，第二个只完整错误支持目录纠正且第一确认停；controller≤2，累计controllercap2→3（旧1不返）、H0cap4→5、原root8/preview16保持。首读active1800/metadata500/rootreal600/offline120最多2批60/cleanup300/每诊断15，原start774301594189000/deadline795901594189000不延，旧截止过不运行，官方研究新0。

UID10001/readonly/原tmpfs容量128+32MiB/nosuid-nodev-noexec/NNP/capdrop/networknone/privateIPC/SHM64MiB/CPU1/768MiB+pids128/无mountsocketportsecret保持，tmpfs uidgid/mode0700仅收紧。HOME/XDG实际service键只容器内同用途，host全局Env不改，pw:browser有限stderr最多64KB/末尾16KB、原2k错误保持。第一成功即probe、不用第二attempt；无新因果或kernel/权限/资源/版本越域即停，第二次仍败停，Root总期不延。

业务PG/四表/role/profile/API/UI/main-browser/native模型/provider/install/fee/Git0。旧preview01与106/103/100/088保留不重启，两个new容器停后保留；不rm/prune/DROP/DELETE/sysctl/daemon/store或全局kill。G11-P原采用及先关口序不重问，真正新组件/信任模型改变才给准确差异，counter无反证也NOT_FULL_H0不签整包。

原107仍独立/110未占未派，旧G10/DEF024—026/E106-SEM有限关闭/O107观察/原R20/recoveryfalse/归档/规则/原始需求不改。HTML、退出恢复、实际provider/检索、Compose-Linux-Nginx边界及最终自用/完整Must/M1/项目仍按原路线未签，不能拿Node真实运行代整个HTML闭环。

本批CHG1084—1094，下一CHG1095。用户只需转当前109C03前缀到原109A+并带回同结果路径，当前没有新实际运行事实或重复采用问题。

## 以下为v2.26及更早历史

"""
    state_path.write_bytes(state.encode("utf-8")+old_state); card_path.write_bytes(draft+b"\n\n"+old_card)
    entries=[(1084,"DocuN/evidence/TASK-109/orchestration-receipt-03/receive.py","纯文件/own CID只读回收C02，未exec或重启。"),
        (1085,"DocuN/evidence/TASK-109/orchestration-receipt-03/receipt.json","37685报告/494源/Node真实与Chrome未ready、Stopped子事实分层，R04ERROR与旧账保留。"),
        (1086,"DocuN/evidence/TASK-109/orchestration-receipt-03/diagnosis-scope.json","Crashpad父目录一般机制与2k截断未知范围，不造151唯一根因，原权限不松。"),
        (1087,"DocuN/results/TASK-109-work-decision.md","置顶C03合并完整stderr/有限tmpfs规范环境/一有据修正及成功同容器probe，原裁定保字节。"),
        (1088,"DocuS/架构动态文档.MD","v1.05真实加载与Crashpad阻断，受信bootstrap普通环境/场景权限不同，不签H0。"),
        (1089,"DocuS/执行动态文档.MD","v2.27实际74根/C03待转交新0/H0和controller明确限额修订，原总期限不延。"),
        (1090,"DocuN/tasks/TASK-109.md","七节C03环境与真实probe整卡，不再按目录/启动/网页拆转，保旧前缀和原卡字节。"),
        (1091,"DocuN/evidence/TASK-109/orchestration-continuation-03-20261009/continuation-input.json","494源/image/实际Chrome文件/错误停止、仅安全Env键声明与目录未观测范围。"),
        (1092,"DocuN/evidence/TASK-109/orchestration-continuation-03-20261009/verification-budget.json","补一root/至多两有据预览/两controller，原计数不返/总deadline不改，business0。"),
        (1093,"DocuN/evidence/TASK-109/orchestration-continuation-03-20261009/window-assignment.json","原109A+强推理待人工转交，107隔离，新使用和实际派发开始0。"),
        (1094,"DocuN/evidence/TASK-109/orchestration-continuation-03-20261009/delivery-proof.json","七节/494源/旧完整报告/旧卡与共享历史/权限子限对应回读，main产品运行0。")]
    proof={"at":NOW,"TASK":"TASK-109","R":"R-103","round":"C03","prefix_bytes":len(draft),"prefix_sha256":sha(draft),
        "card_sha256":sha(card_path.read_bytes()),"sections":sections,"old_card_suffix_exact":card_path.read_bytes().endswith(old_card),
        "report_unchanged":sha(report.read_bytes())==receipt["report_sha256"],"sources_unchanged":len(current),
        "shared_history_exact":{"state":state_path.read_bytes().endswith(old_state),"arch":arch_path.read_bytes().endswith(old_arch),"work":work_path.read_bytes().endswith(old_work)},
        "business_frozen":True,"old_deadline_unchanged":True,"new_used":0,"dispatch":"待转交","CHG":"1084—1094","next_CHG":1095,
        "main_product_build_SQL_test_start":0}
    assert all(proof["shared_history_exact"].values()) and proof["old_card_suffix_exact"] and proof["report_unchanged"]
    for rel,expected in current.items(): assert sha((ROOT/rel).read_bytes())==expected
    save("delivery-proof.json",proof)
    assert all((ROOT/rel).exists() for _,rel,_ in entries)
    ledger_path.write_bytes(old_ledger+("\n\n"+"\n\n".join(f"- CHG-{n:04d}，{NOW}，Codex编排Agent，{rel}。{desc}" for n,rel,desc in entries)+"\n").encode("utf-8"))
    assert ledger_path.read_bytes().startswith(old_ledger)
    print(json.dumps({"card":str(card_path),"prefix":len(draft),"sources":len(current),"state":"v2.27","arch":"v1.05","next_CHG":1095,
        "whole_environment_and_probe":True,"dispatch":"待转交","main_runtime":0},ensure_ascii=False))


if __name__=="__main__": main()
