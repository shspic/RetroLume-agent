// 教学命令 API 客户端：本地先存意图再 POST；核对/恢复只 GET。
// 不含密钥、DSN、provider 或任何授权字段。

export type TeachingAction =
  | "goal" | "plan" | "accept_path" | "exercise" | "expose" | "answer"
  | "calculate" | "evaluate" | "correct" | "abandon" | "select_node";

export type TeachingCommandInput = {
  business_key: string;
  expected_revision: number;
  expected_goal_version: number;
  expected_scope_revision: number;
  action: TeachingAction;
  body: Record<string, unknown>;
};

export type TeachingReceipt = {
  activity_id: string;
  business_key: string;
  action: TeachingAction;
  request_sha256: string;
  status: "accepted" | "started" | "committed" | "history" | "not_sent" | "failed" | "unknown" | "abandoned";
  duplicate_of: string | null;
  record_ids: { record_id: string; kind: string; seq: number }[];
  operation_id: string | null;
  payload_sha256: string | null;
  applied_revision: number | null;
  head_revision_now: number;
  qualification: string;
  error_code: string | null;
  model_called: boolean | null;
  tool_called: boolean | null;
  retry_policy: string;
  exposed_part: Record<string, unknown> | null;
};

export type TeachingRegion = {
  qualification: string;
  record_id?: string;
  [key: string]: unknown;
};

export type TeachingWorkspace = {
  schema: string;
  activity_id: string;
  view_token: string;
  read_at: string;
  head: {
    revision: number;
    goal_version: number;
    phase: string;
    goal_record_id: string | null;
    path_record_id: string | null;
    node_id: string | null;
    exercise_record_id: string | null;
    answer_record_id: string | null;
    feedback_record_id: string | null;
    reason_record_id: string | null;
    pending_business_key: string | null;
  };
  overlay: {
    source_invalid: boolean;
    cancelled: boolean;
    expired: boolean;
    processing: boolean;
    unknown: boolean;
    teaching_disabled_reason?: string | null;
  };
  goal?: TeachingRegion | null;
  path?: TeachingRegion | null;
  proposal?: TeachingRegion | null;
  exercise?: TeachingRegion | null;
  answer?: TeachingRegion | null;
  feedback?: TeachingRegion | null;
  reason?: TeachingRegion | null;
  nodes?: Record<string,{status:string;independent_answers?:string[]}> | null;
  sources?: { source_id: string; version_id: string; valid: boolean; title: string | null; format: string | null }[];
  budgets: Record<string, number | string | null>;
  pending: { business_key: string; action: string; status: string; error_code?: string | null; created_at: string }[];
  history: TeachingHistoryItem[];
  next_cursor?: string | null;
  limits: Record<string, number>;
};

export class TeachingApiError extends Error {
  status: number;
  code: string;
  constructor(status: number, code: string, message: string) {
    super(message);
    this.status = status;
    this.code = code;
  }
}

async function request(path: string, token: string, init: RequestInit = {}): Promise<Record<string, unknown>> {
  let response: Response;
  try {
    response = await fetch(path, { ...init, headers: { ...init.headers, "X-RetroLume-Session": token } });
  } catch {
    throw new TeachingApiError(0, "network", "连接中断，结果未确认；刷新只重读，不会自动重发");
  }
  let data: unknown = null;
  try { data = await response.json(); } catch { data = null; }
  if (!response.ok) {
    const detail = (data as { detail?: unknown } | null)?.detail;
    const code = typeof detail === "object" && detail !== null
      ? String((detail as { code?: string }).code ?? "http_error") : "http_error";
    const message = typeof detail === "string" ? detail
      : typeof detail === "object" && detail !== null
        ? String((detail as { message?: string }).message ?? "请求未完成") : "请求未完成";
    throw new TeachingApiError(response.status, code, message);
  }
  return data as Record<string, unknown>;
}

export async function postTeachingCommand(
  activityId: string, command: TeachingCommandInput, token: string,
): Promise<TeachingReceipt> {
  const data = await request(`/api/activities/${activityId}/teaching/commands`, token, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(command),
  });
  return data as unknown as TeachingReceipt;
}

export async function getTeachingCommand(
  activityId: string, businessKey: string, token: string,
): Promise<Record<string, unknown> | null> {
  return request(`/api/activities/${activityId}/teaching/commands/${businessKey}`, token);
}

export async function getTeachingWorkspace(activityId: string, token: string, signal?: AbortSignal): Promise<TeachingWorkspace | null> {
  const data = await request(`/api/activities/${activityId}/teaching/workspace`, token, { signal });
  return data as unknown as TeachingWorkspace;
}

export type TeachingHistoryItem = { record_id: string; kind: string; seq: number; goal_version: number;
  label: string; created_at: string; qualification?: string };
export type TeachingHistoryPage = { items: TeachingHistoryItem[]; next_cursor: string | null; view_token: string };

export async function getTeachingHistory(activityId: string, token: string, cursor?: string, signal?: AbortSignal): Promise<TeachingHistoryPage> {
  const query = cursor ? `?cursor=${encodeURIComponent(cursor)}` : "";
  return await request(`/api/activities/${activityId}/teaching/history${query}`, token, { signal }) as unknown as TeachingHistoryPage;
}

export async function getTeachingRecord(activityId: string, recordId: string, token: string, signal?: AbortSignal) {
  return request(`/api/activities/${activityId}/teaching/records/${recordId}`, token, { signal });
}

export type TeachingSeed = { activity_id: string; goal: string; operation_id: string; payload_sha256: string };
export async function getTeachingSeed(activityId: string, operationId: string, token: string): Promise<TeachingSeed> {
  return await request(`/api/activities/${activityId}/teaching/seeds/${encodeURIComponent(operationId)}`, token) as unknown as TeachingSeed;
}
export type TeachingCitation = { citation_id: string; source_id: string; version_id: string; source_revision: number;
  title: string; format: string; origin_kind: string; physical_page: number | null; start_line: number; end_line: number; text: string };
export async function getTeachingCitation(activityId: string, recordId: string, id: string, token: string, signal?: AbortSignal) {
  return await request(`/api/activities/${activityId}/teaching/records/${recordId}/citations/${encodeURIComponent(id)}`, token, {signal}) as unknown as {citation:TeachingCitation;read_at:string};
}

export async function getTeachingCapabilities(token: string) {
  return request("/api/activities/capabilities", token);
}
