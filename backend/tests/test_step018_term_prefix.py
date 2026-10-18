"""长中文目标的有限词项通道，完整查询与范围不被改写。"""
import unittest
from app.retrieval.evidence import SourceTextUnit,build_fragments,rank_term_candidates,MAX_QUERY_TERMS

class TermPrefixTests(unittest.TestCase):
    def test_frozen_interview_goal_keeps_bounded_channel_and_scope(self):
        query='围绕这份虚构接口项目资料，练习技术面试，重点是个人分工与测量口径。'
        good=build_fragments(SourceTextUnit('source-R','version-R',1,None,'original','虚构接口项目资料中，我参与缓存路径改造。',True))
        outside=build_fragments(SourceTextUnit('source-M','version-M',1,None,'original','虚构接口项目资料的测量口径。',True))
        with self.assertRaisesRegex(ValueError,'词项数量'):rank_term_candidates(query,good,allowed_versions=frozenset({('source-R','version-R')}))
        ranked=rank_term_candidates(query,good+outside,allowed_versions=frozenset({('source-R','version-R')}),truncate_terms=True)
        self.assertTrue(ranked)
        self.assertTrue(all(x.fragment.source_id=='source-R' and len(x.matched_terms)<=MAX_QUERY_TERMS for x in ranked))

    def test_byte_limit_and_empty_channel_remain_closed(self):
        with self.assertRaisesRegex(ValueError,'16 KiB'):rank_term_candidates('长'*6000,(),allowed_versions=frozenset(),truncate_terms=True)
        self.assertEqual(rank_term_candidates('none',(),allowed_versions=frozenset(),truncate_terms=True),())

if __name__=='__main__':unittest.main()
