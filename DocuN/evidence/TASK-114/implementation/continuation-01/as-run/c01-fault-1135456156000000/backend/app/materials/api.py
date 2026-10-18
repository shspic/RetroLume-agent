"""有界TXT/Markdown导入；仅将原文作为纯文本返回。"""
import asyncio
import io
from uuid import UUID
from fastapi import APIRouter, HTTPException, Request
from fastapi.concurrency import run_in_threadpool
from app.local_session import local_request, local_session
from app.pdf_import import PdfImportError, parse_pdf_bytes
from app.storage.originals import Original, IntegrityError
from .repository import DatabaseUnavailable, VersionConflict
from .locations import excerpt, locations

router = APIRouter(prefix="/api")
MAX_BYTES = 5 * 1024 * 1024


def repository(request):
    # 续作01（D1）：资料与 PDF 面恢复默认固定允许来源/拒绝行为；同源放行仅保留在活动路由。
    local_session(request)
    if request.app.state.materials is None:
        raise HTTPException(503, "本地PostgreSQL尚未配置；资料不会被保存到临时替代数据库")
    return request.app.state.materials


def valid_id(value):
    try:
        return str(UUID(value))
    except (ValueError, TypeError, AttributeError):
        raise HTTPException(400, "无效资料编号") from None


@router.get("/session")
def session(request: Request):
    local_request(request)
    data = getattr(request.app.state, "data_exit", None)
    return {"token": request.app.state.session_token, "storage_configured": request.app.state.materials is not None, "max_bytes": MAX_BYTES,
            "data_context": data.context().public() if data is not None else None}


@router.get("/materials")
async def list_materials(request: Request, offset: int = 0):
    repo = repository(request)
    if offset < 0:
        raise HTTPException(400, "无效分页位置")
    try:
        items = await run_in_threadpool(repo.list, limit=100, offset=offset)
        return {"items": items, "next_offset": offset + len(items) if len(items) == 100 else None}
    except DatabaseUnavailable as error:
        raise HTTPException(503, str(error)) from None


@router.post("/materials")
async def upload(
    request: Request,
    filename: str,
    source_id: str | None = None,
    expected_version: str | None = None,
    expected_revision: int | None = None,
):
    repo = repository(request)
    if len(filename) > 200 or not filename.strip() or any(ord(char) < 32 or char in '/\\:' for char in filename):
        raise HTTPException(400, "文件名无效")
    suffix = filename.rsplit(".", 1)[-1].lower()
    if "." not in filename or suffix not in {"txt", "md", "markdown", "pdf"}:
        raise HTTPException(415, "当前仅支持UTF-8的TXT、Markdown和可提取文字的PDF文件")
    if bool(source_id) != bool(expected_version):
        raise HTTPException(400, "替换需要当前版本编号")
    if source_id:
        source_id, expected_version = valid_id(source_id), valid_id(expected_version)
    if suffix == "pdf":
        if source_id and expected_revision is None:
            raise HTTPException(400, "PDF替换需要当前资料修订号")
        if not source_id and expected_revision is not None:
            raise HTTPException(400, "新PDF不能指定旧资料修订号")
    # 分块接收同样计限，不能仅依赖Content-Length。
    content = bytearray()
    try:
        async with asyncio.timeout(30):
            async for chunk in request.stream():
                if len(content) + len(chunk) > MAX_BYTES:
                    raise HTTPException(413, "单个文件不能超过5 MiB")
                content.extend(chunk)
    except TimeoutError:
        raise HTTPException(408, "接收文件超时，请确认网络后手动重试") from None
    data = bytes(content)
    if suffix != "pdf":
        try:
            text = data.decode("utf-8-sig")
        except UnicodeDecodeError:
            raise HTTPException(422, "文件不是有效UTF-8文本，请转换编码后重试") from None
        if not text.strip() or "\x00" in text:
            raise HTTPException(422, "文件为空或包含二进制内容")
    try:
        if getattr(repo, "data_enabled", False):
            def fenced_upload():
                import hashlib
                from app.data_exit.contracts import DataError
                references = repo.reference_coordinator
                if references is None: raise DataError("data_readonly")
                extraction = parse_pdf_bytes(data) if suffix == 'pdf' else None
                prepared = references.prepare_reference(hashlib.sha256(data).hexdigest(), len(data), source_id=source_id, pdf=suffix == 'pdf')
                with references.acquire_shared(prepared) as pin:
                    original = request.app.state.originals.put(io.BytesIO(data), max_bytes=MAX_BYTES, reference_pin=pin)
                    if suffix == 'pdf':
                        return {'candidate':repo.create_pdf_candidate(source_id=source_id, expected_version=expected_version,
                            expected_revision=expected_revision if expected_revision is not None else 0, filename=filename,
                            sha256=original.sha256,size=original.size,extraction=extraction,reference_pin=pin,prepared_ids=prepared),'query_ready':False}
                    return {'material':repo.save(source_id=source_id, expected_version=expected_version, filename=filename,
                        format='txt' if suffix == 'txt' else 'md', sha256=original.sha256,size=original.size,reference_pin=pin,prepared_ids=prepared)}
            try:return await run_in_threadpool(fenced_upload)
            except PdfImportError:
                raise HTTPException(422,'PDF解析未完成，资料未提交；旧资料保持不变') from None
        original = await run_in_threadpool(request.app.state.originals.put, io.BytesIO(content), max_bytes=MAX_BYTES)
        if suffix == "pdf":
            try:
                extraction = await run_in_threadpool(parse_pdf_bytes, data)
            except PdfImportError as error:
                messages = {
                    "pdf_input_too_large": "PDF超过5 MiB限制",
                    "pdf_invalid": "PDF损坏或格式无效",
                    "pdf_encrypted": "加密PDF暂不支持，请提供未加密版本",
                    "pdf_no_extractable_text": "PDF没有可提取文字；扫描件OCR不在当前范围",
                    "pdf_page_limit_exceeded": "PDF物理页超过50页限制",
                    "pdf_text_limit_exceeded": "PDF提取文字超过2 MiB限制",
                    "pdf_timeout": "PDF解析超时，旧资料保持不变",
                    "pdf_unsupported_platform": "当前平台不支持受限PDF解析",
                    "pdf_sandbox_setup_failed": "PDF受限解析环境未能建立",
                    "pdf_worker_protocol_invalid": "PDF解析结果无效",
                    "pdf_worker_failed": "PDF解析失败，旧资料保持不变",
                }
                raise HTTPException(422, messages.get(error.code, "PDF解析失败，旧资料保持不变")) from None
            candidate = await run_in_threadpool(
                repo.create_pdf_candidate,
                source_id=source_id,
                expected_version=expected_version,
                expected_revision=expected_revision if expected_revision is not None else 0,
                filename=filename,
                sha256=original.sha256,
                size=original.size,
                extraction=extraction,
            )
            return {"candidate": candidate, "query_ready": False}
        row = await run_in_threadpool(repo.save, source_id=source_id, expected_version=expected_version, filename=filename, format="txt" if suffix == "txt" else "md", sha256=original.sha256, size=original.size)
        return {"material": row}
    except KeyError:
        raise HTTPException(404, "待替换资料不存在") from None
    except VersionConflict:
        raise HTTPException(409, "资料已被更新，请刷新后选择替换；旧版本未被覆盖") from None
    except DatabaseUnavailable as error:
        raise HTTPException(503, str(error)) from None
    except (OSError, IntegrityError):
        raise HTTPException(503, "原件保存失败，已保存资料保持不变") from None


@router.get("/materials/{source_id}/content")
async def read_material(source_id: str, request: Request, expected_version: str | None = None, start_line: int | None = None, end_line: int | None = None):
    repo = repository(request)
    if (start_line is None) != (end_line is None):
        raise HTTPException(400, "摘录需要同时提供起始和结束行号")
    if expected_version is not None:
        expected_version = valid_id(expected_version)
    try:
        row = await run_in_threadpool(repo.get, valid_id(source_id))
        if row is None:
            raise HTTPException(404, "资料不存在")
        if expected_version is not None and row["version_id"] != expected_version:
            raise HTTPException(409, "该版本已被替换，不能以当前原文冒充旧引用")
        if row["format"] == "pdf":
            if start_line is not None or end_line is not None:
                raise HTTPException(400, "PDF按物理页回查，不能使用文字行号")
            pdf = await run_in_threadpool(repo.get_active_pdf_pages, row["id"], row["version_id"])
            if pdf is None:
                raise HTTPException(409, "PDF尚未完成逐页核对，不能作为当前资料读取")
            return pdf
        content = await run_in_threadpool(request.app.state.originals.read, Original(row["sha256"], row["size"]), max_bytes=MAX_BYTES)
        text = content.decode("utf-8-sig")
        result = {"material": row, "text": text, "locations": locations(text)}
        if start_line is not None and end_line is not None:
            try:
                result["excerpt"] = {"start_line": start_line, "end_line": end_line, "text": excerpt(text, start_line, end_line)}
            except ValueError as error:
                raise HTTPException(422, str(error)) from None
        return result
    except DatabaseUnavailable as error:
        raise HTTPException(503, str(error)) from None
    except (OSError, IntegrityError, UnicodeDecodeError):
        raise HTTPException(409, "原件不可用或完整性检查失败；未伪造内容") from None
