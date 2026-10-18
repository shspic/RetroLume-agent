"""有界文字 PDF 解析组件。"""
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
from .supervisor import parse_pdf_bytes

__all__ = [
    "PdfEncryptedError",
    "PdfImportError",
    "PdfImportLimits",
    "PdfImportResult",
    "PdfInputTooLargeError",
    "PdfInvalidError",
    "PdfNoExtractableTextError",
    "PdfPage",
    "PdfPageLimitError",
    "PdfProtocolError",
    "PdfSandboxSetupError",
    "PdfTextLimitError",
    "PdfTimeoutError",
    "PdfUnsupportedPlatformError",
    "PdfWorkerError",
    "parse_pdf_bytes",
]
