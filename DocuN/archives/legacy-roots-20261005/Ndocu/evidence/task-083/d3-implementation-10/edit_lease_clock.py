from pathlib import Path
p=Path("backend/app/activities/repository.py"); raw=p.read_bytes(); bom=b"\xef\xbb\xbf" if raw.startswith(b"\xef\xbb\xbf") else b""; s=raw[len(bom):].decode("utf-8").replace("\r\n","\n")
a='            cursor = await connection.execute("SELECT * FROM activities WHERE id = %s FOR UPDATE", (activity_id,))\n            row = await cursor.fetchone()\n            now = datetime.now(timezone.utc)'
b='            cursor = await connection.execute("SELECT *, CURRENT_TIMESTAMP AS database_now FROM activities WHERE id = %s FOR UPDATE", (activity_id,))\n            row = await cursor.fetchone()\n            now = row["database_now"] if row is not None else None'
if s.count(a)!=1: raise RuntimeError(s.count(a))
s=s.replace(a,b,1)
p.write_bytes(bom+s.replace("\n","\r\n").encode("utf-8") if b"\r\n" in raw else bom+s.encode("utf-8"))
