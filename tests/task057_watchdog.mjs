/** TASK-057 独立看门狗（经TASK-059定向修正）：期限监督 + 本卡自有资源的安全收束。
 *
 * 用法：node task057_watchdog.mjs <supervision-state.json>
 * 所有伴生文件都放在状态文件同一目录（由主脚本给出，每次运行唯一）。
 *
 * 就绪握手（TASK-059 修正1）：
 * - 启动先自检进程身份查询工具（tests/task059_proc.ps1）；失败即写 ready 文件
 *   {helper_ok:false} 并以退出码3退出——主脚本据此在创建任何资源前停止。
 * - 读到含可用期限的状态后写 task057-watchdog-ready.json（含本进程PID与采纳的剩余预算），
 *   主脚本确认PID一致且 helper_ok 为真后才启动自有资源。
 *
 * 心跳：每2秒原子写 task057-watchdog-heartbeat.json（本进程单调毫秒+序号），主脚本据此
 * 判定监督是否失联；主脚本的读写一律"临时文件+改名"，本看门狗读取失败时沿用最后有效状态，
 * 不因半写JSON丢掉最后有效的所有权与截止信息。
 *
 * 触发（TASK-059 修正2）：挂钟超过 deadline_at，或自采纳起的单调耗时超过采纳的剩余预算
 * （系统时钟回拨不延长看门狗），或主脚本声明 cleanup_incomplete（未确认停止）。
 * 触发时只处理状态中登记/标记的本卡资源（TASK-059 修正3、4；TASK-061 归属链收缩）：
 * - 应用：状态中已认领（owned !== false）且(PID,创建时间)精确一致的记录；身份一致才停止。
 *   已认领但身份未知（无创建时间）的仍存活记录**进入 unresolved**（不停止、也不当作已停止）。
 *   PID被别的进程复用（创建时间不符）的记录视为已退出，只在 left_alone 里记录，绝不动该PID。
 *   8000端口的监听观察只作诊断：不属于已认领记录的监听者只旁观不停止，但会进入 unresolved
 *   （本次无法确认应用端口已释放）。
 * - 测试浏览器：已认领记录，或命令行含本次唯一 --user-data-dir 标记的 msedge。
 * - 容器：停止之前必须同时通过"本次运行标签 + 本次运行容器名 + 已核实ID"；核对不过就不停止并记
 *   unresolved；不存在则视为已停止。绝不按裸ID或裸名称停止其他容器（含历史保留容器）。
 * 未解决的资源在硬上限内重试；仍不解决则如实写 task057-watchdog-fired.json 后退出（退出码1）。
 *
 * 有界自保：30秒内拿不到可用状态与期限即退出（退出码3），不再长时间空等；
 * 采纳期限后的硬上限=采纳的剩余预算+5分钟应急宽限。
 * finished=true（主脚本确认全部自有资源已停止）是唯一的正常解除信号，退出码0。
 * 不按端口杀未知进程、不按裸PID杀进程、不删除任何文件、除本卡容器外不做其他Docker操作。
 */
import { appendFileSync, readFileSync, renameSync, writeFileSync } from "node:fs";
import { spawnSync } from "node:child_process";
import { dirname, join } from "node:path";
import { classifyRecords, findByCmd, killVerified, portOwner, procToolPresent, queryPids, syncSleep } from "./task059_proc_tree.mjs";

const stateFile = process.argv[2];
if (!stateFile) { console.error("usage: node task057_watchdog.mjs <supervision-state.json>"); process.exit(2); }
const dir = dirname(stateFile);
const readyFile = join(dir, "task057-watchdog-ready.json");
const heartbeatFile = join(dir, "task057-watchdog-heartbeat.json");
const firedFile = join(dir, "task057-watchdog-fired.json");
const eventLog = join(dir, "task057-watchdog-events.log");

const monoStart = process.hrtime.bigint();
const monoMs = () => Number(process.hrtime.bigint() - monoStart) / 1e6;
const NO_STATE_GRACE_MS = 30_000;          // 拿不到可用状态/可用期限的有限自保，不再空等45分钟
const EMERGENCY_GRACE_MS = 5 * 60_000;     // 采纳期限后的应急宽限（重试用）
const RETRY_INTERVAL_MS = 15_000;

function writeJsonAtomic(path, obj) {
  const tmp = `${path}.tmp-${process.pid}`;
  writeFileSync(tmp, JSON.stringify(obj, null, 2));
  renameSync(tmp, path);
}
function logEvent(entry) {
  try { appendFileSync(eventLog, `${new Date().toISOString()} ${JSON.stringify(entry)}\n`); } catch { }
}
function dockerSpawn(args, timeoutMs) {
  const r = spawnSync("docker", args, { encoding: "utf8", timeout: timeoutMs, windowsHide: true, maxBuffer: 8 * 1024 * 1024 });
  return { code: r.status ?? null, stdout: String(r.stdout ?? ""), stderr: String(r.stderr ?? ""), error: r.error ? r.error.message : null };
}
let heartbeatSeq = 0;
/** 心跳：主脚本据此判断监督是否失联；收尾重试期间也持续推进，避免被误判为失联。 */
function writeHeartbeat(state, extra = {}) {
  heartbeatSeq++;
  try {
    writeJsonAtomic(heartbeatFile, {
      pid: process.pid, seq: heartbeatSeq, at: new Date().toISOString(),
      mono_ms: Math.round(monoMs()), run_tag: state?.run_tag ?? null, ...extra,
    });
  } catch { }
}

let lastValidState = null;
/** 读取状态：文件缺失或半写JSON时沿用最后有效状态，不丢所有权与截止信息。 */
function readState() {
  let raw;
  try { raw = readFileSync(stateFile, "utf8"); } catch { return lastValidState; }
  let parsed;
  try { parsed = JSON.parse(raw); } catch { return lastValidState; }
  if (!parsed || typeof parsed !== "object") return lastValidState;
  lastValidState = parsed;
  return parsed;
}

/** 采纳期限：挂钟绝对截止与"预算-已用挂钟"取小，再转成本进程的单调截止。回拨不延长。 */
function adoptDeadline(state) {
  const budgetMs = Number(state?.budget_ms);
  const startedAt = Date.parse(state?.started_at ?? "");
  const deadlineWall = Date.parse(state?.deadline_at ?? "");
  const byWall = Number.isFinite(deadlineWall) ? deadlineWall - Date.now() : Infinity;
  const byBudget = Number.isFinite(startedAt) && Number.isFinite(budgetMs) ? budgetMs - (Date.now() - startedAt) : Infinity;
  const remaining = Math.min(byWall, byBudget);
  if (!Number.isFinite(remaining)) return null;
  return { remaining_ms: Math.max(0, Math.round(remaining)), deadline_at: state?.deadline_at ?? null, basis: { by_wall_ms: Number.isFinite(byWall) ? Math.round(byWall) : null, by_budget_ms: Number.isFinite(byBudget) ? Math.round(byBudget) : null } };
}

/** 停止状态中登记的本卡自有资源；只处理身份可核验的记录。 */
function stopRegisteredResources(state, reason) {
  const actions = [], unresolved = [], leftAlone = [];

  // 1) 自有应用进程树：只认状态中已认领（owned !== false）的记录；端口观察不在此列
  const appRecords = [...(state?.app?.tree ?? [])]
    .filter(r => r && r.owned !== false && Number.isInteger(Number(r.pid)));
  let appClass = null;
  try { appClass = classifyRecords(appRecords); }
  catch (e) { unresolved.push({ resource: "app", kind: "query-failed", reason: `进程查询失败，无法确认停止状态: ${e.message}` }); }
  if (appClass) {
    for (const { rec } of appClass.alive) actions.push({ resource: "app", ...killVerified(rec) });
    for (const { rec } of appClass.unverified) {
      // 已认领但身份未知仍存活：不停止（无法与PID复用区分），按未确认上报（不得当作已停止）
      actions.push({ resource: "app", pid: rec.pid, action: "skip-identity-unknown(不停止)" });
      unresolved.push({ resource: "app", pid: rec.pid, kind: "claimed-identity-unknown", reason: "已认领但创建时间未知；不停止，停止状态未确认" });
    }
    for (const { rec, row } of appClass.reused) {
      actions.push({ resource: "app", pid: rec.pid, action: "skip-pid-reused(创建时间不符)", observed_created: row.created ?? null });
      leftAlone.push({ resource: "app", pid: rec.pid, reason: "该PID现在属于别的进程（创建时间不符）；本卡记录视为已退出，不动该PID" });
    }
    try {
      const recheck = classifyRecords(appRecords);
      for (const { rec } of recheck.alive) unresolved.push({ resource: "app", pid: rec.pid, name: rec.name ?? null, source: rec.source ?? null, kind: "still-alive-after-stop" });
    } catch (e) { unresolved.push({ resource: "app", kind: "recheck-failed", reason: `停止后复核失败: ${e.message}` }); }
  }

  // 1b) 端口诊断（不产生归属）：8000上仍有不属于已认领记录的监听者 → 只旁观，但记为未确认
  const appPort = Number(state?.app_port ?? 0);
  if (appPort > 0) {
    try {
      const listeners = portOwner(appPort).map(r => ({ pid: Number(r.pid), name: r.name ?? null, created: r.created ?? null }));
      const unclaimed = listeners.filter(l => !appRecords.some(r => Number(r.pid) === l.pid));
      if (listeners.length) actions.push({ resource: "port", action: "observe", port: appPort, listeners: listeners.map(l => ({ pid: l.pid, name: l.name })) });
      for (const l of unclaimed) {
        unresolved.push({ resource: "port", port: appPort, pid: l.pid, name: l.name, kind: "unclaimed-listener-not-stopped", reason: "不能证明归属：只旁观不停止，端口未确认释放" });
      }
    } catch (e) { unresolved.push({ resource: "port", kind: "observation-failed", reason: `端口观察失败: ${e.message}` }); }
  }

  // 2) 测试浏览器：已核验记录 + 命令行含本次唯一profile目录的msedge
  const profile = state?.browser?.profile_dir ?? null;
  const browserRecords = [...(state?.browser?.tree ?? [])].filter(r => r && Number.isInteger(Number(r.pid)));
  if (profile) {
    try {
      for (const row of findByCmd(profile)) browserRecords.push({ pid: Number(row.pid), created: row.created ?? null, name: row.name ?? null, source: "cmdline-profile-marker", owned: true });
    } catch (e) { unresolved.push({ resource: "browser", reason: `按profile标记查询失败: ${e.message}` }); }
  }
  if (browserRecords.length) {
    const seen = new Set();
    const unique = browserRecords.filter(r => (seen.has(r.pid) ? false : (seen.add(r.pid), true)));
    try {
      const bClass = classifyRecords(unique);
      for (const { rec } of bClass.alive) actions.push({ resource: "browser", ...killVerified(rec) });
      for (const { rec } of bClass.unverified) leftAlone.push({ resource: "browser", pid: rec.pid, reason: "缺创建时间，身份不可核验，不停止" });
      const recheck = classifyRecords(unique);
      for (const { rec } of recheck.alive) unresolved.push({ resource: "browser", pid: rec.pid, name: rec.name ?? null });
    } catch (e) { unresolved.push({ resource: "browser", reason: `浏览器进程核对失败: ${e.message}` }); }
  }

  // 3) 容器：停止前必须同时通过"本次运行标签 + 本次运行容器名 + 已核实ID"；核对不过不停止
  const cont = state?.container ?? {};
  const ref = cont.id ?? (cont.expect || cont.name ? cont.name : null);
  if (ref) {
    const probe = dockerSpawn(["inspect", ref], 30_000);
    if (probe.error) {
      unresolved.push({ resource: "container", kind: "inspect-unavailable", reason: `docker inspect 无法执行（Docker不可用？）: ${probe.error}` });
    } else if (probe.code !== 0) {
      const err = `${probe.stderr}\n${probe.stdout}`;
      if (/no such (object|container)/i.test(err)) actions.push({ resource: "container", action: "inspect", result: "absent", ref });
      else unresolved.push({ resource: "container", kind: "inspect-error", reason: `docker inspect 失败(exit=${probe.code})，不能断定容器状态: ${err.trim().slice(0, 300)}` });
    } else {
      let info = null;
      try { info = JSON.parse(probe.stdout)[0]; } catch (e) { unresolved.push({ resource: "container", kind: "inspect-parse-failed", reason: `docker inspect 输出不可解析: ${e.message}` }); }
      if (info) {
        const problems = [];
        const label = String(info?.Config?.Labels?.["retrolume-run"] ?? "");
        const name = String(info?.Name ?? "").replace(/^\//, "");
        if (!cont.run_label || label !== cont.run_label) problems.push(`运行标签 ${label || "(空)"} 不是本次运行标记 ${cont.run_label || "(空)"}`);
        if (cont.name && name !== cont.name) problems.push(`容器名 ${name || "(空)"} 不是本次运行容器名 ${cont.name}`);
        if (cont.id && info?.Id !== cont.id) problems.push(`容器ID ${info?.Id ?? "(空)"} 不是已核实的本次容器ID ${cont.id}`);
        if (problems.length) {
          actions.push({ resource: "container", action: "skip-stop(标签/ID核对不过，未停止)", detail: problems });
          if (!cont.id) {
            // 无已核实ID且标签不符：不是本次运行创建的容器，只旁观
            leftAlone.push({ resource: "container", reason: "同名容器不带本次运行标签，不是本次资源，未停止", detail: problems });
          } else {
            unresolved.push({ resource: "container", kind: "ownership-mismatch-not-stopped", detail: problems, observed_id: info?.Id ?? null });
          }
        } else if (info?.State?.Running === false) {
          actions.push({ resource: "container", action: "already-stopped", id: info.Id });
        } else {
          const stop = dockerSpawn(["stop", "--time", "5", info.Id], 60_000);
          actions.push({ resource: "container", action: "docker stop --time 5", id: info.Id, exit_code: stop.code, error: stop.error ?? (stop.stderr.trim().slice(0, 200) || null) });
          let ok = false;
          for (let i = 0; i < 10 && !ok; i++) {
            syncSleep(1_000);
            const re = dockerSpawn(["inspect", "-f", "{{.State.Running}}", info.Id], 20_000);
            if (re.code === 0 && re.stdout.trim() === "false") ok = true;
          }
          if (ok) actions.push({ resource: "container", action: "stop-confirmed", id: info.Id });
          else unresolved.push({ resource: "container", id: info.Id, kind: "stop-unconfirmed", reason: "docker stop 后未在限时内确认停止" });
        }
      }
    }
  }

  return { reason, actions, unresolved, left_alone: leftAlone };
}

/** 触发：停止已登记自有资源；未解决则在硬上限内重试，仍不解决则如实记录后退出。 */
function fire(state, reason, hardCapMono) {
  const attempts = [];
  for (let attempt = 1; ; attempt++) {
    writeHeartbeat(state, { firing: true, fire_reason: reason, attempt });
    let outcome;
    try { outcome = stopRegisteredResources(state, reason); }
    catch (e) { outcome = { reason, actions: [], unresolved: [{ resource: "all", reason: `停止过程异常: ${e.message}` }], left_alone: [] }; }
    attempts.push({ attempt, at: new Date().toISOString(), mono_ms: Math.round(monoMs()), ...outcome });
    try {
      writeJsonAtomic(firedFile, {
        fired_at: new Date().toISOString(), reason, deadline_at: state?.deadline_at ?? null,
        run_tag: state?.run_tag ?? null, attempts,
      });
    } catch (e) { logEvent({ event: "fired-file-write-failed", error: String(e.message) }); }
    logEvent({ event: "fired", reason, attempt, unresolved: outcome.unresolved.length, left_alone: outcome.left_alone.length });
    if (!outcome.unresolved.length) process.exit(1);
    if (monoMs() > hardCapMono) {
      logEvent({ event: "hard-cap-with-unresolved", unresolved: outcome.unresolved });
      process.exit(1);
    }
    syncSleep(RETRY_INTERVAL_MS);
  }
}

function main() {
  if (!procToolPresent()) {
    writeJsonAtomic(readyFile, { pid: process.pid, helper_ok: false, fatal: "tests/task059_proc.ps1 缺失，进程身份无法核验", at: new Date().toISOString() });
    logEvent({ event: "exit-no-helper" });
    process.exit(3);
  }
  try {
    const self = queryPids([process.pid]);
    if (!self.some(r => Number(r.pid) === process.pid && r.created)) throw new Error("自检未返回本进程创建时间");
  } catch (e) {
    writeJsonAtomic(readyFile, { pid: process.pid, helper_ok: false, fatal: `进程身份查询工具自检失败: ${e.message}`, at: new Date().toISOString() });
    logEvent({ event: "exit-helper-self-check-failed", error: String(e.message) });
    process.exit(3);
  }

  let adopted = null;
  for (;;) {
    const state = readState();
    writeHeartbeat(state, { adopted: !!adopted });

    if (state) {
      if (state.finished === true && state.cleanup_incomplete !== true) {
        logEvent({ event: "release-seen-finished" });
        process.exit(0);
      }
      if (!adopted) {
        const a = adoptDeadline(state);
        if (a) {
          adopted = { ...a, at_mono: monoMs() };
          writeJsonAtomic(readyFile, {
            pid: process.pid, helper_ok: true, adopted_remaining_ms: a.remaining_ms,
            deadline_at: a.deadline_at, basis: a.basis, run_tag: state.run_tag ?? null, at: new Date().toISOString(),
          });
          logEvent({ event: "adopted-deadline", remaining_ms: a.remaining_ms });
        }
      }
    }

    if (state && state.cleanup_incomplete === true) {
      fire(state, "cleanup-incomplete(主脚本声明停止未全部确认)", (adopted ? adopted.at_mono + adopted.remaining_ms : monoMs()) + EMERGENCY_GRACE_MS);
    }

    if (state && adopted) {
      const hardCapMono = adopted.at_mono + adopted.remaining_ms + EMERGENCY_GRACE_MS;
      const monoLeft = adopted.remaining_ms - (monoMs() - adopted.at_mono);
      const deadlineWall = Date.parse(state.deadline_at ?? "");
      const wallHit = Number.isFinite(deadlineWall) && Date.now() > deadlineWall;
      if (monoLeft <= 0 || wallHit) {
        fire(state, monoLeft <= 0 ? "monotonic-deadline(单调耗时到期限；时钟回拨不延长)" : "wall-deadline(挂钟绝对截止)", hardCapMono);
      }
      if (monoMs() > hardCapMono) fire(state, "hard-cap(期限后应急宽限已用尽)", hardCapMono);
    }
    // 拿不到可用期限（状态缺失、半写且无最后有效状态、或期限字段不可解析）→ 有限宽限后退出，
    // 不存在"状态坏了还能空等45分钟"的路径。
    if (!adopted && monoMs() > NO_STATE_GRACE_MS) {
      writeJsonAtomic(firedFile, {
        fired_at: new Date().toISOString(),
        reason: state ? "no-usable-deadline-within-30s" : "no-valid-state-within-30s",
        deadline_at: state?.deadline_at ?? null, attempts: [],
      });
      logEvent({ event: "exit-no-usable-deadline", waited_ms: Math.round(monoMs()), had_state: !!state });
      process.exit(3);
    }
    syncSleep(2_000);
  }
}

main();
