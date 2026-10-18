"""PDF bytes 到待人工核对分页文字的失败关闭监督器。"""
from __future__ import annotations

import json
import os
from pathlib import Path
import sys
import tempfile

from ._windows_job import JobSetupError, JobTimeout, run_in_job
from .contracts import PdfImportLimits, PdfImportResult, PdfPage
from .errors import (
    PdfEncryptedError,
    PdfImportError,
    PdfInputTooLargeError,
    PdfInvalidError,
    PdfNoExtractableTextError,
    PdfPageLimitError,
    PdfProtocolError,
    PdfSandboxSetupError,
    PdfTextLimitError,
    PdfTimeoutError,
    PdfUnsupportedPlatformError,
    PdfWorkerError,
)


_ERROR_TYPES: dict[str, type[PdfImportError]] = {
    error.code: error for error in (
        PdfEncryptedError,
        PdfInvalidError,
        PdfNoExtractableTextError,
        PdfPageLimitError,
        PdfTextLimitError,
        PdfWorkerError,
    )
}


def parse_pdf_bytes(data: bytes, *, limits: PdfImportLimits | None = None) -> PdfImportResult:
    """提取物理分页文字；结果始终为待人工核对，不能直接批准学习使用。"""
    if not isinstance(data, bytes):
        raise TypeError("data must be bytes")
    selected = limits or PdfImportLimits()
    selected.validate()
    if len(data) > selected.max_input_bytes:
        raise PdfInputTooLargeError(
            f"PDF is {len(data)} bytes; limit is {selected.max_input_bytes}"
        )
    if not data:
        raise PdfInvalidError("The file is not a readable PDF")
    if os.name != "nt":
        raise PdfUnsupportedPlatformError("This PDF worker currently requires Windows Job Objects")

    backend_root = Path(__file__).resolve().parents[2]
    with tempfile.TemporaryDirectory(prefix="retrolume-pdf-") as temporary:
        temp_root = Path(temporary)
        input_path = temp_root / "input.pdf"
        output_path = temp_root / "output.json"
        input_path.write_bytes(data)
        command = _build_worker_command(input_path, output_path, selected)
        try:
            completed = run_in_job(
                command,
                cwd=str(backend_root),
                timeout_seconds=selected.timeout_seconds,
                memory_bytes=selected.process_memory_bytes,
            )
        except JobTimeout as exc:
            raise PdfTimeoutError(str(exc)) from None
        except JobSetupError as exc:
            raise PdfSandboxSetupError(str(exc)) from None

        if completed.exit_code != 0:
            raise PdfWorkerError(f"PDF worker exited with code {completed.exit_code}")
        if not output_path.is_file():
            raise PdfProtocolError("PDF worker returned no result")
        output_size = output_path.stat().st_size
        if output_size > selected.max_output_bytes:
            raise PdfProtocolError("PDF worker result exceeded its protocol limit")
        try:
            payload = json.loads(output_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError):
            raise PdfProtocolError("PDF worker returned invalid JSON") from None
    return _decode_payload(payload, selected)


def _build_worker_command(input_path: Path, output_path: Path, limits: PdfImportLimits) -> list[str]:
    return [
        sys.executable,
        "-m",
        "app.pdf_import.worker",
        "--input",
        str(input_path),
        "--output",
        str(output_path),
        "--max-pages",
        str(limits.max_pages),
        "--max-text-bytes",
        str(limits.max_text_bytes),
        "--max-output-bytes",
        str(limits.max_output_bytes),
    ]


def _decode_payload(payload: object, limits: PdfImportLimits) -> PdfImportResult:
    if not isinstance(payload, dict) or not isinstance(payload.get("ok"), bool):
        raise PdfProtocolError("PDF worker result has an invalid envelope")
    if payload["ok"] is False:
        error = payload.get("error")
        if not isinstance(error, dict) or not isinstance(error.get("code"), str) or not isinstance(error.get("message"), str):
            raise PdfProtocolError("PDF worker error has an invalid shape")
        error_type = _ERROR_TYPES.get(error["code"])
        if error_type is None:
            raise PdfProtocolError(f"PDF worker returned unknown error code {error['code']!r}")
        raise error_type(error["message"][:500])

    page_count = payload.get("page_count")
    raw_pages = payload.get("pages")
    raw_warnings = payload.get("warnings")
    if (
        isinstance(page_count, bool)
        or not isinstance(page_count, int)
        or not 1 <= page_count <= limits.max_pages
        or not isinstance(raw_pages, list)
        or len(raw_pages) != page_count
    ):
        raise PdfProtocolError("PDF worker returned an invalid page count")
    warnings = _decode_warnings(raw_warnings)
    pages: list[PdfPage] = []
    total_text_bytes = 0
    for expected_page, raw_page in enumerate(raw_pages, start=1):
        if (
            not isinstance(raw_page, dict)
            or raw_page.get("physical_page") != expected_page
            or not isinstance(raw_page.get("text"), str)
        ):
            raise PdfProtocolError("PDF worker returned an invalid physical page")
        page_warnings = _decode_warnings(raw_page.get("warnings"))
        text = raw_page["text"]
        total_text_bytes += len(text.encode("utf-8"))
        if total_text_bytes > limits.max_text_bytes:
            raise PdfProtocolError("PDF worker returned text beyond the configured limit")
        pages.append(PdfPage(expected_page, text, page_warnings))
    if not any(page.text.strip() for page in pages):
        raise PdfProtocolError("PDF worker returned no extractable text as success")
    return PdfImportResult(page_count, tuple(pages), warnings)


def _decode_warnings(value: object) -> tuple[str, ...]:
    if not isinstance(value, list) or len(value) > 100 or any(not isinstance(item, str) or len(item) > 200 for item in value):
        raise PdfProtocolError("PDF worker returned invalid warnings")
    return tuple(value)
