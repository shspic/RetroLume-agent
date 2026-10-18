"""真实矩阵前冻结完整方法、独立对象、生命周期和停止预期。"""
import ast,hashlib,json
from uuid import uuid4
from .control import ROOT,CONTINUE_ROOT,atomic,batch,source_snapshot

def main():
    out=CONTINUE_ROOT/"matrix-preflight";out.mkdir(exist_ok=False)
    with batch("offline","C03-freeze-complete-real-methods",maximum=120):
        files=list((ROOT/"backend/tests/fixtures/task111").glob("c03*"))+list((ROOT/"frontend/tests/task111").glob("c03*"))
        for p in files:
            if p.suffix==".py":ast.parse(p.read_text(encoding="utf-8"))
        from .c03_faults import NAMES
        objects={}
        for key in ("domain_budget_group","minimum_reserve_reject","race_source","race_parent","race_memory","race_cancel",*("fault_"+n for n in NAMES)):
            objects[key]={"activity_id":str(uuid4()),"classification":"new retained C03 synthetic prerequisite through real producers"}
        objects["race_memory"]["memory_id"]=str(uuid4())
        capabilities=["hash","history","data","blob","file","http","https","popup","newframe","network","fetch","xhr","websocket","download","chooser","system","model_tool","markup","parent","top","named","form"]
        cases=[{"case":"core-repair","function":"c03_phase_a.probe","lifecycle":1,"method":"final production fixed script/frame, real ready<=8,58.8/zero/negative ACK+PNG+TreeProof"},
          {"case":"normal-N1-N2-and-late-guards","function":"c03_step.ui + c03_ui.cjs","lifecycle":4,"method":"two final Native same-object UI chains; two additional exact owner/view/generation lifecycles also cover persistent start budget"},
          {"case":"domain-budget-shared","function":"c03_matrix.boundaries + budgets","lifecycle":3,"object":"domain_budget_group","method":"domain/50000 limit; duplicate init; successful create discarded reply with concurrent same-key; all three share one activity immutable budget"}]
        for kind in ("source","parent","memory","cancel"):
            cases.append({"case":"cache-qualification-"+kind,"function":"c03_matrix.races","lifecycle":1,"object":"race_"+kind,"injection":"production frame local candidate captured before production _owner_row starts; await barrier; actual COMMIT invalidation; release","expected":"no frame/body/input; independent automatic stop and private init/EOF/CLI/Job proof"})
        for name in NAMES:
            cases.append({"case":name,"function":"c03_fault_actor.scenario + c03_faults.rescue","lifecycle":1,"object":"fault_"+name,
              "injection":name,"expected":"unconfirmed/full reserve/no new start then exact independent cleanup and persistent restart recovery" if name in ("both_supervisors_death","control_path_lost","hard_deadline") else "exact production stop, kernel/private init birth + CID/image/nonce + kill/wait/events + owned CLI/Job/EOF",
              "fault_variant":"one frozen image; never signed as production navigation proof"})
        value={"permit":"TASK-111-G11-C03-20261011","objects":objects,"cases":cases,"planned_remaining_baseline_lifecycles":sum(c["lifecycle"] for c in cases),
          "prior_C03_core_lifecycles":1,"prior_core_failure_retained":True,"prior_related_repair_charge":1,"new_names_only":"16..44 after used15",
          "capability_inputs":capabilities,"minimum_reserve_reject_lifecycles":0,"known_failed_same_cause_repair_count":{"literal_assembly":0,"frame_retention":1},
          "sources":[{"path":p.relative_to(ROOT).as_posix(),"sha256":hashlib.sha256(p.read_bytes()).hexdigest()} for p in files if p.is_file()]}
        assert value["planned_remaining_baseline_lifecycles"]==22
        assert value["planned_remaining_baseline_lifecycles"]+1<=30
        atomic(CONTINUE_ROOT/"matrix-plan.json",value);source_snapshot(out)
        atomic(out/"complete-method-preflight.json",{"status":"METHODS_PRESENT_FROZEN_NOT_YET_RUN","remaining_baseline_lifecycles":22,"overall_new_ceiling":30})
    print("C03 complete methods and22 lifecycle plan frozen")

if __name__=="__main__":main()
