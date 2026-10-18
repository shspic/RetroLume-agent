/** TASK-064 离线检查（B档单批，4例，无新依赖、无网络/数据库/进程）。
 *
 * 复用 TASK-063 原始迁移后结构JSON（只读），反例仅在内存副本上构造：
 * a 原始真实清单通过局部谓词；
 * b 去掉status值域约束 → 失败；
 * c 去掉decided_at一致性约束 → 失败；
 * d pending分支IS NULL与非pending分支IS NOT NULL反转 → 失败。
 * 与主脚本共用 tests/task064_candidate_constraints.mjs 同一实现，不复制谓词。
 */
import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
import {
  candidateConstraintProblems,
  matchesCandidateStatusDomain,
  matchesCandidateDecidedAtConsistency,
} from "./task064_candidate_constraints.mjs";

const EVIDENCE = join(
  dirname(fileURLToPath(import.meta.url)), "..", "Ndocu", "evidence", "task-063",
  "task063-resume1-20260921T0905Z", "task057-db-schema-inventory-after-migration.json",
);
const inventory = JSON.parse(readFileSync(EVIDENCE, "utf8"));
const cons = inventory.constraints;

test("a: 原始真实清单通过候选约束局部谓词", () => {
  assert.deepEqual(candidateConstraintProblems(cons), []);
});

test("b: 去掉status值域约束后失败", () => {
  const broken = cons.filter(
    c => !(c.table === "pdf_review_candidates" && c.name === "pdf_review_candidates_status_check"),
  );
  const problems = candidateConstraintProblems(broken);
  assert.ok(problems.some(p => p.includes("值域")), `应报值域缺失，实际：${problems.join("；")}`);
  assert.ok(!problems.some(p => p.includes("一致性")), "不应连带报一致性缺失");
});

test("c: 去掉decided_at一致性约束后失败", () => {
  const broken = cons.filter(
    c => !(c.table === "pdf_review_candidates" && c.name === "pdf_review_candidates_check"),
  );
  const problems = candidateConstraintProblems(broken);
  assert.ok(problems.some(p => p.includes("一致性")), `应报一致性缺失，实际：${problems.join("；")}`);
  assert.ok(!problems.some(p => p.includes("值域")), "不应连带报值域缺失");
});

test("d: pending分支IS NULL与非pending分支IS NOT NULL反转后失败", () => {
  const invertedDef =
    "CHECK ((((status = 'pending'::text) AND (decided_at IS NOT NULL)) OR ((status <> 'pending'::text) AND (decided_at IS NULL))))";
  const broken = cons.map(c =>
    (c.table === "pdf_review_candidates" && c.name === "pdf_review_candidates_check")
      ? { ...c, def: invertedDef }
      : c,
  );
  const problems = candidateConstraintProblems(broken);
  assert.ok(problems.some(p => p.includes("一致性")), `反转约束应被拒绝，实际：${problems.join("；")}`);
  assert.equal(matchesCandidateDecidedAtConsistency(invertedDef), false);
  assert.equal(matchesCandidateStatusDomain(invertedDef), false);
});
