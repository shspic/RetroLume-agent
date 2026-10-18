"""PDF 逐页核对输入验证；不改写解析器返回的原始文字。"""
from dataclasses import dataclass


MAX_SUPPLEMENT_BYTES = 64 * 1024


@dataclass(frozen=True)
class ReviewPage:
    physical_page: int
    reviewed: bool
    supplement: str | None = None


def validate_review_pages(page_count: int, pages: list[ReviewPage]) -> tuple[ReviewPage, ...]:
    if type(page_count) is not int or page_count <= 0:
        raise ValueError("PDF候选页数无效")
    if not pages:
        raise ValueError("必须逐页核对后才能确认")
    numbers: list[int] = []
    for page in pages:
        if type(page.physical_page) is not int or not 1 <= page.physical_page <= page_count:
            raise ValueError("核对页码超出PDF物理页范围")
        if page.reviewed is not True:
            raise ValueError(f"第{page.physical_page}页尚未明确核对")
        if page.supplement is not None:
            if not isinstance(page.supplement, str):
                raise ValueError("用户补充必须是文字")
            if len(page.supplement.encode("utf-8")) > MAX_SUPPLEMENT_BYTES:
                raise ValueError(f"第{page.physical_page}页的用户补充不能超过64 KiB")
        numbers.append(page.physical_page)
    if len(numbers) != len(set(numbers)):
        raise ValueError("同一物理页不能重复确认")
    if set(numbers) != set(range(1, page_count + 1)):
        raise ValueError("核对页列表不完整，不能确认")
    return tuple(sorted(pages, key=lambda page: page.physical_page))
