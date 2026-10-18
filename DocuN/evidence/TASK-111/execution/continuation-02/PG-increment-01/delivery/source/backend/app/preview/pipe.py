"""限长匿名管道封包。页面文本不进入此解析器。"""
from __future__ import annotations
import hashlib
import json
import struct
import zlib
from .description import canonical, load_json

HEAD_FIELDS={"protocol","type","preview_id","generation","artifact_sha256","channel_nonce","seq","body_bytes","body_sha256"}
LIMITS={"ready":16384,"status":4096,"input_ack":4096,"frame":524288}


class PipeError(ValueError):pass


def validate_png(body):
    """只接受固定截图的有界8-bit PNG；CRC、压缩终结和扫描行都必须完整。"""
    if not 24<=len(body)<=524288 or body[:8]!=b"\x89PNG\r\n\x1a\n":raise PipeError("frame_format")
    position=8;chunks=0;channels=None;compressed=bytearray();ended=False
    while position<len(body):
        if ended or position+12>len(body) or chunks>=4096:raise PipeError("frame_encoding")
        length=struct.unpack("!I",body[position:position+4])[0];kind=body[position+4:position+8];end=position+12+length
        if end>len(body) or not all(65<=byte<=90 or 97<=byte<=122 for byte in kind):raise PipeError("frame_encoding")
        data=body[position+8:position+8+length];expected=struct.unpack("!I",body[position+8+length:end])[0]
        if zlib.crc32(kind+data)&0xffffffff!=expected:raise PipeError("frame_crc")
        if kind==b"IHDR":
            if chunks or length!=13:raise PipeError("frame_header")
            width,height,depth,color,compression,filter_method,interlace=struct.unpack("!IIBBBBB",data)
            if (width,height)!=(640,480) or depth!=8 or color not in (0,2,4,6) or (compression,filter_method,interlace)!=(0,0,0):raise PipeError("frame_dimensions_or_codec")
            channels={0:1,2:3,4:2,6:4}[color]
        elif channels is None:raise PipeError("frame_header")
        elif kind==b"IDAT":compressed.extend(data)
        elif kind==b"IEND":
            if length or not compressed:raise PipeError("frame_end")
            ended=True
        elif kind==b"PLTE":
            if not 3<=length<=768 or length%3:raise PipeError("frame_palette")
        elif kind[0]&32==0:raise PipeError("frame_unknown_critical_chunk")
        position=end;chunks+=1
    if not ended or channels is None:raise PipeError("frame_incomplete")
    size=480*(1+640*channels)
    try:
        inflater=zlib.decompressobj();pixels=inflater.decompress(bytes(compressed),size+1)
    except zlib.error:raise PipeError("frame_compression") from None
    if len(pixels)!=size or not inflater.eof or inflater.unused_data or inflater.unconsumed_tail:
        raise PipeError("frame_scanline_size")
    if any(pixels[row*(1+640*channels)]>4 for row in range(480)):raise PipeError("frame_filter")


def send_packet(stream,identity,kind,seq,body):
    data=canonical(body).encode("utf-8")
    if kind not in {"init","input","stop"} or not 1<=len(data)<=(65536 if kind=="init" else 1024):raise PipeError("outbound_size")
    head={"protocol":"retrolume.preview.v2","type":kind,"preview_id":identity["preview_id"],"generation":identity["generation"],
          "artifact_sha256":identity["artifact_sha256"],"channel_nonce":identity["channel_nonce"],"seq":seq,
          "body_bytes":len(data),"body_sha256":hashlib.sha256(data).hexdigest()}
    header=canonical(head).encode("utf-8")
    if len(header)>2048:raise PipeError("header_size")
    stream.write(struct.pack("!I",len(header))+header+data);stream.flush()


def _read_exact(stream,count):
    parts=bytearray()
    while len(parts)<count:
        chunk=stream.read(count-len(parts))
        if not chunk:raise EOFError("pipe_eof")
        parts.extend(chunk)
    return bytes(parts)


def read_packet(stream,identity):
    prefix=_read_exact(stream,4);length=struct.unpack("!I",prefix)[0]
    if not 1<=length<=2048:raise PipeError("header_size")
    raw=_read_exact(stream,length);head=load_json(raw,2048)
    fields=HEAD_FIELDS|({"format","width","height"} if head.get("type")=="frame" else set())
    if set(head)!=fields or canonical(head).encode("utf-8")!=raw or head["protocol"]!="retrolume.preview.v2" or head["type"] not in LIMITS:
        raise PipeError("header_fields")
    for key in ("preview_id","generation","artifact_sha256","channel_nonce"):
        if type(head[key]) is not type(identity[key]) or head[key]!=identity[key]:raise PipeError("pipe_identity")
    if type(head["seq"]) is not int or head["seq"]<0 or type(head["body_bytes"]) is not int or not 1<=head["body_bytes"]<=LIMITS[head["type"]]:
        raise PipeError("packet_size_or_sequence")
    body=_read_exact(stream,head["body_bytes"])
    if hashlib.sha256(body).hexdigest()!=head["body_sha256"]:raise PipeError("body_hash")
    if head["type"]=="frame":
        if head["format"]!="png" or type(head["width"]) is not int or type(head["height"]) is not int or head["width"]!=640 or head["height"]!=480 or body[:8]!=b"\x89PNG\r\n\x1a\n" or len(body)<24:
            raise PipeError("frame_format")
        if struct.unpack("!II",body[16:24])!=(640,480):raise PipeError("frame_dimensions")
        validate_png(body)
        return head,body
    value=load_json(body,LIMITS[head["type"]])
    if type(value) is not dict:raise PipeError("body_object")
    return head,value
