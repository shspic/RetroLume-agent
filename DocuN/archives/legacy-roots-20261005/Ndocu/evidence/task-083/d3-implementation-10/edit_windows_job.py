from pathlib import Path
p=Path("backend/app/worker/windows_job.py"); raw=p.read_bytes(); bom=b"\xef\xbb\xbf" if raw.startswith(b"\xef\xbb\xbf") else b""; s=raw[len(bom):].decode("utf-8").replace("\r\n","\n")
def rep(a,b):
 global s
 if s.count(a)!=1: raise RuntimeError((s.count(a),a[:80]))
 s=s.replace(a,b,1)
rep("ERROR_ALREADY_EXISTS = 183\n", "ERROR_ALREADY_EXISTS = 183\nERROR_FILE_NOT_FOUND = 2\nERROR_ACCESS_DENIED = 5\n")
rep('class JobUnknown(RuntimeError):\n    """不能确认Job身份、状态或终止结果；调用者必须失败关闭。"""\n', 'class JobUnknown(RuntimeError):\n    """不能确认Job身份、状态或终止结果；调用者必须失败关闭。"""\n\n\nclass JobOpenError(JobUnknown):\n    """保留 OpenJobObjectW 的原始 Windows 错误码。"""\n\n    def __init__(self, code: int):\n        self.code = code\n        super().__init__(f"OpenJobObjectW Windows error {code}")\n')
rep('    api.CreateMutexW.argtypes =', '    api.GetCurrentProcessId.argtypes = []\n    api.GetCurrentProcessId.restype = wintypes.DWORD\n    api.ProcessIdToSessionId.argtypes = [wintypes.DWORD, ctypes.POINTER(wintypes.DWORD)]\n    api.ProcessIdToSessionId.restype = wintypes.BOOL\n    api.CreateMutexW.argtypes =')
rep('def _activity_key(activity_id: str) -> str:', 'def current_process_session_id() -> int:\n    """可信 SUP 自身进程的 Windows 会话号；读取失败不得启动工作。"""\n    api = _kernel()\n    session = wintypes.DWORD()\n    if not api.ProcessIdToSessionId(api.GetCurrentProcessId(), ctypes.byref(session)):\n        raise _error("ProcessIdToSessionId")\n    return int(session.value)\n\n\ndef _activity_key(activity_id: str) -> str:')
rep('        if not handle:\n            # 包括不存在/会话不符/ACL拒绝；调用者绝不将其推断为旧树为空。\n            raise _error("OpenJobObjectW")', '        if not handle:\n            # 只有 ERROR_FILE_NOT_FOUND 可成为同会话旧树不存在的候选证据。\n            raise JobOpenError(ctypes.get_last_error())')
p.write_bytes(bom+s.replace("\n","\r\n").encode("utf-8") if b"\r\n" in raw else bom+s.encode("utf-8"))
