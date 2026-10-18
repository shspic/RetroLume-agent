// 教学工作区：目标/诊断 → 路径接受 → 练习 → 零费保存答 → 有据反馈 →
// 续答/复测 → 更新理由 → 重开。完整待发正文先入原生 IndexedDB、
// 摘要台账再入 localStorage，成功后才 POST；失败保留输入且零 POST。

import { useCallback, useEffect, useRef, useState } from "react";
import { TeachingExercise } from "./TeachingExercise";
import { TeachingFeedback, type FeedbackView } from "./TeachingFeedback";
import {
  getTeachingCommand, getTeachingWorkspace, getTeachingRecord, postTeachingCommand,
  getTeachingHistory, type TeachingHistoryItem, type TeachingSeed,
  TeachingApiError, type TeachingAction, type TeachingCommandInput, type TeachingReceipt,
  type TeachingRegion, type TeachingWorkspace,
} from "./teachingApi";
import { buildTeachingCommand, newTeachingKey } from "./teachingDrafts";
import {
  appendTeachingIntent, loadTeachingIntents, removeTeachingIntent, saveTeachingDraft,
  updateTeachingIntent, readTeachingDraft, removeTeachingDraft, type TeachingIntentSummary,
  teachingEditorOwner,
} from "./teachingIntents";
import { compareTeachingIntent } from "./teachingIntentMatch";
import { TeachingCitations, citationIds } from "./TeachingCitations";

const POLL_MS = 3000;
const OBSERVE_MAX_SECONDS = 120;
const OBSERVE_MAX_TRIES = 40;
const ANSWER_MAX = 4096;

const PHASE_TEXT: Record<string, string> = {
  needs_goal: "待保存目标",
  needs_plan: "待生成路径",
  path_review: "待确认路径",
  ready: "可获取练习",
  exercise_ready: "已有练习题",
  answer_saved: "已保存作答",
  feedback_ready: "已有反馈",
};

const ERROR_TEXT: Record<string, string> = {
  command_key_conflict: "该业务键已绑定不同内容；原意图保留，请用新键或只读核对",
  stage_conflict: "当前阶段不允许该动作，或同父槽已有不同内容",
  version_conflict: "教学修订版本已变化，请刷新工作区",
  goal_changed: "目标版本已变化，请刷新工作区",
  source_invalid: "资料已失效；用户文字仍可保存，但派生内容暂停",
  activity_cancelled: "活动已取消，历史可读",
  activity_expired: "活动已到期，历史可读",
  budget_exhausted: "活动有限额度已用尽；仍可零费保存目标、作答与纠错",
  unknown_slot: "该命令已不在可启动状态，请只读核对",
  launch_already_claimed: "该动作已被启动过，不能重复发起",
  teaching_not_configured: "教学层未配置（需显式 teaching 配置段）",
  teaching_config_incompatible: "教学输出配置超过活动或服务上限",
  tool_limit_unconfigured: "核算未启用：需要显式 finite_calculate 配置与工具额度",
  tool_limit_exhausted: "工具额度已用尽",
  input_too_large: "内容超过上限，输入已保留在本机",
  context_limit: "上下文超过限额，请缩小目标或活动范围",
  history_limit: "历史记录已达上限，请新建活动",
  integrity_error: "数据完整性检查失败，已停止推进",
  record_denied: "结果提交被拒绝（未确认）",
  record_unconfirmed: "结果提交未确认",
  unknown: "结果未知，可能已执行；不会自动重发",
};

function errorText(code: string | null | undefined): string {
  if (!code) return "";
  return ERROR_TEXT[code] ?? `内部错误（${code}）`;
}

function toFeedbackView(region: TeachingRegion): FeedbackView {
  const list = (value: unknown) => (Array.isArray(value) ? value : []);
  const excerpt = (item: Record<string, unknown>) => ({
    answer_excerpt: String(item.answer_excerpt ?? ""),
    explanation: String(item.explanation ?? ""),
    citations: Array.isArray(item.citations) ? item.citations.filter((id):id is string=>typeof id==='string') : [],
  });
  const take = (key: string) => list(region[key])
    .map(item => item as Record<string, unknown>).filter(item => "answer_excerpt" in item)
    .map(excerpt);
  return {
    correctParts: take("correct_parts"),
    errors: take("errors"),
    evidenceGaps: take("evidence_gaps"),
    causeHypotheses: list(region.cause_hypotheses).map(item => {
      const value = item as Record<string, unknown>;
      return {
        hypothesis: String(value.hypothesis ?? ""),
        evidence_for: String(value.evidence_for ?? ""),
        confidence: String(value.confidence ?? "unknown"),
      };
    }),
    observations: list(region.dimension_observations).map(item => {
      const value = item as Record<string, unknown>;
      return {
        id: String(value.id ?? ""),
        observation: String(value.observation ?? "unknown"),
        reason: String(value.reason ?? ""),
      };
    }),
    nextFocus: (() => {
      const value = region.next_focus as Record<string, unknown> | null | undefined;
      if (!value || typeof value !== "object") return null;
      return {
        focus_dimension: String(value.focus_dimension ?? ""),
        reason: String(value.reason ?? ""),
        suggested_mode: String(value.suggested_mode ?? "review"),
      };
    })(),
  };
}

export function TeachingWorkspace({
  activityId, token, scopeRevision, teachingAvailable, calculationAvailable,
  onCapabilitiesDirty, seed,
}: {
  activityId: string;
  token: string;
  scopeRevision: number;
  teachingAvailable: boolean;
  calculationAvailable: boolean;
  onCapabilitiesDirty?: () => void;
  seed?: TeachingSeed | null;
}) {
  const [workspace, setWorkspace] = useState<TeachingWorkspace | null>(null);
  const [feedback, setFeedback] = useState<FeedbackView | null>(null);
  const [goalText, setGoalText] = useState("");
  const [answerText, setAnswerText] = useState("");
  const [correctionText, setCorrectionText] = useState("");
  const [intents, setIntents] = useState<TeachingIntentSummary[]>([]);
  const [intentsOk, setIntentsOk] = useState(true);
  const [busy, setBusy] = useState("");
  const [notice, setNotice] = useState("");
  const [error, setError] = useState("");
  const [readError, setReadError] = useState("");
  const [historyDetail,setHistoryDetail] = useState<Record<string,unknown>|null>(null);
  const [correctionTarget,setCorrectionTarget] = useState<string|null>(null);
  const [olderHistory,setOlderHistory] = useState<TeachingHistoryItem[]>([]);
  const [historyNext,setHistoryNext] = useState<string|null>(null);
  const [historyLoading,setHistoryLoading] = useState(false);
  const [historyNotice,setHistoryNotice] = useState("");
  const [editConflict,setEditConflict] = useState(false);
  const [selectedSeed,setSelectedSeed] = useState<TeachingSeed|null>(null);
  const editing = useRef<{activity_id:string;head:TeachingWorkspace['head'];scope_revision:number;key:string;draft_key:string|null}|null>(null);
  const editorOwner = useRef<string|null>(null);
  const dirty = useRef({answer:false,goal:false,correction:false});
  const workspaceToken = useRef("");
  const historySeq = useRef(0);
  const historyAbort = useRef<AbortController|null>(null);
  const pageSeq = useRef(0);
  const pageAbort = useRef<AbortController|null>(null);
  const editSeq=useRef(0);
  const activityRef=useRef(activityId);
  activityRef.current=activityId;
  const scopeRef=useRef(scopeRevision);
  scopeRef.current=scopeRevision;

  const mounted = useRef(true);
  const inFlight = useRef(false);
  const readSeq = useRef(0);
  const contextKey = useRef("");
  const observe = useRef({ startedAt: 0, tries: 0 });
  const abort = useRef<AbortController | null>(null);
  const draftId = useRef<string | null>(null);

  useEffect(() => {
    mounted.current = true;
    return () => { mounted.current = false; abort.current?.abort(); ++historySeq.current; historyAbort.current?.abort();
      ++pageSeq.current; pageAbort.current?.abort(); };
  }, []);

  const reloadIntents = useCallback(() => {
    const current = loadTeachingIntents();
    setIntents(current.items.filter(item => item.activity_id === activityId));
    setIntentsOk(current.ok);
  }, [activityId]);

  const refresh = useCallback(async (quiet = false) => {
    if (!mounted.current) return;
    const seq = ++readSeq.current;
    abort.current?.abort();
    const controller = new AbortController();
    abort.current = controller;
    try {
      const view = await getTeachingWorkspace(activityId, token, controller.signal);
      if (!mounted.current || seq !== readSeq.current) return;
      if (view === null) { setReadError("教学读取不可用（未确认）"); return; }
      const key = [activityId, view.head.goal_record_id, view.head.path_record_id, view.head.node_id,
        view.head.exercise_record_id, view.head.answer_record_id].join("|");
      const editKey = `${key}|${view.head.revision}`;
      const owner=await teachingEditorOwner();
      if (!mounted.current||seq!==readSeq.current) return;
      editorOwner.current=owner;
      const ownDraftKey=owner ? `edit-${editKey}|${owner}` : null;
      if (view.view_token !== workspaceToken.current) {
        workspaceToken.current=view.view_token; ++pageSeq.current; pageAbort.current?.abort();
        setOlderHistory([]); setHistoryNext(view.next_cursor??null); setHistoryLoading(false);
      }
      if (key !== contextKey.current) {
        // 编辑身份独立于新快照；外部新答不把旧文字改绑为其supersedes。
        contextKey.current = key;
        setFeedback(null);
        ++historySeq.current; historyAbort.current?.abort();
        setHistoryDetail(null);
        setCorrectionTarget(null);
        draftId.current = null;
        const editAt=editSeq.current;
        if (editing.current && (dirty.current.answer||dirty.current.correction)) {
          setEditConflict(true);
        } else {
          editing.current={activity_id:activityId,head:{...view.head},scope_revision:scopeRef.current,key:editKey,draft_key:ownDraftKey};
          setEditConflict(false);
          const draft=ownDraftKey ? await readTeachingDraft(ownDraftKey) : null;
          if (!mounted.current||seq!==readSeq.current) return;
          if (editAt===editSeq.current) {
            setAnswerText(draft?.content??String(view.answer?.text??""));
            dirty.current.answer=Boolean(draft);
            if (!dirty.current.goal) setGoalText(String(view.goal?.goal??""));
            if (!dirty.current.correction) setCorrectionText("");
          }
        }
      } else if (editing.current?.head.revision !== view.head.revision) {
        if (dirty.current.answer||dirty.current.correction) setEditConflict(true);
        else editing.current={activity_id:activityId,head:{...view.head},scope_revision:scopeRef.current,key:editKey,draft_key:ownDraftKey};
      }
      setWorkspace(view);
      setReadError("");
      if (!view.overlay.processing && !view.overlay.unknown) {
        observe.current = { startedAt: 0, tries: 0 };
      }
      // 反馈正文直接消费同一 workspace 快照的 feedback 区域（DEF-005：
      // 单语句一致读取；坏单项/来源失效时该区域已带资格标记）。
      const feedbackRegion = view.feedback;
      if (feedbackRegion && feedbackRegion.qualification === "current") {
        setFeedback(toFeedbackView(feedbackRegion));
      } else {
        setFeedback(null);
      }
    } catch (reason) {
      if (!mounted.current || seq !== readSeq.current) return;
      if (reason instanceof TeachingApiError && reason.status === 0) {
        setReadError("读取未确认（连接中断）；只读核对，不自动重发");
        return;
      }
      if (!quiet) setReadError(reason instanceof Error ? reason.message : "教学读取失败");
    }
  }, [activityId, token]);

  useEffect(() => {
    ++readSeq.current; ++historySeq.current; historyAbort.current?.abort(); ++pageSeq.current; pageAbort.current?.abort();
    contextKey.current=""; workspaceToken.current=""; setWorkspace(null); setBusy("");
    editing.current=null; dirty.current={answer:false,goal:false,correction:false}; setEditConflict(false);
    setOlderHistory([]); setHistoryDetail(null); setCorrectionTarget(null); setHistoryNotice("");
    reloadIntents(); void refresh();
    return ()=>{ ++readSeq.current; abort.current?.abort(); ++historySeq.current; historyAbort.current?.abort(); ++pageSeq.current; pageAbort.current?.abort(); };
  }, [reloadIntents, refresh]);
  useEffect(()=>{
    if (seed?.activity_id===activityId) { setSelectedSeed(seed); setGoalText(seed.goal); dirty.current.goal=true; }
    else setSelectedSeed(null);
  },[seed,activityId]);
  useEffect(()=>{
    const onStorage=()=>reloadIntents();
    window.addEventListener("storage",onStorage);
    return ()=>window.removeEventListener("storage",onStorage);
  },[reloadIntents]);

  // 单 workspace 轮询：3 秒节拍、不重叠、hidden 暂停、卸载清理、
  // 未知观察 120 秒/40 次后停止。
  useEffect(() => {
    if (!workspace) return;
    let timer: number | null = null;
    const poll = async () => {
      if (inFlight.current || document.hidden) return;
      const state = observe.current;
      if (state.tries >= OBSERVE_MAX_TRIES
          || (state.startedAt > 0 && (Date.now() - state.startedAt) / 1000 > OBSERVE_MAX_SECONDS)) {
        stop();
        setNotice("已停止自动观察；可手动刷新只读核对，不会自动重发或占用执行单元。");
        return;
      }
      if (state.startedAt === 0) state.startedAt = Date.now();
      state.tries += 1;
      inFlight.current = true;
      try { await refresh(true); } finally { inFlight.current = false; }
    };
    const start = () => { if (timer === null) timer = window.setInterval(() => { void poll(); }, POLL_MS); };
    const stop = () => { if (timer !== null) { window.clearInterval(timer); timer = null; } };
    const onVisibility = () => {
      if (document.hidden) stop();
      else { start(); void poll(); }
    };
    if (workspace.overlay.processing || workspace.overlay.unknown) {
      start();
      document.addEventListener("visibilitychange", onVisibility);
    }
    return () => { stop(); document.removeEventListener("visibilitychange", onVisibility); };
  }, [workspace, refresh]);

  async function submit(action: TeachingAction, body: Record<string, unknown>,
                         extra?: Partial<TeachingIntentSummary>) {
    if (busy || !intentsOk) return;
    if ((action==='answer'||action==='correct') && editConflict) { setError("输入仍属于旧作答身份；请先核对并明确沿用草稿"); return; }
    const submittedContext=contextKey.current;
    const stillCurrent=()=>mounted.current&&activityRef.current===activityId&&contextKey.current===submittedContext;
    setBusy(action); setError(""); setNotice("");
    const key = newTeachingKey();
    const input: Omit<TeachingCommandInput, "body"> = {
      business_key: key,
      expected_revision: workspace?.head.revision ?? 0,
      expected_goal_version: workspace?.head.goal_version ?? 0,
      expected_scope_revision: scopeRevision,
      action,
    };
    if (action==='answer' && editing.current) {
      input.expected_revision=editing.current.head.revision;
      input.expected_goal_version=editing.current.head.goal_version;
      input.expected_scope_revision=editing.current.scope_revision;
    }
    try {
      const built = await buildTeachingCommand(activityId, { ...input, body });
      // 顺序：规范字节 → IndexedDB 完整正文 → localStorage 摘要 → POST 一次。
      const stored = await saveTeachingDraft({
        draft_id: `draft-${key}`,
        activity_id: activityId,
        goal_record_id: workspace?.head.goal_record_id ?? null,
        exercise_record_id: workspace?.head.exercise_record_id ?? null,
        answer_record_id: workspace?.head.answer_record_id ?? null,
        path_record_id: workspace?.head.path_record_id ?? null,
        node_id: workspace?.head.node_id ?? null,
        head_revision: input.expected_revision,
        content: built.request_body,
        created_at: new Date().toISOString(),
      });
      if (!stored) { setError("本机草稿写入失败，输入已保留，未发出任何请求"); return; }
      draftId.current = `draft-${key}`;
      const summary: TeachingIntentSummary = {
        key, action, activity_id: activityId,
        head_revision: input.expected_revision, goal_version: input.expected_goal_version,
        scope_revision: input.expected_scope_revision,
        exercise_id: workspace?.head.exercise_record_id ?? undefined,
        answer_id: workspace?.head.answer_record_id ?? undefined,
        request_sha: built.request_sha256, draft_id: draftId.current,
        created_at: new Date().toISOString(), state: "pending",
        ...extra,
      };
      if (!await appendTeachingIntent(summary)) {
        setError("本机恢复台账写入失败，未发出任何请求");
        return;
      }
      reloadIntents();
      if (!await updateTeachingIntent(key, { state: "submitted" })) {
        setError("本机恢复台账确认失败，未发出请求"); return;
      }
      reloadIntents();
      let receipt: TeachingReceipt;
      try {
        receipt = await postTeachingCommand(activityId, { ...input, body }, token);
      } catch (reason) {
        const known = reason instanceof TeachingApiError && reason.status > 0;
        await updateTeachingIntent(key, known
          ? { state: "refused", last_code: (reason as TeachingApiError).code, last_message: (reason as Error).message }
          : { state: "unconfirmed" });
        if (!stillCurrent()) return;
        reloadIntents();
        if (known) setError(errorText((reason as TeachingApiError).code) || (reason as Error).message);
        else setNotice("结果未确认（连接中断）；输入已保留在本机，刷新只做只读核对，不会自动重发。");
        return;
      }
      if (receipt.activity_id!==activityId||receipt.business_key!==key||receipt.action!==action||receipt.request_sha256!==built.request_sha256) {
        await updateTeachingIntent(key,{state:"unconfirmed",last_code:"receipt_mismatch"});
        if (stillCurrent()) { reloadIntents(); setError("回执身份无法核对，原意图已保留"); }
        return;
      }
      if (receipt.status === "committed" || receipt.status === "history") {
        await removeTeachingIntent(key); await removeTeachingDraft(`draft-${key}`);
        if (stillCurrent()) reloadIntents();
      } else if (["unknown","failed","not_sent"].includes(receipt.status)) {
        await updateTeachingIntent(key, { state: "unconfirmed", last_code: receipt.error_code ?? undefined, last_message:receipt.status });
        reloadIntents();
      } else {
        await updateTeachingIntent(key, { state: "submitted" }); reloadIntents();
      }
      if (!stillCurrent()) return;
      if (receipt.status==='committed') {
        if (action==='answer') dirty.current.answer=false;
        if (action==='correct') dirty.current.correction=false;
        if (action==='goal') { dirty.current.goal=false; setSelectedSeed(null); }
      }
      if (receipt.duplicate_of) {
        setNotice("同内容已被同一父槽的其他键接收，返回既有事实，未产生第二次效果。");
      } else if (receipt.status === "committed") {
        setNotice(action === "answer" ? "作答已零费保存（未调用模型）。" : "命令已提交。");
      }
      await refresh(true);
    } finally {
      if (mounted.current&&activityRef.current===activityId) setBusy("");
    }
  }

  async function reconcile(intent: TeachingIntentSummary) {
    setBusy(`reconcile-${intent.key}`); setError(""); setNotice("");
    try {
      const value = await getTeachingCommand(activityId, intent.key, token);
      const match = compareTeachingIntent(intent, value);
      if (match === "matching" && ["committed","history"].includes(String((value as Record<string, unknown>).status))) {
        await removeTeachingIntent(intent.key);
        if (intent.draft_id) await removeTeachingDraft(intent.draft_id);
        reloadIntents();
        setNotice("已只读核对：匹配同一持久命令（未产生第二次动作）。");
      } else if (match === "conflict") {
        await updateTeachingIntent(intent.key, { state: "refused", last_code: "command_key_conflict" });
        reloadIntents();
        setError("已核对：该键绑定不同内容，保留本机输入，未覆盖旧事实。");
      } else {
        const status=String(value?.status??"unknown");
        const unclaimed=value?.retry_policy==='same_key_before_claim';
        await updateTeachingIntent(intent.key, { state: "unconfirmed",last_message:status,last_code:unclaimed?'same_key_before_claim':undefined }); reloadIntents();
        setNotice(unclaimed?'已接受且尚未领取启动；可明确恢复原意图一次。':status==="failed"||status==="not_sent"?"已确认本次失败；可显式以新键重试。":"结果仍在途或未知；仅核对，不会重复启动。");
      }
      await refresh(true);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "核对未完成");
    } finally { if (mounted.current) setBusy(""); }
  }

  async function resumeAccepted(intent: TeachingIntentSummary) {
    if (busy||!intent.draft_id) return;
    const context=contextKey.current; setBusy(`resume-${intent.key}`); setError('');
    const current=()=>mounted.current&&activityRef.current===activityId&&context===contextKey.current;
    try {
      const stored=await readTeachingDraft(intent.draft_id);
      const receipt=await getTeachingCommand(activityId,intent.key,token);
      if (!stored||compareTeachingIntent(intent,receipt)!=='matching'||receipt?.retry_policy!=='same_key_before_claim') {
        if(current()) setNotice('原命令不再满足未领取启动条件；已只读核对，没有重发。'); return;
      }
      const original=JSON.parse(stored.content) as Record<string,unknown>;
      delete original.activity_id;
      const result=await postTeachingCommand(activityId,{...original,business_key:intent.key} as TeachingCommandInput,token);
      if (result.request_sha256!==intent.request_sha||result.business_key!==intent.key) throw new Error('恢复回执身份未确认');
      if (['committed','history'].includes(result.status)) { await removeTeachingIntent(intent.key); await removeTeachingDraft(intent.draft_id); }
      else await updateTeachingIntent(intent.key,{state:'unconfirmed',last_message:result.status,last_code:result.error_code??undefined});
      if(current()) { reloadIntents(); setNotice('原意图恢复已返回；不会自动再发。'); await refresh(true); }
    } catch(reason) { if(current()) setError(reason instanceof Error?reason.message:'恢复未确认，原意图保留'); }
    finally { if(mounted.current&&activityRef.current===activityId) setBusy(''); }
  }

  function useCurrentBinding(keepText: boolean) {
    if (!workspace) return;
    const key=[activityId,workspace.head.goal_record_id,workspace.head.path_record_id,workspace.head.node_id,
      workspace.head.exercise_record_id,workspace.head.answer_record_id,workspace.head.revision].join('|');
    editing.current={activity_id:activityId,head:{...workspace.head},scope_revision:scopeRef.current,key,
      draft_key:editorOwner.current?`edit-${key}|${editorOwner.current}`:null};
    setEditConflict(false); ++editSeq.current;
    if (!keepText) { setAnswerText(String(workspace.answer?.text??'')); dirty.current.answer=false; setCorrectionText(''); dirty.current.correction=false; }
    setNotice(keepText?'已明确将未保存文字沿用到当前作答；原身份草稿仍保留。':'已载入当前作答；旧草稿仍保留在本机。');
  }

  async function selectHistory(item: TeachingHistoryItem) {
    const seq=++historySeq.current, context=contextKey.current;
    historyAbort.current?.abort(); const active=new AbortController(); historyAbort.current=active;
    setHistoryDetail(null); setCorrectionTarget(null); setHistoryNotice('正在读取所选历史…');
    try {
      const record=await getTeachingRecord(activityId,item.record_id,token,active.signal);
      if (!mounted.current||activityRef.current!==activityId||seq!==historySeq.current||active.signal.aborted||context!==contextKey.current) return;
      setHistoryDetail(record); setHistoryNotice('所选记录仅供历史核对，当前工作区保持不变。');
      setCorrectionTarget(['path_proposal','path_accept','feedback','progress'].includes(item.kind)?item.record_id:null);
    } catch (reason) {
      if (mounted.current&&seq===historySeq.current&&!active.signal.aborted&&context===contextKey.current)
        setHistoryNotice(reason instanceof Error?reason.message:'历史读取未确认');
    }
  }

  async function loadEarlier() {
    if (!historyNext||historyLoading) return;
    const cursor=historyNext, expectedToken=workspaceToken.current, seq=++pageSeq.current;
    pageAbort.current?.abort(); const active=new AbortController(); pageAbort.current=active;
    setHistoryLoading(true); setHistoryNotice('');
    try {
      const page=await getTeachingHistory(activityId,token,cursor,active.signal);
      if (!mounted.current||activityRef.current!==activityId||seq!==pageSeq.current||active.signal.aborted||expectedToken!==workspaceToken.current) return;
      if (page.view_token!==expectedToken) throw new TeachingApiError(409,'snapshot_changed','历史版本已变化，请刷新工作区后重新翻页');
      setOlderHistory(previous=>[...previous,...page.items.filter(item=>!previous.some(p=>p.record_id===item.record_id))]);
      setHistoryNext(page.next_cursor);
    } catch (reason) {
      if (mounted.current&&seq===pageSeq.current&&!active.signal.aborted)
        setHistoryNotice(reason instanceof TeachingApiError&&reason.status===409?'历史版本已变化，请刷新工作区后重新翻页':reason instanceof Error?reason.message:'历史分页未确认');
    } finally { if(mounted.current&&seq===pageSeq.current) setHistoryLoading(false); }
  }

  const head = workspace?.head;
  const overlay = workspace?.overlay;
  const budgets=workspace?.budgets;
  const exhausted=Boolean(budgets&&(Number(budgets.requests_reserved)>=Number(budgets.max_requests)
    ||Number(budgets.cost_reserved_microunits)>=Number(budgets.max_cost_microunits)
    ||Number(budgets.running_reserved_seconds)+Number(budgets.running_settled_seconds)>=Number(budgets.max_running_seconds)));
  const canLocal = Boolean(workspace) && !readError && !overlay?.cancelled && !overlay?.expired;
  const canModel = canLocal && Boolean(teachingAvailable) && !exhausted && !overlay?.source_invalid && !overlay?.processing && !overlay?.unknown;
  const canTool = canLocal && calculationAvailable && !overlay?.source_invalid && !overlay?.processing && !overlay?.unknown
    && Number(budgets?.tools_reserved)<Number(budgets?.max_tool_calls)
    && Number(budgets?.running_reserved_seconds)+Number(budgets?.running_settled_seconds)<Number(budgets?.max_running_seconds);
  const noModelReason = !teachingAvailable ? "教学层未配置" : overlay?.processing ? "有在途命令" : overlay?.unknown ? "存在未知结果" : "";
  const reasonBody=(workspace?.reason?.body??{}) as Record<string,unknown>;
  const reasonObservations=(reasonBody.observations??{}) as Record<string,unknown>;
  const reasonCount=(key:string)=>Array.isArray(reasonObservations[key])?(reasonObservations[key] as unknown[]).length:0;

  return (
    <section className="ws-teaching" aria-label="教学工作区">
      <div className="section-title">
        <h4>教学闭环（零费保存 · 显式评价）</h4>
        <span className="quiet">
          {head ? `${PHASE_TEXT[head.phase] ?? head.phase} · 修订 ${head.revision} · 目标版本 ${head.goal_version}` : "读取中…"}
        </span>
      </div>
      <button className="secondary" disabled={busy!==""} onClick={()=>void refresh()}>刷新教学工作区（只读）</button>
      {readError && <p role="alert" className="failure">{readError}</p>}
      {error && <p role="alert" className="failure">{error}<button onClick={() => setError("")}>关闭</button></p>}
      {notice && <p role="status" className="notice">{notice}<button className="secondary" onClick={() => setNotice("")}>知道了</button></p>}
      {overlay?.processing&&<p role="status">教学动作正在处理中；本页只读观察，不自动再发请求。</p>}
      {overlay?.unknown&&<p role="status">结果未知，可能已执行。仅可只读核对，不自动重发或释放未知槽。</p>}
      {overlay?.source_invalid&&<p role="status">资料已失效：已保存的用户文字仍可历史查看，资料派生内容暂停。</p>}
      {overlay?.cancelled && <p className="quiet">活动已取消：新正文不再写入，已提交事实仍可历史查看。</p>}
      {overlay?.expired && <p className="quiet">活动已到期：仅只读；本机草稿可复制到新建活动。</p>}

      <div className="ws-teaching-block">
        <h5>1. 目标与诊断</h5>
        <label htmlFor="teaching-goal">学习目标（零费保存，不调用模型）</label>
        <textarea
          id="teaching-goal" value={goalText} maxLength={1024} disabled={busy !== ""}
          placeholder="例如：能正确换算平均速度并说明数量级"
          onChange={event => { editSeq.current++; dirty.current.goal=true; setSelectedSeed(null); setGoalText(event.target.value); }}
        />
        <button
          className="primary" disabled={busy !== "" || !goalText.trim() || !canLocal}
          onClick={() => void submit("goal", {
            goal: goalText.trim(),
            self_report: null, domain: null, seed_operation_id: selectedSeed?.operation_id??null, seed_payload_sha256: selectedSeed?.payload_sha256??null,
          })}
        >保存目标（不调用模型）</button>
        {selectedSeed&&<p role="status">已载入G7目标；保存时保留原成果身份，不调用模型或重新启动首次学习。</p>}
        <p className="quiet">
          目标每次保存生成新版本；旧反馈、题目与作答保留为历史。没有观察前能力标记为未知，不从目标文字推断。
        </p>
      </div>

      <div className="ws-teaching-block">
        <h5>2. 路径建议与接受</h5>
        <button
          className="secondary"
          disabled={busy !== "" || !canModel || head?.goal_version === 0 || (noModelReason !== "" ? true : false)}
          onClick={() => void submit("plan", { confirmed: true, correction_record_id: null, retry_of: null })}
        >生成/重订路径（1 次模型）</button>
        <button
          className="secondary" disabled={busy !== "" || !canLocal || head?.phase !== "path_review"}
          onClick={() => {
            const proposal=workspace?.proposal?.record_id;
            if (proposal) void submit("accept_path", { proposal_record_id:proposal });
          }}
        >接受当前路径（零费）</button>
        {(workspace?.proposal||workspace?.path)&&<div aria-label="学习路径">
          <p>{String(workspace.proposal?.message??"已接受当前路径")}</p>
          <ol>{((workspace.proposal?.nodes??workspace.path?.nodes??[]) as Record<string,unknown>[]).map((node,index)=><li key={String(node.node_id??index)}>
            <strong>{String(node.title)}</strong>：{String(node.objective)}<p>依据与理由：{String(node.rationale)}</p>
            <TeachingCitations activityId={activityId} recordId={workspace.proposal?.record_id??workspace.path?.record_id}
              ids={citationIds(node)} token={token} label={`路径 n${index+1}`} />
            <p>前置节点：{(node.prerequisites as number[]).map(n=>`n${n+1}`).join("、")||"无"} · {workspace.nodes?.[`n${index+1}`]?.status??"尚未观察"}</p>
            {workspace.head.path_record_id&&<button className="secondary" disabled={busy!==""||!canLocal||overlay?.processing||overlay?.unknown}
              onClick={()=>void submit("select_node",{path_record_id:workspace.head.path_record_id,node_id:`n${index+1}`,archive_current:Boolean(workspace.head.exercise_record_id)})}>选择节点 n{index+1}（保留当前题为历史）</button>}
          </li>)}</ol>
        </div>}
        <p className="quiet">
          路径建议只是建议：接受后才能出练习。模型提供的节点、前置与理由须经服务端校验，不能回传权威字段。
        </p>
      </div>

      <div className="ws-teaching-block">
        <h5>3. 当前练习</h5>
        <TeachingExercise
          workspace={workspace} token={token} busy={busy !== ""}
          onExpose={part => {
            if (!workspace?.head.exercise_record_id) return;
            void submit("expose", { exercise_record_id: workspace.head.exercise_record_id, part });
          }}
        />
        <div className="ws-exercise-actions">
          <button
            className="secondary"
            disabled={busy !== "" || !canModel || head?.path_record_id === null || head?.phase !== "ready"}
            onClick={() => {
              if (!workspace?.head.path_record_id || !workspace.head.node_id) return;
              void submit("exercise", {
                confirmed: true, path_record_id: workspace.head.path_record_id,
                node_id: workspace.head.node_id, purpose: "initial",
                parent_feedback_record_id: null, retry_of: null,
              });
            }}
          >获取练习（1 次模型）</button>
          <button
            className="secondary"
            disabled={busy !== "" || !canModel || head?.phase !== "feedback_ready"}
            onClick={() => {
              if (!workspace?.head.path_record_id || !workspace.head.node_id
                  || !workspace.head.feedback_record_id) return;
              void submit("exercise", {
                confirmed: true, path_record_id: workspace.head.path_record_id,
                node_id: workspace.head.node_id, purpose: "retest",
                parent_feedback_record_id: workspace.head.feedback_record_id, retry_of: null,
              });
            }}
          >新实例复测（1 次模型）</button>
          <button className="secondary" disabled={busy!==""||!canModel||head?.phase!=="feedback_ready"}
            onClick={()=>{if (head?.path_record_id&&head.node_id&&head.feedback_record_id) void submit("exercise",{
              confirmed:true,path_record_id:head.path_record_id,node_id:head.node_id,purpose:"continuation",
              parent_feedback_record_id:head.feedback_record_id,retry_of:null,
            });}}>反馈后续练习（1 次模型）</button>
        </div>
      </div>

      <div className="ws-teaching-block">
        <h5>4. 作答草稿与保存（零费）</h5>
        {editConflict&&<div role="alert" aria-label="作答身份变化">
          <p>作答或修订身份已变化。未保存文字仍绑定原作答及修订 {editing.current?.head.revision}，请核对新作答后再保存。</p>
          <button className="secondary" onClick={()=>useCurrentBinding(true)}>明确沿用草稿到当前作答</button>
          <button className="secondary" onClick={()=>useCurrentBinding(false)}>载入当前作答（保留旧草稿）</button>
        </div>}
        {Boolean(workspace?.answer?.text)&&<p aria-label="已保存作答">已保存作答：{String(workspace?.answer?.text)}</p>}
        <label htmlFor="teaching-answer">作答</label>
        <textarea
          id="teaching-answer" value={answerText} maxLength={ANSWER_MAX} disabled={busy !== ""}
          placeholder="写下你的答案与依据（仅保存在本机浏览器，成功保存后成为不可变记录）"
          onChange={event => {
            editSeq.current++; dirty.current.answer=true; setAnswerText(event.target.value);
            const binding=editing.current;
            if (!binding?.draft_key) { setNotice("本机编辑身份未就绪，文字仍保留在当前页面。"); return; }
            void saveTeachingDraft({draft_id:binding.draft_key,activity_id:binding.activity_id,
              goal_record_id:binding?.head.goal_record_id,exercise_record_id:binding?.head.exercise_record_id,answer_record_id:binding?.head.answer_record_id,
              path_record_id:binding?.head.path_record_id,node_id:binding?.head.node_id,head_revision:binding?.head.revision,
              editor_owner_id:editorOwner.current??undefined,
              content:event.target.value,created_at:new Date().toISOString()});
          }}
        />
        <div className="ws-exercise-actions">
          <button
            className="primary"
            disabled={busy !== "" || !canLocal || editConflict || !workspace?.head.exercise_record_id || !answerText.trim()}
            onClick={() => {
              if (!workspace?.head.exercise_record_id) return;
              void submit("answer", {
                exercise_record_id: workspace.head.exercise_record_id,
                kind: workspace.head.answer_record_id ? "continuation" : "initial",
                text: answerText,
                supersedes_answer_record_id: workspace.head.answer_record_id,
              });
            }}
          >保存作答（零费，不调用模型）</button>
          <button
            className="secondary"
            disabled={busy !== "" || !canLocal || editConflict || !workspace?.head.answer_record_id || !answerText.trim()}
            onClick={() => {
              if (!workspace?.head.exercise_record_id || !workspace.head.answer_record_id) return;
              void submit("answer", {
                exercise_record_id: workspace.head.exercise_record_id, kind: "revision",
                text: answerText, supersedes_answer_record_id: workspace.head.answer_record_id,
              });
            }}
          >提交修正版（零费）</button>
        </div>
        <p className="quiet">
          保存与评价是两个独立动作：保存零费，评价才消耗一次模型。保存成功但评价失败时，作答仍可恢复。
        </p>
      </div>

      <div className="ws-teaching-block">
        <h5>5. 有限核算（需显式配置）</h5>
        <button
          className="secondary"
          disabled={busy !== "" || !canTool || !workspace?.head.answer_record_id || !workspace.exercise?.reference_available}
          onClick={() => {
            if (!workspace?.head.exercise_record_id || !workspace.head.answer_record_id) return;
            void submit("calculate", {
              confirmed: true, exercise_record_id: workspace.head.exercise_record_id,
              answer_record_id: workspace.head.answer_record_id, reference_point_id: "p1", retry_of: null,
            });
          }}
        >核算参考要点（1 次有限计算）</button>
        <p className="quiet">
          核算只按已保存、已展示的固定数值参考构造一次有限计算；不从作答文字猜算式，不执行用户程序。
        </p>
      </div>

      <div className="ws-teaching-block">
        <h5>6. 评价与反馈</h5>
        <button
          className="primary"
          disabled={busy !== "" || !canModel || !["answer_saved","feedback_ready"].includes(head?.phase??"") || !workspace?.head.answer_record_id}
          onClick={() => {
            if (!workspace?.head.exercise_record_id || !workspace.head.answer_record_id) return;
            void submit("evaluate", {
              confirmed: true, exercise_record_id: workspace.head.exercise_record_id,
              answer_record_id: workspace.head.answer_record_id, correction_record_id: workspace.reason?.kind==="correction"?workspace.reason.record_id:null, retry_of: null,
            });
          }}
        >请求评价（1 次模型）</button>
        <TeachingFeedback workspace={workspace} feedback={feedback} token={token} />
        {workspace?.reason&&<div aria-label="更新或保留理由"><h6>更新或保留理由</h6>
          <p>{String(reasonBody.reason??workspace.reason.message??reasonBody.text??"当前事实保留，等待你的下一次明确动作。")}</p>
          {workspace.reason.kind==="progress"&&<p>本节点独立作答 {reasonCount("independent_answers")} 个，辅助观察 {reasonCount("assisted")} 个，争议观察 {reasonCount("contested")} 个。{reasonBody.advance?`当前节点已从 ${String(reasonBody.node_before)} 前进至 ${String(reasonBody.node_after)}。`:"当前节点保留。"}</p>}
          {workspace.reason.kind==="calculation"&&<p>有限核算结果：{String(reasonBody.value_decimal??workspace.reason.value_decimal??"未确认")}</p>}
        </div>}
      </div>

      <div className="ws-teaching-block">
        <h5>7. 纠错与历史</h5>
        <label htmlFor="teaching-correction">你的纠错说明（用户补充，不是已验证事实）</label>
        <textarea
          id="teaching-correction" value={correctionText} maxLength={1024} disabled={busy !== ""}
          onChange={event => { dirty.current.correction=true; setCorrectionText(event.target.value); }}
        />
        <button
          className="secondary"
          disabled={busy !== "" || !canLocal || editConflict || !(correctionTarget||workspace?.head.feedback_record_id||workspace?.head.reason_record_id) || !correctionText.trim()}
          onClick={() => {
            const target=correctionTarget||workspace?.head.feedback_record_id||workspace?.head.reason_record_id;
            if (!target) return;
            void submit("correct", {
              target_record_id:target, text: correctionText.trim(),
              disputed_dimensions: [],
            });
          }}
        >提交纠错（零费）</button>
        <p className="quiet">
          纠错不会覆盖原答案或原反馈：相反的两版评价并存，相关观察标记为有争议，不用于推进。
        </p>
        <ul className="ws-history">
          {[...(workspace?.history??[]),...olderHistory].map(item => (
            <li key={item.record_id} className="quiet">{item.label} · 目标版本 {item.goal_version} · {new Date(item.created_at).toLocaleString("zh-CN", { hour12: false })}
              <button className="secondary" onClick={()=>void selectHistory(item)}>查看记录 · {item.seq}</button></li>
          ))}
        </ul>
        {historyNext&&<button className="secondary" disabled={historyLoading} onClick={()=>void loadEarlier()}>查看更早历史（只读）</button>}
        {historyNotice&&<p role="status">{historyNotice}</p>}
        {historyDetail&&<div aria-label="历史记录正文" data-record-id={String(historyDetail.record_id)}><p>读取资格：{String(historyDetail.qualification)}</p><pre style={{whiteSpace:"pre-wrap"}}>{JSON.stringify(historyDetail.public_body,null,2)}</pre></div>}
        {historyDetail&&<TeachingCitations activityId={activityId} recordId={String(historyDetail.record_id)} ids={citationIds(historyDetail.public_body)} token={token} label="所选历史" />}
      </div>

      {intents.length > 0 && (
        <div className="ws-teaching-block">
          <h5>未确认的教学动作</h5>
          {intents.map(intent => (
            <div key={intent.key} className="ws-intent">
              <p className="quiet">
                {intent.action} · {intent.state === "refused" ? "已被拒绝" : "结果未确认"} · 修订 {intent.head_revision}
                {intent.last_code ? ` · ${errorText(intent.last_code)}` : ""}
              </p>
              <button className="secondary" disabled={busy !== ""} onClick={() => void reconcile(intent)}>核对（只读）</button>
              {intent.last_code==='same_key_before_claim'&&<button className="secondary" disabled={busy!==''||!canLocal||overlay?.source_invalid||exhausted}
                onClick={()=>void resumeAccepted(intent)}>明确恢复原意图（同键）</button>}
              {["failed","not_sent"].includes(intent.last_message??"")&&<button className="secondary" disabled={busy!==""||!canModel} onClick={()=>{
                if (!intent.draft_id) return;
                void readTeachingDraft(intent.draft_id).then(draft=>{
                  if (!draft) return;
                  const original=JSON.parse(draft.content) as {action:TeachingAction;body:Record<string,unknown>};
                  void submit(original.action,{...original.body,retry_of:intent.key});
                });
              }}>显式新键重试</button>}
              <button className="secondary" disabled={busy!==""||!canLocal} onClick={()=>void submit("abandon",{target_business_key:intent.key})}>放弃服务器显示（零费）</button>
              <button className="secondary" disabled={busy !== ""} onClick={() => { void removeTeachingIntent(intent.key).then(reloadIntents); }}>
                放弃本机提示
              </button>
            </div>
          ))}
          <p className="quiet">放弃只清除本机提示，不撤回已提交或延迟到达的请求，也不释放服务端未知槽。</p>
        </div>
      )}
    </section>
  );
}
