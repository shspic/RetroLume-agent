/** TASK-059/TASK-061 进程身份辅助（只读查询 + 身份核验 + 已核验停止）。
 *
 * 身份与归属是两件事（TASK-061 明确）：
 * - 身份 = (PID, 创建时间) 无损规范化后精确相等。创建时间比对**无任何容差**；未知或不匹配一律
 *   视为"身份未知/不是本卡资源"，既不停止、也不能据此宣布已停止。
 * - 归属必须来自本次直接 spawn，或已核实自有父进程的后代链；端口/监听观察只作诊断，永不产生归属。
 * - 同一PID的不同创建时间 = 不同代次（PID被复用），按 (PID, 创建时间) 分别保存，绝不只按PID合并。
 * - 只停止"已核验身份的自有记录"；不按端口杀进程、不按裸PID杀进程、不按名称杀进程。
 *
 * 查询实际由 tests/task059_proc.ps1 完成（只读，输出JSON）。
 */
import { spawnSync } from "node:child_process";
import { existsSync } from "node:fs";
import { join } from "node:path";

export const PROC_PS1 = join(import.meta.dirname, "task059_proc.ps1");
const POWERSHELL = "powershell.exe";

/** 工具文件是否存在（预检用；缺失即阻塞，不静默降级）。 */
export function procToolPresent() {
  return existsSync(PROC_PS1);
}

function psJson(args, { timeoutMs = 30_000 } = {}) {
  const r = spawnSync(POWERSHELL, ["-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass", "-File", PROC_PS1, ...args], {
    encoding: "utf8", timeout: timeoutMs, windowsHide: true, maxBuffer: 64 * 1024 * 1024,
  });
  if (r.error) throw new Error(`进程查询工具执行失败: ${r.error.message}`);
  if (r.status !== 0) throw new Error(`进程查询工具退出码 ${String(r.status)}: ${String(r.stderr ?? "").trim().slice(0, 400)}`);
  const out = String(r.stdout ?? "").trim();
  if (!out) return [];
  const parsed = JSON.parse(out);
  return Array.isArray(parsed) ? parsed : [parsed];
}

/** 按PID查询（只返回存在的进程）。查询失败抛错：调用方必须按"未知"处理，不得当作"已停止"。 */
export function queryPids(pids) {
  const ids = [...new Set(pids.map(Number).filter(Number.isInteger).filter(n => n > 0))];
  if (!ids.length) return [];
  return psJson(["-Mode", "query", "-Pids", ids.join(",")]);
}

/** 递归查询以 rootPid 为根的当前后代。 */
export function descendants(rootPid) {
  return psJson(["-Mode", "descendants", "-RootPid", String(rootPid)]);
}

/** 命令行包含 match 的进程（大小写不敏感）。match 必须是本次运行唯一的标记。 */
export function findByCmd(match) {
  if (!match) return [];
  return psJson(["-Mode", "find", "-CmdMatch", match]);
}

/** 监听本机端口的进程（用于证据与交叉核对；其结果不作为杀进程依据）。 */
export function portOwner(port) {
  return psJson(["-Mode", "portowner", "-Port", String(port)]);
}

/** 创建时间无损规范化：只统一语法（分隔符空格→T、逗号小数点→点、结尾z→Z、去首尾空白），
 * 不删减任何数字位、不四舍五入、不做时区换算。空值或无法规范化返回 null（调用方按"身份未知"处理）。 */
export function normalizeCreated(value) {
  if (value === null || value === undefined) return null;
  const s = String(value).trim();
  if (!s) return null;
  return s
    .replace(/^(\d{4}-\d{2}-\d{2})[ tT](\d{2}:\d{2}:\d{2})/, "$1T$2")
    .replace(/,(\d)/, ".$1")
    .replace(/[zZ]$/, "Z");
}

/** 身份一致性：同一创建时间经无损规范化后必须精确相等；无容差、未知即false。 */
export function createdMatches(a, b) {
  const ka = normalizeCreated(a);
  const kb = normalizeCreated(b);
  return ka !== null && kb !== null && ka === kb;
}

/** 由查询行生成身份记录。owned=false 的记录只登记不停止。 */
export function toRecord(row, { source, owned = true, extra = {} } = {}) {
  return {
    pid: Number(row.pid),
    created: row.created ?? null,
    name: row.name ?? null,
    cmd_tail: String(row.cmd ?? "").slice(0, 200),
    source, owned: !!owned, ...extra,
  };
}

/** 代次键：(PID, 创建时间规范化值)；创建时间未知的记录单独成一档，不与已知身份的同PID记录合并。 */
export function recordKey(rec) {
  const created = normalizeCreated(rec?.created);
  return `${Number(rec?.pid)}|${created === null ? "created-unknown" : created}`;
}

export function mergeRecords(list, rec) {
  if (!rec || !Number.isInteger(rec.pid)) return;
  const key = recordKey(rec);
  const hit = list.find(x => recordKey(x) === key);
  if (!hit) { list.push(rec); return; }
  hit.name = hit.name ?? rec.name;
  hit.cmd_tail = hit.cmd_tail || rec.cmd_tail;
  if (hit.source !== rec.source) {
    if (!Array.isArray(hit.sources)) hit.sources = [hit.source];
    if (!hit.sources.includes(rec.source)) hit.sources.push(rec.source);
  }
}

/**
 * 分类记录：alive=仍存活且身份一致；gone=已不存在；reused=PID已被别的进程占用（本卡资源视为已退出）；
 * unverified=仍存活但无创建时间或查询失败之外的身份依据（不得停止，也不得据此判定已停止）。
 */
export function classifyRecords(records, { timeoutMs = 30_000 } = {}) {
  const usable = records.filter(r => r && Number.isInteger(r.pid));
  const ids = [...new Set(usable.map(r => r.pid))];
  const rows = ids.length ? queryPids(ids) : [];
  const byPid = new Map(rows.map(r => [Number(r.pid), r]));
  const alive = [], gone = [], reused = [], unverified = [];
  for (const rec of usable) {
    const row = byPid.get(rec.pid);
    if (!row) { gone.push({ rec }); continue; }
    if (!rec.created) { unverified.push({ rec, row }); continue; }
    if (createdMatches(row.created, rec.created)) alive.push({ rec, row });
    else reused.push({ rec, row });
  }
  return { alive, gone, reused, unverified };
}

/** 核验身份一致后停止该进程树（taskkill /T /F）；身份不符或已不存在则不动。 */
export function killVerified(rec, { timeoutMs = 20_000 } = {}) {
  const rows = queryPids([rec.pid]);
  const row = rows.find(r => Number(r.pid) === Number(rec.pid));
  if (!row) return { pid: rec.pid, action: "skip-not-alive", stopped: false };
  if (!rec.created || !createdMatches(row.created, rec.created)) {
    return { pid: rec.pid, action: "skip-identity-mismatch(不视为本卡资源)", stopped: false, observed_created: row.created ?? null };
  }
  const r = spawnSync("taskkill", ["/PID", String(rec.pid), "/T", "/F"], { encoding: "utf8", timeout: timeoutMs, windowsHide: true });
  return {
    pid: rec.pid, action: "taskkill /PID /T /F", stopped: true,
    exit_code: r.status ?? null, stderr: String(r.stderr ?? "").trim().slice(0, 300),
  };
}

export function syncSleep(ms) {
  Atomics.wait(new Int32Array(new SharedArrayBuffer(4)), 0, false, ms);
}
