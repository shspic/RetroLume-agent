from pathlib import Path
p=Path("backend/tests/fixtures/task083/offline_unit.py"); raw=p.read_bytes(); bom=b"\xef\xbb\xbf" if raw.startswith(b"\xef\xbb\xbf") else b""; s=raw[len(bom):].decode("utf-8").replace("\r\n","\n")
a='    def resume(self):\n        self.events.append("resume")'
b='    def process_creation_time_100ns(self):\n        return 1\n\n    def resume(self):\n        self.events.append("resume")'
if s.count(a)!=1: raise RuntimeError(s.count(a))
s=s.replace(a,b,1);p.write_bytes(bom+s.replace("\n","\r\n").encode("utf-8") if b"\r\n" in raw else bom+s.encode("utf-8"))
