"""受本地会话保护的 PDF 候选、原件与确认接口。"""
from urllib.parse import quote

from fastapi import APIRouter, HTTPException, Request, Response
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel, ConfigDict, Field

from app.materials.api import MAX_BYTES, repository, valid_id
from app.materials.repository import DatabaseUnavailable, VersionConflict
from app.storage.originals import IntegrityError, Original

from .contracts import ReviewPage


router = APIRouter(prefix="/api")


class ReviewPageInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    physical_page: int
    reviewed: bool
    supplement: str | None = Field(default=None, max_length=65536)


class ConfirmInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version_id: str
    pages: list[ReviewPageInput] = Field(max_length=50)


def _database_error(error: DatabaseUnavailable) -> HTTPException:
    return HTTPException(503, str(error))


@router.get("/pdf-candidates")
async def list_candidates(request: Request):
    repo = repository(request)
    try:
        return {"items": await run_in_threadpool(repo.list_pdf_candidates)}
    except DatabaseUnavailable as error:
        raise _database_error(error) from None


@router.get("/pdf-candidates/{candidate_id}")
async def read_candidate(candidate_id: str, request: Request):
    repo = repository(request)
    try:
        candidate = await run_in_threadpool(repo.get_pdf_candidate, valid_id(candidate_id))
        if candidate is None:
            raise HTTPException(404, "PDF候选不存在")
        return {"candidate": candidate}
    except DatabaseUnavailable as error:
        raise _database_error(error) from None


async def _original_response(metadata: dict, request: Request) -> Response:
    try:
        content = await run_in_threadpool(
            request.app.state.originals.read,
            Original(metadata["sha256"], metadata["size"]),
            max_bytes=MAX_BYTES,
        )
    except (OSError, ValueError, IntegrityError):
        raise HTTPException(409, "PDF原件不可用或完整性检查失败") from None
    filename = quote(metadata["filename"], safe="")
    return Response(
        content=content,
        media_type="application/pdf",
        headers={"Content-Disposition": f"inline; filename*=UTF-8''{filename}"},
    )


@router.get("/pdf-candidates/{candidate_id}/original")
async def read_candidate_original(candidate_id: str, request: Request):
    repo = repository(request)
    try:
        metadata = await run_in_threadpool(repo.get_pdf_candidate_original, valid_id(candidate_id))
        if metadata is None:
            raise HTTPException(404, "PDF候选不存在")
        return await _original_response(metadata, request)
    except DatabaseUnavailable as error:
        raise _database_error(error) from None


@router.post("/pdf-candidates/{candidate_id}/confirm")
async def confirm_candidate(candidate_id: str, body: ConfirmInput, request: Request):
    repo = repository(request)
    reviews = [ReviewPage(page.physical_page, page.reviewed, page.supplement) for page in body.pages]
    try:
        if getattr(repo, 'data_enabled', False):
            def fenced_confirm():
                from app.data_exit.contracts import DataError
                references = repo.reference_coordinator
                if references is None:raise DataError('data_readonly')
                candidate = repo.get_pdf_candidate(valid_id(candidate_id))
                if candidate is None:raise KeyError(candidate_id)
                prepared = references.prepare_reference(candidate['sha256'],candidate['size'],source_id=candidate['source_id'],
                    version_id=candidate['version_id'],candidate_id=candidate['candidate_id'])
                with references.acquire_shared(prepared) as pin:
                    request.app.state.originals.verify(Original(candidate['sha256'],candidate['size']),reference_pin=pin)
                    return repo.confirm_pdf_candidate(candidate_id=valid_id(candidate_id),version_id=valid_id(body.version_id),pages=reviews,reference_pin=pin)
            return {'material':await run_in_threadpool(fenced_confirm),'query_ready':True}
        material = await run_in_threadpool(
            repo.confirm_pdf_candidate,
            candidate_id=valid_id(candidate_id),
            version_id=valid_id(body.version_id),
            pages=reviews,
        )
        return {"material": material, "query_ready": True}
    except KeyError:
        raise HTTPException(404, "PDF候选不存在") from None
    except ValueError as error:
        raise HTTPException(422, str(error)) from None
    except VersionConflict:
        raise HTTPException(409, "资料或候选已更新；本次确认未覆盖当前版本") from None
    except DatabaseUnavailable as error:
        raise _database_error(error) from None


@router.post("/pdf-candidates/{candidate_id}/skip")
async def skip_candidate(candidate_id: str, request: Request):
    repo = repository(request)
    try:
        candidate = await run_in_threadpool(repo.skip_pdf_candidate, valid_id(candidate_id))
        return {"candidate": candidate, "query_ready": False}
    except KeyError:
        raise HTTPException(404, "PDF候选不存在") from None
    except VersionConflict:
        raise HTTPException(409, "该PDF候选已处理，请刷新候选列表") from None
    except DatabaseUnavailable as error:
        raise _database_error(error) from None


@router.get("/materials/{source_id}/original")
async def read_active_pdf_original(source_id: str, request: Request, expected_version: str):
    repo = repository(request)
    try:
        metadata = await run_in_threadpool(
            repo.get_active_pdf_original,
            valid_id(source_id),
            valid_id(expected_version),
        )
        if metadata is None:
            raise HTTPException(404, "当前PDF资料不存在")
        return await _original_response(metadata, request)
    except VersionConflict:
        raise HTTPException(409, "该版本已被替换，不能以当前PDF冒充旧引用") from None
    except DatabaseUnavailable as error:
        raise _database_error(error) from None
