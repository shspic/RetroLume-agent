import {dataStorageKey} from "../data/context";
// 提交意图台账：让“请求已提交但响应丢失”在刷新后仍可核对。
// 台账不是授权：只存业务键与用户自己输入的文本，不含密钥、令牌或返回正文；
// 服务端不读取它，清除它不影响任何服务端行为（只失去恢复提示）。

export type IntentKind = "create" | "continue" | "learning_first" | "learning_followup";
export type IntentState = "pending" | "submitted" | "unconfirmed" | "refused";

export type PendingIntent = {
  intent_id: string;
  kind: IntentKind;
  state: IntentState;
  created_at: string;
  activity_id: string;
  source_ids?: string[];
  operation_id?: string;
  parent_operation_id?: string;
  followup?: string;
  business_key?: string;
  goal?: string;
  last_code?: string;
  last_message?: string;
};

const STORAGE_KEY = () => dataStorageKey("retrolume.pending-intents.v1");

function isIntent(value: unknown): value is PendingIntent {
  if (typeof value !== "object" || value === null) return false;
  const item = value as Record<string, unknown>;
  return (
    typeof item.intent_id === "string" &&
    (item.kind === "create" || item.kind === "continue" || item.kind === "learning_first" || item.kind === "learning_followup") &&
    (item.state === "pending" || item.state === "submitted" || item.state === "unconfirmed" || item.state === "refused") &&
    typeof item.created_at === "string" &&
    typeof item.activity_id === "string" &&
    (item.source_ids === undefined || (Array.isArray(item.source_ids) && item.source_ids.every(id => typeof id === "string"))) &&
    (item.operation_id === undefined || typeof item.operation_id === "string") &&
    (item.parent_operation_id === undefined || typeof item.parent_operation_id === "string") &&
    (item.followup === undefined || typeof item.followup === "string") &&
    (item.business_key === undefined || typeof item.business_key === "string") &&
    (item.goal === undefined || typeof item.goal === "string") &&
    (item.kind !== "learning_first" || (typeof item.business_key === "string" && typeof item.goal === "string")) &&
    (item.kind !== "learning_followup" || (typeof item.business_key === "string" && typeof item.followup === "string" && typeof item.parent_operation_id === "string"))
  );
}

export function loadIntents(): { ok: boolean; items: PendingIntent[] } {
  try {
    const raw = localStorage.getItem(STORAGE_KEY());
    if (raw === null) return { ok: true, items: [] };
    const data = JSON.parse(raw) as unknown;
    if (!Array.isArray(data)) return { ok: false, items: [] };
    const items = data.filter(isIntent);
    if (items.length !== data.length) return { ok: false, items };
    return { ok: true, items };
  } catch {
    return { ok: false, items: [] };
  }
}

export function saveIntents(items: PendingIntent[]): boolean {
  try {
    localStorage.setItem(STORAGE_KEY(), JSON.stringify(items));
    return true;
  } catch {
    return false;
  }
}

export function appendIntent(intent: PendingIntent): boolean {
  const current = loadIntents();
  if (!current.ok) return false;
  if (current.items.some(item => item.intent_id === intent.intent_id)) return true;
  return saveIntents([...current.items, intent]);
}

export function updateIntent(intent_id: string, patch: Partial<PendingIntent>): boolean {
  const current = loadIntents();
  if (!current.ok) return false;
  return saveIntents(current.items.map(item => (item.intent_id === intent_id ? { ...item, ...patch } : item)));
}

export function removeIntent(intent_id: string): boolean {
  const current = loadIntents();
  if (!current.ok) return false;
  return saveIntents(current.items.filter(item => item.intent_id !== intent_id));
}

export function clearIntents(): boolean {
  try {
    localStorage.removeItem(STORAGE_KEY());
    return true;
  } catch {
    return false;
  }
}

export function normalizeSourceIds(ids: string[]): string[] {
  return [...new Set(ids)].sort();
}

export function newActivityId(): string {
  return crypto.randomUUID();
}

export function newOperationKey(): string {
  const stamp = new Date().toISOString().replace(/[-:.TZ]/g, "").slice(0, 14);
  const bytes = crypto.getRandomValues(new Uint8Array(4));
  const suffix = Array.from(bytes).map(item => item.toString(16).padStart(2, "0")).join("");
  return `ui-${stamp}-${suffix}`;
}
