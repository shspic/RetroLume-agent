"""TASK-053 的有限合成证据/词项基线验证。"""
import unittest
from unittest.mock import patch

from app.retrieval import SourceTextUnit, build_fragments, rank_term_candidates, verify_fragment


def unit(**changes):
    values = dict(source_id="source-a", version_id="version-1", source_revision=1, physical_page=None, origin_kind="original", text="默认资料", ready_for_learning=True)
    values.update(changes)
    return SourceTextUnit(**values)


class RetrievalTests(unittest.TestCase):
    def test_crlf_chinese_english_text_is_cut_without_rewrite(self):
        original = "中文 Spring\r\nEnglish term"
        fragments = build_fragments(unit(text=original), max_fragment_codepoints=64)
        self.assertEqual([item.text for item in fragments], ["中文 Spring\r\n", "English term"])
        self.assertEqual([(item.start_offset, item.end_offset, item.start_line) for item in fragments], [(0, 11, 1), (11, 23, 2)])
        self.assertTrue(all(verify_fragment(unit(text=original), item) for item in fragments))

    def test_long_line_and_fragment_limit_are_bounded(self):
        original = "abcdefghij"
        self.assertEqual([item.text for item in build_fragments(unit(text=original), max_fragment_codepoints=4)], ["abcd", "efgh", "ij"])
        with self.assertRaisesRegex(ValueError, "数量"):
            build_fragments(unit(text=original), max_fragment_codepoints=2, max_fragments=2)

        def guarded_spans(_text):
            yield 0, 1
            yield 2, 3
            raise AssertionError("片段上限拒绝前不应扫描后续行")

        with patch("app.retrieval.evidence.line_spans", guarded_spans):
            with self.assertRaisesRegex(ValueError, "数量"):
                build_fragments(unit(text="a\nb\nc"), max_fragment_codepoints=1, max_fragments=1)

    def test_id_and_excerpt_verify_deterministically(self):
        source = unit(text="证据原文")
        first = build_fragments(source)[0]
        second = build_fragments(source)[0]
        self.assertEqual(first.evidence_id, second.evidence_id)
        self.assertTrue(verify_fragment(source, first))
        self.assertFalse(verify_fragment(source, first.__class__(**{**first.__dict__, "text": "伪造原文"})))

    def test_same_named_materials_do_not_merge_sources(self):
        first = build_fragments(unit(source_id="source-a", text="同名资料"))[0]
        second = build_fragments(unit(source_id="source-b", text="同名资料"))[0]
        self.assertNotEqual(first.evidence_id, second.evidence_id)
        self.assertFalse(verify_fragment(unit(source_id="source-b", text="同名资料"), first))

    def test_stale_version_and_not_ready_are_rejected(self):
        fragment = build_fragments(unit(version_id="version-2", physical_page=3, origin_kind="user_supplement", text="补充"))[0]
        self.assertFalse(verify_fragment(unit(version_id="version-1", physical_page=3, origin_kind="user_supplement", text="补充"), fragment))
        with self.assertRaisesRegex(ValueError, "未就绪"):
            build_fragments(unit(ready_for_learning=False))

    def test_scope_precedes_bounded_ranking_and_no_evidence_is_empty(self):
        allowed = build_fragments(unit(source_id="allowed", version_id="v1", text="Spring 框架 Spring"))[0]
        hidden = build_fragments(unit(source_id="hidden", version_id="v1", text="Spring Spring Spring"))[0]
        results = rank_term_candidates("Spring 框架", (hidden, allowed), allowed_versions=frozenset({("allowed", "v1")}), top_k=1)
        self.assertEqual([item.fragment.source_id for item in results], ["allowed"])
        self.assertEqual(results[0].matched_terms, ("spring", "框架"))
        self.assertEqual(rank_term_candidates("不存在", (allowed,), allowed_versions=frozenset({("allowed", "v1")})), ())


if __name__ == "__main__":
    unittest.main()
