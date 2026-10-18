/** TASK-057 独立看门狗：绝对期限监督，只处理状态文件中登记的本卡自有资源。
 *
 * 用法：node task057_watchdog.mjs <supervision-state.json>
 * 行为：
 * - 每2秒读取状态文件；发现 finished=true 即正常退出（退出码0）。
 * - 超过 deadline_at 仍未结束：对登记的 app_pid 执行 taskkill /T /F（仅自有进程树）、
 *   对登记的 container_id 执行 docker stop --time 5（仅自有容器），写 watchdog-fired.json 后以退出码1退出。
 * - 状态文件缺失/损坏时持续等待，但最长45分钟后自保退出（退出码1），避免无限驻留。
 * 不读取其他资源、不做其他Docker操作、不删除任何文件。
 */
import { readFileSync, writeFileSync } from "node:fs";
import { spawnSync } from "node:child_process";
import { join, dirname } from "node:path";

const stateFile = process.argv[2];
if (!stateFile) { console.error("usage: node task057_watchdog.mjs <supervision-state.json>"); process.exit(2); }
const firedFile = join(dirname(stateFile), "task057-watchdog-fired.json");
const watchdogStart = Date.now();
const MAX_WATCH_MS = 45 * 60_000;

function readState() {
  try { return JSON.parse(readFileSync(stateFile, "utf8")); } catch { return null; }
}

function syncSleep(ms) {
  Atomics.wait(new Int32Array(new SharedArrayBuffer(4)), 0, false, ms);
}

while (true) {
  const state = readState();
  if (state?.finished) process.exit(0);
  const deadline = Date.parse(state?.deadline_at ?? "");
  if (Number.isFinite(deadline) && Date.now() > deadline) {
    const actions = [];
    if (state?.app_pid) {
      const tk = spawnSync("taskkill", ["/PID", String(state.app_pid), "/T", "/F"], { encoding: "utf8", windowsHide: true, timeout: 30_000 });
      actions.push({ action: "taskkill /T /F app tree", pid: state.app_pid, exit_code: tk.status ?? null });
    }
    if (state?.container_id) {
      const stop = spawnSync("docker", ["stop", "--time", "5", state.container_id], { encoding: "utf8", windowsHide: true, timeout: 60_000 });
      actions.push({ action: "docker stop --time 5 container", id: state.container_id, exit_code: stop.status ?? null });
    }
    writeFileSync(firedFile, JSON.stringify({ fired_at: new Date().toISOString(), deadline_at: state?.deadline_at ?? null, actions }, null, 2));
    process.exit(1);
  }
  if (Date.now() - watchdogStart > MAX_WATCH_MS) {
    try {
      writeFileSync(firedFile, JSON.stringify({ fired_at: new Date().toISOString(), reason: "watchdog self-timeout without state file completion", deadline_at: state?.deadline_at ?? null, actions: [] }, null, 2));
    } catch {}
    process.exit(1);
  }
  syncSleep(2_000);
}
