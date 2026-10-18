"""只读身份核对、续写报告原字节后缀并保存真实交付账。"""
import datetime as dt
import hashlib
import json
from pathlib import Path
import re
import time

ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).resolve().parent
def sha(raw):return hashlib.sha256(raw).hexdigest()
def save(name,value):(OUT/name).write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf-8')

def main():
    report=ROOT/'DocuN/results/TASK-115-result.md'
    old=(OUT/'prior-result.md').read_bytes()
    assert len(old)==37767 and sha(old)=='7d34ec7e7f433effe3bf51367c68229a566dc525361a30c4b2c496702f4ca67a'
    assert report.read_bytes()==old
    prefix=(OUT/'review-prefix.md').read_bytes()
    links=re.findall(r'\]\((D:/[^)]+)\)',prefix.decode('utf-8'))
    missing=[]
    for value in links:
        p=re.sub(r':\d+$','',value)
        if p.endswith('/delivery.json'):continue
        if not Path(p).exists():missing.append(value)
    assert not missing,missing
    assert b'*' not in prefix
    before=json.loads((OUT/'protected-before.json').read_text(encoding='utf-8'))
    changed=[]
    for entry in before['files']:
        p=Path(entry['path'])
        if not p.is_file() or sha(p.read_bytes())!=entry['sha256']:changed.append(str(p))
    assert not changed,changed
    report.write_bytes(prefix+old)
    raw=report.read_bytes();assert raw[-len(old):]==old and raw[:len(prefix)]==prefix
    now=dt.datetime.now(dt.timezone.utc);mono=time.monotonic_ns()
    receipt=json.loads((OUT/'receipt.json').read_text(encoding='utf-8'))
    start=dt.datetime.fromisoformat(receipt['conservative_start_utc'].replace('Z','+00:00'))
    recorded=dt.datetime.fromisoformat(receipt['observed_utc'])
    elapsed=max((now-start).total_seconds(),(mono-receipt['observed_monotonic_ns'])/1e9+(recorded-start).total_seconds())
    receipt.update(final_observed_utc=now.isoformat(),final_observed_monotonic_ns=mono,
         review_active_seconds_conservative=elapsed,cumulative_active_seconds_conservative=5490.683454+elapsed,
         review_remaining_seconds=max(0,7200-elapsed),original_total_remaining_seconds=max(0,21600-5490.683454-elapsed),
         returned=True,master_acceptance='未填写')
    assert elapsed<7200 and receipt['cumulative_active_seconds_conservative']<21600
    assert all(v==0 for v in receipt['new_business_counts'].values())
    save('receipt.json',receipt)
    value={'utc':now.isoformat(),'report_path':str(report),'bytes':len(raw),'sha256':sha(raw),
      'prefix_bytes':len(prefix),'old_suffix_bytes':len(old),'old_suffix_sha256':sha(raw[-len(old):]),
      'old_suffix_preserved':True,'readback_complete':True,'protected_input_changes':changed,'broken_links':missing,
      'review_active_seconds_conservative':elapsed,'cumulative_active_seconds_conservative':5490.683454+elapsed,
      'new_business_counts':receipt['new_business_counts'],
      'suggested_def_closure':{'DEF034':'可关闭','DEF035':'暂不关闭','DEF036':'暂不关闭','DEF037':'可关闭'},
      'finite_STEP017_suggestion':'不通过/暂不关闭','master_final_acceptance':'未填写'}
    save('delivery.json',value)
    print(json.dumps(value,ensure_ascii=False))

if __name__=='__main__':main()
