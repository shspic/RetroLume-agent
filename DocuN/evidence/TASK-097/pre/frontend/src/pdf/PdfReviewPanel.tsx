import { useEffect, useRef, useState } from "react";
import { GlobalWorkerOptions, getDocument, type PDFDocumentProxy, type RenderTask } from "pdfjs-dist";
import workerUrl from "pdfjs-dist/build/pdf.worker.min.mjs?url";
import "./pdf-review.css";

GlobalWorkerOptions.workerSrc = workerUrl;

const MAX_CANVAS_PIXELS = 4_000_000;

export type PdfMaterial = {id: string; title: string; version_id: string; revision: number; size: number; format: string; created_at: string};
type CandidateRow = {
  candidate_id: string; source_id: string; version_id: string; filename: string; sha256: string;
  size: number; page_count: number; status: string; revision: number; current_version: string | null;
};
type CandidatePage = {version_id: string; physical_page: number; raw_text: string; identity: "pdf_extracted_text"; warnings: string[]};
type CandidateDetail = CandidateRow & {pages: CandidatePage[]; query_ready: false};

async function jsonRequest(token: string, path: string, init: RequestInit = {}) {
  let response: Response;
  try {
    response = await fetch(path, {...init, headers: {...init.headers, "X-RetroLume-Session": token}});
  } catch {
    throw new Error("连接中断，请刷新候选列表确认当前状态。");
  }
  const data = await response.json();
  if (!response.ok) throw new Error(typeof data.detail === "string" ? data.detail : "请求未完成");
  return data;
}

function PdfPageCanvas({candidateId, pageNumber, token, onRenderStatus}: {
  candidateId: string; pageNumber: number; token: string; onRenderStatus: (page: number, ready: boolean) => void;
}) {
  const canvas = useRef<HTMLCanvasElement>(null);
  const renderTask = useRef<RenderTask | null>(null);
  const loadingTaskRef = useRef<ReturnType<typeof getDocument> | null>(null);
  const statusCallback = useRef(onRenderStatus);
  const [document, setDocument] = useState<PDFDocumentProxy | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {statusCallback.current = onRenderStatus;}, [onRenderStatus]);
  useEffect(() => {
    const controller = new AbortController();
    let active = true;
    let loadingTask: ReturnType<typeof getDocument> | null = null;
    setDocument(null); setError("");
    fetch(`/api/pdf-candidates/${candidateId}/original`, {
      signal: controller.signal,
      headers: {"X-RetroLume-Session": token},
    }).then(async response => {
      if (!response.ok) {
        const data = await response.json().catch(() => ({}));
        throw new Error(typeof data.detail === "string" ? data.detail : "无法读取PDF原件");
      }
      return response.arrayBuffer();
    }).then(bytes => {
      if (!active) return;
      loadingTask = getDocument({
        data: new Uint8Array(bytes),
        enableXfa: false,
        useSystemFonts: false,
        disableRange: true,
        disableStream: true,
        disableAutoFetch: true,
        maxImageSize: MAX_CANVAS_PIXELS,
        useWorkerFetch: false,
      });
      loadingTaskRef.current = loadingTask;
      return loadingTask.promise;
    }).then(pdf => {
      if (!active || !pdf) {if (loadingTask) void loadingTask.destroy(); return;}
      setDocument(pdf);
    }).catch(reason => {
      if (active && !(reason instanceof DOMException && reason.name === "AbortError")) {
        setError(reason instanceof Error ? reason.message : "PDF原页加载失败");
      }
    });
    return () => {
      active = false;
      controller.abort();
      renderTask.current?.cancel();
      renderTask.current = null;
      const task = loadingTaskRef.current ?? loadingTask;
      loadingTaskRef.current = null;
      if (task) void task.destroy();
    };
  }, [candidateId, token]);

  useEffect(() => {
    statusCallback.current(pageNumber, false);
    setError("");
    if (!document || !canvas.current) return;
    let active = true;
    document.getPage(pageNumber).then(page => {
      if (!active || !canvas.current) return;
      const natural = page.getViewport({scale: 1.35});
      const reduction = Math.min(1, Math.sqrt(MAX_CANVAS_PIXELS / (natural.width * natural.height)));
      const viewport = page.getViewport({scale: 1.35 * reduction});
      const target = canvas.current;
      target.width = Math.max(1, Math.floor(viewport.width));
      target.height = Math.max(1, Math.floor(viewport.height));
      target.style.aspectRatio = `${target.width} / ${target.height}`;
      const context = target.getContext("2d", {alpha: false});
      if (!context) throw new Error("浏览器无法创建PDF画布");
      renderTask.current?.cancel();
      const task = page.render({canvas: target, canvasContext: context, viewport});
      renderTask.current = task;
      return task.promise.then(() => {
        if (active && renderTask.current === task) statusCallback.current(pageNumber, true);
      }).finally(() => page.cleanup());
    }).catch(reason => {
      if (active && reason?.name !== "RenderingCancelledException") {
        statusCallback.current(pageNumber, false);
        setError(reason instanceof Error ? reason.message : "PDF原页渲染失败");
      }
    });
    return () => {
      active = false;
      renderTask.current?.cancel();
      renderTask.current = null;
    };
  }, [document, pageNumber]);

  return <div className="pdf-canvas-wrap">
    {!document && !error && <p role="status">正在加载PDF原件…</p>}
    {error && <p className="failure" role="alert">{error}。该页不能确认。</p>}
    <canvas ref={canvas} aria-label={`PDF物理页 ${pageNumber}`} />
  </div>;
}

export function PdfReviewPanel({token, reloadKey, onActivated}: {
  token: string; reloadKey: number; onActivated: (material: PdfMaterial) => void;
}) {
  const [candidates, setCandidates] = useState<CandidateRow[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [detail, setDetail] = useState<CandidateDetail | null>(null);
  const [pageNumber, setPageNumber] = useState(1);
  const [checked, setChecked] = useState<Record<number, boolean>>({});
  const [supplements, setSupplements] = useState<Record<number, string>>({});
  const [rendered, setRendered] = useState<Set<number>>(new Set());
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  async function reload() {
    const data = await jsonRequest(token, "/api/pdf-candidates");
    setCandidates(data.items);
    setSelectedId(previous => data.items.some((item: CandidateRow) => item.candidate_id === previous) ? previous : data.items[0]?.candidate_id ?? null);
  }

  useEffect(() => {void reload().catch(reason => setError(reason.message));}, [token, reloadKey]);
  useEffect(() => {
    if (!selectedId) {setDetail(null); return;}
    const controller = new AbortController();
    setError(""); setNotice(""); setDetail(null); setPageNumber(1); setChecked({}); setSupplements({}); setRendered(new Set());
    jsonRequest(token, `/api/pdf-candidates/${selectedId}`, {signal: controller.signal})
      .then(data => {if (!controller.signal.aborted) setDetail(data.candidate);})
      .catch(reason => {if (!controller.signal.aborted) setError(reason.message);});
    return () => controller.abort();
  }, [selectedId, token]);

  const page = detail?.pages.find(item => item.physical_page === pageNumber);
  const allReviewed = !!detail && detail.pages.length === detail.page_count && detail.pages.every(item => checked[item.physical_page] && rendered.has(item.physical_page));

  function markRendered(page: number, ready: boolean) {
    setRendered(previous => {
      const next = new Set(previous);
      if (ready) next.add(page); else next.delete(page);
      return next;
    });
    if (!ready) setChecked(previous => ({...previous, [page]: false}));
  }

  async function confirm() {
    if (!detail || !allReviewed || busy) return;
    setBusy(true); setError(""); setNotice("");
    try {
      const data = await jsonRequest(token, `/api/pdf-candidates/${detail.candidate_id}/confirm`, {
        method: "POST", headers: {"Content-Type": "application/json"},
        body: JSON.stringify({version_id: detail.version_id, pages: detail.pages.map(item => ({
          physical_page: item.physical_page, reviewed: true, supplement: supplements[item.physical_page] || null,
        }))}),
      });
      setNotice("逐页确认已保存，该PDF现在可供后续查询。");
      onActivated(data.material);
      await reload();
    } catch (reason) {setError(reason instanceof Error ? reason.message : "确认失败");}
    finally {setBusy(false);}
  }

  async function skip() {
    if (!detail || busy) return;
    setBusy(true); setError(""); setNotice("");
    try {
      await jsonRequest(token, `/api/pdf-candidates/${detail.candidate_id}/skip`, {method: "POST"});
      setNotice("已跳过该候选；原件和此前可用版本均保留。");
      await reload();
    } catch (reason) {setError(reason instanceof Error ? reason.message : "跳过失败");}
    finally {setBusy(false);}
  }

  if (!candidates.length && !detail) return notice ? <p className="notice" role="status">{notice}</p> : null;
  return <section className="pdf-review" aria-labelledby="pdf-review-title">
    <div className="section-title"><div><p className="eyebrow">PDF HUMAN REVIEW</p><h2 id="pdf-review-title">待核对PDF</h2></div><span>{candidates.length} 份</span></div>
    {candidates.length > 1 && <label>选择候选<select value={selectedId ?? ""} onChange={event => setSelectedId(event.target.value)}>{candidates.map(item => <option key={item.candidate_id} value={item.candidate_id}>{item.filename}</option>)}</select></label>}
    {detail && page && <>
      <div className="pdf-review-meta"><strong>{detail.filename}</strong><span>候选版本 {detail.version_id.slice(0, 8)} · SHA-256 {detail.sha256.slice(0, 12)}…</span><span>待核对，不会供学习或查询使用{detail.current_version ? "；此前版本仍在用" : ""}</span></div>
      <div className="pdf-page-controls"><button disabled={pageNumber <= 1} onClick={() => setPageNumber(value => value - 1)}>上一页</button><strong>物理页 {pageNumber} / {detail.page_count}</strong><button disabled={pageNumber >= detail.page_count} onClick={() => setPageNumber(value => value + 1)}>下一页</button></div>
      <div className="pdf-compare">
        <PdfPageCanvas candidateId={detail.candidate_id} pageNumber={pageNumber} token={token} onRenderStatus={markRendered}/>
        <div className="pdf-extracted"><h3>该页提取文字</h3><p className="quiet">这是 pypdf 原始提取结果，不代表版面或语义已自动验证。</p><pre>{page.raw_text}</pre>
          <label className="review-check"><input type="checkbox" checked={!!checked[pageNumber]} disabled={!rendered.has(pageNumber)} onChange={event => setChecked(previous => ({...previous, [pageNumber]: event.target.checked}))}/>我已对照原页核对本页</label>
          <label>用户补充（可选，独立保存，不覆盖原提取文字）<textarea value={supplements[pageNumber] ?? ""} maxLength={65536} onChange={event => setSupplements(previous => ({...previous, [pageNumber]: event.target.value}))}/></label>
        </div>
      </div>
      <p className="quiet">已核对并成功渲染 {detail.pages.filter(item => checked[item.physical_page] && rendered.has(item.physical_page)).length} / {detail.page_count} 页。必须逐页完成。</p>
      <div className="pdf-actions"><button className="secondary" disabled={busy} onClick={() => void skip()}>跳过候选</button><button className="primary" disabled={busy || !allReviewed} onClick={() => void confirm()}>确认并设为当前资料</button></div>
    </>}
    {notice && <p role="status" className="notice">{notice}</p>}
    {error && <p role="alert" className="failure">{error}</p>}
  </section>;
}
