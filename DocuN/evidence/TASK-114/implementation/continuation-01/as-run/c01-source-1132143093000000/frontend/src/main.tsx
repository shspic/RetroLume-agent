import {dataFetch} from "./data/context";
import {setDataContext,useDataContext,ReadOnlyBusiness,type DataContext} from "./data/context";
import {DataWorkspace} from "./data/DataWorkspace";
import { StrictMode, useEffect, useRef, useState } from "react";
import { createRoot } from "react-dom/client";
import "./style.css";
import "./locations.css";
import { PdfReviewPanel, type PdfMaterial } from "./pdf/PdfReviewPanel";
import { ActivityWorkspace } from "./activities/ActivityWorkspace";

type Material = {id: string; title: string; version_id: string; revision: number; size: number; format: string; created_at: string};
type Result = {name: string; state: "等待" | "上传中" | "已保存" | "待核对" | "失败"; message?: string};
type Session = {token: string; storage_configured: boolean; max_bytes: number; data_context?:DataContext|null};
type Locations = {line_ending: string; trailing_newline: boolean; total_lines: number; total_paragraphs: number; paragraphs: {paragraph: number; start_line: number; end_line: number}[]; paragraphs_truncated: boolean};
type Excerpt = {start_line: number; end_line: number; text: string};
type ViewIdentity = {generation: number; sourceId: string; versionId: string};
type PdfContentPage = {version_id: string; physical_page: number; raw_text: string; identity: "pdf_extracted_text"; supplements: {id: string; version_id: string; physical_page: number; text: string; identity: "user_supplement"}[]};

function App() {
  const dataContext=useDataContext();
  const [session, setSession] = useState<Session | null>(null);
  const [items, setItems] = useState<Material[]>([]);
  const [selected, setSelected] = useState<Material | null>(null);
  const [text, setText] = useState("");
  const [pdfPages, setPdfPages] = useState<PdfContentPage[]>([]);
  const [loaded, setLoaded] = useState<Material | null>(null);
  const [locations, setLocations] = useState<Locations | null>(null);
  const [excerpt, setExcerpt] = useState<Excerpt | null>(null);
  const [startLine, setStartLine] = useState("");
  const [endLine, setEndLine] = useState("");
  const [error, setError] = useState("");
  const [viewError, setViewError] = useState("");
  const [results, setResults] = useState<Result[]>([]);
  const [busy, setBusy] = useState(false);
  const [loading, setLoading] = useState(false);
  const [nextOffset, setNextOffset] = useState<number | null>(null);
  const [candidateReload, setCandidateReload] = useState(0);
  const [view, setView] = useState<"materials" | "activities" | "interview" | "data">("materials");
  const picker = useRef<HTMLInputElement>(null);
  const replacement = useRef<HTMLInputElement>(null);
  const excerptRequest = useRef<AbortController | null>(null);
  const activeView = useRef<ViewIdentity | null>(null);
  const viewGeneration = useRef(0);
  const readerMaterial = selected && loaded && selected.id === loaded.id && selected.version_id === loaded.version_id ? loaded : null;

  function isActiveView(identity: ViewIdentity) {
    const current = activeView.current;
    return current?.generation === identity.generation && current.sourceId === identity.sourceId && current.versionId === identity.versionId;
  }

  function activateMaterial(material: Material) {
    excerptRequest.current?.abort();
    excerptRequest.current = null;
    const identity = {generation: ++viewGeneration.current, sourceId: material.id, versionId: material.version_id};
    activeView.current = identity;
    setSelected({...material}); setText(""); setPdfPages([]); setLoaded(null); setLocations(null); setExcerpt(null); setStartLine(""); setEndLine(""); setViewError("");
  }

  async function api(path: string, init: RequestInit = {}, token = session?.token) {
    let response: Response;
    try {response = await dataFetch(path, {...init, headers: {...init.headers, "X-RetroLume-Session": token ?? ""}});}
    catch (reason) {if (reason instanceof DOMException && reason.name === "AbortError") throw reason; throw new Error("连接中断，保存结果可能未知；请刷新列表确认，不会自动重传。");}
    const data = await response.json();
    if (!response.ok) throw new Error(typeof data.detail === "string" ? data.detail : "请求未完成，请检查输入后重试");
    return data;
  }
  async function refresh(token = session?.token, offset = 0) {
    const data = await api(`/api/materials?offset=${offset}`, {}, token);
    setItems(previous => offset === 0 ? data.items : [...previous, ...data.items]);
    setNextOffset(data.next_offset);
  }
  useEffect(() => {
    let active = true;
    fetch("/api/session").then(response => {if (!response.ok) throw new Error("无法连接本地服务"); return response.json();})
      .then(async data => {if (!active) return; setDataContext(data.data_context??null); setSession(data); if (data.storage_configured) await refresh(data.token);})
      .catch(reason => {if (active) setError(reason.message);});
    return () => {active = false;};
  }, []);
  useEffect(() => {
    if (!selected || !session) return;
    const controller = new AbortController();
    excerptRequest.current?.abort();
    excerptRequest.current = null;
    const identity = {generation: ++viewGeneration.current, sourceId: selected.id, versionId: selected.version_id};
    activeView.current = identity;
    setText(""); setPdfPages([]); setLoaded(null); setLocations(null); setExcerpt(null); setStartLine(""); setEndLine(""); setViewError(""); setLoading(true);
    const query = new URLSearchParams({expected_version: identity.versionId});
    api(`/api/materials/${identity.sourceId}/content?${query}`, {signal: controller.signal})
      .then(data => {
        if (controller.signal.aborted || !isActiveView(identity) || data.material.id !== identity.sourceId || data.material.version_id !== identity.versionId) return;
        if (data.material.format === "pdf") setPdfPages(data.pages);
        else setText(data.text);
        // 正文和标注必须来自同一响应，不能沿用旧列表的版本号。
        setLoaded(data.material);
        setLocations(data.locations ?? null);
        setItems(previous => previous.map(item => item.id === data.material.id ? data.material : item));
      })
      .catch(reason => {if (!controller.signal.aborted && isActiveView(identity)) setViewError(reason.message);})
      .finally(() => {if (!controller.signal.aborted && isActiveView(identity)) setLoading(false);});
    return () => controller.abort();
  }, [selected, session?.token]);

  async function readExcerpt() {
    if (!readerMaterial) return;
    const start = Number(startLine), end = Number(endLine);
    if (!Number.isInteger(start) || !Number.isInteger(end)) {setViewError("请输入完整的起止行号"); return;}
    const identity = activeView.current;
    if (!identity || identity.sourceId !== readerMaterial.id || identity.versionId !== readerMaterial.version_id) return;
    excerptRequest.current?.abort();
    const controller = new AbortController();
    excerptRequest.current = controller;
    setViewError(""); setExcerpt(null);
    try {
      const query = new URLSearchParams({expected_version: identity.versionId, start_line: String(start), end_line: String(end)});
      const data = await api(`/api/materials/${identity.sourceId}/content?${query}`, {signal: controller.signal});
      if (controller.signal.aborted || !isActiveView(identity) || data.material.id !== identity.sourceId || data.material.version_id !== identity.versionId) return;
      setExcerpt(data.excerpt);
      setLoaded(data.material); setLocations(data.locations);
    } catch (reason) {if (!controller.signal.aborted && isActiveView(identity)) setViewError(reason instanceof Error ? reason.message : "无法读取摘录");}
  }

  async function upload(files: FileList | null, target: Material | null = null) {
    if (!files?.length || !session || busy) return;
    const batch = Array.from(files);
    if (batch.length > 10) {setError("每批最多选择10个文件，请分批导入。"); return;}
    setError(""); setBusy(true);
    setResults(batch.map(file => ({name: file.name, state: "等待"})));
    for (let index = 0; index < batch.length; index++) {
      const file = batch[index];
      const update = (state: Result["state"], message?: string) => setResults(previous => previous.map((row, i) => i === index ? {...row, state, message} : row));
      update("上传中");
      try {
        if (file.size > session.max_bytes) throw new Error("单个文件不能超过5 MiB");
        if (!/\.(txt|md|markdown|pdf)$/i.test(file.name)) throw new Error("请选择TXT、Markdown或PDF文件");
        const query = new URLSearchParams({filename: file.name});
        if (target) {query.set("source_id", target.id); query.set("expected_version", target.version_id); query.set("expected_revision", String(target.revision));}
        const data = await api(`/api/materials?${query}`, {method: "POST", headers: {"Content-Type": "application/octet-stream"}, body: file});
        if (data.candidate) {update("待核对", "请在待核对PDF区逐页对照；此前可用版本保持不变。"); setCandidateReload(value => value + 1);}
        else {update("已保存"); if (target) activateMaterial(data.material);}
      } catch (reason) {update("失败", reason instanceof Error ? reason.message : "网络中断：结果未知，请刷新列表确认；不会自动重传");}
    }
    try {await refresh();} catch (reason) {setError(reason instanceof Error ? reason.message : "列表刷新失败");}
    setBusy(false);
  }

  return <div className="workspace">
    <aside className="rail"><div className="wordmark">R<span>RetroLume</span></div><p className="rail-caption">溯光教育 · 本地工作台</p><nav><div className={view === "materials" ? "nav-active" : "nav-muted"} role="button" tabIndex={0} style={{cursor: "pointer"}} onClick={() => setView("materials")}>▤ <span>我的资料</span></div><div className={view === "activities" ? "nav-active" : "nav-muted"} role="button" tabIndex={0} style={{cursor: "pointer"}} onClick={() => setView("activities")}>▦ <span>学习活动</span></div><div className={view === "interview" ? "nav-active" : "nav-muted"} role="button" tabIndex={0} style={{cursor: "pointer"}} onClick={() => setView("interview")}>模拟面试</div></nav><div className="local-note"><span className="status-dot"/> 个人本地空间<br/><small>资料是学习的起点</small></div></aside>
    <main className="main"><button className="secondary" onClick={()=>setView('data')}>数据与备份</button>{view === 'data' ? <DataWorkspace token={session?.token??''} onSelection={async()=>{window.location.reload();}}/> : <ReadOnlyBusiness key={dataContext?.instance_id??'legacy'}>{view !== "materials" ? <ActivityWorkspace key={view} token={session?.token ?? ""} variant={view === "interview" ? "interview" : "learning"}/> : (<>
      <header><div><p className="eyebrow">YOUR KNOWLEDGE, IN CONTEXT</p><h1>我的资料</h1><p className="subtitle">保存原始内容，为接下来的学习保留依据。</p></div><button className="primary" disabled={busy || !session?.storage_configured} onClick={() => picker.current?.click()}>＋ 导入资料</button></header>
      <input ref={picker} hidden aria-label="选择资料" type="file" multiple accept=".txt,.md,.markdown,.pdf,application/pdf" onChange={event => {void upload(event.target.files); event.target.value = "";}}/>
      <input ref={replacement} hidden aria-label="选择替换文件" type="file" accept=".txt,.md,.markdown,.pdf,application/pdf" onChange={event => {void upload(event.target.files, readerMaterial); event.target.value = "";}}/>
      {!session && !error && <p role="status">正在连接本地服务…</p>}
      {session && !session.storage_configured && <div className="notice" role="status"><strong>本地资料库尚未连接</strong><p>页面和上传流程已接入服务。PostgreSQL初始化完成后即可保存资料；当前不会临时存到其他数据库。</p></div>}
      {error && <div className="error" role="alert">{error}<button onClick={() => {setError(""); void refresh().catch(reason => setError(reason.message));}}>刷新列表</button></div>}
      <div className="upload-card"><div className="file-symbol">Aa</div><div><h2>从一份熟悉的资料开始</h2><p>支持UTF-8编码的TXT、Markdown和可提取文字的PDF。每个文件最多5 MiB，每批最多10个。</p><p className="quiet">PDF必须逐页对照原页确认后才可用。坏文件单独显示原因，其他文件继续导入；更新已有资料请使用“替换文件”。</p></div></div>
      {results.length > 0 && <section className="batch" aria-label="本批导入结果" aria-live="polite"><h2>{busy ? "正在导入" : "本批导入结果"}</h2>{results.map((row, i) => <div className="batch-row" key={i}><span>{row.name}</span><span className={row.state === "失败" ? "failure" : ""}>{row.state}</span>{row.message && <small>{row.message}</small>}</div>)}</section>}
      {session?.storage_configured && <PdfReviewPanel token={session.token} reloadKey={candidateReload} onActivated={(material: PdfMaterial) => {void refresh().then(() => activateMaterial(material)).catch(reason => setError(reason.message));}}/>}
      <div className="content-grid"><section className="library"><div className="section-title"><h2>已保存资料</h2><span>{items.length} 份{nextOffset !== null ? " +" : ""}</span></div>
        {!items.length ? <div className="empty"><div>▤</div><h3>还没有资料</h3><p>导入后，原文与版本会显示在这里。</p></div> : <ul>{items.map(item => <li key={item.id}><button className={`material ${selected?.id === item.id ? "selected" : ""}`} onClick={() => activateMaterial(item)}><span className="format">{item.format.toUpperCase()}</span><span className="material-name"><strong>{item.title}</strong><small>{(item.size / 1024).toFixed(1)} KB · 版本 {item.revision}</small></span><span aria-hidden="true">↗</span></button></li>)}</ul>}
        {nextOffset !== null && <button onClick={() => void refresh(session?.token, nextOffset).catch(reason => setError(reason.message))}>加载更多</button>}
      </section><section className="reader"><div className="section-title"><h2>{selected ? "原文" : "原文预览"}</h2>{selected && <button className="secondary" disabled={busy || loading || !readerMaterial} onClick={() => replacement.current?.click()}>替换文件</button>}</div>
        {selected ? <><h3 className="reader-title">{(readerMaterial ?? selected).title}</h3><p className="quiet">版本 {(readerMaterial ?? selected).revision} · 只读原文</p>{loading ? <p role="status">正在读取…</p> : readerMaterial?.format === "pdf" ? <div className="pdf-active-pages"><p className="quiet">已逐页确认，可供后续查询。PDF片段只按版本与物理页定位；用户补充保持独立身份。</p>{viewError && <p role="alert" className="failure">{viewError}</p>}{pdfPages.map(page => <article key={page.physical_page}><h4>物理页 {page.physical_page}</h4><pre>{page.raw_text}</pre>{page.supplements.map(item => <div className="notice" key={item.id}><strong>用户补充</strong><p>{item.text}</p></div>)}</article>)}</div> : <><div className="location-panel"><p>共 {locations?.total_lines ?? "—"} 行，{locations?.total_paragraphs ?? "—"} 段 · 换行 {locations?.line_ending ?? "—"}</p><p className="quiet">行号从 1 开始；末尾换行会形成一个可定位的空末行。仅显示前 12 段位置，不逐行生成内容。</p><ol className="location-list">{locations?.paragraphs.slice(0, 12).map(item => <li key={item.paragraph}>第 {item.paragraph} 段：{item.start_line}–{item.end_line} 行</li>)}</ol><div className="line-picker"><label>起始行<input value={startLine} inputMode="numeric" onChange={event => setStartLine(event.target.value)} /></label><label>结束行<input value={endLine} inputMode="numeric" onChange={event => setEndLine(event.target.value)} /></label><button className="secondary" onClick={() => void readExcerpt()} disabled={!readerMaterial}>查看摘录</button></div>{excerpt && <pre className="excerpt" aria-label="按原文行号摘录">{excerpt.text}</pre>}</div>{viewError && <p role="alert" className="failure">{viewError}</p>}<pre>{text}</pre></>}</> : <div className="empty"><h3>选择一份资料</h3><p>在左侧打开文件，回看它的原始内容。</p></div>}
      </section></div>
      <footer>原文以纯文本显示，不执行文件中的脚本或HTML。学习与面试功能将在后续接入。</footer>
      </>)}</ReadOnlyBusiness>}
    </main>
  </div>;
}
createRoot(document.getElementById("root")!).render(<StrictMode><App/></StrictMode>);
