import { useEffect, useRef, useState } from "react";
import { PdfCitationPage } from "../pdf/PdfReviewPanel";
import { getTeachingCitation, type TeachingCitation } from "./teachingApi";

export function citationIds(value: unknown): string[] {
  const ids = new Set<string>();
  function visit(item: unknown) {
    if (Array.isArray(item)) item.forEach(visit);
    else if (item && typeof item === "object") {
      const object = item as Record<string, unknown>;
      if (Array.isArray(object.citations)) object.citations.forEach(id => { if (typeof id === "string") ids.add(id); });
      Object.values(object).forEach(visit);
    }
  }
  visit(value);
  return [...ids];
}

export function TeachingCitations({activityId, recordId, ids, token, label}: {
  activityId: string; recordId?: string; ids: string[]; token: string; label: string;
}) {
  const [citation, setCitation] = useState<TeachingCitation | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const sequence = useRef(0);
  const controller = useRef<AbortController | null>(null);
  const identity = `${activityId}|${recordId}|${ids.join("|")}`;
  useEffect(() => {
    ++sequence.current; controller.current?.abort(); setCitation(null); setError(""); setLoading(false);
    return () => { ++sequence.current; controller.current?.abort(); };
  }, [identity]);
  async function show(id: string) {
    if (!recordId) return;
    const seq = ++sequence.current;
    controller.current?.abort(); const active = new AbortController(); controller.current = active;
    setCitation(null); setError(""); setLoading(true);
    try {
      const result = await getTeachingCitation(activityId, recordId, id, token, active.signal);
      if (seq === sequence.current && !active.signal.aborted) setCitation(result.citation);
    } catch (reason) {
      if (seq === sequence.current && !active.signal.aborted) setError(reason instanceof Error ? reason.message : "依据读取未确认");
    } finally {
      if (seq === sequence.current && !active.signal.aborted) setLoading(false);
    }
  }
  if (!recordId || !ids.length) return null;
  return <div className="ws-citations" aria-label={`${label}依据`}>
    {ids.map((id, index) => <button className="secondary" key={id} onClick={() => void show(id)}>查看依据 · {label} · {index + 1}</button>)}
    {loading && <p role="status">正在回查原文与位置…</p>}
    {error && <p role="alert">{error}</p>}
    {citation && <div aria-label="教学引用原文">
      <strong>{citation.title} · {citation.origin_kind === "user_supplement" ? "用户补充" : "原文"}</strong>
      <p>版本 {citation.source_revision} · {citation.version_id} · {citation.physical_page ? `物理页 ${citation.physical_page}` : `原文行 ${citation.start_line}–${citation.end_line}`}</p>
      <pre style={{whiteSpace:"pre-wrap"}}>{citation.text}</pre>
      {citation.format === "pdf" && citation.physical_page && <PdfCitationPage token={token}
        sourceId={citation.source_id} versionId={citation.version_id} pageNumber={citation.physical_page} />}
    </div>}
  </div>;
}
