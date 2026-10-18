"""本次管道/owner与客户端修正的离线检查；不冒PG、浏览器或树停止证明。"""
from __future__ import annotations
import ast
import asyncio
from copy import deepcopy
import hashlib
import io
import json
import struct
import zlib
from .control import ROOT,EVIDENCE,batch,atomic,reserve,run,source_snapshot,event


def main():
    folder=EVIDENCE/"offline-03";folder.mkdir(exist_ok=False)
    with batch("offline","typed-pipe-owner-client-guard-repair",maximum=300):
        source_snapshot(folder)
        for name in ("api.py","pipe.py","production_supervisor.py"):
            ast.parse((ROOT/"backend/app/preview"/name).read_text(encoding="utf-8"),filename=name)
        from app.preview.description import canonical
        from app.preview.pipe import read_packet,PipeError,validate_png
        identity={"preview_id":"2672ce7f-c64f-4605-8395-109a47310d06","generation":1,"artifact_sha256":"a"*64,"channel_nonce":"b"*64}
        def packet(body,kind="status",**changes):
            head={"protocol":"retrolume.preview.v2","type":kind,**identity,"seq":1,"body_bytes":len(body),"body_sha256":hashlib.sha256(body).hexdigest()}
            if kind=="frame":head.update(format="png",width=640,height=480)
            head.update(changes);encoded=canonical(head).encode()
            return io.BytesIO(struct.pack("!I",len(encoded))+encoded+body)
        status=b'{"state":"stopping"}';read_packet(packet(status),identity)
        negatives=[]
        for key,value in (("generation",True),("generation",1.0),("seq",True),("channel_nonce","c"*64),("protocol","retrolume.preview.v1"),("extra","code"),("body_sha256","d"*64)):
            try:read_packet(packet(status,**{key:value}),identity)
            except PipeError:negatives.append(key)
            else:raise AssertionError("invalid typed header accepted: "+key)
        # 一个标准编码的有限合成PNG，仅作codec与封包解析oracle。
        def chunk(kind,data):return struct.pack("!I",len(data))+kind+data+struct.pack("!I",zlib.crc32(kind+data)&0xffffffff)
        header=chunk(b"IHDR",struct.pack("!IIBBBBB",640,480,8,2,0,0,0))
        idat=chunk(b"IDAT",zlib.compress(b"\0"*(480*(1+640*3))));end=chunk(b"IEND",b"")
        png=b"\x89PNG\r\n\x1a\n"+header+idat+end;validate_png(png);read_packet(packet(png,"frame"),identity)
        corrupted=bytearray(png);corrupted[30]^=1
        bad_pngs=[bytes(corrupted),png[:-12],png+b"x",b"\x89PNG\r\n\x1a\n"+header+chunk(b"IDAT",zlib.compress(b"\0"*(480*(1+640*3)+1)))+end,
          b"\x89PNG\r\n\x1a\n"+header+chunk(b"IDAT",zlib.compress(b"\xff"*(480*(1+640*3))))+end]
        for value in bad_pngs:
            try:read_packet(packet(value,"frame"),identity)
            except PipeError:negatives.append("PNG")
            else:raise AssertionError("invalid PNG accepted")
        try:read_packet(packet(png,"frame",width=640.0),identity)
        except PipeError:negatives.append("float_width")
        else:raise AssertionError("float width accepted")
        from app.preview.production_supervisor import PreviewController
        owner="12"*32;row={"generation":1,"owner_key_sha256":hashlib.sha256(bytes.fromhex(owner)).hexdigest(),"state":"ready","eligible":True}
        class LiteralRow:
            async def read_html_preview(self,aid,pid):return deepcopy(row)
        # 只验证status的纯owner决策，不构造真实controller/mutex或假称数据库授权通过。
        controller=object.__new__(PreviewController);controller.ledger=LiteralRow()
        controller.current={"aid":"activity","preview_id":identity["preview_id"],"generation":1,"last_contact_ns":123}
        async def owner_cases():
            for key in (None,"34"*32,"12 "*32):
                visible=await controller.status("activity",identity["preview_id"],key)
                assert "owner_key_sha256" not in visible and controller.current["last_contact_ns"]==123
            await controller.status("activity",identity["preview_id"],owner)
            assert controller.current["last_contact_ns"]>123
        asyncio.run(owner_cases())
        reserve("frontend_typecheck_build_batches",{"reason":"artifact/citation selection and stop polling changed"})
        run(["C:\\Program Files\\nodejs\\npm.cmd","run","build"],folder,cwd=ROOT/"frontend",maximum=180,name="frontend-build")
        atomic(folder/"result.json",{"status":"PASS_TARGETED_OFFLINE_ONLY","header_png_negatives":len(negatives),
              "owner_refresh_unit_cases":4,"frontend_typecheck_build":True,"real_PG_browser_stop_race":False,"runtime_starts":0})
        event("guard_offline_complete",{"folder":str(folder),"classification":"unit/codec/typecheck only"})


if __name__=="__main__":main()
