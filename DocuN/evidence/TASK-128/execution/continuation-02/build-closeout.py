from pathlib import Path
E=Path(__file__).absolute().parent
s=(E.parent/'finalize.py').read_text(encoding='utf-8').replace('R=E.parents[3]','R=E.parents[4]')
s=s.replace("allowed=['deploy/initialize_normal.py','backend/tests/test_normal_install.py','deploy/normal-install.md','README.md']","allowed=['deploy/normal-install.md','README.md']")
s=s.replace("[E,E/'entry-04',E/'entry-05',E/'entry-05-ready']","[E,E/'entry-07',E/'entry-08']")
s=s.replace("'api_holding_seconds':0","'api_holding_seconds':sum(v['seconds'] for v in state['api_intervals'])")
s=s.replace("'diagnostic_did_not_apply':True","'source_apply_replayed':False,'planned_interrupted_apply_performed':True")
s=s.replace("state=json.loads((E/'checkpoint.json').read_bytes())",'''state=json.loads((E/'checkpoint.json').read_bytes())
# 首次停止断言失败，持有上界延长到随后全部PID不存在的证据写入时刻。
first=state['api_intervals'][0]
confirmed_epoch=(E/'api-stop-diagnosis.json').stat().st_mtime
original_seconds=first['seconds']
first['parent_exit_observation_seconds']=original_seconds
first['seconds']=max(original_seconds,confirmed_epoch-first['start_epoch'])
first['stop_confirmation_basis']='api-stop-diagnosis.json filesystem write time; conservative upper bound, exact child exit time unknown'
first['stopped']=datetime.datetime.fromtimestamp(confirmed_epoch,datetime.timezone.utc).isoformat()
(E/'holding-adjustment.json').write_text(json.dumps({'original_parent_interval_seconds':original_seconds,'conservative_first_api_holding_seconds':first['seconds'],'cumulative_api_upper_bound_seconds':sum(v['seconds'] for v in state['api_intervals']),'raw_diagnosis_preserved':True},indent=2),encoding='utf-8')
(E/'checkpoint.json').write_text(json.dumps(state,ensure_ascii=False,indent=2),encoding='utf-8')
pid_rows=[]
for interval in state['api_intervals']:
    for old in interval.get('processes',[]):
        try:
            ref=w.ProcessRef(old['pid']);same=ref.birth==old['birth'];alive=ref.alive()
            assert not same or not alive
            pid_rows.append({'pid':old['pid'],'expected_birth':old['birth'],'same_birth':same,'alive':alive});ref.close()
        except OSError as error:
            assert error.errno==87
            pid_rows.append({'pid':old['pid'],'expected_birth':old['birth'],'already_absent':True})
(E/'final-api-process-check.json').write_text(json.dumps(pid_rows,indent=2),encoding='utf-8')''')
(E/'closeout.py').write_text(s,encoding='utf-8')
