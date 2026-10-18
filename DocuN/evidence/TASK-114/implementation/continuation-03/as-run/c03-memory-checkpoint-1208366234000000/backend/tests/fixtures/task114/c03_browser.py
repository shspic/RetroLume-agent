"""最终dist一次合并route矩阵；无服务器，无旧profile/PG/API消费者。"""
import ctypes
from ctypes import wintypes
import json
import queue
import subprocess
import sys
import threading
import time
from c03_support import C03Budget, ROOT, EVIDENCE, freeze, sample, save
sys.path.insert(0, str(ROOT / 'backend'))
from app.preview.process import birth


def memory():
    class Memory(ctypes.Structure):
        _fields_ = [('length', ctypes.c_ulong), ('load', ctypes.c_ulong),
                    *[(name, ctypes.c_ulonglong) for name in ('total_phys', 'available_phys', 'total_page', 'available_page', 'total_virtual', 'available_virtual', 'extended')]]
    value = Memory(); value.length = ctypes.sizeof(value)
    if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(value)): raise RuntimeError('内存采样失败')
    result = {**sample(), 'available_bytes': value.available_phys, 'minimum_bytes': 2 * 1024 ** 3,
              'ready': value.available_phys >= 2 * 1024 ** 3}
    save(EVIDENCE / 'observations' / ('browser-memory-' + str(time.monotonic_ns()) + '.json'), result)
    return result


def end_exact(pid, stamp):
    observed = birth(pid)
    return observed['state'] == 'exited' or observed['state'] == 'running' and observed.get('birth') != stamp


def terminate_exact(pid, stamp):
    # 只对已登记准确消费者的同一内核handle核birth后收尾，PID复用不停止。
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    kernel.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]; kernel.OpenProcess.restype = wintypes.HANDLE
    kernel.GetProcessTimes.argtypes = [wintypes.HANDLE, *[ctypes.POINTER(wintypes.FILETIME)] * 4]
    kernel.TerminateProcess.argtypes = [wintypes.HANDLE, wintypes.UINT]; kernel.CloseHandle.argtypes = [wintypes.HANDLE]
    handle = kernel.OpenProcess(0x1000 | 1 | 0x100000, False, pid)
    if not handle:
        if end_exact(pid, stamp): return
        raise ctypes.WinError(ctypes.get_last_error())
    try:
        times = [wintypes.FILETIME() for _ in range(4)]
        if not kernel.GetProcessTimes(handle, *map(ctypes.byref, times)): raise ctypes.WinError(ctypes.get_last_error())
        actual = times[0].dwLowDateTime | times[0].dwHighDateTime << 32
        if actual == stamp and not end_exact(pid, stamp):
            if not kernel.TerminateProcess(handle, 124): raise ctypes.WinError(ctypes.get_last_error())
    finally: kernel.CloseHandle(handle)


def main():
    budget = C03Budget(); budget.check()
    observed = memory()
    if not observed['ready']:
        print(json.dumps({'state': 'not_run', 'reason': 'memory_gate', 'available_GiB': observed['available_bytes'] / 1024 ** 3})); return 78
    label = 'c03-browser-' + str(time.monotonic_ns()); out = EVIDENCE / 'batches' / label; out.mkdir(parents=True)
    profile = EVIDENCE / 'synthetic/browser-root' / label; profile.mkdir(parents=True)
    budget.root('c03-browser-group'); as_run = freeze(label); budget.reserve('browser_start')
    argv = ['node', str(ROOT / 'frontend/tests/task114-c03-inputs.mjs'), str(ROOT), str(out), str(profile)]
    start = sample(); method = {'label': label, 'start': start, 'argv': argv, 'cwd': str(ROOT),
        'root': 'c03-browser-group', 'layer': '真实Chromium/最终dist/all routes，零TCP监听/API/PG/真实selector',
        'as_run': str(as_run.relative_to(ROOT)), 'profile': str(profile), 'memory': observed, 'timeout_seconds': 180}
    save(out / 'method-begin.json', method); budget.event('c03.browser.begin', method)
    process = None; identities = []; closed = False; code = 124; lines = queue.Queue()
    def register(pid, kind, parent=None):
        actual = birth(pid)
        if actual['state'] != 'running': raise RuntimeError('消费者birth未捕获')
        stamp = actual['birth']; identity = f'{kind}:{pid}:{stamp}'
        metadata = {'pid': pid, 'birth': stamp, 'profile': str(profile), 'parent_pid': parent, 'run': label}
        budget.created(identity, kind, metadata); budget.begin(identity)
        value = budget.load(); resource = next(r for r in value['resources'] if r['identity'] == identity)
        resource['begin_ns'] = start['mono_ns']; resource['begin_basis'] = '创建controller前同步采样，Chrome同点上界保守扣；精确PID/birth另记'
        budget.save(value); identities.append((identity, pid, stamp)); budget.event('c03.consumer.binding', metadata)
    try:
        with (out / 'stderr.log').open('xb') as stderr:
            process = subprocess.Popen(argv, cwd=ROOT, stdout=subprocess.PIPE, stderr=stderr, text=True, encoding='utf-8', creationflags=subprocess.CREATE_NO_WINDOW)
            register(process.pid, 'browser-controller')
            def reader():
                try:
                    for line in process.stdout: lines.put(line)
                finally: lines.put(None)
            thread = threading.Thread(target=reader, daemon=True); thread.start()
            while True:
                if time.monotonic_ns() - start['mono_ns'] > 180 * 1e9: raise RuntimeError('Browser单方法180秒停止门')
                budget.check()
                try: line = lines.get(timeout=.2)
                except queue.Empty: continue
                if line is None: break
                with (out / 'events.jsonl').open('a', encoding='utf-8') as stream: stream.write(line)
                event = json.loads(line)
                if event['event'] == 'browser_spawn': register(event['pid'], 'browser', process.pid)
                if event['event'] == 'browser_closed': closed = bool(event['confirmed'])
            code = process.wait(timeout=10)
    finally:
        # 正常方法由真实browser.close收尾；异常时仅核对/结束本轮准确对象，不签未证停止。
        for _, pid, stamp in reversed(identities):
            if not end_exact(pid, stamp): terminate_exact(pid, stamp)
        if process: process.wait(timeout=10)
        closure = []
        for identity, pid, stamp in reversed(identities):
            ended = end_exact(pid, stamp)
            detail = {'identity': identity, 'pid': pid, 'birth': stamp, 'process_ended': ended, 'actual_browser_close': closed}
            closure.append(detail)
            if not ended: raise RuntimeError('准确Browser消费者仍运行')
            budget.end(identity, detail)
        end = sample(); method.update(end=end, seconds=(end['mono_ns'] - start['mono_ns']) / 1e9, exit_code=code, closure=closure)
        save(out / 'method.json', method); budget.event('c03.browser.end', method)
    print(json.dumps({'label': label, 'exit_code': code, 'browser_close_confirmed': closed, 'evidence': str(out)}))
    return code


if __name__ == '__main__': sys.exit(main())
