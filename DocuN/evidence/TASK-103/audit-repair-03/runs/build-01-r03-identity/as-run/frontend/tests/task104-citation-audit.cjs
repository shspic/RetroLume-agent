// TASK104 真实页面只读引用迟到补证，全部业务写请求拒绝并记失败。
const { chromium } = require("playwright");
const fs = require("fs"), path = require("path"), crypto = require("crypto"), cp = require("child_process");
const root = path.resolve(__dirname, "../..");
const runDir = path.resolve(process.env.TASK104_RUN_DIR || "");
const evidence = path.join(root, "DocuN/evidence/TASK-104") + path.sep;
if (!runDir.startsWith(evidence)) throw Error("证据目录越界");
const out = path.join(runDir, "browser");
fs.mkdirSync(out, { recursive: true });
const target = JSON.parse(fs.readFileSync(path.join(runDir, "browser-target.json"), "utf8"));
const write = (name, value) => fs.writeFileSync(path.join(out, name), JSON.stringify(value, null, 2), "utf8");
const digest = bytes => crypto.createHash("sha256").update(bytes).digest("hex");
const assert = (value, message) => { if (!value) throw Error(message); };
const network = [], loaded = [], api = [], errors = [], failed = [], forbidden = [], responseTasks = [];
let context, page, release, heldResolve, handlerDoneResolve;
const held = new Promise(resolve => heldResolve = resolve);
const handlerDone = new Promise(resolve => handlerDoneResolve = resolve);
const controller = {};
const now = () => new Date().toISOString();
const waitFor = async (predicate, message, timeout = 15000) => {
  const deadline = Date.now() + timeout;
  while (!predicate()) {
    if (Date.now() >= deadline) throw Error(message);
    await new Promise(resolve => setTimeout(resolve, 50));
  }
};
async function capture(label) {
  fs.writeFileSync(path.join(out, label + "-dom.html"), await page.content(), "utf8");
  fs.writeFileSync(path.join(out, label + "-text.txt"), await page.locator("body").innerText(), "utf8");
  await page.screenshot({ path: path.join(out, label + ".png"), fullPage: true });
}
function responseObserver(response) {
  const task = (async () => {
    const url = new URL(response.url()), pathname = url.pathname;
    network.push({ event: "response", at: now(), path: pathname + url.search, method: response.request().method(), status: response.status() });
    if (pathname === "/api/session") return; // 会话令牌仅在实际页面内存，原件不保存。
    try {
      const bytes = await response.body();
      if (pathname.startsWith("/api/") && response.request().method() === "GET") {
        const value = JSON.parse(bytes.toString("utf8"));
        api.push({ at: now(), path: pathname + url.search, pathname, status: response.status(), sha256: digest(bytes), data: value });
      } else if (pathname === "/" || pathname.startsWith("/assets/")) {
        const filename = pathname === "/" ? "index.html" : path.basename(pathname);
        const store = path.join(out, "loaded", filename);
        fs.mkdirSync(path.dirname(store), { recursive: true });
        fs.writeFileSync(store, bytes);
        const product = path.join(root, "frontend/dist", pathname === "/" ? "index.html" : pathname.slice(1));
        const productBytes = fs.readFileSync(product);
        loaded.push({ at: now(), path: pathname, bytes: bytes.length, sha256: digest(bytes), product_sha256: digest(productBytes), full_bytes_equal: bytes.equals(productBytes), saved: store });
      }
    } catch (error) {
      if (pathname !== target.citation_path) errors.push({ kind: "response_read", at: now(), path: pathname, message: String(error) });
    }
  })();
  responseTasks.push(task);
}
function latest(pathname) { return [...api].reverse().find(x => x.pathname === pathname && x.status === 200); }
function currentList() {
  const groups = api.filter(x => x.pathname === "/api/activities" && x.status === 200);
  let items = [];
  for (const item of groups) {
    if (!new URLSearchParams(item.path.split("?")[1] || "").has("cursor")) items = [];
    for (const value of item.data.items || []) if (!items.some(old => old.activity_id === value.activity_id)) items.push(value);
  }
  return items;
}
async function selectActivity(id) {
  const library = page.locator("section.library");
  let index = currentList().findIndex(x => x.activity_id === id);
  for (let attempt = 0; index < 0 && attempt < 10; attempt++) {
    const more = library.getByRole("button", { name: "加载更多", exact: true });
    assert(await more.count(), "实际列表没有该活动或更多游标");
    const oldCount = currentList().length;
    await more.click();
    await waitFor(() => currentList().length > oldCount, "实际活动分页未完成");
    index = currentList().findIndex(x => x.activity_id === id);
  }
  assert(index >= 0, "目标不在已实际读取的活动列表");
  const buttons = library.locator("button.material");
  await buttons.nth(index).waitFor({ state: "visible" });
  const expected = currentList()[index];
  const clickAt = now();
  await buttons.nth(index).click();
  const workspacePath = "/api/activities/" + id + "/teaching/workspace";
  await waitFor(() => !!latest(workspacePath) && latest(workspacePath).at >= clickAt, "新活动工作区GET没有确认");
  const detail = latest("/api/activities/" + id);
  assert(detail && detail.data.activity.activity_id === id, "点击后详情ID不匹配真实列表");
  const workspace = latest(workspacePath);
  assert(workspace.data.activity_id === id, "教学工作区身份不匹配");
  await page.locator(".ws-teaching").waitFor({ state: "visible" });
  const text = await page.locator("section.reader").innerText();
  write("selection-" + id + ".json", { clickAt, index, listItem: expected, detail_id: detail.data.activity.activity_id, workspace, reader_text: text, list_pages: api.filter(x => x.pathname === "/api/activities") });
  return workspace.data;
}
async function processIdentities() {
  const script = "$taskAll=@(Get-CimInstance Win32_Process); $taskIds=[System.Collections.Generic.HashSet[int]]::new(); [void]$taskIds.Add(" + process.pid + "); $taskChanged=$true; while($taskChanged){$taskChanged=$false; foreach($taskProc in $taskAll){if($taskIds.Contains([int]$taskProc.ParentProcessId)){if($taskIds.Add([int]$taskProc.ProcessId)){$taskChanged=$true}}}}; @($taskAll | Where-Object {$taskIds.Contains([int]$_.ProcessId)} | ForEach-Object {[pscustomobject]@{pid=$_.ProcessId;parent=$_.ParentProcessId;created=$_.CreationDate.ToUniversalTime().ToString('o');command=$_.CommandLine;exe=$_.ExecutablePath}}) | ConvertTo-Json -Compress";
  const raw = cp.execFileSync("powershell.exe", ["-NoProfile", "-Command", script], { timeout: 12000, windowsHide: true }).toString().trim();
  const value = raw ? JSON.parse(raw) : [];
  write("process-identities.json", Array.isArray(value) ? value : [value]);
}
(async () => {
  let report = { status: "FAIL", executed: true, business_POST: 0 };
  try {
    const profile = path.join(runDir, "browser-profile");
    context = await chromium.launchPersistentContext(profile, { headless: true, viewport: { width: 1440, height: 1000 }, downloadsPath: path.join(runDir, "downloads") });
    context.setDefaultTimeout(15000);
    await context.route("**/*", async route => {
      const request = route.request(), url = new URL(request.url());
      if (url.protocol.startsWith("http") && (url.hostname !== "127.0.0.1" || url.port !== "18103" || !["GET", "HEAD"].includes(request.method()))) {
        forbidden.push({ at: now(), method: request.method(), path: url.pathname, host: url.host });
        await route.abort("blockedbyclient");
      } else await route.continue();
    });
    page = await context.newPage();
    page.on("request", request => {
      const url = new URL(request.url());
      network.push({ event: "request", at: now(), path: url.pathname + url.search, method: request.method() });
    });
    page.on("response", responseObserver);
    page.on("requestfailed", request => failed.push({ at: now(), path: new URL(request.url()).pathname, error: request.failure()?.errorText }));
    page.on("pageerror", error => errors.push({ kind: "pageerror", at: now(), message: String(error) }));
    page.on("console", message => { if (message.type() === "error") errors.push({ kind: "console", at: now(), message: message.text(), location: message.location() }); });
    await page.goto("http://127.0.0.1:18103");
    await page.getByRole("button", { name: "学习活动", exact: false }).click();
    await waitFor(() => currentList().length > 0, "真实默认活动列表未返回");
    await processIdentities();
    const first = await selectActivity(target.activity_id);
    const region = first.proposal || first.path;
    assert(region && region.record_id === target.record_id && first.view_token === target.view_token, "当前路径记录或viewToken不匹配");
    assert(region.nodes?.[0]?.citations?.includes(target.citation_id), "原引用不属于当前第一路径节点");
    await capture("01-before-citation");
    const gate = new Promise(resolve => release = resolve);
    await page.route("**" + target.citation_path, async route => {
      controller.request_at = now();
      controller.path = new URL(route.request().url()).pathname;
      controller.method = route.request().method();
      controller.auth_header_present = !!route.request().headers()["x-retrolume-session"];
      const response = await route.fetch();
      const bytes = await response.body();
      controller.service_200_at = now();
      controller.status = response.status();
      controller.response_sha256 = digest(bytes);
      controller.response = JSON.parse(bytes.toString("utf8"));
      assert(controller.status === 200 && controller.response.citation.citation_id === target.citation_id && controller.response.citation.text, "挂起引用没有取得真正服务GET200");
      fs.writeFileSync(path.join(out, "actual-citation-response.json"), bytes);
      heldResolve();
      await gate;
      controller.release_attempt_at = now();
      try {
        await route.fulfill({ response, body: bytes });
        controller.delivered_at = now();
      } catch (error) { controller.delivery_error = String(error); }
      write("late-citation-controller.json", controller);
      handlerDoneResolve();
    });
    await page.getByRole("button", { name: "查看依据 · 路径 n1 · 1", exact: true }).click();
    await Promise.race([held, new Promise((_, reject) => setTimeout(() => reject(Error("实际引用GET未到达")), 15000))]);
    await capture("02-held-response");
    controller.switch_started_at = now();
    const switched = await selectActivity(target.switch_activity_id);
    controller.switch_completed_at = now();
    assert(switched.activity_id !== target.activity_id, "没有真正切到另一身份");
    await capture("03-switched-before-release");
    release();
    await Promise.race([handlerDone, new Promise((_, reject) => setTimeout(() => reject(Error("晚交付尝试未完成")), 12000))]);
    await page.waitForTimeout(700);
    assert(latest("/api/activities/" + target.switch_activity_id + "/teaching/workspace").data.activity_id === target.switch_activity_id, "当前网络身份被改回");
    assert(await page.locator('[aria-label="教学引用原文"]').count() === 0, "旧引用原文或位置在新面板复活");
    const selectedButton = page.locator("section.library button.material.selected");
    assert(await selectedButton.count() === 1, "当前活动列表选择不唯一");
    const selectedIndex = await selectedButton.evaluate(element => Array.from(element.parentElement.parentElement.querySelectorAll("button.material")).indexOf(element));
    assert(currentList()[selectedIndex]?.activity_id === target.switch_activity_id, "当前DOM选择不是新活动");
    await capture("04-after-late-delivery");
    await Promise.all(responseTasks);
    const expectedAbort = failed.filter(x => x.path === target.citation_path && /ERR_ABORTED/.test(x.error || ""));
    const unknownErrors = errors.filter(x => !(x.kind === "console" && /ERR_ABORTED/.test(x.message) && expectedAbort.length && (!x.location?.url || new URL(x.location.url).pathname === target.citation_path)));
    assert(unknownErrors.length === 0, "出现不能归因于所测Abort的错误");
    assert(forbidden.length === 0 && !network.some(x => x.method === "POST"), "只读补证出现写请求或外部请求");
    assert(loaded.some(x => x.path.endsWith(".js")) && loaded.some(x => x.path.endsWith(".css")) && loaded.every(x => x.full_bytes_equal), "实际加载bundle字节不一致");
    report = { status: "PASS", executed: true, activity_id: target.activity_id, record_id: target.record_id, citation_id: target.citation_id, view_token: first.view_token, switched_activity_id: switched.activity_id, switched_view_token: switched.view_token, actual_service_status: controller.status, delivery: controller.delivery_error ? "实际取消路径" : "已尝试交付", expected_abort: expectedAbort, old_citation_panel_count: 0, business_POST: 0, forbidden: 0, unknown_errors: unknownErrors, loaded };
  } catch (error) {
    report.error = String(error);
    if (page) { try { await capture("failure"); } catch (captureError) { report.capture_error = String(captureError); } }
  } finally {
    if (release) release();
    if (context) { try { await context.close(); } catch (closeError) { report.close_error = String(closeError); } }
    write("late-citation-controller-final.json", controller);
    write("network.json", network);
    write("api-responses.json", api);
    write("errors.json", { errors, failed, forbidden });
    write("loaded-bundle.json", loaded);
    write("result.json", report);
    console.log(JSON.stringify({ status: report.status, error: report.error, business_POST: network.filter(x => x.method === "POST").length }));
    process.exitCode = report.status === "PASS" ? 0 : 1;
  }
})();
