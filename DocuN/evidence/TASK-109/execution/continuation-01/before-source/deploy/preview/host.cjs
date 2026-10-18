"use strict";
// 本模块仅承载关口反例，未实现或声明全协议导航否决器。
const fs = require("node:fs");
const crypto = require("node:crypto");
const pw = require("./vendor/playwright-core");
let sequence = 0;
function sha(bytes) { return crypto.createHash("sha256").update(bytes).digest("hex"); }
async function shaFile(path) {
  const hash = crypto.createHash("sha256");
  for await (const chunk of fs.createReadStream(path)) hash.update(chunk);
  return hash.digest("hex");
}
function emit(kind, data) {
  const body = Buffer.from(JSON.stringify({ kind, data }), "utf8");
  if (body.length > 4096) throw new Error("关口观测超过有限上界");
  const header = Buffer.from(JSON.stringify({ protocol: "retrolume.preview.h0.v1", type: "observation", seq: ++sequence, body_bytes: body.length, body_sha256: sha(body) }), "utf8");
  const prefix = Buffer.alloc(4); prefix.writeUInt32BE(header.length);
  process.stdout.write(Buffer.concat([prefix, header, body]));
}
function processFacts() {
  const rows = [];
  for (const name of fs.readdirSync("/proc")) {
    if (!/^[0-9]+$/.test(name)) continue;
    try {
      const raw = fs.readFileSync(`/proc/${name}/status`, "utf8");
      const row = { pid: Number(name) };
      for (const field of ["Name", "PPid", "Uid", "NoNewPrivs", "Seccomp", "NSpid"]) {
        const line = raw.split("\n").find(item => item.startsWith(field + ":"));
        if (line) row[field] = line.slice(field.length + 1).trim();
      }
      rows.push(row);
    } catch { /* 进程消失不冒读到当前状态。 */ }
  }
  return { own_uid: process.getuid(), own_gid: process.getgid(), node: process.version, kernel: require("node:os").release(), pid_namespace: fs.readlinkSync("/proc/self/ns/pid"), init_namespace: fs.readlinkSync("/proc/1/ns/pid"), rows };
}
async function launch() {
  const executable = pw.chromium.executablePath();
  emit("load_identity", { node: process.version, package: require("./vendor/playwright-core/package.json").version, executable, executable_sha256: await shaFile(executable), input_manifest_sha256: sha(fs.readFileSync("/opt/preview/input-manifest.json")) });
  const browser = await pw.chromium.launch({ executablePath: executable, headless: true, chromiumSandbox: true, ignoreDefaultArgs: ["--disable-popup-blocking"], timeout: 8000 });
  const cdp = await browser.newBrowserCDPSession();
  const version = await cdp.send("Browser.getVersion");
  const command = await cdp.send("Browser.getBrowserCommandLine");
  emit("browser_identity", { version, arguments: command.arguments });
  if (browser.version() !== "151.0.7922.34" || process.getuid() !== 10001 || command.arguments.includes("--no-sandbox")) throw new Error("固定版本或非root sandbox身份不符");
  await cdp.send("Target.setDiscoverTargets", { discover: true });
  const targetEvents = [];
  cdp.on("Target.targetCreated", event => targetEvents.push({ kind: "created", type: event.targetInfo.type, id: event.targetInfo.targetId, url: event.targetInfo.url.slice(0, 256) }));
  cdp.on("Target.targetDestroyed", event => targetEvents.push({ kind: "destroyed", id: event.targetId }));
  return { browser, cdp, targetEvents };
}
async function context(browser) {
  const value = await browser.newContext({ viewport: { width: 640, height: 480 }, deviceScaleFactor: 1, serviceWorkers: "block", acceptDownloads: false });
  await value.route(() => true, route => route.abort());
  await value.routeWebSocket(() => true, socket => socket.close());
  return value;
}
async function loadFrame(value, html, control = false) {
  const page = await value.newPage();
  page.on("dialog", dialog => dialog.dismiss());
  await page.setContent(fs.readFileSync("/opt/preview/wrapper.html", "utf8"));
  // 仅私有无害对照授popup，其参数不进入产品HTTP或模型协议。
  await page.evaluate(({ html, control }) => {
    const frame = document.createElement("iframe");
    frame.id = "h0_frame";
    frame.setAttribute("sandbox", control ? "allow-scripts allow-popups" : "allow-scripts");
    frame.srcdoc = html;
    document.body.appendChild(frame);
  }, { html, control });
  const element = await page.$("#h0_frame");
  const frame = await element.contentFrame();
  await frame.waitForSelector("#h0_ready", { timeout: 2000 });
  return { page, frame };
}
async function snapshot(value, cdp) {
  const targets = (await cdp.send("Target.getTargets")).targetInfos.filter(row => ["page", "iframe"].includes(row.type)).map(row => ({ id: row.targetId, type: row.type, url: row.url.slice(0, 256) }));
  const pages = value.pages().map(page => ({ url: page.url().slice(0, 256), frames: page.frames().map(frame => ({ url: frame.url().slice(0, 256), parent: frame.parentFrame() !== null })) }));
  return { targets, pages };
}
async function trustedClick(page, frame, id) {
  const item = frame.locator("#" + id);
  const box = await item.boundingBox({ timeout: 2000 });
  if (!box) throw new Error("真实按钮没有可见位置");
  const x = box.x + box.width / 2; const y = box.y + box.height / 2;
  if (x < 0 || x >= 640 || y < 0 || y >= 480) throw new Error("输入坐标越界");
  emit("trusted_input", { id, x, y, method: "page.mouse.click" });
  await page.mouse.click(x, y);
  await new Promise(resolve => setTimeout(resolve, 250));
}
module.exports = { emit, sha, processFacts, launch, context, loadFrame, snapshot, trustedClick };
