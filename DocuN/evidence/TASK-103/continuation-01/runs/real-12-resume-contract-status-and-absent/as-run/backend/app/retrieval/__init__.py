"""版本化原文片段与有限词项候选；不含向量、数据库或 HTTP 接口。"""

from .evidence import (
    EvidenceFragment,
    RetrievalCandidate,
    SourceTextUnit,
    build_fragments,
    rank_term_candidates,
    verify_fragment,
)

__all__ = [
    "EvidenceFragment",
    "RetrievalCandidate",
    "SourceTextUnit",
    "build_fragments",
    "rank_term_candidates",
    "verify_fragment",
]
