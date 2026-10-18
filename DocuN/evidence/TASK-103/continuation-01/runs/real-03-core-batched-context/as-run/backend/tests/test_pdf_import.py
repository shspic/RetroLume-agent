"""TASK-047：只验证有界 PDF 解析组件，不代表人工原页核对已完成。"""
from __future__ import annotations

import ctypes
from io import BytesIO
import os
from pathlib import Path
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

from pypdf import PdfWriter

from app.pdf_import import (
    PdfEncryptedError,
    PdfImportLimits,
    PdfInvalidError,
    PdfNoExtractableTextError,
    PdfPageLimitError,
    PdfTextLimitError,
    PdfTimeoutError,
    parse_pdf_bytes,
)


@unittest.skipUnless(os.name == "nt", "TASK-047 only supports Windows Job Objects")
class PdfImportTests(unittest.TestCase):
    def test_two_physical_pages_keep_extracted_text_and_require_review(self):
        original = _text_pdf(["first page", "second page"])

        result = parse_pdf_bytes(original)

        self.assertEqual(result.page_count, 2)
        self.assertEqual([page.physical_page for page in result.pages], [1, 2])
        self.assertEqual([page.text.strip() for page in result.pages], ["first page", "second page"])
        self.assertEqual(result.review_status, "pending_human_review")
        self.assertIn("HUMAN_REVIEW_REQUIRED_BEFORE_LEARNING_USE", result.warnings)
        self.assertEqual(original, _text_pdf(["first page", "second page"]))

    def test_damaged_pdf_is_rejected(self):
        with self.assertRaises(PdfInvalidError) as raised:
            parse_pdf_bytes(b"%PDF-1.7\nnot a valid object graph")
        self.assertEqual(raised.exception.code, "pdf_invalid")

    def test_encrypted_pdf_is_rejected_even_when_it_has_no_text(self):
        writer = PdfWriter()
        writer.add_blank_page(width=72, height=72)
        writer.encrypt("secret")
        output = BytesIO()
        writer.write(output)

        with self.assertRaises(PdfEncryptedError):
            parse_pdf_bytes(output.getvalue())

    def test_image_only_or_blank_pdf_has_no_fabricated_text(self):
        writer = PdfWriter()
        writer.add_blank_page(width=72, height=72)
        output = BytesIO()
        writer.write(output)

        with self.assertRaises(PdfNoExtractableTextError):
            parse_pdf_bytes(output.getvalue())

    def test_page_and_utf8_text_limits_reject_the_whole_result(self):
        with self.subTest("physical pages"):
            with self.assertRaises(PdfPageLimitError):
                parse_pdf_bytes(
                    _text_pdf(["one", "two", "three"]),
                    limits=PdfImportLimits(max_pages=2),
                )
        with self.subTest("UTF-8 extracted text"):
            with self.assertRaises(PdfTextLimitError):
                parse_pdf_bytes(
                    _text_pdf(["abcdef"]),
                    limits=PdfImportLimits(max_text_bytes=3),
                )

    def test_timeout_terminates_the_owned_worker_process(self):
        with tempfile.TemporaryDirectory() as temporary:
            pid_path = Path(temporary) / "pid.txt"

            def slow_command(_input: Path, _output: Path, _limits: PdfImportLimits) -> list[str]:
                script = (
                    "from pathlib import Path; import os,sys,time; "
                    "Path(sys.argv[1]).write_text(str(os.getpid()), encoding='ascii'); "
                    "time.sleep(60)"
                )
                return [sys.executable, "-c", script, str(pid_path)]

            with patch("app.pdf_import.supervisor._build_worker_command", side_effect=slow_command):
                with self.assertRaises(PdfTimeoutError):
                    parse_pdf_bytes(
                        b"%PDF-controlled-timeout-test",
                        limits=PdfImportLimits(timeout_seconds=0.25),
                    )

            self.assertTrue(pid_path.is_file(), "controlled worker did not start")
            pid = int(pid_path.read_text(encoding="ascii"))
            deadline = time.monotonic() + 1.0
            while _process_is_active(pid) and time.monotonic() < deadline:
                time.sleep(0.02)
            self.assertFalse(_process_is_active(pid), "timed-out worker remained active")


def _process_is_active(pid: int) -> bool:
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.OpenProcess.argtypes = [ctypes.c_ulong, ctypes.c_int, ctypes.c_ulong]
    kernel32.OpenProcess.restype = ctypes.c_void_p
    kernel32.GetExitCodeProcess.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_ulong)]
    kernel32.GetExitCodeProcess.restype = ctypes.c_int
    kernel32.CloseHandle.argtypes = [ctypes.c_void_p]
    kernel32.CloseHandle.restype = ctypes.c_int
    handle = kernel32.OpenProcess(0x1000, False, pid)
    if not handle:
        return False
    try:
        exit_code = ctypes.c_ulong()
        if not kernel32.GetExitCodeProcess(handle, ctypes.byref(exit_code)):
            return False
        return exit_code.value == 259
    finally:
        kernel32.CloseHandle(handle)


def _text_pdf(page_texts: list[str]) -> bytes:
    """生成只含内建 Helvetica 与文字流的小型合成 PDF。"""
    objects: list[bytes] = []
    page_ids = [3 + index * 2 for index in range(len(page_texts))]
    kids = b" ".join(f"{object_id} 0 R".encode("ascii") for object_id in page_ids)
    objects.append(b"<< /Type /Catalog /Pages 2 0 R >>")
    objects.append(b"<< /Type /Pages /Kids [" + kids + b"] /Count " + str(len(page_ids)).encode("ascii") + b" >>")
    for object_id, text in zip(page_ids, page_texts, strict=True):
        content_id = object_id + 1
        page = (
            b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 300 144] "
            b"/Resources << /Font << /F1 << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> >> >> "
            b"/Contents " + str(content_id).encode("ascii") + b" 0 R >>"
        )
        safe_text = text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)").encode("ascii")
        stream = b"BT /F1 12 Tf 20 100 Td (" + safe_text + b") Tj ET"
        contents = b"<< /Length " + str(len(stream)).encode("ascii") + b" >>\nstream\n" + stream + b"\nendstream"
        objects.extend([page, contents])

    result = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = [0]
    for object_id, body in enumerate(objects, start=1):
        offsets.append(len(result))
        result.extend(f"{object_id} 0 obj\n".encode("ascii"))
        result.extend(body)
        result.extend(b"\nendobj\n")
    xref_offset = len(result)
    result.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    result.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        result.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    result.extend(
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_offset}\n%%EOF\n".encode("ascii")
    )
    return bytes(result)


if __name__ == "__main__":
    unittest.main()
