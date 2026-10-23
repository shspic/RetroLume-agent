"""Private approval clocks. Unknown boot/clock domains never authorize a send.

Windows QPC is system wide. A boot GUID distinguishes its otherwise undefined
epoch across boots, including API/operator/worker process restarts. The native
boot information query is optional: an unsupported/ambiguous result closes Q.
No clock is set, and no clock information enters a provider request.
"""
import ctypes
from datetime import datetime, timezone
import os
import time
from uuid import UUID

from .contracts import DataError, digest


def domain():
    if os.name!='nt':raise DataError('q_clock_domain_unknown')
    info=time.get_clock_info('monotonic')
    if not info.monotonic or info.adjustable or info.implementation not in ('QueryPerformanceCounter()','GetTickCount64()'):
        raise DataError('q_clock_domain_unknown')
    query=ctypes.WinDLL('ntdll').NtQuerySystemInformation
    query.argtypes=[ctypes.c_ulong,ctypes.c_void_p,ctypes.c_ulong,ctypes.POINTER(ctypes.c_ulong)]
    query.restype=ctypes.c_long
    data=ctypes.create_string_buffer(32);length=ctypes.c_ulong()
    # SystemBootEnvironmentInformation: GUID, firmware type, padding, boot flags.
    if query(90,data,len(data),ctypes.byref(length))!=0 or length.value!=32:
        raise DataError('q_clock_domain_unknown')
    boot=UUID(bytes_le=data.raw[:16])
    if boot.int==0:raise DataError('q_clock_domain_unknown')
    return digest('windows-boot-clock.v1:'+info.implementation+':'+str(boot))


def sample():
    identity=domain()
    before=time.monotonic_ns();utc=datetime.now(timezone.utc);after=time.monotonic_ns()
    if after<before or after-before>1_000_000_000:raise DataError('q_clock_sample_unknown')
    return {'domain':identity,'mono_ns':before,'upper_ns':after,'utc':utc.isoformat()}


def certificate(now,end):
    issued=datetime.fromisoformat(now['utc']);duration=(end-issued).total_seconds()
    if issued.utcoffset() is None or not 0<duration<=900:raise DataError('q_clock_deadline_invalid')
    return {'schema':'retrolume.q-clock.v1','domain':now['domain'],'issued_mono_ns':now['mono_ns'],
            'issued_upper_ns':now['upper_ns'],'deadline_mono_ns':now['mono_ns']+int(duration*1e9)}


def validate(body,last,now):
    """Return a denial reason, or None. The caller persists irreversible denials.

    Exact UTC regressions relative to any observed sample reject immediately.
    The 1s allowance below bounds sampling/NTP drift, never the 900s deadline.
    """
    try:
        clock=body.get('clock');issued=datetime.fromisoformat(body['issued_at']);end=datetime.fromisoformat(body['expires_at'])
        wall=datetime.fromisoformat(now['utc'])
        if not clock or clock['schema']!='retrolume.q-clock.v1' or not now['domain'] or clock['domain']!=now['domain']:
            return 'q_clock_domain_unknown'
        if any(x.utcoffset() is None for x in (issued,end,wall)):return 'q_clock_domain_unknown'
        duration=(end-issued).total_seconds()
        start=clock['issued_mono_ns'];upper=clock['issued_upper_ns'];deadline=clock['deadline_mono_ns']
        if not (0<duration<=900 and 0<=start<=upper<start+1_000_000_001
                and deadline==start+int(duration*1e9)):return 'q_clock_certificate_invalid'
        if now['mono_ns']<upper or now['upper_ns']<now['mono_ns']:return 'q_clock_regressed'
        prior=last or {'utc':body['issued_at'],'mono_ns':start,'upper_ns':upper,'domain':clock['domain']}
        if prior['domain']!=clock['domain']:return 'q_clock_domain_unknown'
        if wall<issued or wall<datetime.fromisoformat(prior['utc']) or now['mono_ns']<prior['mono_ns']:
            return 'q_clock_regressed'
        if wall>=end or now['mono_ns']>=deadline:return 'q_approval_expired'
        # Detect a backwards UTC step even between the first two observations.
        if (wall-issued).total_seconds()<(now['mono_ns']-upper)/1e9-1:
            return 'q_clock_regressed'
        if (wall-datetime.fromisoformat(prior['utc'])).total_seconds()<(now['mono_ns']-prior['upper_ns'])/1e9-1:
            return 'q_clock_regressed'
        return None
    except (KeyError,TypeError,ValueError,OverflowError):
        return 'q_clock_domain_unknown'
