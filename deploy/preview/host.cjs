"use strict";
// 本模块仅承载关口反例，未实现或声明全协议导航否决器。
const fs = require("node:fs");
const crypto = require("node:crypto");
const pw = require("./vendor/playwright-core");
let sequence = 0;
let recordSequence = 0;
const pageSessions = new WeakMap();
const pageObservers = new WeakMap();
const engineEvents = [];
const pageSignals = [];
function sha(bytes) { return crypto.createHash("sha256").update(bytes).digest("hex"); }
async function shaFile(path) {
  const hash = crypto.createHash("sha256");
  for await (const chunk of fs.createReadStream(path)) hash.update(chunk);
  return hash.digest("hex");
}
function emit(kind, data) {
  const body = Buffer.from(JSON.stringify({ kind, data }), "utf8");
  if (body.length > 16384) throw new Error("关口观测超过有限累计上界");
  if (body.length > 4096) {
    const id = ++recordSequence;
    const count = Math.ceil(body.length / 2048);
    for (let index = 0; index < count; index++) emit("bounded_chunk", { id, index, count, full_bytes: body.length, full_sha256: sha(body), base64: body.subarray(index * 2048, (index + 1) * 2048).toString("base64") });
    return;
  }
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
      for (const field of ["Name", "PPid", "Uid", "NoNewPrivs", "Seccomp", "NSpid", "CapEff", "CapBnd"]) {
        const line = raw.split("\n").find(item => item.startsWith(field + ":"));
        if (line) row[field] = line.slice(field.length + 1).trim();
      }
      const stat = fs.readFileSync(`/proc/${name}/stat`, "utf8");
      row.start_ticks = stat.slice(stat.lastIndexOf(")") + 2).trim().split(/\s+/)[19];
      row.pid_namespace = fs.readlinkSync(`/proc/${name}/ns/pid`);
      rows.push(row);
    } catch { /* 进程消失不冒读到当前状态。 */ }
  }
  return { own_uid: process.getuid(), own_gid: process.getgid(), node: process.version, kernel: require("node:os").release(), pid_namespace: fs.readlinkSync("/proc/self/ns/pid"), init_namespace: fs.readlinkSync("/proc/1/ns/pid"), rows };
}
async function launch() {
  const executable = pw.chromium.executablePath();
  emit("load_identity", { node: process.version, package: require("./vendor/playwright-core/package.json").version, executable, executable_sha256: await shaFile(executable), input_manifest_sha256: sha(fs.readFileSync("/opt/preview/input-manifest.json")) });
  const browser = await pw.chromium.launch({ executablePath: executable, headless: true, chromiumSandbox: true, args: ["--enable-automation"], ignoreDefaultArgs: ["--disable-popup-blocking"], timeout: 8000 });
  const cdp = await browser.newBrowserCDPSession();
  const version = await cdp.send("Browser.getVersion");
  emit("browser_version", { version, source: "Browser.getVersion", playwright_version_value: browser.version() });
  const command = await cdp.send("Browser.getBrowserCommandLine");
  if (!Array.isArray(command.arguments) || command.arguments.some(value => typeof value !== "string")) throw new Error("真实命令行字段结构不符");
  emit("browser_identity", { version, arguments: command.arguments, source: "Browser.getBrowserCommandLine", added_standard_argument: "--enable-automation", observation_impact: "标准自动化配置使命令行接口可用，可能影响页面的自动化识别；不替代浏览器自身sandbox原件。" });
  if (browser.version() !== "151.0.7922.34" || process.getuid() !== 10001 || command.arguments.includes("--no-sandbox") || !command.arguments.includes("--enable-automation")) throw new Error("固定版本或非root sandbox身份不符");
  await cdp.send("Target.setDiscoverTargets", { discover: true });
  const targetEvents = [];
  cdp.on("Target.targetCreated", event => targetEvents.push({ kind: "created", type: event.targetInfo.type, id: event.targetInfo.targetId, url: event.targetInfo.url.slice(0, 256), browserContextId: event.targetInfo.browserContextId ?? null, openerId: event.targetInfo.openerId ?? null }));
  cdp.on("Target.targetDestroyed", event => targetEvents.push({ kind: "destroyed", id: event.targetId }));
  return { browser, cdp, targetEvents };
}
async function context(browser) {
  const value = await browser.newContext({ viewport: { width: 640, height: 480 }, deviceScaleFactor: 1, serviceWorkers: "block", acceptDownloads: false });
  value.setDefaultTimeout(2000);
  value.setDefaultNavigationTimeout(2000);
  await value.route(() => true, route => route.abort());
  await value.routeWebSocket(() => true, socket => socket.close());
  value.on("page", page => {
    page.on("console", message => {
      const text = message.text();
      const prefix = "TASK109_SIGNAL:";
      if (!text.startsWith(prefix)) return;
      if (pageSignals.length >= 256 || text.length > 1024) throw new Error("固定页手势观测超限");
      const data = JSON.parse(text.slice(prefix.length));
      pageSignals.push({ ...data, source: "固定fixture真实console事件", location: message.location(), page_url: page.url().slice(0, 256) });
    });
    const pending = value.newCDPSession(page).then(async session => {
      for (const name of ["Page.frameAttached", "Page.frameNavigated", "Page.navigatedWithinDocument", "Page.frameDetached", "Page.frameRequestedNavigation", "Page.frameScheduledNavigation"]) session.on(name, event => {
        if (engineEvents.length >= 256) throw new Error("引擎观测事件超限");
        engineEvents.push({ name, frameId: event.frameId ?? event.frame?.id, parentId: event.parentFrameId ?? event.frame?.parentId ?? null, loaderId: event.frame?.loaderId ?? null, url: (event.url ?? event.frame?.url ?? "").slice(0, 256), reason: event.reason ?? null, disposition: event.disposition ?? null });
      });
      await session.send("Page.enable");
      pageSessions.set(page, session);
      return session;
    }).catch(error => {
      emit("observer_error", { message: String(error.message).slice(0, 2000) });
      return { error };
    });
    pageObservers.set(page, pending);
  });
  return value;
}
async function observerReady(page) {
  const pending = pageObservers.get(page);
  if (!pending) throw new Error("页面引擎观察器没有登记");
  let timer;
  try {
    const result = await Promise.race([pending, new Promise((_, reject) => { timer = setTimeout(() => reject(new Error("触发前引擎观察器未就绪")), 2000); })]);
    if (result.error) throw result.error;
    if (!pageSessions.has(page)) throw new Error("页面引擎观察器缺失");
    return result;
  } finally { clearTimeout(timer); }
}
async function loadFrame(value, html, control = false) {
  const page = await value.newPage();
  page.on("dialog", dialog => dialog.dismiss());
  await observerReady(page);
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
  if (!element) throw new Error("固定目标iframe缺失");
  const frame = await element.contentFrame();
  if (!frame || frame.parentFrame() !== page.mainFrame()) throw new Error("固定目标不是根页唯一直接子frame");
  await frame.waitForSelector("#h0_ready", { timeout: 2000 });
  if (!await frame.evaluate(() => window.h0_script_ready === true)) throw new Error("固定页脚本未执行，不能用未触发签拒绝");
  return { page, frame };
}
async function snapshot(value, cdp) {
  const targets = (await cdp.send("Target.getTargets")).targetInfos.filter(row => ["page", "iframe"].includes(row.type)).map(row => ({ id: row.targetId, type: row.type, url: row.url.slice(0, 256) }));
  const pages = [];
  for (const page of value.pages()) {
    const session = await observerReady(page);
    const tree = await session.send("Page.getFrameTree");
    const frames = [];
    function collect(row) {
      frames.push({ id: row.frame.id, parent: row.frame.parentId ?? null, loaderId: row.frame.loaderId, url: row.frame.url.slice(0, 256) });
      for (const child of row.childFrames ?? []) collect(child);
    }
    collect(tree.frameTree);
    const dom = await session.send("DOMSnapshot.captureSnapshot", { computedStyles: [] });
    if (!Array.isArray(dom.documents) || !Array.isArray(dom.strings)) throw new Error("DOMSnapshot真实字段结构不符");
    const documents = dom.documents.map(doc => ({ frameId: dom.strings[doc.frameId], url: dom.strings[doc.documentURL], backendNodeId: doc.nodes.backendNodeId[0] }));
    pages.push({ url: page.url().slice(0, 256), frames, documents });
  }
  return { targets, pages };
}
async function trustedClick(page, frame, id) {
  const item = frame.locator("#" + id);
  const box = await item.boundingBox({ timeout: 2000 });
  if (!box) throw new Error("真实按钮没有可见位置");
  const x = box.x + box.width / 2; const y = box.y + box.height / 2;
  if (x < 0 || x >= 640 || y < 0 || y >= 480) throw new Error("输入坐标越界");
  emit("trusted_input", { id, x, y, method: "page.mouse.click", page_url: page.url().slice(0, 256), frame_url: frame.url().slice(0, 256), direct_child: frame.parentFrame() === page.mainFrame() });
  await page.mouse.click(x, y);
  await new Promise(resolve => setTimeout(resolve, 2000));
}
module.exports = { emit, sha, processFacts, launch, context, observerReady, loadFrame, snapshot, trustedClick, engineEvents, pageSignals };
