"""仅由监督器启动的 PDF 提取子进程。"""
from __future__ import annotations

import argparse
from io import BytesIO
import json
from pathlib import Path
import sys


def main() -> int:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--max-pages", required=True, type=int)
    parser.add_argument("--max-text-bytes", required=True, type=int)
    parser.add_argument("--max-output-bytes", required=True, type=int)
    args = parser.parse_args()

    try:
        payload = _extract(Path(args.input).read_bytes(), args.max_pages, args.max_text_bytes)
    except _ExpectedFailure as exc:
        payload = {"ok": False, "error": {"code": exc.code, "message": exc.message}}
    except Exception:
        payload = {
            "ok": False,
            "error": {"code": "pdf_worker_failed", "message": "PDF extraction failed unexpectedly"},
        }

    encoded = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    if len(encoded) > args.max_output_bytes:
        encoded = json.dumps({
            "ok": False,
            "error": {"code": "pdf_worker_protocol_too_large", "message": "PDF worker output exceeded its limit"},
        }, separators=(",", ":")).encode("utf-8")
    Path(args.output).write_bytes(encoded)
    return 0


def _extract(data: bytes, max_pages: int, max_text_bytes: int) -> dict[str, object]:
    try:
        from pypdf import PdfReader
        reader = PdfReader(BytesIO(data), strict=False)
        if reader.is_encrypted:
            raise _ExpectedFailure("pdf_encrypted", "Encrypted PDFs are not supported")
        page_count = len(reader.pages)
    except _ExpectedFailure:
        raise
    except Exception:
        raise _ExpectedFailure("pdf_invalid", "The file is not a readable PDF")

    if page_count > max_pages:
        raise _ExpectedFailure("pdf_page_limit_exceeded", f"PDF has {page_count} pages; limit is {max_pages}")

    pages: list[dict[str, object]] = []
    total_text_bytes = 0
    has_visible_text = False
    for index, page in enumerate(reader.pages, start=1):
        try:
            text = page.extract_text() or ""
        except Exception:
            raise _ExpectedFailure("pdf_invalid", f"Text extraction failed on physical page {index}")
        encoded_length = len(text.encode("utf-8"))
        total_text_bytes += encoded_length
        if total_text_bytes > max_text_bytes:
            raise _ExpectedFailure("pdf_text_limit_exceeded", f"Extracted text exceeds {max_text_bytes} UTF-8 bytes")
        page_warnings: list[str] = []
        if not text.strip():
            page_warnings.append("NO_EXTRACTABLE_TEXT_ON_PAGE")
        else:
            has_visible_text = True
        pages.append({"physical_page": index, "text": text, "warnings": page_warnings})

    if not has_visible_text:
        raise _ExpectedFailure(
            "pdf_no_extractable_text",
            "PDF has no extractable text; it may be scanned or image-only",
        )
    return {
        "ok": True,
        "page_count": page_count,
        "pages": pages,
        "warnings": [
            "PYPDF_TEXT_HAS_NO_LAYOUT_FIDELITY_GUARANTEE",
            "HUMAN_REVIEW_REQUIRED_BEFORE_LEARNING_USE",
        ],
    }


class _ExpectedFailure(Exception):
    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message


if __name__ == "__main__":
    sys.exit(main())
