from pathlib import Path
p=Path("backend/app/worker/session.py"); raw=p.read_bytes(); bom=b"\xef\xbb\xbf" if raw.startswith(b"\xef\xbb\xbf") else b""; s=raw[len(bom):].decode("utf-8").replace("\r\n","\n")
a='    manager_created_100ns: int | None = None\n\n\nclass _StopSession'
b='    manager_created_100ns: int | None = None\n    running_owner_session_id: int | None = None\n\n\nclass _StopSession'
if s.count(a)!=1: raise RuntimeError(s.count(a))
s=s.replace(a,b,1)
a='            timing_diagnostic,\n        )\n        if interrupted is not None:'
b='            timing_diagnostic,\n            running_owner_session_id=session_id if lease is not None else None,\n        )\n        if interrupted is not None:'
if s.count(a)!=1: raise RuntimeError(s.count(a))
s=s.replace(a,b,1)
p.write_bytes(bom+s.replace("\n","\r\n").encode("utf-8") if b"\r\n" in raw else bom+s.encode("utf-8"))
