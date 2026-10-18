"""一次接续前向工程许可并核销E112-01；原账、失败及旧截止全部保留。"""
import hashlib,json,time
from decimal import Decimal
from datetime import datetime,timezone
from .control import ROOT,EVIDENCE,C07_ROOT,atomic,locked,read_state,event

def main():
    out=C07_ROOT
    assert not (out/'timing.json').exists(), 'C07不得重复接收'
    accepted=json.loads((out/'accepted.json').read_text(encoding='utf-8'))
    scope=ROOT/'DocuN/evidence/TASK-111/orchestration-receipt-08'
    caps=json.loads((scope/'continuation-budget.json').read_text(encoding='utf-8'))
    adjustment=json.loads((scope/'PG-hold-disposition.json').read_text(encoding='utf-8'))
    for raw in adjustment['raw_files']:
        path=ROOT/raw['path'].replace('\\','/').split('project_NO3_RetroLume-agent/',1)[1]
        assert len(path.read_bytes())==raw['bytes'] and hashlib.sha256(path.read_bytes()).hexdigest()==raw['sha256']
    assert Decimal(adjustment['missing_hold_seconds'])==Decimal(adjustment['stop_confirmation_ns']-adjustment['root6_end_ns'])/Decimal(10**9)
    with locked():
        b=read_state();assert b['active_batch'] is None and b['counts']==caps['current_counts']
        assert not any(x.get('issue')=='E112-01' for x in b.get('execution_time_adjustments',[]))
        old=b['time_seconds']['real'];assert abs(old-float(adjustment['recorded_real_seconds']))<1e-8
        before=(EVIDENCE/'budget.json').read_bytes()
        assert before==(out/'pre/DocuN__evidence__TASK-111__execution__budget.json').read_bytes()
        row=dict(issue='E112-01',permit=caps['permit'],at_utc=datetime.now(timezone.utc).isoformat(),at_ns=time.monotonic_ns(),
            real_seconds_before=old,added_real_seconds=float(adjustment['missing_hold_seconds']),real_seconds_after=float(adjustment['conservative_real_seconds']),
            historical_cap_seconds=16200,historical_excess_seconds='626.566',basis=adjustment,prior_budget_sha256=hashlib.sha256(before).hexdigest(),
            not_retroactively_authorized=True,counter_changes=False)
        b.setdefault('execution_time_adjustments',[]).append(row);b['time_seconds']['real']=row['real_seconds_after']
        # 首读未采钟，明确保留缺口；总窗口在首个真实采钟前保守扣300秒，不冒精确首读。
        start=accepted['first_clock_ns']-accepted['conservative_window_margin_seconds']*10**9
        timing=dict(permit=caps['permit'],base_product_permit=caps['base_product_permit'],accepted_ns=start,
            accepted_utc=accepted['first_clock_utc'],first_sample_ns=accepted['first_clock_ns'],exact_first_read_clock_missing=True,
            conservative_window_margin_seconds=300,deadline_ns=start+14400*10**9,business_deadline_ns=start+13800*10**9,
            original_deadline_ns=b['deadline_ns'],hard_count_caps=caps['cumulative_caps'],prior_counts=b['counts'].copy(),
            prior_time_seconds=b['time_seconds'].copy(),new_real_limit_seconds=2400,cumulative_real_limit_seconds=20400,
            prior_authorized_work_seconds=129600,cumulative_authorized_work_seconds=144000,integrated_seconds=14400,
            cleanup_reserved_seconds=600,same_control_root=caps['same_control_root'],allowed_preview_names=caps['preview_names'],
            phase='metadata',phase_start_ns=accepted['first_clock_ns'],used_seconds=dict(metadata=0,implementation_offline=0,real=0,cleanup=0))
        atomic(out/'E112-01-adjustment.json',row)
        atomic(out/'timing.json',timing)
        atomic(out/'preview-name-plan.json',[str(n) for n in range(56,66)])
        b['prior_C06_deadline_ns']=b['deadline_ns'];b['prior_C06_business_deadline_ns']=b['business_deadline_ns']
        b['prior_C06_count_caps']=b['continuation_caps'];b['continuation']=caps['permit'];b['continuation_permit']=caps['permit']
        b['continuation_caps']=caps['cumulative_caps'];b['deadline_ns']=timing['deadline_ns'];b['business_deadline_ns']=timing['business_deadline_ns']
        atomic(EVIDENCE/'budget.json',b)
    event('C07_received_and_E112_01_adjusted',dict(adjustment=row,timing=timing),cleanup=True)
    check=read_state();assert sum(x.get('issue')=='E112-01' for x in check['execution_time_adjustments'])==1
    assert abs(check['time_seconds']['real']-16826.566)<1e-8
    print(json.dumps(dict(status='C07_FORWARD_PERMIT_AND_SINGLE_ADJUSTMENT',real=check['time_seconds']['real'],counts=check['counts'],deadline_ns=check['deadline_ns'])))

if __name__=='__main__':main()
