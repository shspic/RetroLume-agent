import {dataStorageKey} from "../data/context";
import { teachingEditorOwner } from "./teachingIntents";
import { canonicalMemory } from "./memoryApi";

const SUMMARY = () => dataStorageKey("retrolume.memory-intents.v1");
const DB = () => dataStorageKey("retrolume-memory");
export type MemoryIntent = { key: string; action: string; memory_id: string; owner: string; request_sha: string;
  draft_id: string; state: "pending" | "submitted" | "unconfirmed" | "refused"; created_at: string };
export type MemoryDraft = { id: string; memory_id: string; owner: string; version: number; revision: number;
  body_sha: string; content: string };
export const memoryEditorOwner = teachingEditorOwner;
export function loadMemoryIntents(): { ok: boolean; items: MemoryIntent[] } {
  try {
    const raw = localStorage.getItem(SUMMARY());
    if (!raw) return { ok: true, items: [] };
    const items = JSON.parse(raw) as MemoryIntent[];
    if (!Array.isArray(items) || items.length > 16 || items.some(i => typeof i.key !== "string" ||
      typeof i.request_sha !== "string" || typeof i.owner !== "string" || typeof i.memory_id !== "string"))
      return { ok: false, items: [] };
    return { ok: true, items };
  } catch { return { ok: false, items: [] }; }
}
export async function mutateMemoryIntents(change: (items: MemoryIntent[]) => MemoryIntent[]): Promise<boolean> {
  if (!navigator.locks) return false;
  try {
    return await navigator.locks.request(SUMMARY(), () => {
      const current = loadMemoryIntents(); if (!current.ok) return false;
      const next = change(current.items); const raw = canonicalMemory(next);
      if (next.length > 16 || new TextEncoder().encode(raw).length > 32768) return false;
      localStorage.setItem(SUMMARY(), raw); return true;
    });
  } catch { return false; }
}
export const appendMemoryIntent = (intent: MemoryIntent) => mutateMemoryIntents(items => [intent, ...items.filter(i => i.key !== intent.key)]);
export const updateMemoryIntent = (key: string, state: MemoryIntent["state"]) =>
  mutateMemoryIntents(items => items.map(i => i.key === key ? { ...i, state } : i));
export const removeMemoryIntent = (key: string) => mutateMemoryIntents(items => items.filter(i => i.key !== key));

function openDb(): Promise<IDBDatabase | null> {
  return new Promise(resolve => {
    try {
      const req = indexedDB.open(DB(), 1);
      req.onupgradeneeded = () => { if (!req.result.objectStoreNames.contains("drafts")) req.result.createObjectStore("drafts", { keyPath: "id" }); };
      req.onsuccess = () => resolve(req.result); req.onerror = () => resolve(null);
    } catch { resolve(null); }
  });
}
export async function saveMemoryDraft(draft: MemoryDraft): Promise<boolean> {
  const db = await openDb(); if (!db) return false;
  return new Promise(resolve => {
    const tx = db.transaction("drafts", "readwrite"); const store = tx.objectStore("drafts");
    const req = store.getAll();
    req.onsuccess = () => {
      const others = (req.result as MemoryDraft[]).filter(x => x.id !== draft.id);
      const bytes = others.reduce((sum, x) => sum + new TextEncoder().encode(x.content).length, 0)
        + new TextEncoder().encode(draft.content).length;
      if (others.length >= 16 || bytes > 262144) { tx.abort(); return; }
      store.put(draft);
    };
    tx.oncomplete = () => { db.close(); resolve(true); }; tx.onabort = () => { db.close(); resolve(false); };
    tx.onerror = () => { db.close(); resolve(false); };
  });
}
export async function readMemoryDraft(id: string): Promise<MemoryDraft | null> {
  const db = await openDb(); if (!db) return null;
  return new Promise(resolve => {
    const tx = db.transaction("drafts", "readonly"); const req = tx.objectStore("drafts").get(id);
    let value: MemoryDraft | null = null; req.onsuccess = () => { value = req.result ?? null; };
    tx.oncomplete = () => { db.close(); resolve(value); }; tx.onabort = () => { db.close(); resolve(null); };
  });
}
export async function removeMemoryDraft(id: string): Promise<boolean> {
  const db = await openDb(); if (!db) return false;
  return new Promise(resolve => {
    const tx = db.transaction("drafts", "readwrite"); tx.objectStore("drafts").delete(id);
    tx.oncomplete = () => { db.close(); resolve(true); }; tx.onabort = () => { db.close(); resolve(false); };
  });
}
export async function removeMemoryDraftIfCurrent(id: string, current: () => boolean): Promise<boolean> {
  const db = await openDb(); if (!db) return false;
  if (!current()) { db.close(); return false; }
  return new Promise(resolve => {
    const tx = db.transaction("drafts", "readwrite"); const store = tx.objectStore("drafts");
    const req = store.get(id); let removed = false;
    req.onsuccess = () => {
      // 同一事件内核当前编辑身份；随后新编辑的事务排在此删除之后，不清新草稿。
      if (current()) { store.delete(id); removed = true; }
    };
    tx.oncomplete = () => { db.close(); resolve(removed); };
    tx.onabort = tx.onerror = () => { db.close(); resolve(false); };
  });
}
export async function clearMemoryDraftsForId(memoryId: string): Promise<boolean> {
  const db = await openDb(); if (!db) return false;
  return new Promise(resolve => {
    const tx = db.transaction("drafts", "readwrite"); const store = tx.objectStore("drafts"); const req = store.getAll();
    req.onsuccess = () => (req.result as MemoryDraft[]).filter(d => d.memory_id === memoryId).forEach(d => store.delete(d.id));
    tx.oncomplete = () => { db.close(); resolve(true); }; tx.onabort = () => { db.close(); resolve(false); };
  });
}



export async function submitTrackedMemory(command: import("./memoryApi").MemoryCommand, token: string) {
  const api = await import("./memoryApi");
  const owner = await memoryEditorOwner();
  if (!owner) throw new api.MemoryApiError(0, "recovery_unavailable", "本机恢复身份未就绪，输入保留，未发出请求。");
  const body = api.memoryCommandBody(command);
  const digest = await api.memoryDigest(body);
  const draftId = "intent|" + command.business_key + "|" + owner;
  if (!await saveMemoryDraft({ id: draftId, memory_id: command.memory_id, owner, version: 0,
    revision: command.expected_revision, body_sha: "", content: JSON.stringify(command) }))
    throw new api.MemoryApiError(0, "recovery_unavailable", "本机正文保存失败，未发出请求。");
  const intent: MemoryIntent = { key: command.business_key, action: command.action, memory_id: command.memory_id,
    owner, request_sha: digest, draft_id: draftId, state: "pending", created_at: new Date().toISOString() };
  if (!await appendMemoryIntent(intent) || !await updateMemoryIntent(intent.key, "submitted"))
    throw new api.MemoryApiError(0, "recovery_unavailable", "恢复台账写入失败，未发出请求。");
  try {
    const receipt = await api.postMemory(command, token);
    if (receipt.business_key !== command.business_key || receipt.memory_id !== command.memory_id ||
      receipt.action !== command.action || receipt.request_sha256 !== digest)
      throw new api.MemoryApiError(0, "receipt_mismatch", "回执身份未确认，原意图保留。");
    if (receipt.status === "committed") {
      await removeMemoryIntent(intent.key); await removeMemoryDraft(draftId);
      if (command.action === "revoke") await clearMemoryDraftsForId(command.memory_id);
    }
    return receipt;
  } catch (reason) {
    await updateMemoryIntent(intent.key, reason instanceof api.MemoryApiError && reason.status > 0 ? "refused" : "unconfirmed");
    throw reason;
  }
}


export async function submitTrackedMemoryCreate(activityId: string, sourceIds: string[],
  entries: import("./memoryApi").MemoryChoice[], token: string) {
  const api = await import("./memoryApi");
  const owner = await memoryEditorOwner();
  if (!owner) throw new Error("本机恢复身份不可用，未创建活动。");
  const body = { activity_id: activityId, source_ids: [...sourceIds].sort(), memory_selection: { confirmed: true, entries } };
  const hash = await api.memoryDigest(body);
  const draftId = "create|" + activityId + "|" + owner;
  if (!await saveMemoryDraft({ id: draftId, memory_id: activityId, owner, version: 0, revision: 0, body_sha: "",
    content: JSON.stringify(body) }) || !await appendMemoryIntent({ key: activityId, memory_id: activityId, owner,
      action: "create_activity", request_sha: hash, draft_id: draftId, state: "pending", created_at: new Date().toISOString() }) ||
    !await updateMemoryIntent(activityId, "submitted")) throw new Error("恢复台账未保存，未创建活动。");
  try {
    const result = await api.memoryRequest<{ activity: { memory_selection?: { create_request_sha256: string } } }>("/api/activities", token,
      { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
    if (result.activity.memory_selection?.create_request_sha256 !== hash) throw new Error("创建身份未确认，原意图保留。");
    await removeMemoryIntent(activityId); await removeMemoryDraft(draftId); return result;
  } catch (reason) {
    await updateMemoryIntent(activityId, reason instanceof api.MemoryApiError && reason.status > 0 ? "refused" : "unconfirmed");
    throw reason;
  }
}
