import { useEffect, useRef, useState } from "react";
import { PdfCitationPage } from "../pdf/PdfReviewPanel";

type Citation = {
  citation_id: string; source_id: string; version_id: string; source_revision: number;
  title: string; format: string; origin_kind: string; physical_page: number | null;
  start_line: number; end_line: number; text: string;
};
export type LearningDocument = {
  action: "first" | "followup"; request_sha256: string;
  profile: "learning.v1"; goal: string; question: string | null; retrieval_mode: string;
  catalog: Citation[]; limitations: string[];
  result: { kind: string; message: string; segments: { text: string; citations: string[] }[]; questions: string[] };
};

export function isLearningDocument(value: unknown, operationId?: string): value is LearningDocument {
  if (typeof value !== "object" || value === null) return false;
  const item = value as Record<string, unknown>;
  const digest = item.request_sha256;
  const bound = typeof digest === "string" && /^[a-f0-9]{64}$/.test(digest) && typeof operationId === "string" &&
    (item.action === "first" ? operationId === `learn-first-v1.${digest}` :
      item.action === "followup" && /^learn-next-v1\.[a-f0-9-]{36}\.[a-f0-9]{64}$/.test(operationId) && operationId.endsWith(`.${digest}`));
  return bound && item.profile === "learning.v1" && typeof item.goal === "string" &&
    Array.isArray(item.limitations) && Array.isArray(item.catalog) && typeof item.result === "object" && item.result !== null;
}

const KINDS: Record<string, string> = { answer: "学习答案", clarification: "需要补充信息", no_evidence: "证据不足", conflict: "来源冲突" };

export function LearningResult({document: result, activityId, operationId, token}: {
  document: LearningDocument; activityId: string; operationId: string; token: string;
}) {
  const [citation, setCitation] = useState<Citation | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [updated, setUpdated] = useState("");
  const controller = useRef<AbortController | null>(null);
  const sequence = useRef(0);
  useEffect(() => {
    sequence.current += 1;
    controller.current?.abort();
    setCitation(null); setError(""); setLoading(false); setUpdated("");
    return () => { sequence.current += 1; controller.current?.abort(); };
  }, [activityId, operationId]);

  async function showCitation(id: string) {
    const seq = ++sequence.current;
    controller.current?.abort();
    const active = new AbortController();
    controller.current = active;
    setCitation(null); setError(""); setLoading(true);
    try {
      const response = await fetch(`/api/activities/${activityId}/learning/operations/${encodeURIComponent(operationId)}/citations/${encodeURIComponent(id)}`, {
        signal: active.signal, headers: { "X-RetroLume-Session": token },
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail?.message ?? "引用原文不可用");
      if (seq !== sequence.current || active.signal.aborted) return;
      setCitation(data.citation as Citation); setUpdated(new Date(data.read_at).toLocaleString("zh-CN", { hour12: false }));
    } catch (reason) {
      if (seq === sequence.current && !active.signal.aborted) {
        setError(reason instanceof Error ? reason.message : "引用读取失败");
        setUpdated(new Date().toLocaleString("zh-CN", { hour12: false }));
      }
    } finally {
      if (seq === sequence.current && !active.signal.aborted) setLoading(false);
    }
  }

  return <section className="ws-learning-result" aria-label="学习成果">
    <h4>{KINDS[result.result.kind] ?? "学习成果"}</h4>
    <p>确认目标：{result.goal}</p>
    {result.question && <p>本次续问：{result.question}</p>}
    <p>{result.result.message}</p>
    {result.result.segments.map((segment, index) => <div className="ws-answer-segment" key={index}>
      <p>{segment.text}</p>
      <div className="ws-citations">{segment.citations.map(id => {
        const entry = result.catalog.find(e => e.citation_id === id);
        return <button className="secondary" key={id} onClick={() => void showCitation(id)}>
          查看引用 · {entry?.title ?? "未知资料"} · {entry?.origin_kind === "user_supplement" ? "用户补充" : "原文"}
          {entry?.physical_page ? ` · 物理页 ${entry.physical_page}` : ` · 行 ${entry?.start_line}–${entry?.end_line}`}
        </button>;
      })}</div>
    </div>)}
    {result.result.questions.length > 0 && <ul>{result.result.questions.map((q, i) => <li key={i}>{q}</li>)}</ul>}
    <p className="quiet">有限词项模式 · {result.limitations.join(" ")}</p>
    <div className="ws-citation-reader" aria-label="引用原文">
      {loading && <p role="status">正在回查引用原文…</p>}
      {error && <p className="failure" role="alert">{error}</p>}
      {updated && <p className="quiet">引用最后核对 {updated}</p>}
      {citation && <>
        <h4>{citation.title} · {citation.origin_kind === "user_supplement" ? "用户补充" : "原文"}</h4>
        <p className="quiet">版本 {citation.source_revision} · {citation.version_id} ·
          {citation.physical_page ? `物理页 ${citation.physical_page}` : `原文行 ${citation.start_line}–${citation.end_line}`}</p>
        <pre>{citation.text}</pre>
        {citation.format === "pdf" && citation.physical_page && <PdfCitationPage token={token}
          sourceId={citation.source_id} versionId={citation.version_id} pageNumber={citation.physical_page} />}
      </>}
    </div>
  </section>;
}
