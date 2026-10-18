// 教学意图摘要台账（localStorage，≤16 条/总 32768 字节）与
// 完整待发正文库（原生 IndexedDB，≤16 草稿/总 262144 字节）。
// 不迁改旧 retrolume.pending-intents.v1；本机草稿绝非教学历史。

const SUMMARY_KEY = "retrolume.teaching-intents.v1";
const DB_NAME = "retrolume-teaching";
const STORE = "drafts";
const MAX_SUMMARY_ITEMS = 16;
const MAX_SUMMARY_TOTAL_BYTES = 32768;
const MAX_DRAFTS = 16;
const MAX_DRAFT_TOTAL_BYTES = 262144;

export type TeachingIntentSummary = {
  key: string;
  action: string;
  activity_id: string;
  head_revision: number;
  goal_version: number;
  scope_revision: number;
  exercise_id?: string;
  answer_id?: string;
  parent_id?: string;
  request_sha?: string;
  draft_id?: string;
  created_at: string;
  state: "pending" | "submitted" | "committed" | "unconfirmed" | "refused";
  last_code?: string;
  last_message?: string;
};

function isSummary(value: unknown): value is TeachingIntentSummary {
  if (typeof value !== "object" || value === null) return false;
  const item = value as Record<string, unknown>;
  return typeof item.key === "string" && typeof item.action === "string"
    && typeof item.activity_id === "string" && typeof item.head_revision === "number"
    && typeof item.goal_version === "number" && typeof item.scope_revision === "number"
    && typeof item.created_at === "string" && typeof item.state === "string";
}

export function loadTeachingIntents(): { ok: boolean; items: TeachingIntentSummary[] } {
  try {
    const raw = localStorage.getItem(SUMMARY_KEY);
    if (raw === null) return { ok: true, items: [] };
    const data = JSON.parse(raw) as unknown;
    if (!Array.isArray(data)) return { ok: false, items: [] };
    const items = data.filter(isSummary).slice(0, MAX_SUMMARY_ITEMS);
    return { ok: items.length === data.length, items };
  } catch {
    return { ok: false, items: [] };
  }
}

function checkBudget(items: TeachingIntentSummary[]): boolean {
  const serialized = JSON.stringify(items);
  return items.length <= MAX_SUMMARY_ITEMS
    && new TextEncoder().encode(serialized).length <= MAX_SUMMARY_TOTAL_BYTES;
}

export function saveTeachingIntents(items: TeachingIntentSummary[]): boolean {
  try {
    if (!checkBudget(items)) return false;
    localStorage.setItem(SUMMARY_KEY, JSON.stringify(items));
    return true;
  } catch {
    return false;
  }
}

export function appendTeachingIntent(summary: TeachingIntentSummary): boolean {
  const current = loadTeachingIntents();
  if (!current.ok) return false;
  const merged = [summary, ...current.items.filter(item => item.key !== summary.key)].slice(0, MAX_SUMMARY_ITEMS);
  return saveTeachingIntents(merged);
}

export function updateTeachingIntent(key: string, patch: Partial<TeachingIntentSummary>): boolean {
  const current = loadTeachingIntents();
  if (!current.ok) return false;
  return saveTeachingIntents(current.items.map(item => (item.key === key ? { ...item, ...patch } : item)));
}

export function removeTeachingIntent(key: string): boolean {
  const current = loadTeachingIntents();
  if (!current.ok) return false;
  return saveTeachingIntents(current.items.filter(item => item.key !== key));
}

// --- IndexedDB 草稿正文库 ---

export type TeachingDraft = {
  draft_id: string;
  activity_id: string;
  goal_record_id?: string | null;
  exercise_record_id?: string | null;
  answer_record_id?: string | null;
  supersedes_answer_record_id?: string | null;
  content: string;
  created_at: string;
};

function openDb(): Promise<IDBDatabase | null> {
  return new Promise(resolve => {
    if (typeof indexedDB === "undefined") { resolve(null); return; }
    try {
      const request = indexedDB.open(DB_NAME, 1);
      request.onupgradeneeded = () => {
        const db = request.result;
        if (!db.objectStoreNames.contains(STORE)) db.createObjectStore(STORE, { keyPath: "draft_id" });
      };
      request.onsuccess = () => resolve(request.result);
      request.onerror = () => resolve(null);
    } catch {
      resolve(null);
    }
  });
}

async function withStore<T>(mode: IDBTransactionMode, run: (store: IDBObjectStore) => IDBRequest<T>): Promise<T | null> {
  const db = await openDb();
  if (db === null) return null;
  return new Promise(resolve => {
    try {
      const transaction = db.transaction(STORE, mode);
      const request = run(transaction.objectStore(STORE));
      request.onsuccess = () => resolve(request.result as T);
      request.onerror = () => resolve(null);
      transaction.onabort = () => resolve(null);
    } catch {
      resolve(null);
    }
  });
}

export async function saveTeachingDraft(draft: TeachingDraft): Promise<boolean> {
  const existing = await listTeachingDrafts();
  if (existing.ok && existing.drafts.length >= MAX_DRAFTS
      && !existing.drafts.some(d => d.draft_id === draft.draft_id)) {
    // 容量满：不自动清旧输入，由用户选择具体草稿保留/删除。
    return false;
  }
  if (existing.ok) {
    const total = existing.drafts.filter(d => d.draft_id !== draft.draft_id)
      .reduce((sum, d) => sum + new TextEncoder().encode(d.content).length, 0)
      + new TextEncoder().encode(draft.content).length;
    if (total > MAX_DRAFT_TOTAL_BYTES) return false;
  }
  const result = await withStore("readwrite", store => store.put(draft) as IDBRequest<unknown>);
  return result !== null;
}

export async function listTeachingDrafts(): Promise<{ ok: boolean; drafts: TeachingDraft[] }> {
  const result = await withStore<TeachingDraft[]>("readonly", store => store.getAll() as IDBRequest<TeachingDraft[]>);
  if (result === null) return { ok: false, drafts: [] };
  return { ok: true, drafts: result.slice(0, MAX_DRAFTS) };
}

export async function readTeachingDraft(draftId: string): Promise<TeachingDraft | null> {
  const result = await withStore<TeachingDraft>("readonly", store => store.get(draftId) as IDBRequest<TeachingDraft>);
  return result ?? null;
}

export async function removeTeachingDraft(draftId: string): Promise<boolean> {
  const result = await withStore("readwrite", store => store.delete(draftId) as IDBRequest<unknown>);
  return result !== null;
}
