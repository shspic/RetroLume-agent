"use strict";
// 仅本卡固定可信程序：有限临时目录核验，再进入原镜像counter。
const fs = require("node:fs");
const path = require("node:path");
const crypto = require("node:crypto");
const util = require("node:util");
process.env.DEBUG = "pw:browser";
process.env.DEBUG_COLORS = "0";
const debug = require("/opt/preview/vendor/playwright-core/lib/utilsBundle.js").debug;
debug.log = (...values) => process.stderr.write(util.format(...values) + "\n");
debug.enable("pw:browser");
const host = require("/opt/preview/host.cjs");
const followup_parent_dir = "";
const runtime_env = {
  HOME: "/home/preview",
  XDG_CONFIG_HOME: "/home/preview/.config",
  XDG_CACHE_HOME: "/home/preview/.cache",
  XDG_RUNTIME_DIR: "/home/preview/.runtime",
  TMPDIR: "/tmp/task109-private"
};
function inspectDirectory(directory, expectedMode, initialize) {
  if (initialize) fs.mkdirSync(directory, { recursive: true, mode: 0o700 });
  const stat = fs.statSync(directory);
  const result = { path: directory, uid: stat.uid, gid: stat.gid, mode: (stat.mode & 0o7777).toString(8), is_directory: stat.isDirectory() };
  if (!stat.isDirectory() || stat.uid !== 10001 || stat.gid !== 10001 || (stat.mode & 0o7777) !== expectedMode) throw Object.assign(new Error("目录归属或模式不符"), { code: "DIRECTORY_IDENTITY", directory, observed: result });
  const probe = path.join(directory, "task109-write-" + crypto.randomBytes(8).toString("hex"));
  fs.writeFileSync(probe, Buffer.from("TASK109"), { flag: "wx", mode: 0o600 });
  const written = fs.statSync(probe);
  result.write_probe = { path: probe, bytes: written.size, uid: written.uid, gid: written.gid, mode: (written.mode & 0o7777).toString(8), exclusive_success: written.size === 7 };
  return result;
}
try {
  if (process.getuid() !== 10001 || process.getgid() !== 10001) throw new Error("固定非root身份不符");
  for (const [name, value] of Object.entries(runtime_env)) if (process.env[name] !== value) throw new Error("选定运行目录环境不一致: " + name);
  host.emit("runtime_environment", { uid: process.getuid(), gid: process.getgid(), selected_environment: runtime_env, debug_category: "pw:browser", debug_sink: "stderr" });
  host.emit("runtime_directory", inspectDirectory("/tmp", 0o1777, false));
  for (const directory of Object.values(runtime_env)) host.emit("runtime_directory", inspectDirectory(directory, 0o700, directory !== "/home/preview"));
  if (followup_parent_dir) {
    const allowed = ["/home/preview/.config/chromium/Crash Reports", "/home/preview/.config/google-chrome/Crash Reports", "/home/preview/.config/google-chrome-for-testing/Crash Reports", "/home/preview/.config/microsoft-edge/Crash Reports"];
    if (!allowed.includes(followup_parent_dir)) throw new Error("复验目录不在固定白名单");
    host.emit("runtime_directory_followup", inspectDirectory(followup_parent_dir, 0o700, true));
  }
  host.emit("bootstrap_ready", { original_counter: "/opt/preview/h0-counter.cjs", image_bytes_changed: false, no_probe_file_delete: true });
  require("/opt/preview/h0-counter.cjs");
} catch (error) {
  host.emit("terminal", { verdict: "ERROR", phase: "runtime_directory_bootstrap", message: String(error.message).slice(0, 1000), code: error.code ?? null, directory: error.directory ?? null, observed: error.observed ?? null });
  setInterval(() => {}, 1000);
}
