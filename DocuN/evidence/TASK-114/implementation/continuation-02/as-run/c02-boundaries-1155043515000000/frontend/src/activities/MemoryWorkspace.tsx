import { useEffect, useRef, useState } from "react";
import { getMemory, getMemoryImpact, getMemoryReceipt, listMemories, memoryRequest,
  type MemoryChoice, type MemoryCommand, type MemoryImpact, type MemoryItem, type MemoryView } from "./memoryApi";
import { loadMemoryIntents, memoryEditorOwner, readMemoryDraft, removeMemoryIntent, removeMemoryDraft,
  saveMemoryDraft, removeMemoryDraftIfCurrent, submitTrackedMemory, submitTrackedMemoryCreate, type MemoryIntent } from "./memoryIntents";
import "./memory-workspace.css";

const kinds: Record<string, string> = { self_report: "用户自报", preference: "学习偏好", focus: "待练难点", learning_observation: "当时有限观察" };
const states: Record<string, string> = { current: "可明确选用", superseded: "旧版本，只读", revoked: "已撤销", memory_dependency_invalid: "依据已失效" };

export function MemoryWorkspace({ token, choices = [], onChoicesChange }: {
  token: string; choices?: MemoryChoice[]; onChoicesChange?: (value: MemoryChoice[]) => void;
}) {
  const [items, setItems] = useState<MemoryItem[]>([]);
  const [next, setNext] = useState<string | null>(null);
  const [caps, setCaps] = useState<{ read: boolean; write: boolean; cleanup: boolean } | null>(null);
  const [view, setView] = useState<MemoryView | null>(null);
  const [title, setTitle] = useState("");
  const [text, setText] = useState("");
  const [kind, setKind] = useState("self_report");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [impact, setImpact] = useState<MemoryImpact | null>(null);
  const [impactAction, setImpactAction] = useState<"revise" | "revoke" | null>(null);
  const [conflict, setConflict] = useState(false);
  const [reading,setReading]=useState(false);
  const [pendingView,setPendingView]=useState<MemoryView|null>(null);
  const [ownerReady,setOwnerReady]=useState(false);
  const [readUnconfirmed,setReadUnconfirmed]=useState(false);
  const [intents, setIntents] = useState<MemoryIntent[]>([]);
  const [intentsOk, setIntentsOk] = useState(true);
  const owner = useRef<string | null>(null);
  const binding = useRef<{ id: string; version: number; revision: number; sha: string } | null>(null);
  const readSequence = useRef(0);
  const editSequence = useRef(0);
  const dirty = useRef(false);
  const mounted = useRef(true);
  const lifecycle = useRef(0);
  const newId = useRef<string>(crypto.randomUUID());
  const controller = useRef<AbortController | null>(null);
  const draftKey = () => binding.current && owner.current ? ["edit", binding.current.id, binding.current.version,
    binding.current.revision, binding.current.sha, owner.current].join("|") : null;
  const reloadIntents = () => { const value = loadMemoryIntents(); setIntents(value.items); setIntentsOk(value.ok); };
  async function refresh(authorized: () => boolean = () => true) {
    const generation = lifecycle.current;
    const current = () => mounted.current && generation === lifecycle.current && authorized();
    try {
      const result = await listMemories(token);
      if (current()) { setItems(result.items); setNext(result.next_cursor); reloadIntents(); }
    } catch (reason) { if (current()) setError(reason instanceof Error ? reason.message : "记忆读取未确认"); }
  }
  useEffect(() => {
    mounted.current = true;
    const generation = ++lifecycle.current;
    const currentInstance = () => mounted.current && generation === lifecycle.current;
    setBusy(false);
    void memoryEditorOwner().then(async value => {
      if (!currentInstance()) return;
      owner.current=value;
      setOwnerReady(Boolean(value));
      if(!value||!mounted.current||binding.current)return;
      const key="retrolume.memory-new-id.v1:"+value;
      let id=sessionStorage.getItem(key);
      if(!id){id=crypto.randomUUID();sessionStorage.setItem(key,id);}
      newId.current=id;binding.current={id,version:0,revision:0,sha:""};
      const edited=editSequence.current,sequence=readSequence.current;const draft=await readMemoryDraft(["edit",id,0,0,"",value].join("|"));
      if(draft&&currentInstance()&&sequence===readSequence.current&&binding.current?.id===id&&edited===editSequence.current&&!view) {
        const content=JSON.parse(draft.content);setTitle(content.title);setText(content.text);setKind(content.kind);dirty.current=true;
      }
    });
    void memoryRequest<{ read: boolean; write: boolean; cleanup: boolean }>("/api/memories/capabilities", token).then(value => { if (currentInstance()) setCaps(value); }).catch(() => { if (currentInstance()) setCaps(null); });
    void refresh();
    const storage = (event: StorageEvent) => { if (event.key === "retrolume.memory-intents.v1") reloadIntents(); };
    window.addEventListener("storage", storage);
    return () => { mounted.current = false; ++lifecycle.current; ++readSequence.current; controller.current?.abort(); window.removeEventListener("storage", storage); };
  }, [token]);

  async function select(id: string, explicit = false, keep = false) {
    const sequence = ++readSequence.current; controller.current?.abort();
    if (id !== binding.current?.id) setNotice("");
    const active = new AbortController(); controller.current = active;
    const editedAt = editSequence.current;
    setReading(true);setImpact(null);setImpactAction(null);setError("");setReadUnconfirmed(false);
    try {
      const row = await getMemory(id, token, active.signal);
      if (!mounted.current || sequence !== readSequence.current) return;
      const key=owner.current?["edit",row.memory_id,row.version,row.revision,row.body_sha256,owner.current].join("|"):null;
      const draft=key?await readMemoryDraft(key):null;
      if (sequence !== readSequence.current || !mounted.current) return;
      if(!row.body&&!explicit&&binding.current?.id!==row.memory_id&&(dirty.current||editedAt!==editSequence.current)){
        setPendingView(row);setConflict(true);return;
      }
      if(!row.body){
        binding.current={id:row.memory_id,version:row.version,revision:row.revision,sha:row.body_sha256};
        setView(row);setTitle("");setText("");setPendingView(null);setConflict(false);dirty.current=false;return;
      }
      if(editedAt!==editSequence.current||(!explicit&&dirty.current&&binding.current&&
        (binding.current.id!==row.memory_id||binding.current.revision!==row.revision||binding.current.sha!==row.body_sha256))){
        setPendingView(row);setConflict(true);return;
      }
      binding.current = { id: row.memory_id, version: row.version, revision: row.revision, sha: row.body_sha256 };
      setView(row);setPendingView(null);
      if (!keep) {
        const content = draft ? JSON.parse(draft.content) as { title: string; text: string; kind: string } : row.body;
        setTitle(content?.title ?? ""); setText(content?.text ?? ""); setKind(content?.kind ?? row.claim_kind);
        dirty.current = Boolean(draft);
      }else if(key&&owner.current){
        dirty.current=true;
        await saveMemoryDraft({id:key,memory_id:row.memory_id,owner:owner.current,version:row.version,revision:row.revision,
          body_sha:row.body_sha256,content:JSON.stringify({title,text,kind})});
      }
      setConflict(false);
    } catch (reason) { if (sequence === readSequence.current && mounted.current) {setReadUnconfirmed(true);setError(reason instanceof Error ? reason.message : "记忆未确认");} }
    finally{if(sequence===readSequence.current&&mounted.current)setReading(false);}
  }
  function persistEdit(nextTitle: string, nextText: string, nextKind: string) {
    dirty.current = true; ++editSequence.current;
    const key = draftKey(); const current = binding.current;
    if (key && current && owner.current) void saveMemoryDraft({ id: key, memory_id: current.id, owner: owner.current,
      version: current.version, revision: current.revision, body_sha: current.sha,
      content: JSON.stringify({ title: nextTitle, text: nextText, kind: nextKind }) });
  }
  function fresh() {
    ++readSequence.current; controller.current?.abort(); newId.current = crypto.randomUUID();
    if(owner.current)sessionStorage.setItem("retrolume.memory-new-id.v1:"+owner.current,newId.current);
    binding.current = { id: newId.current, version: 0, revision: 0, sha: "" };
    dirty.current = false; setView(null); setTitle(""); setText(""); setKind("self_report");
    setConflict(false);setPendingView(null);setReading(false);setReadUnconfirmed(false); setImpact(null); setImpactAction(null);setNotice("");setError("");
  }
  async function execute(command: MemoryCommand) {
    if (busy || !intentsOk || conflict) return;
    const submittedSequence=readSequence.current;
    const submittedEdit=editSequence.current,submittedDraft=draftKey();
    const submittedGeneration = lifecycle.current, submittedOwner = owner.current;
    const submittedBinding = binding.current ? { ...binding.current } : null;
    const sameInstance = () => mounted.current && lifecycle.current === submittedGeneration;
    const sameEditor = () => sameInstance() && owner.current === submittedOwner && readSequence.current === submittedSequence
      && binding.current?.id === submittedBinding?.id && binding.current?.version === submittedBinding?.version
      && binding.current?.revision === submittedBinding?.revision && binding.current?.sha === submittedBinding?.sha;
    const unchangedEditor = () => sameEditor() && editSequence.current === submittedEdit;
    const identity = command.memory_id; setBusy(true); setError(""); setNotice("");
    try {
      const receipt = await submitTrackedMemory(command, token);
      if (!sameInstance()) return;
      reloadIntents();
      if (receipt.status !== "committed") throw new Error("保存结果未确认，原意图保留");
      if (!sameEditor()) return;
      if(submittedEdit!==editSequence.current){
        setNotice("保存已确认，读取期间的新输入仍保留，请核对版本。");
        await refresh(sameEditor);
        if (sameEditor()) await select(identity);
        return;
      }
      if(submittedDraft)await removeMemoryDraftIfCurrent(submittedDraft, unchangedEditor);
      if (!sameEditor()) return;
      if (submittedEdit !== editSequence.current) {
        setNotice("保存已确认，读取期间的新输入仍保留，请核对版本。");
        await refresh(sameEditor);
        if (sameEditor()) await select(identity);
        return;
      }
      dirty.current = false;
      if(command.action==='save'&&newId.current===identity&&owner.current){
        newId.current=crypto.randomUUID();sessionStorage.setItem("retrolume.memory-new-id.v1:"+owner.current,newId.current);
      }
      setNotice(command.action === "revoke" ? (receipt.purge_state_now === "done" ? "已撤销，本条在线记忆正文已清理；原始事实和保留副本仍在。" : "已撤销，内容清理待核对；不会再用于生成。") : "已确认保存，未调用模型。");
      setImpact(null); setImpactAction(null);
      await refresh(unchangedEditor);
      if (unchangedEditor()) await select(identity, true);
    } catch (reason) {
      if (sameEditor()) { setError(reason instanceof Error ? reason.message : "动作未确认"); reloadIntents(); }
    } finally { if (sameInstance()) setBusy(false); }
  }
  async function preview(action: "revise" | "revoke") {
    if (!view || busy || conflict || reading || readUnconfirmed) return;
    setError("");
    const sequence=readSequence.current;
    try {
      const result=await getMemoryImpact(view.memory_id, binding.current?.revision ?? view.revision, action, token);
      if(mounted.current&&sequence===readSequence.current){setImpact(result);setImpactAction(action);}
    }
    catch (reason) { setError(reason instanceof Error ? reason.message : "变动影响未确认"); }
  }
  function save() {
    const current = binding.current ?? { id: newId.current, revision: 0, sha: "", version: 0 };
    if(reading||conflict)return;
    if (view) { void preview("revise"); return; }
    void execute({ business_key: crypto.randomUUID(), memory_id: current.id, expected_revision: 0, action: "save", body: { kind, title, text } });
  }
  async function choose(item: MemoryItem) {
    if (!onChoicesChange || busy) return;
    if (choices.some(x => x.memory_id === item.memory_id)) { onChoicesChange(choices.filter(x => x.memory_id !== item.memory_id)); return; }
    if (choices.length >= 4) { setError("每次活动最多明确选择四条记忆"); return; }
    try {
      const row = await getMemory(item.memory_id, token);
      if (row.qualification !== "current") throw new Error("该记忆已变化，请刷新核对");
      onChoicesChange([...choices, { memory_id: row.memory_id, version: row.version, revision: row.revision, body_sha256: row.body_sha256 }]);
    } catch (reason) { setError(reason instanceof Error ? reason.message : "选用未确认"); }
  }
  async function reconcile(intent: MemoryIntent) {
    setError("");
    try {
      if(intent.action==='create_activity'){
        const row=await memoryRequest<{activity:{memory_selection?:{create_request_sha256:string}}}>("/api/activities/"+intent.memory_id,token);
        if(row.activity.memory_selection?.create_request_sha256!==intent.request_sha)throw new Error("创建意图与活动身份不一致");
        await removeMemoryIntent(intent.key);await removeMemoryDraft(intent.draft_id);reloadIntents();setNotice("已只读确认原活动选择");return;
      }
      const receipt = await getMemoryReceipt(intent.key, token);
      if (receipt.business_key !== intent.key || receipt.request_sha256 !== intent.request_sha || receipt.memory_id !== intent.memory_id)
        throw new Error("收据身份不一致，原意图保留");
      if (receipt.status === "committed") { await removeMemoryIntent(intent.key); await removeMemoryDraft(intent.draft_id); }
      reloadIntents(); setNotice("已只读核对，未重发动作"); await refresh();
    } catch (reason) { setError(reason instanceof Error ? reason.message : "只读核对未确认"); }
  }
  async function retry(intent: MemoryIntent) {
    if(busy)return;
    const draft=await readMemoryDraft(intent.draft_id);
    if(!draft){setError("原意图正文不可读，未发出请求");return;}
    if(intent.action!=="create_activity"){void execute(JSON.parse(draft.content) as MemoryCommand);return;}
    setBusy(true);setError("");
    try{
      const original=JSON.parse(draft.content) as {activity_id:string;source_ids:string[];memory_selection:{entries:MemoryChoice[]}};
      await submitTrackedMemoryCreate(original.activity_id,original.source_ids,original.memory_selection.entries,token);
      setNotice("已明确重试原活动选择");reloadIntents();
    }catch(reason){setError(reason instanceof Error?reason.message:"创建未确认");reloadIntents();}
    finally{setBusy(false);}
  }
  return <section className="memory-workspace" aria-label="学习记忆工作区">
    <div className="memory-heading"><h2>学习记忆</h2><button className="secondary" onClick={() => { void refresh(); if (view) void select(view.memory_id); }}>刷新记忆</button></div>
    <p className="quiet">显式保存的背景与活动历史分别保留。自报和有限观察可辨；旧作答不算新活动的独立表现。</p>
    {!caps?.read && <p role="status">学习记忆暂不可用，请核对本地设置。</p>}
    {error && <p role="alert" className="error">{error}</p>}
    {notice && <p role="status" className="notice">{notice}</p>}
    <div className="memory-grid">
      <div className="memory-list">
        <button className="secondary" disabled={!caps?.write || busy} onClick={fresh}>新建用户记忆</button>
        {items.map(item => <div className="memory-item" key={item.memory_id}>
          {onChoicesChange && <input aria-label={"选用记忆 " + (item.title ?? "不可用记忆")} type="checkbox"
            checked={choices.some(c => c.memory_id === item.memory_id)} disabled={item.qualification !== "current" || busy} onChange={() => void choose(item)} />}
          <button className="memory-open" onClick={() => void select(item.memory_id)}>{item.title ?? "不可用记忆"}</button>
          <small>{kinds[item.claim_kind]} · 版本 {item.version} · {states[item.qualification] ?? "待核对"}</small>
        </div>)}
        {next && <button className="secondary" onClick={() => void listMemories(token, next).then(page => { setItems(old => [...old, ...page.items]); setNext(page.next_cursor); }).catch(reason => setError(reason.message))}>读取更早记忆</button>}
        {onChoicesChange && <p>新活动已明确选择 {choices.length} 条，版本固定，不自动切换新版。</p>}
      </div>
      <div className="memory-detail" aria-busy={reading} data-memory-id={binding.current?.id??""}
        data-memory-revision={binding.current?.revision??0} data-memory-version={binding.current?.version??0}
        data-memory-sha={binding.current?.sha??""} data-editor-owner={owner.current??""}>
        {reading&&<p role="status">正在核对记忆与本机草稿，当前输入仍保留。</p>}
        {view && <p>{kinds[view.claim_kind]} · 版本 {view.version} · {view.uncertainty === "limited" ? "有限观察，长期能力未知" : "用户陈述，尚未验证"}
          · {states[view.qualification] ?? "依据不可用"}</p>}
        {conflict && <div role="alert"><p>记忆身份已有变化，原草稿未改绑。请核对后明确选择。</p>
          {pendingView && <><p>待核对版本 {pendingView.version} · {pendingView.body?.title??"不可用记忆"}</p>
          <button disabled={reading} onClick={() => void select(pendingView.memory_id, true)}>明确载入新版</button>
          <button disabled={reading} onClick={() => void select(pendingView.memory_id, true, true)}>明确沿用草稿至新版</button></>}</div>}
        {(!view || view.body) && <>
          <label>记忆标题<input aria-label="记忆标题" value={title} maxLength={80} onChange={e => { setTitle(e.target.value); persistEdit(e.target.value, text, kind); }} /></label>
          <label>记忆性质<select value={kind} disabled={view?.claim_kind === "learning_observation"} onChange={e => { setKind(e.target.value); persistEdit(title, text, e.target.value); }}>
            <option value="self_report">用户自报</option><option value="preference">学习偏好</option><option value="focus">待练难点</option>
            {kind === "learning_observation" && <option value="learning_observation">当时有限观察</option>}
          </select></label>
          <label>用户正文或注记<textarea aria-label="用户正文或注记" value={text} maxLength={1024} onChange={e => { setText(e.target.value); persistEdit(title, e.target.value, kind); }} /></label>
          {view?.body?.observation && <div><p>受检层保留原始事件，用户注记不会覆盖它。</p><pre>{JSON.stringify(view.body.observation, null, 2)}</pre></div>}
          {view?.dependencies && <details><summary>来源与事件身份</summary>{view.dependencies.map((d, i) =>
            <p key={i}>{d.dependency_kind === "source" ? "资料版本 " + d.source_version_id :
              d.dependency_kind === "event" ? "活动 " + d.origin_activity_id + " · 事件 " + d.record_id : "上游记忆 " + d.upstream_memory_id}</p>)}</details>}
          <button className="primary" disabled={!caps?.write || busy || reading || readUnconfirmed || conflict || !ownerReady || !title.trim() || (kind !== "learning_observation" && !text.trim())} onClick={save}>{view ? "预览记忆修正影响" : "保存用户记忆"}</button>
        </>}
        {view?.state === "active" && <button className="secondary" disabled={busy || reading || readUnconfirmed || conflict || !caps?.write} onClick={() => void preview("revoke")}>预览撤销并清理</button>}
        {view?.state === "revoked" && <p>已撤销，旧选择及依赖背景不可再使用。{view.purge_state === "done" ? "本条在线正文已清理。" : "内容清理待核对。"}</p>}
        {view?.state === "revoked" && view.purge_state !== "done" && <button disabled={busy || reading || readUnconfirmed || !caps?.cleanup} onClick={() => {
          if (!view.revocation_key) return;
          void getMemoryReceipt(view.revocation_key, token).then(receipt => execute({ business_key: crypto.randomUUID(),
            memory_id: view.memory_id, expected_revision: view.revision, action: "purge", body: { revocation_key: view.revocation_key,
              manifest_sha256: receipt.manifest_sha256, confirm_memory_cleanup: true } })).catch(reason => setError(reason.message));
        }}>明确重试原清单清理</button>}
      </div>
    </div>
    {impact && impactAction && view && <div className="memory-impact" role="dialog" aria-label="记忆变动确认">
      <p>本条共 {impact.version_count} 个版本，影响 {impact.activity_count} 个活动和 {impact.dependent_memory_count} 条派生记忆。</p>
      <p>{impact.effect} 所有既有选择不会自动换新版。清理只处理本条全部在线记忆正文，不删原始作答、资料、活动历史或备份。</p>
      <button className="primary" disabled={busy || reading || readUnconfirmed || conflict} onClick={() => void execute({ business_key: crypto.randomUUID(),
        memory_id: view.memory_id, expected_revision: binding.current?.revision ?? view.revision, action: impactAction,
        body: impactAction === "revise" ? { kind, title, text, base_body_sha256: binding.current?.sha,
          impact_token: impact.impact_token } : { impact_token: impact.impact_token, confirm_revoke: true, purge_memory_content: true } })}>
        {impactAction === "revoke" ? "确认撤销并清理本条记忆" : "确认追加修订版本"}</button>
      <button className="secondary" onClick={() => { setImpact(null); setImpactAction(null); }}>保留，不执行</button>
    </div>}
    {!!intents.length && <div aria-label="记忆未确认动作"><h3>未确认的记忆动作</h3>
      <p>刷新只读核对，原键和本机正文保留。</p>{intents.map(intent => <div key={intent.key}>
        <span>{intent.action} · {intent.state}</span><button className="secondary" onClick={() => void reconcile(intent)}>只读核对记忆动作</button>
        <button className="secondary" disabled={busy} onClick={() => void retry(intent)}>明确同键重试原记忆意图</button>
      </div>)}</div>}
  </section>;
}

