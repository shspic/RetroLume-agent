/** TASK-059 进程身份辅助（只读查询 + 身份核验 + 已核验停止）。
 *
 * 所有权规则（本卡只处理自有资源）：
 * - 每条记录 = (PID, 创建时间) + 名称/命令行摘要 + 来源；创建时间在同一台机器上对同一进程稳定，
 *   因此"同一PID但创建时间不同"只可能是PID被复用，属于别的进程，一律不视为本卡资源、不停止。
 * - 只停止"已核验身份"的记录；没有创建时间或身份不符的记录只记录、不停止。
 * - 不按端口杀进程、不按裸PID杀进程、不按名称杀进程。
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

export function createdMatches(a, b) {
  if (!a || !b) return false;
  if (String(a) === String(b)) return true;
  const ta = Date.parse(a), tb = Date.parse(b);
  return Number.isFinite(ta) && Number.isFinite(tb) && Math.abs(ta - tb) <= 1_000;
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

export function mergeRecords(list, rec) {
  if (!rec || !Number.isInteger(rec.pid)) return;
  const key = `${rec.pid}`;
  const hit = list.find(x => `${x.pid}` === key);
  if (!hit) { list.push(rec); return; }
  if (!hit.created && rec.created) { hit.created = rec.created; hit.name = hit.name ?? rec.name; }
  if (hit.source !== rec.source && !hit.sources) hit.sources = [hit.source, rec.source];
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
