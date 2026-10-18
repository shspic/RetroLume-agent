"""TXT/Markdown 的纯文本行段定位；不改写或解释原文。"""
import re

MAX_PARAGRAPHS = 100
MAX_EXCERPT_LINES = 500
_NEWLINE = re.compile(r"\r\n|\r|\n")


def line_spans(text: str):
    """逐行返回正文范围；换行符属于前一行，末尾换行保留空末行。"""
    start = 0
    for match in _NEWLINE.finditer(text):
        yield start, match.start()
        start = match.end()
    yield start, len(text)


def newline_style(text: str) -> str:
    style = None
    for match in _NEWLINE.finditer(text):
        current = match.group()
        if style is None:
            style = current
        elif style != current:
            return "mixed"
    if style is None:
        return "none"
    return {"\r\n": "CRLF", "\n": "LF", "\r": "CR"}[style]


def locations(text: str) -> dict:
    paragraphs = []
    start = None
    total_lines = 0
    total_paragraphs = 0
    for number, (line_start, line_end) in enumerate(line_spans(text), start=1):
        total_lines = number
        if text[line_start:line_end].strip():
            if start is None:
                start = number
        elif start is not None:
            total_paragraphs += 1
            if total_paragraphs <= MAX_PARAGRAPHS:
                paragraphs.append({"paragraph": total_paragraphs, "start_line": start, "end_line": number - 1})
            start = None
    if start is not None:
        total_paragraphs += 1
        if total_paragraphs <= MAX_PARAGRAPHS:
            paragraphs.append({"paragraph": total_paragraphs, "start_line": start, "end_line": total_lines})
    return {
        "line_ending": newline_style(text),
        "trailing_newline": text.endswith(("\r", "\n")),
        "total_lines": total_lines,
        "total_paragraphs": total_paragraphs,
        "paragraphs": paragraphs,
        "paragraphs_truncated": total_paragraphs > MAX_PARAGRAPHS,
    }


def excerpt(text: str, start_line: int, end_line: int) -> str:
    if start_line < 1 or end_line < start_line:
        raise ValueError("行号范围超出原文")
    if end_line - start_line + 1 > MAX_EXCERPT_LINES:
        raise ValueError(f"单次摘录最多{MAX_EXCERPT_LINES}行")
    selected_start = None
    for number, (line_start, line_end) in enumerate(line_spans(text), start=1):
        if number == start_line:
            selected_start = line_start
        if number == end_line and selected_start is not None:
            # 结束行的终止符不属于摘录；中间行的原始 CRLF/LF/CR 保留。
            return text[selected_start:line_end]
    raise ValueError("行号范围超出原文")
