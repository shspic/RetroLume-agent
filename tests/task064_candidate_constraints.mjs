/** TASK-064 纯函数：pdf_review_candidates 候选状态/decided_at 约束核对。
 *
 * 背景（TASK-063 exit1 反例）：backend/migrations/003_pdf_review.sql 中候选表的
 * status 值域与 status/decided_at 一致性在 PostgreSQL pg_get_constraintdef 导出中
 * 是两条独立 CHECK；旧谓词要求同一 CHECK 同时含 'confirmed'/'skipped'/decided_at，
 * 会误拒绝正确迁移。本模块按固定 DDL 的实际导出表示做局部核对，不建通用 SQL 解析器。
 *
 * 核对口径：
 * - 只支持本项目固定 DDL 的已知导出形式；做有限空白规范化后与固定结构精确比对，
 *   未知表示、关键词拼凑、反向条件（IS NULL / IS NOT NULL 反转）一律拒绝，不默认成功。
 * - 值域与一致性不要求同处一条 CHECK，分别存在即可。
 * - 本模块为纯函数：不 import 任何会启动资源的主脚本，不访问网络/数据库/进程。
 */

// 固定结构来源：
// - 值域：003 第14行 status IN ('pending','confirmed','skipped')
//   的实际导出（task-063 原始结构JSON pdf_review_candidates_status_check）。
// - 一致性：003 第23行
//   CHECK ((status='pending' AND decided_at IS NULL) OR (status<>'pending' AND decided_at IS NOT NULL))
//   的实际导出（task-063 原始结构JSON pdf_review_candidates_check）。
const STATUS_DOMAIN_EXPECTED =
  "CHECK ((status = ANY (ARRAY['pending'::text, 'confirmed'::text, 'skipped'::text])))";
const DECIDED_AT_CONSISTENCY_EXPECTED =
  "CHECK ((((status = 'pending'::text) AND (decided_at IS NULL)) OR ((status <> 'pending'::text) AND (decided_at IS NOT NULL))))";

/** 有限空白规范化：连续空白折叠为单个空格并去首尾。 */
function normalizeWhitespace(def) {
  return String(def).replace(/\s+/g, " ").trim();
}

/** 候选状态值域检查约束（pending/confirmed/skipped）是否为已知正确导出形式。 */
export function matchesCandidateStatusDomain(def) {
  return normalizeWhitespace(def) === STATUS_DOMAIN_EXPECTED;
}

/** 状态/decided_at 一致性检查约束（pending→NULL，非pending→NOT NULL）是否为已知正确导出形式。 */
export function matchesCandidateDecidedAtConsistency(def) {
  return normalizeWhitespace(def) === DECIDED_AT_CONSISTENCY_EXPECTED;
}

/**
 * 对 fetchSchemaInventory 导出的 constraints 数组核对候选表两条约束。
 * 返回问题列表（空数组 = 通过）。值域与一致性分别核对，不要求同一 CHECK。
 */
export function candidateConstraintProblems(cons) {
  const problems = [];
  const checks = (Array.isArray(cons) ? cons : [])
    .filter(c => c && c.table === "pdf_review_candidates" && c.type === "c");
  if (!checks.some(c => matchesCandidateStatusDomain(c.def))) {
    problems.push("缺 pdf_review_candidates.status 值域检查约束（pending/confirmed/skipped）");
  }
  if (!checks.some(c => matchesCandidateDecidedAtConsistency(c.def))) {
    problems.push("缺 pdf_review_candidates 状态/decided_at 一致性检查约束");
  }
  return problems;
}
