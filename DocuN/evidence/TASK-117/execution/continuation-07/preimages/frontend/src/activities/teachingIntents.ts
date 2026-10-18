import {dataStorageKey} from "../data/context";
// 教学意图摘要台账（localStorage，≤16 条/总 32768 字节）与
// 完整待发正文库（原生 IndexedDB，≤16 草稿/总 262144 字节）。
// 不迁改旧 retrolume.pending-intents.v1；本机草稿绝非教学历史。

const SUMMARY_KEY = () => dataStorageKey("retrolume.teaching-intents.v1");
const DB_NAME = () => dataStorageKey("retrolume-teaching");
const STORE = "drafts";
const MAX_SUMMARY_ITEMS = 16;
const MAX_SUMMARY_TOTAL_BYTES = 32768;
const MAX_DRAFTS = 16;
const MAX_DRAFT_TOTAL_BYTES = 262144;

const EDITOR_OWNER_KEY = () => dataStorageKey("retrolume.teaching-editor-owner.v1");
let editorOwner: Promise<string | null> | null = null;

export function teachingEditorOwner(): Promise<string | null> {
  if (editorOwner) return editorOwner.then(id=>{
    // 会话存储身份被更换时不能把原链自动改绑给新owner。
    try{return id&&sessionStorage.getItem(EDITOR_OWNER_KEY())===id?id:null;}catch{return null;}
  });
  editorOwner = new Promise(resolve => {
    if (!navigator.locks || !crypto.randomUUID) { resolve(null); return; }
    void (async () => {
      let candidate: string;
      try {
        const saved=sessionStorage.getItem(EDITOR_OWNER_KEY());
        candidate=saved && /^[0-9a-f-]{36}$/.test(saved) ? saved : crypto.randomUUID();
      } catch { resolve(null); return; }
      // A duplicated/opener tab can inherit sessionStorage. A live Web Lock makes
      // the owner unique; reload keeps its id after the old document releases it.
      for (let tries=0;tries<2;tries++) {
        const id=candidate;
        const acquired=await new Promise<boolean>(ready => {
          void navigator.locks.request(`${EDITOR_OWNER_KEY()}:${id}`,{ifAvailable:true},async lock => {
            if (!lock) { ready(false); return; }
            try { sessionStorage.setItem(EDITOR_OWNER_KEY(),id); }
            catch { ready(false); return; }
            resolve(id);ready(true);
            // Document destruction releases the lock; no server or business slot.
            await new Promise<void>(() => {});
          }).catch(()=>ready(false));
        });
        if (acquired) return;
        candidate=crypto.randomUUID();
      }
      resolve(null);
    })().catch(()=>resolve(null));
  });
  return editorOwner;
}

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
  editor_owner_id?: string;
  view_token?: string;
  namespace?: string;
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
    const raw = localStorage.getItem(SUMMARY_KEY());
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
    localStorage.setItem(SUMMARY_KEY(), JSON.stringify(items));
    return true;
  } catch {
    return false;
  }
}

async function mutateSummaries(change: (items: TeachingIntentSummary[]) => TeachingIntentSummary[]): Promise<boolean> {
  // 回环原生浏览器具有 Web Locks；缺失时保持零 POST，不退回竞态写入。
  if (!navigator.locks) return false;
  try {
    return await navigator.locks.request(SUMMARY_KEY(), () => {
      const current = loadTeachingIntents();
      return current.ok && saveTeachingIntents(change(current.items));
    });
  } catch { return false; }
}

export function appendTeachingIntent(summary: TeachingIntentSummary): Promise<boolean> {
  return mutateSummaries(items => [summary, ...items.filter(item => item.key !== summary.key)]);
}

export function updateTeachingIntent(key: string, patch: Partial<TeachingIntentSummary>): Promise<boolean> {
  return mutateSummaries(items => items.map(item => item.key === key ? { ...item, ...patch } : item));
}

export function removeTeachingIntent(key: string): Promise<boolean> {
  return mutateSummaries(items => items.filter(item => item.key !== key));
}

// --- IndexedDB 草稿正文库 ---

export type TeachingDraft = {
  draft_id: string;
  activity_id: string;
  goal_record_id?: string | null;
  exercise_record_id?: string | null;
  answer_record_id?: string | null;
  path_record_id?: string | null;
  node_id?: string | null;
  head_revision?: number;
  editor_owner_id?: string;
  supersedes_answer_record_id?: string | null;
  content: string;
  created_at: string;
};

function openDb(): Promise<IDBDatabase | null> {
  return new Promise(resolve => {
    if (typeof indexedDB === "undefined") { resolve(null); return; }
    try {
      const request = indexedDB.open(DB_NAME(), 1);
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
      let value: T | null = null;
      request.onsuccess = () => { value = request.result as T; };
      transaction.oncomplete = () => { db.close(); resolve(value); };
      request.onerror = () => { db.close(); resolve(null); };
      transaction.onabort = () => { db.close(); resolve(null); };
    } catch {
      resolve(null);
    }
  });
}

export async function saveTeachingDraft(draft: TeachingDraft): Promise<boolean> {
  const db = await openDb();
  if (!db) return false;
  // 同一 readwrite 事务中核总量并写入，多个页面不能分别通过旧容量检查。
  return new Promise(resolve => {
    try {
      const transaction = db.transaction(STORE, "readwrite");
      const store = transaction.objectStore(STORE);
      const request = store.getAll();
      request.onsuccess = () => {
        const drafts = request.result as TeachingDraft[];
        const others = drafts.filter(d => d.draft_id !== draft.draft_id);
        const bytes = others.reduce((sum, d) => sum + new TextEncoder().encode(d.content).length, 0)
          + new TextEncoder().encode(draft.content).length;
        if (others.length >= MAX_DRAFTS || bytes > MAX_DRAFT_TOTAL_BYTES) { transaction.abort(); return; }
        store.put(draft);
      };
      transaction.oncomplete = () => { db.close(); resolve(true); };
      transaction.onabort = () => { db.close(); resolve(false); };
      transaction.onerror = () => { db.close(); resolve(false); };
    } catch { db.close(); resolve(false); }
  });
}

export async function listTeachingDrafts(): Promise<{ ok: boolean; drafts: TeachingDraft[] }> {
  const result = await withStore<TeachingDraft[]>("readonly", store => store.getAll() as IDBRequest<TeachingDraft[]>);
  if (result === null) return { ok: false, drafts: [] };
  return { ok: result.length <= MAX_DRAFTS, drafts: result };
}

export async function readTeachingDraft(draftId: string): Promise<TeachingDraft | null> {
  const result = await withStore<TeachingDraft>("readonly", store => store.get(draftId) as IDBRequest<TeachingDraft>);
  return result ?? null;
}

export async function removeTeachingDraft(draftId: string): Promise<boolean> {
  const result = await withStore("readwrite", store => store.delete(draftId) as IDBRequest<unknown>);
  return result !== null;
}
