import { useCallback, useEffect, useRef, useState } from "react";
import "./activity-workspace.css";
import { isLearningDocument, LearningResult } from "./LearningResult";
import {
  appendIntent, clearIntents, loadIntents, newActivityId, newOperationKey,
  normalizeSourceIds, removeIntent, updateIntent, type PendingIntent,
} from "./pendingIntents";

type Capabilities = {
  storage_ready: boolean;
  storage_reason: string | null;
  create: { available: boolean; reason: string | null };
  continue: { available: boolean; reason: string | null };
  learning?: { available: boolean; reason: string | null; max_input_chars: number; max_output_tokens: number | null };
  quota_preview: Record<string, number | string[] | null> | null;
  provider: { provider: string; model: string } | null;
  supervision_management_budget_seconds: number;
  window_seconds: number;
  followup_max_chars: number;
};

type ActivityFacts = {
  activity_id: string; status: string; created_at: string; updated_at: string;
  deadline_at: string; cancelled_at: string | null; scope_revision: number;
  max_requests: number; requests_reserved: number;
  max_cost_microunits: number; cost_reserved_microunits: number; reserve_cost_microunits: number;
  max_running_seconds: number; running_reserved_seconds: number; running_settled_seconds: number;
  last_settled_generation?: number | null; last_settled_seconds?: number | null;
  max_tool_calls: number | null; tools_reserved: number;
  source_count: number; source_titles: string[];
  allowed_models?: { provider: string; model: string }[];
  sources?: { source_id: string; title: string; valid: boolean }[];
};

type OperationRow = {
  operation_id: string; kind: string; state: string; disposition: string | null;
  error_code: string | null; reserved_at: string; dispatch_started_at: string | null;
  recorded_at: string | null; prompt_tokens: number | null; completion_tokens: number | null;
  finish_reason: string | null; returned_model: string | null; committed_at: string | null;
  read_status: string; payload_available: boolean;
  payload: { format: string; value: unknown } | null;
};

type MaterialOption = { id: string; title: string; version_id: string; revision: number; format: string };

class ApiError extends Error {
  status: number;
  code: string;
  constructor(status: number, code: string, message: string) { super(message); this.status = status; this.code = code; }
}

const REASON_TEXT: Record<string, string> = {
  config_missing: "本地活动配置缺失（见 config/activity.example.json 模板）",
  config_invalid: "本地活动配置无效",
  config_incompatible: "本地活动配置与监督预算不兼容",
  provider_key_not_configured: "尚未在本地注入模型密钥",
  storage_not_ready: "活动数据表未初始化",
  database_not_configured: "本地数据库未配置",
  database_unavailable: "数据库暂不可用",
  learning_not_configured: "未配置首次学习（见本地学习配置说明）",
  learning_config_invalid: "学习配置格式或输出上限无效",
  learning_config_incompatible: "学习输出上限超过活动或服务预算",
};

const ERROR_TEXT: Record<string, string> = {
  deadline_exceeded: "等待模型响应超时，远端是否已执行未知",
  delivery_unknown: "发送结果未知，不会自动重发",
  transport_unknown: "传输结果未知，不会自动重发",
  request_not_sent: "确认未发出；该请求已计入次数与费用预扣",
  record_denied: "结果未能提交到本地账本（未确认）",
  record_unconfirmed: "结果提交未确认",
  cancelled: "执行被取消",
  executor_lost: "执行者失联（保守未知）",
  invalid_response_json: "远端响应不是合法 JSON",
  invalid_response_shape: "远端响应结构异常",
  invalid_usage: "远端用量字段异常",
  truncated_output: "输出被截断",
  empty_output: "远端返回空内容",
  invalid_output_json: "远端输出不是合法 JSON",
  payload_limit: "正文超过大小上限",
  invalid_payload: "正文封套非法",
  context_limit: "请求超出上下文限额",
  output_token_limit: "输出超过配置上限",
  response_too_large: "远端响应过大",
  invalid_learning_output: "已收到响应，但学习结构或引用无效，未保存为可用成果",
  learning_input_conflict: "该动作已绑定不同输入，请核对已有成果",
  learning_slot_occupied: "首次动作已存在，请只读核对",
  invalid_learning_profile: "学习上下文检查失败，调用已关闭",
  learning_validation_unavailable: "学习条件暂不可验证，调用已关闭",
};

function errorText(code: string | null): string {
  if (!code) return "";
  return ERROR_TEXT[code] ?? "内部错误（未分类）";
}

function operationStatusText(row: OperationRow): string {
  switch (row.read_status) {
    case "committed_current": return "已提交，正文可回查";
    case "committed_history_cancelled": return "已提交（活动已取消，仅供历史查看）";
    case "invalidated_scope_changed": return "已失效，活动范围已变化";
    case "invalidated_source": return "已失效，资料已被替换或移除";
    case "unresolved": return row.state === "unknown" ? "结果未知，可能已发出；不会自动重发" : "进行中，结果尚未提交";
    case "terminal_without_payload": return "已结束但无正文记录";
    default: return "尚无此项操作";
  }
}

function reasonText(reason: string | null | undefined): string {
  if (!reason) return "";
  return REASON_TEXT[reason] ?? reason;
}

function fmt(value: string | null | undefined): string {
  if (!value) return "—";
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? value : date.toLocaleString("zh-CN", { hour12: false });
}

function activityLabel(item: ActivityFacts): string {
  if (!item.source_titles.length) return item.source_count ? `${item.source_count} 份资料` : "无来源范围";
  const names = item.source_titles.map(title => `「${title}」`).join("");
  return item.source_count > item.source_titles.length ? `${names}等 ${item.source_count} 份资料` : names;
}

function statusBadge(status: string): string {
  return status === "running" ? "运行中" : status === "cancelled" ? "已取消" : "空闲";
}

export function ActivityWorkspace({ token }: { token: string }) {
  const [caps, setCaps] = useState<Capabilities | null>(null);
  const [capsError, setCapsError] = useState("");
  const [items, setItems] = useState<ActivityFacts[]>([]);
  const [listCursor, setListCursor] = useState<string | null>(null);
  const [listError, setListError] = useState("");
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [detail, setDetail] = useState<ActivityFacts | null>(null);
  const [operations, setOperations] = useState<OperationRow[]>([]);
  const [opsCursor, setOpsCursor] = useState<string | null>(null);
  const [openOperation, setOpenOperation] = useState<OperationRow | null>(null);
  const [detailError, setDetailError] = useState("");
  const [intents, setIntents] = useState<PendingIntent[]>([]);
  const [intentsOk, setIntentsOk] = useState(true);
  const [materials, setMaterials] = useState<MaterialOption[]>([]);
  const [picked, setPicked] = useState<string[]>([]);
  const [followup, setFollowup] = useState("");
  const [goal, setGoal] = useState("");
  const [goalConfirmed, setGoalConfirmed] = useState(false);
  const [continueFor, setContinueFor] = useState<string | null>(null);
  const [confirmingCancel, setConfirmingCancel] = useState(false);
  const [busy, setBusy] = useState("");
  const [notice, setNotice] = useState("");
  const [error, setError] = useState("");
  const [lastUpdated, setLastUpdated] = useState("");
  const selectedRef = useRef<string | null>(null);
  selectedRef.current = selectedId;
  // 续作01（D2）：异步响应上下文保护——切换、卸载或迟到读取不得覆盖
  // 新的选择；轮询在途防重入；隐藏暂停、恢复只 GET、卸载清理。
  const mountedRef = useRef(true);
  useEffect(() => {
    mountedRef.current = true;
    return () => { mountedRef.current = false; };
  }, []);
  const pollInFlight = useRef(false);
  const listSeq = useRef(0);
  const detailSeq = useRef(0);
  const openSeq = useRef(0);
  const opsLoadSeq = useRef(0);
  const learningWriteRef = useRef(false);

  const api = useCallback(async (path: string, init: RequestInit = {}) => {
    let response: Response;
    try {
      response = await fetch(path, { ...init, headers: { ...init.headers, "X-RetroLume-Session": token } });
    } catch {
      throw new ApiError(0, "network", "连接中断，结果未确认；刷新只重读，不会自动重发");
    }
    let data: unknown = null;
    try { data = await response.json(); } catch { data = null; }
    if (!response.ok) {
      const detail = (data as { detail?: unknown } | null)?.detail;
      const code = typeof detail === "object" && detail !== null ? String((detail as { code?: string }).code ?? "http_error") : "http_error";
      const message = typeof detail === "string" ? detail
        : typeof detail === "object" && detail !== null ? String((detail as { message?: string }).message ?? "请求未完成")
        : "请求未完成，请稍后重试";
      throw new ApiError(response.status, code, message);
    }
    return data as Record<string, unknown>;
  }, [token]);

  const reloadIntents = useCallback(() => {
    const current = loadIntents();
    setIntents(current.items);
    setIntentsOk(current.ok);
  }, []);

  const refreshCapabilities = useCallback(async () => {
    try {
      const data = await api("/api/activities/capabilities");
      setCaps(data as unknown as Capabilities);
      setCapsError("");
    } catch (reason) {
      setCapsError(reason instanceof Error ? reason.message : "无法读取活动能力状态");
    }
  }, [api]);

  const refreshList = useCallback(async (quiet = false, cursor?: string) => {
    const seq = ++listSeq.current;
    try {
      const query = cursor ? `?cursor=${encodeURIComponent(cursor)}` : "";
      const data = await api(`/api/activities${query}`);
      if (!mountedRef.current || seq !== listSeq.current) return; // 迟到响应不覆盖新读取
      const page = (data.items as unknown as ActivityFacts[]) ?? [];
      setItems(previous => (cursor ? [...previous, ...page] : page));
      setListCursor(data.next_cursor as string | null);
      setListError("");
      setLastUpdated(new Date().toLocaleString("zh-CN", { hour12: false }));
    } catch (reason) {
      if (!mountedRef.current || seq !== listSeq.current) return;
      if (!quiet) setListError(reason instanceof Error ? reason.message : "无法读取活动列表");
    }
  }, [api]);

  const refreshDetail = useCallback(async (activityId: string, quiet = false) => {
    const seq = ++detailSeq.current;
    try {
      const [detailData, opsData] = await Promise.all([
        api(`/api/activities/${activityId}`),
        api(`/api/activities/${activityId}/operations?limit=100`),
      ]);
      if (!mountedRef.current || seq !== detailSeq.current || selectedRef.current !== activityId) return;
      setDetail(detailData.activity as unknown as ActivityFacts);
      setOperations((opsData.items as unknown as OperationRow[]) ?? []);
      setOpsCursor(opsData.next_cursor as string | null);
      setDetailError("");
      setLastUpdated(new Date().toLocaleString("zh-CN", { hour12: false }));
    } catch (reason) {
      if (!mountedRef.current || seq !== detailSeq.current || selectedRef.current !== activityId) return;
      if (!quiet) setDetailError(reason instanceof Error ? reason.message : "无法读取活动详情");
    }
  }, [api]);

  const selectActivity = useCallback(async (activityId: string) => {
    openSeq.current += 1; // 使切换前的在途展开响应失效
    selectedRef.current = activityId; // 渲染期同步之外的显式同步，保证本请求上下文检查正确
    setSelectedId(activityId);
    setOpenOperation(null);
    setContinueFor(null);
    setGoal(""); setGoalConfirmed(false);
    setConfirmingCancel(false);
    await refreshDetail(activityId);
  }, [refreshDetail]);

  const loadMaterials = useCallback(async () => {
    try {
      const data = await api("/api/materials?offset=0");
      setMaterials(((data.items as MaterialOption[]) ?? []));
    } catch {
      setMaterials([]);
    }
  }, [api]);

  useEffect(() => {
    if (!token) return;
    reloadIntents();
    void refreshCapabilities();
    void refreshList();
  }, [token, reloadIntents, refreshCapabilities, refreshList]);

  useEffect(() => {
    if (!token || !caps?.storage_ready) return;
    void loadMaterials();
  }, [token, caps?.storage_ready, loadMaterials]);

  const loadMoreOperations = useCallback(async () => {
    if (!selectedId || !opsCursor) return;
    const seq = ++opsLoadSeq.current;
    const activityId = selectedId;
    const cursor = opsCursor;
    try {
      const data = await api(`/api/activities/${activityId}/operations?limit=100&cursor=${encodeURIComponent(cursor)}`);
      if (!mountedRef.current || seq !== opsLoadSeq.current || selectedRef.current !== activityId) return;
      setOperations(previous => [...previous, ...((data.items as unknown as OperationRow[]) ?? [])]);
      setOpsCursor(data.next_cursor as string | null);
    } catch (reason) {
      if (!mountedRef.current || seq !== opsLoadSeq.current || selectedRef.current !== activityId) return;
      setDetailError(reason instanceof Error ? reason.message : "无法读取更多操作");
    }
  }, [api, selectedId, opsCursor]);

  const toggleOperation = useCallback(async (row: OperationRow) => {
    openSeq.current += 1; // 任何面板切换都使在途展开响应失效
    const seq = openSeq.current;
    if (openOperation?.operation_id === row.operation_id) {
      setOpenOperation(null);
      return;
    }
    setOpenOperation(row);
    const activityId = selectedRef.current;
    if (!activityId) return;
    // 列表不带正文；展开时按单操作读取补全（仅读取，不产生任何动作）。
    try {
      const data = await api(`/api/activities/${activityId}/operations/${row.operation_id}`);
      if (!mountedRef.current || seq !== openSeq.current) return; // 迟到正文不覆盖新面板
      setOpenOperation(data.operation as unknown as OperationRow);
    } catch {
      /* 保持列表行信息；正文不可得时按状态说明显示（迟到失败同样不动新面板） */
    }
  }, [api, openOperation?.operation_id]);

  const anyRunning = items.some(item => item.status === "running") || detail?.status === "running";
  useEffect(() => {
    if (!token || !(anyRunning || intents.length > 0 || busy)) return;
    let timer: number | null = null;
    // 简单在途标志实现：上一轮未完成则跳过本次节拍，自动轮询不重叠；
    // 读取函数自身捕获拒绝，finally 必然释放标志，单次失败不永久卡死。
    const poll = async () => {
      if (pollInFlight.current || document.hidden) return;
      pollInFlight.current = true;
      try {
        await refreshList(true);
        const activityId = selectedRef.current;
        if (activityId) await refreshDetail(activityId, true);
      } finally {
        pollInFlight.current = false;
      }
    };
    const start = () => {
      if (timer === null) timer = window.setInterval(() => { void poll(); }, 3000);
    };
    const stop = () => {
      if (timer !== null) { window.clearInterval(timer); timer = null; }
    };
    const onVisibility = () => {
      // 页面隐藏暂停自动轮询；恢复显示重新调度并立即做一次只 GET 轮询。
      if (document.hidden) stop();
      else { start(); void poll(); }
    };
    start();
    document.addEventListener("visibilitychange", onVisibility);
    return () => {
      stop();
      document.removeEventListener("visibilitychange", onVisibility);
    };
  }, [token, anyRunning, intents.length, busy, refreshList, refreshDetail]);

  async function reconcileCreate(intent: PendingIntent) {
    setBusy(`reconcile-${intent.intent_id}`);
    try {
      const data = await api(`/api/activities/${intent.activity_id}`);
      const fact = data.activity as unknown as ActivityFacts;
      const actual = (fact.sources ?? []).map(item => item.source_id).sort();
      const intended = [...(intent.source_ids ?? [])].sort();
      if (JSON.stringify(actual) === JSON.stringify(intended)) {
        removeIntent(intent.intent_id); reloadIntents();
        setNotice("已核对该活动与意图的资料范围一致；实际额度以该活动持久事实为准。");
        await refreshList(true);
        await selectActivity(intent.activity_id);
      } else {
        setError("发现该活动编号已存在，但资料范围与本次意图不一致：未按成功处理，请人工核对后再决定。");
      }
    } catch (reason) {
      if (reason instanceof ApiError && reason.status === 404) {
        setNotice("尚未发现该动作已开始的记录；即使原请求稍后到达，同一活动编号也至多创建一个活动。可重试同一意图或放弃。");
      } else {
        setError(reason instanceof Error ? reason.message : "核对未完成");
      }
    } finally {
      setBusy("");
    }
  }

  async function reconcileContinue(intent: PendingIntent) {
    setBusy(`reconcile-${intent.intent_id}`);
    try {
      const data = await api(`/api/activities/${intent.activity_id}/operations/${intent.operation_id}`);
      removeIntent(intent.intent_id); reloadIntents();
      setNotice("已找到该继续动作的操作记录；结果以下方操作列表与正文为准（不会重发）。");
      await refreshList(true);
      await selectActivity(intent.activity_id);
      setOpenOperation(data.operation as unknown as OperationRow);
    } catch (reason) {
      if (reason instanceof ApiError && reason.status === 404) {
        setNotice("尚未发现该继续动作开始的持久迹象；即使原请求稍后到达，同一操作键也至多产生一次执行。");
      } else {
        setError(reason instanceof Error ? reason.message : "核对未完成");
      }
    } finally {
      setBusy("");
    }
  }

  async function submitCreate(intent: PendingIntent) {
    setBusy("create");
    if (!updateIntent(intent.intent_id, { state: "submitted" })) {
      setBusy(""); reloadIntents(); setError("恢复记录不可写，动作未发出。"); return;
    }
    reloadIntents();
    try {
      await api("/api/activities", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ activity_id: intent.activity_id, source_ids: intent.source_ids }),
      });
      removeIntent(intent.intent_id); reloadIntents();
      setPicked([]);
      setNotice("活动已零费创建。请填写并确认学习目标，再显式开始学习。");
      await refreshList(true);
      await selectActivity(intent.activity_id);
    } catch (reason) {
      if (reason instanceof ApiError && reason.status === 409 && reason.code === "activity_exists") {
        await reconcileCreate(intent);
      } else if (reason instanceof ApiError && reason.status > 0) {
        updateIntent(intent.intent_id, { state: "refused", last_code: reason.code, last_message: reason.message });
        reloadIntents();
        setError(reason.message);
      } else {
        updateIntent(intent.intent_id, { state: "unconfirmed" });
        reloadIntents();
        setNotice("动作结果未确认（连接中断）；已保留恢复记录，刷新后只做只读核对，不会自动重发。");
      }
    } finally {
      setBusy("");
    }
  }

  async function createActivity() {
    if (busy) return;
    if (!caps?.create.available) { setError(`新建未开放：${reasonText(caps?.create.reason)}`); return; }
    if (!intentsOk) { setError("恢复记录不可用：为避免出现无法核对的重复动作，新建已暂停；请优先清除本机恢复记录。"); return; }
    const sourceIds = normalizeSourceIds(picked);
    if (!sourceIds.length) { setError("请先选择资料范围"); return; }
    const intent: PendingIntent = {
      intent_id: crypto.randomUUID(), kind: "create", state: "pending",
      created_at: new Date().toISOString(), activity_id: newActivityId(), source_ids: sourceIds,
    };
    if (!appendIntent(intent)) {
      setError("恢复记录写入失败：为避免重复动作，新建已暂停。");
      reloadIntents();
      return;
    }
    reloadIntents();
    await submitCreate(intent);
  }

  async function submitContinue(intent: PendingIntent) {
    setBusy(`continue-${intent.intent_id}`);
    if (!updateIntent(intent.intent_id, { state: "submitted" })) {
      setBusy(""); reloadIntents(); setError("恢复记录不可写，动作未发出。"); return;
    }
    reloadIntents();
    try {
      const data = await api(`/api/activities/${intent.activity_id}/continuations`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          parent_operation_id: intent.parent_operation_id,
          new_operation_id: intent.operation_id,
          followup: intent.followup,
        }),
      });
      removeIntent(intent.intent_id); reloadIntents();
      const business = data.business as { read_status?: string } | null;
      const supervision = data.supervision as { state?: string } | null;
      if (business?.read_status === "committed_current") {
        setNotice("本次继续已提交正文，可在操作列表中查看。");
      } else if (data.status === "supervision_unknown" || supervision?.state === "local_owner_busy") {
        setNotice("本次动作未获监督结论或与正在进行的动作冲突；请按持久事实核对，不会自动重发。");
      } else {
        setNotice(`本次继续结果：${String(data.status)}。`);
      }
      await refreshDetail(intent.activity_id, true);
      await refreshList(true);
    } catch (reason) {
      if (reason instanceof ApiError && reason.status > 0) {
        updateIntent(intent.intent_id, { state: "refused", last_code: reason.code, last_message: reason.message });
        reloadIntents();
        setError(reason.message);
      } else {
        updateIntent(intent.intent_id, { state: "unconfirmed" });
        reloadIntents();
        setNotice("继续动作结果未确认（连接中断）；已保留恢复记录，可稍后核对。");
      }
    } finally {
      setBusy("");
    }
  }

  async function continueFromOperation() {
    if (!detail || !continueFor || busy) return;
    if (!intentsOk) { setError("恢复记录不可用：为避免出现无法核对的重复动作，继续已暂停；请优先清除本机恢复记录。"); return; }
    const text = followup.trim();
    if (!text) { setError("请输入要继续的内容"); return; }
    if (isLearningDocument(openOperation?.payload?.value, openOperation?.operation_id)) {
      if (!caps?.learning?.available) { setError(`学习续问未开放：${reasonText(caps?.learning?.reason)}`); return; }
      await createLearningIntent("learning_followup", text, continueFor);
      return;
    }
    const intent: PendingIntent = {
      intent_id: crypto.randomUUID(), kind: "continue", state: "pending",
      created_at: new Date().toISOString(), activity_id: detail.activity_id,
      operation_id: newOperationKey(), parent_operation_id: continueFor, followup: text,
    };
    if (!appendIntent(intent)) {
      setError("恢复记录写入失败：为避免重复动作，继续已暂停。");
      reloadIntents();
      return;
    }
    reloadIntents();
    setContinueFor(null);
    setFollowup("");
    await submitContinue(intent);
  }

  async function retryIntent(intent: PendingIntent) {
    if (busy) return;
    if (intent.kind === "create") { await submitCreate(intent); return; }
    if (intent.kind === "learning_first" || intent.kind === "learning_followup") { await submitLearning(intent); return; }
    await submitContinue(intent);
  }

  async function reconcileLearning(intent: PendingIntent) {
    setBusy(`reconcile-${intent.intent_id}`);
    try {
      const action = intent.kind === "learning_first" ? "first" : "followup";
      const data = await api(`/api/activities/${intent.activity_id}/learning/intents/${intent.business_key}?action=${action}`);
      const row = data.operation as OperationRow | null;
      if (row === null) {
        setNotice("尚无持久操作记录，原请求可能仍在途；可由你显式重试同一意图，不会自动重发。");
        return;
      }
      if (row.read_status !== "unresolved") removeIntent(intent.intent_id);
      else updateIntent(intent.intent_id, { state: "unconfirmed", operation_id: row.operation_id });
      reloadIntents();
      await selectActivity(intent.activity_id);
      setOpenOperation(row);
      setNotice("已只读核对学习动作。未知结果保留提示，可能已执行；同键重试只返回已存在的持久事实。");
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "核对未完成");
    } finally { setBusy(""); }
  }

  async function submitLearning(intent: PendingIntent) {
    if (learningWriteRef.current) return;
    learningWriteRef.current = true;
    setBusy(`learning-${intent.intent_id}`);
    if (!updateIntent(intent.intent_id, { state: "submitted" })) {
      learningWriteRef.current = false;
      setBusy(""); reloadIntents(); setError("恢复记录不可写，学习动作未发出。"); return;
    }
    reloadIntents();
    const first = intent.kind === "learning_first";
    try {
      const data = await api(`/api/activities/${intent.activity_id}/learning/${first ? "first" : "followups"}`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify(first ? { business_key: intent.business_key, goal: intent.goal, confirmed: true }
          : { business_key: intent.business_key, parent_operation_id: intent.parent_operation_id, question: intent.followup, confirmed: true }),
      });
      if (data.status === "precheck") {
        removeIntent(intent.intent_id); reloadIntents();
        if (selectedRef.current === intent.activity_id) setNotice(`未调用模型：${String((data.precheck as {message: string}).message)}`);
        return;
      }
      const business = data.business as {read_status?: string} | null;
      const unresolved = business?.read_status === "unresolved" || data.status === "supervision_unknown";
      if (unresolved) updateIntent(intent.intent_id, { state: "unconfirmed", operation_id: String(data.operation_id) });
      else removeIntent(intent.intent_id);
      reloadIntents();
      await refreshList(true);
      if (selectedRef.current !== intent.activity_id || !mountedRef.current) return;
      await refreshDetail(intent.activity_id, true);
      if (data.operation_id) {
        const seq = ++openSeq.current;
        const saved = await api(`/api/activities/${intent.activity_id}/operations/${encodeURIComponent(String(data.operation_id))}`);
        if (seq === openSeq.current && selectedRef.current === intent.activity_id && mountedRef.current) setOpenOperation(saved.operation as unknown as OperationRow);
      }
      if (selectedRef.current === intent.activity_id && mountedRef.current) {
        setNotice(business?.read_status === "committed_current" ? "学习成果已持久提交，可查看引用并显式续问。"
          : unresolved ? "学习结果未确认，可能已执行；请核对持久事实，不会自动重新调用。"
          : "本次学习已结束，持久状态以下方操作记录为准。");
      }
    } catch (reason) {
      const known = reason instanceof ApiError && reason.status > 0 && reason.status < 500;
      updateIntent(intent.intent_id, known ? { state: "refused", last_code: (reason as ApiError).code, last_message: (reason as Error).message } : { state: "unconfirmed" });
      reloadIntents();
      if (selectedRef.current === intent.activity_id && mountedRef.current) {
        setError(reason instanceof Error ? reason.message : "学习结果未确认；请只读核对");
      }
    } finally { learningWriteRef.current = false; if (mountedRef.current) setBusy(""); }
  }

  async function createLearningIntent(kind: "learning_first" | "learning_followup", text: string, parent?: string) {
    if (!detail || busy || learningWriteRef.current || !intentsOk || !caps?.learning?.available) return;
    text = text.trim();
    if (!text || text.length > 1024 || new TextEncoder().encode(text).length > 4096) {
      setError("请填写具体目标或问题，最多1024字和4096 UTF-8字节。"); return;
    }
    const intent: PendingIntent = { intent_id: crypto.randomUUID(), kind, state: "pending",
      created_at: new Date().toISOString(), activity_id: detail.activity_id, business_key: crypto.randomUUID(),
      ...(kind === "learning_first" ? { goal: text } : { followup: text, parent_operation_id: parent }) };
    if (!appendIntent(intent)) { reloadIntents(); setError("恢复记录写入失败，学习动作未发出。"); return; }
    reloadIntents(); setContinueFor(null); setFollowup("");
    await submitLearning(intent);
  }

  function abandonIntent(intent: PendingIntent) {
    removeIntent(intent.intent_id);
    reloadIntents();
    setNotice("已放弃该恢复提示；这不撤回任何已提交或延迟到达的请求。");
  }

  async function cancelActivity() {
    if (!detail || busy) return;
    setConfirmingCancel(false);
    setBusy("cancel");
    try {
      await api(`/api/activities/${detail.activity_id}/cancel`, { method: "POST" });
      setNotice("已取消：不会再开始新动作；正在运行的本机执行会在其窗口内停止；已发往远端的调用无法撤回；已预扣的请求与费用不退还。");
      await refreshDetail(detail.activity_id, true);
      await refreshList(true);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "取消失败");
    } finally {
      setBusy("");
    }
  }

  function canContinue(row: OperationRow): boolean {
    return row.kind === "model" && row.read_status === "committed_current" && detail?.status !== "cancelled";
  }

  if (!token) {
    return <div className="ws"><p role="status">正在连接本地服务…</p></div>;
  }

  return (
    <div className="ws">
      <header>
        <div>
          <p className="eyebrow">YOUR ACTIVITIES, IN FACTS</p>
          <h1>学习活动</h1>
          <p className="subtitle">每次活动限定资料范围与有限预算；这里查看活动、四类预算与每次运行的事实结果。</p>
        </div>
        <button className="secondary" onClick={() => { void refreshCapabilities(); void refreshList(); void loadMaterials(); if (selectedId) void refreshDetail(selectedId); }}>刷新</button>
      </header>
      <p className="quiet">最后更新：{lastUpdated || "—"}（页面读取时间；各面板独立读取，不合并为同一瞬间）</p>

      {capsError && <div className="error" role="alert">{capsError}</div>}
      {error && <div className="error" role="alert">{error}<button onClick={() => setError("")}>关闭</button></div>}
      {notice && <div className="notice" role="status">{notice}<button className="secondary" onClick={() => setNotice("")}>知道了</button></div>}

      {!caps && !capsError && <p role="status">正在读取活动能力状态…</p>}
      {caps && (
        <div className="ws-capabilities">
          <span className={caps.storage_ready ? "ws-cap ok" : "ws-cap blocked"}>
            读取与取消：{caps.storage_ready ? "可用" : `未就绪（${reasonText(caps.storage_reason)}）`}
          </span>
          <span className={caps.create.available ? "ws-cap ok" : "ws-cap blocked"}>
            新建活动：{caps.create.available ? "可用" : `未开放（${reasonText(caps.create.reason)}）`}
          </span>
          <span className={caps.continue.available ? "ws-cap ok" : "ws-cap blocked"}>
            显式继续：{caps.continue.available ? "可用" : `未开放（${reasonText(caps.continue.reason)}）`}
          </span>
          <span className={caps.learning?.available ? "ws-cap ok" : "ws-cap blocked"}>
            开始学习：{caps.learning?.available ? "可用 · 有限词项" : `未开放（${reasonText(caps.learning?.reason ?? "learning_not_configured")}）`}
          </span>
          {caps.storage_ready && (
            <span className="ws-cap">监督管理工作预算最长 {caps.supervision_management_budget_seconds} 秒（不含排队、前后读取与清理时间）</span>
          )}
        </div>
      )}

      {(intents.length > 0 || !intentsOk) && (
        <section className="ws-intents" aria-label="上次动作未确认">
          <h2>上次动作未确认</h2>
          {!intentsOk && (
            <p className="failure">
              本机恢复记录不可用或已损坏：新建、学习与继续已暂停，避免出现无法核对的重复动作；读取与取消不受影响。
              <button className="secondary" onClick={() => { clearIntents(); reloadIntents(); }}>清除恢复记录</button>
            </p>
          )}
          {intents.map(intent => (
            <div className="ws-intent" key={intent.intent_id}>
              <p>
                {intent.kind === "create" ? "新建活动" : intent.kind === "learning_first" ? "首次学习" : intent.kind === "learning_followup" ? "学习续问" : "显式继续"} · {intent.state === "refused" ? "已被拒绝" : "结果未确认"}
                {" · 发起于 "}{fmt(intent.created_at)}
              </p>
              <p className="quiet">
                活动 {intent.activity_id.slice(0, 8)}…
                {intent.operation_id ? ` · 操作键 ${intent.operation_id}` : ""}
                {intent.followup ? ` · 内容摘要 ${intent.followup.slice(0, 40)}${intent.followup.length > 40 ? "…" : ""}` : ""}
                {intent.goal ? ` · 目标 ${intent.goal.slice(0, 40)}` : ""}
                {intent.last_code ? ` · 拒绝原因（${intent.last_code}）${intent.last_message ?? ""}` : ""}
              </p>
              <div className="ws-intent-actions">
                <button className="secondary" disabled={busy !== ""} onClick={() => (intent.kind === "create" ? void reconcileCreate(intent)
                  : intent.kind === "continue" ? void reconcileContinue(intent) : void reconcileLearning(intent))}>核对（只读）</button>
                <button className="secondary" disabled={busy !== ""} onClick={() => void retryIntent(intent)}>重新提交同一意图</button>
                <button className="secondary" disabled={busy !== ""} onClick={() => abandonIntent(intent)}>放弃</button>
              </div>
              <p className="quiet">核对只读取事实；原请求可能在途——刷新与断线不会自动重试，也不会生成新的键。放弃只清除提示，不撤回已提交或延迟到达的请求。</p>
            </div>
          ))}
        </section>
      )}

      {caps?.storage_ready && (
        <section className="ws-create">
          <h2>新建活动</h2>
          <p className="quiet">新建只确定资料范围与有限预算，不会立即产生模型调用。创建后确认目标并显式开始学习。</p>
          {caps.create.available ? (
            <>
              <div className="ws-pick">
                {materials.length === 0 && <p className="quiet">还没有可用资料；请先在「我的资料」导入并核对资料。</p>}
                {materials.map(material => (
                  <label key={material.id} className="ws-pick-row">
                    <input
                      type="checkbox"
                      checked={picked.includes(material.id)}
                      onChange={event => setPicked(previous => event.target.checked
                        ? [...previous, material.id]
                        : previous.filter(id => id !== material.id))}
                    />
                    <span>{material.title}</span>
                    <small>{material.format.toUpperCase()} · 版本 {material.revision}</small>
                  </label>
                ))}
              </div>
              {caps.quota_preview && (
                <dl className="ws-quota">
                  <div><dt>活动期限</dt><dd>{String(caps.quota_preview.deadline_hours)} 小时</dd></div>
                  <div><dt>模型请求上限</dt><dd>{String(caps.quota_preview.max_requests)} 次</dd></div>
                  <div><dt>费用上限</dt><dd>{String(caps.quota_preview.max_cost_microunits)} 微单位（单次预留 {String(caps.quota_preview.reserve_cost_microunits)}）</dd></div>
                  <div><dt>运行时间上限</dt><dd>{String(caps.quota_preview.max_running_seconds)} 秒</dd></div>
                  <div><dt>单次输出上限</dt><dd>{String(caps.quota_preview.max_output_tokens)} token</dd></div>
                  <div><dt>工具</dt><dd>未配置（本版本不执行工具）</dd></div>
                </dl>
              )}
              <p className="quiet">额度来自本地服务端配置，界面不可修改；达到上限会拒绝新动作。</p>
              <button className="primary" disabled={busy !== "" || !picked.length} onClick={() => void createActivity()}>
                {busy === "create" ? "正在创建…" : "创建活动"}
              </button>
            </>
          ) : (
            <p className="quiet">新建未开放：{reasonText(caps.create.reason)}。只读与取消不受影响。</p>
          )}
        </section>
      )}

      <div className="content-grid">
        <section className="library">
          <div className="section-title"><h2>活动列表</h2><span>{items.length} 项{listCursor ? " +" : ""}</span></div>
          {listError && <p role="alert" className="failure">{listError}</p>}
          {!listError && !items.length && (
            <div className="empty">
              <div>▦</div>
              <h3>还没有学习活动</h3>
              <p>新建活动只确定资料范围与有限预算，不会立即产生任何模型调用。<br />刷新与断线只会重新读取，不会重发任何业务动作。</p>
            </div>
          )}
          <ul>
            {items.map(item => (
              <li key={item.activity_id}>
                <button className={`material ${selectedId === item.activity_id ? "selected" : ""}`} onClick={() => void selectActivity(item.activity_id)}>
                  <span className="format">{statusBadge(item.status)}</span>
                  <span className="material-name">
                    <strong>{activityLabel(item)}</strong>
                    <small>剩余请求 {Math.max(item.max_requests - item.requests_reserved, 0)} / {item.max_requests} · 创建于 {fmt(item.created_at)}</small>
                  </span>
                  <span aria-hidden="true">↗</span>
                </button>
              </li>
            ))}
          </ul>
          {listCursor && <button className="secondary" onClick={() => void refreshList(false, listCursor)}>加载更多</button>}
        </section>

        <section className="reader">
          <div className="section-title">
            <h2>{detail ? "活动详情" : "活动详情预览"}</h2>
            {detail && (
              <span className="ws-detail-actions">
                <button className="secondary" disabled={busy !== ""} onClick={() => setConfirmingCancel(true)}>取消活动</button>
              </span>
            )}
          </div>
          {!detail && <div className="empty"><h3>选择一个活动</h3><p>查看范围、预算与运行结果。</p></div>}
          {detail && (
            <>
              {detailError && <p role="alert" className="failure">{detailError}</p>}
              <h3 className="reader-title">{activityLabel(detail)} · {statusBadge(detail.status)}</h3>
              <p className="quiet">创建于 {fmt(detail.created_at)} · 最近更新 {fmt(detail.updated_at)} · 期限 {fmt(detail.deadline_at)}{detail.cancelled_at ? ` · 取消于 ${fmt(detail.cancelled_at)}` : ""}</p>
              {confirmingCancel && (
                <div className="notice" role="alert">
                  <p>取消后不会开始新的动作；正在运行的本机执行会在其自身窗口内停止；已发往远端的调用无法撤回；已预扣的请求次数与费用不退还。</p>
                  <button className="secondary" disabled={busy !== ""} onClick={() => void cancelActivity()}>确认取消</button>
                  <button className="secondary" onClick={() => setConfirmingCancel(false)}>返回</button>
                </div>
              )}

              <div className="ws-block">
                <h4>资料范围 · 范围修订 {detail.scope_revision}</h4>
                {(detail.sources ?? []).map(source => (
                  <p key={source.source_id} className={source.valid ? "quiet" : "failure"}>
                    · {source.title}（{source.valid ? "当前有效" : "已失效：资料已被替换或移除"}）
                  </p>
                ))}
                {!detail.sources?.length && <p className="quiet">无来源范围。</p>}
                <p className="quiet">活动使用创建时的资料版本快照；替换资料后旧成果只读保留，正文可能不可回查。</p>
              </div>

              <div className="ws-block">
                <h4>预算（预扣口径与不确定事实分开显示）</h4>
                <p>模型请求：已预扣 {detail.requests_reserved} / 上限 {detail.max_requests}（预扣不因取消或失败退还）</p>
                <p>费用：已预扣 {detail.cost_reserved_microunits} / 上限 {detail.max_cost_microunits}（单次预留 {detail.reserve_cost_microunits}，微单位，不代表真实账单）</p>
                <p>
                  时间：上限 {detail.max_running_seconds} 秒 · 已结算 {detail.running_settled_seconds} 秒 · 当前预留 {detail.running_reserved_seconds} 秒
                  （可用 {Math.max(detail.max_running_seconds - detail.running_settled_seconds - detail.running_reserved_seconds, 0)} 秒）
                </p>
                <p className="quiet">
                  已结算秒数按本机实际执行的单调测量累计，含取消或残留的保守折叠；账本只保留最近一次结算
                  {detail.last_settled_generation !== null && detail.last_settled_generation !== undefined ? `（代次 ${detail.last_settled_generation}，${detail.last_settled_seconds} 秒）` : ""}，
                  不提供逐窗口历史。本机单窗口有硬性停止（单调时限）；账本的租约与到期判定使用系统时钟。
                </p>
                <p>工具次数：未配置（本版本不执行工具）</p>
                {detail.status === "running" && (
                  <p className="ws-running">运行中（账本事实）：存在一个执行窗口；执行存活未知——账本无法证明本机执行进程是否仍在运行，本页不据此推断。</p>
                )}
              </div>

              <div className="ws-block ws-learning-start" aria-label="开始学习">
                <h4>开始学习</h4>
                <p>资料范围以本活动上方来源为准。仅发送本次必要片段及你的目标，供
                  {caps?.provider ? ` ${caps.provider.provider} / ${caps.provider.model} ` : "已配置的模型服务"}组织学习成果。</p>
                <p className="quiet">有限词项检索 · 最多10份资料、8片段、累计5 MiB原件 · 未启用向量，召回可能遗漏。引用身份和位置可核对，结论仍需审阅。</p>
                {operations.some(row => row.operation_id.startsWith("learn-first-v1.")) ?
                  <p>首次学习动作已存在，请打开下方持久记录；有可用成果时可显式续问。未知或失败不会自动重新调用。</p>
                  : <>
                    <label htmlFor="learning-goal">学习目标或具体问题</label>
                    <textarea id="learning-goal" value={goal} maxLength={1024} placeholder="例如：解释资料中的事务原子性，并给出学习重点"
                      disabled={busy !== ""} onChange={event => { setGoal(event.target.value); setGoalConfirmed(false); }} />
                    <label className="ws-confirm-goal"><input type="checkbox" checked={goalConfirmed}
                      onChange={event => setGoalConfirmed(event.target.checked)} />
                      我确认目标、所选资料范围、服务用途和上方有限额度；本次将耗用一次请求及一次费用预留</label>
                    <p className="quiet">本次输出最多 {caps?.learning?.max_output_tokens ?? "—"} token。新建零费，开始学习才进入受控调用链。远端已发出的调用不能撤回。</p>
                    <button className="primary" disabled={busy !== "" || !goal.trim() || !goalConfirmed || !intentsOk || !caps?.learning?.available
                      || detail.status === "cancelled" || detail.status === "running" || detail.sources?.some(s => !s.valid)
                      || detail.requests_reserved >= detail.max_requests || detail.running_reserved_seconds + detail.running_settled_seconds >= detail.max_running_seconds}
                      onClick={() => void createLearningIntent("learning_first", goal)}>确认并开始学习</button>
                    {!caps?.learning?.available && <p className="quiet">学习未开放：{reasonText(caps?.learning?.reason ?? "learning_not_configured")}。读取、新建和取消按各自配置可用。</p>}
                  </>}
              </div>

              <div className="ws-block">
                <h4>操作与结果</h4>
                {!operations.length && <p className="quiet">尚无操作。确认目标后可开始首次学习。</p>}
                <ul className="ws-operations">
                  {operations.map(row => {
                    // 列表不携正文；展开时以取回的单操作数据为准渲染（回退列表行）。
                    const op = openOperation?.operation_id === row.operation_id ? openOperation : row;
                    return (
                      <li key={row.operation_id}>
                        <button className={`ws-op ${openOperation?.operation_id === row.operation_id ? "selected" : ""}`} onClick={() => void toggleOperation(row)}>
                          <span>{row.operation_id}</span>
                          <span>{row.kind === "tool" ? "本地计算" : "模型调用"}</span>
                          <span>{operationStatusText(row)}</span>
                          <small>{fmt(row.recorded_at ?? row.dispatch_started_at ?? row.reserved_at)}</small>
                        </button>
                        {openOperation?.operation_id === row.operation_id && (
                          <div className="ws-op-detail">
                            {op.error_code && <p className="failure">失败原因：{errorText(op.error_code)}</p>}
                            <p className="quiet">
                              预留 {fmt(op.reserved_at)} · 确认开始 {fmt(op.dispatch_started_at)} · 记录 {fmt(op.recorded_at)} · 提交 {fmt(op.committed_at)}
                              {op.returned_model ? ` · 返回模型 ${op.returned_model}` : ""}
                              {op.prompt_tokens !== null ? ` · 提示 ${op.prompt_tokens} / 补全 ${op.completion_tokens ?? 0} token` : ""}
                            </p>
                            {op.payload
                              ? isLearningDocument(op.payload.value, op.operation_id)
                                ? <LearningResult key={`${detail.activity_id}:${op.operation_id}`} document={op.payload.value}
                                  activityId={detail.activity_id} operationId={op.operation_id} token={token} />
                                : <pre>{op.payload.format === "json" ? JSON.stringify(op.payload.value, null, 2) : String(op.payload.value)}</pre>
                              : op.read_status === "invalidated_scope_changed" || op.read_status === "invalidated_source"
                                ? <p className="quiet">正文已失效（活动范围或资料已变化），不再提供。</p>
                                : <p className="quiet">尚无正文（结果未提交或未知）。</p>}
                            {canContinue(op) && (
                              continueFor === row.operation_id ? (
                                <div className="ws-continue">
                                  <textarea
                                    value={followup}
                                    aria-label="续问内容"
                                    maxLength={isLearningDocument(op.payload?.value, op.operation_id) ? 1024 : caps?.followup_max_chars ?? 4096}
                                    placeholder="输入要继续的内容（只保存在本机浏览器，可随时清除）"
                                    onChange={event => setFollowup(event.target.value)}
                                  />
                                  <p className="quiet">
                                    本次动作将消耗 1 次模型请求与 1 次单次费用预留；当前剩余请求 {Math.max(detail.max_requests - detail.requests_reserved, 0)}，
                                    剩余费用 {Math.max(detail.max_cost_microunits - detail.cost_reserved_microunits, 0)} 微单位。
                                  </p>
                                  <button className="primary" disabled={busy !== "" || !intentsOk || (isLearningDocument(op.payload?.value, op.operation_id) && !caps?.learning?.available)} onClick={() => void continueFromOperation()}>
                                    {busy.startsWith("continue-") ? "执行中…" : "发出并等待"}
                                  </button>
                                  <button className="secondary" onClick={() => { setContinueFor(null); setFollowup(""); }}>返回</button>
                                </div>
                              ) : (
                                <button className="secondary" disabled={busy !== "" || !intentsOk || (isLearningDocument(op.payload?.value, op.operation_id) ? !caps?.learning?.available : !caps?.continue.available)} onClick={() => { setContinueFor(row.operation_id); setFollowup(""); }}>
                                  {isLearningDocument(op.payload?.value, op.operation_id) ? "从该学习成果续问…" : "从该成果继续…"}
                                </button>
                              )
                            )}
                            {op.kind === "tool" && <p className="quiet">工具结果仅可只读查看，不能作为继续依据。</p>}
                            {!caps?.continue.available && op.kind === "model" && op.read_status === "committed_current" && (
                              <p className="quiet">显式继续未开放：{reasonText(caps?.continue.reason)}。</p>
                            )}
                          </div>
                        )}
                      </li>
                    );
                  })}
                </ul>
                {opsCursor && <button className="secondary" onClick={() => void loadMoreOperations()}>加载更多操作</button>}
              </div>
            </>
          )}
        </section>
      </div>
      <footer>活动数据来自本地持久账本；页面只读取事实，动作仅由明确点击触发；正文纯文本展示，不执行其中的脚本或 HTML。</footer>
    </div>
  );
}
