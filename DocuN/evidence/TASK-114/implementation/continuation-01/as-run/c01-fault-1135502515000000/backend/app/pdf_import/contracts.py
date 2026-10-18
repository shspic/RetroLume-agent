"""有界 PDF 文字提取的输入限制与结果契约。"""
from dataclasses import dataclass


MIB = 1024 * 1024


@dataclass(frozen=True)
class PdfImportLimits:
    max_input_bytes: int = 5 * MIB
    max_pages: int = 50
    max_text_bytes: int = 2 * MIB
    timeout_seconds: float = 10.0
    max_output_bytes: int = 8 * MIB
    process_memory_bytes: int = 256 * MIB

    def validate(self) -> None:
        _bounded_int("max_input_bytes", self.max_input_bytes, 1, 5 * MIB)
        _bounded_int("max_pages", self.max_pages, 1, 50)
        _bounded_int("max_text_bytes", self.max_text_bytes, 1, 2 * MIB)
        _bounded_number("timeout_seconds", self.timeout_seconds, 0.05, 10.0)
        _bounded_int("max_output_bytes", self.max_output_bytes, 1024, 16 * MIB)
        _bounded_int("process_memory_bytes", self.process_memory_bytes, 64 * MIB, 512 * MIB)


@dataclass(frozen=True)
class PdfPage:
    physical_page: int
    text: str
    warnings: tuple[str, ...]


@dataclass(frozen=True)
class PdfImportResult:
    page_count: int
    pages: tuple[PdfPage, ...]
    warnings: tuple[str, ...]
    extraction_method: str = "pypdf-6.17.0"
    review_status: str = "pending_human_review"


def _bounded_int(name: str, value: object, minimum: int, maximum: int) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or not minimum <= value <= maximum:
        raise ValueError(f"{name} must be an integer between {minimum} and {maximum}")


def _bounded_number(name: str, value: object, minimum: float, maximum: float) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not minimum <= value <= maximum:
        raise ValueError(f"{name} must be between {minimum} and {maximum}")
