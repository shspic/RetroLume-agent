const { chromium } = require("playwright");
const fs = require("fs");
const path = require("path");
const evidence = path.resolve(__dirname, "../../DocuN/evidence/TASK-103");
const attempt=process.env.RETROLUME_TASK103_BROWSER_ATTEMPT || "01";
const out = path.join(evidence, "browser-"+attempt);
const title="浏览器合成记忆😀"+attempt;
const backgroundTitle="浏览器固定背景"+attempt;
let activePage;
fs.mkdirSync(out, { recursive: true });
const cases = [], network = [];
let browser;
function save() { fs.writeFileSync(path.join(out, "checkpoint.json"), JSON.stringify({ cases, network }, null, 2)); }
function ok(name, values = {}) { cases.push({ name, status: "PASS", executed: true, ...values }); save(); }
function assert(value, message) { if (!value) throw new Error(message); }
async function activity(page) {
  await page.getByRole("button", { name: "学习活动", exact: false }).click();
  await page.getByRole("heading", { name: "学习记忆", exact: true }).waitFor();
  await page.getByRole("button", { name: "新建用户记忆", exact: true }).waitFor({ state: "visible" });
}
function workspace(page) { return page.getByRole("region", { name: "学习记忆工作区", exact: true }); }
async function findMemory(page, title) {
  const ws = workspace(page);
  for (let n = 0; n < 8; n++) {
    if (await ws.getByRole("button", { name: title, exact: true }).count()) return;
    const more = ws.getByRole("button", { name: "读取更早记忆", exact: true });
    if (!await more.count()) break;
    await more.click(); await page.waitForTimeout(100);
  }
  throw new Error("memory item not found in bounded pages");
}
(async () => {
  try {
    const profile = path.join(evidence, "workspace", "browser-profile-"+attempt);
    const context = await chromium.launchPersistentContext(profile, { headless: true });
    browser = { contexts: () => [context], close: () => context.close() };
    const page = await context.newPage(); activePage=page;
    page.setDefaultTimeout(8000);
    page.on("request", request => {
      const url = new URL(request.url());
      if (url.pathname.startsWith("/api/")) network.push({ method: request.method(), path: url.pathname });
    });
    const errors = [];
    page.on("pageerror", error => errors.push(error.message));
    await page.goto("http://127.0.0.1:18103");
    await activity(page);
    await page.screenshot({ path: path.join(out, "01-workspace.png"), fullPage: true });
    const ws = workspace(page);
    await ws.getByRole("button", { name: "新建用户记忆", exact: true }).click();
    await ws.getByLabel("记忆标题", { exact: true }).fill(title);
    await ws.getByLabel("用户正文或注记", { exact: true }).fill("我需要继续练习速度单位");
    const before = network.filter(n => n.method === "POST").length;
    await ws.getByRole("button", { name: "保存用户记忆", exact: true }).click();
    await ws.getByText("已确认保存，未调用模型。", { exact: true }).waitFor();
    await page.waitForFunction(() => !document.querySelector(".memory-detail button.primary")?.disabled);
    assert(network.filter(n => n.method === "POST").length === before + 1, "save produced more than one POST");
    ok("actual UI explicit self-report save", { posts: 1 });
    await findMemory(page, title);
    await ws.getByRole("button", { name: title, exact: true }).click();
    await ws.getByLabel("用户正文或注记", { exact: true }).fill("未保存草稿不会自动提交");
    await page.waitForTimeout(200);
    const readsBefore = network.length;
    const postsBefore = network.filter(n => n.method === "POST").length;
    await page.reload(); await activity(page);
    assert(network.slice(readsBefore).every(n => n.method === "GET"), "reload emitted write");
    ok("refresh navigation only GET", { post_delta: network.filter(n => n.method === "POST").length - postsBefore });
    await findMemory(page, title);
    await ws.getByRole("button", { name: title, exact: true }).click();
    await ws.getByRole("button",{name:"预览记忆修正影响",exact:true}).waitFor();
    await page.waitForTimeout(150);
    assert(await ws.getByLabel("用户正文或注记", { exact: true }).inputValue() === "未保存草稿不会自动提交", "same owner draft did not restore");
    const ownA = await page.evaluate(() => sessionStorage.getItem("retrolume.teaching-editor-owner.v1"));
    const [other] = await Promise.all([context.waitForEvent("page"), page.evaluate(() => window.open("/", "_blank"))]);
    await other.waitForLoadState(); await activity(other);
    await other.waitForTimeout(150);
    const ownB = await other.evaluate(() => sessionStorage.getItem("retrolume.teaching-editor-owner.v1"));
    assert(ownA && ownB && ownA !== ownB, "copied tab reused live owner");
    ok("native Web Locks owner separation", { distinct: true });
    await findMemory(other, title);
    await workspace(other).getByRole("button", { name: title, exact: true }).click();
    await workspace(other).getByLabel("用户正文或注记", { exact: true }).fill("第二标签旧版本草稿");
    await ws.getByRole("button", { name: "预览记忆修正影响", exact: true }).click();
    await ws.getByRole("dialog", { name: "记忆变动确认", exact: true }).waitFor();
    await ws.getByRole("button", { name: "确认追加修订版本", exact: true }).click();
    await ws.getByText("已确认保存，未调用模型。", { exact: true }).waitFor();
    await page.waitForFunction(() => !document.querySelector(".memory-detail button.primary")?.disabled);
    await workspace(other).getByRole("button", { name: "预览记忆修正影响", exact: true }).click();
    await workspace(other).getByRole("alert").filter({ hasText: "记忆已有新版本" }).waitFor();
    assert(await workspace(other).getByLabel("用户正文或注记", { exact: true }).inputValue() === "第二标签旧版本草稿", "CAS lost old text");
    ok("two tabs stale CAS preserves original text");
    await ws.getByRole("button", { name: "预览撤销并清理", exact: true }).click();
    await ws.getByRole("dialog", { name: "记忆变动确认", exact: true }).waitFor();
    await ws.getByRole("button", { name: "确认撤销并清理本条记忆", exact: true }).click();
    await ws.getByText("已撤销，本条在线记忆正文已清理；原始事实和保留副本仍在。", { exact: true }).waitFor();
    assert(await ws.getByLabel("用户正文或注记", { exact: true }).count() === 0, "withdrawn body still rendered");
    ok("revoke and cleanup UI suppresses body");
    await ws.getByRole("button", { name: "新建用户记忆", exact: true }).click();
    await ws.getByLabel("记忆标题", { exact: true }).fill(backgroundTitle);
    await ws.getByLabel("用户正文或注记", { exact: true }).fill("<script>window.__task103_xss=1</script>我是自报");
    await ws.getByRole("button", { name: "保存用户记忆", exact: true }).click();
    await ws.getByText("已确认保存，未调用模型。", { exact: true }).waitFor();
    await page.waitForFunction(() => !document.querySelector(".memory-detail button.primary")?.disabled);
    assert(await page.evaluate(() => window.__task103_xss) === undefined, "memory XSS executed");
    await findMemory(page, backgroundTitle);
    await ws.getByRole("checkbox", { name: "选用记忆 "+backgroundTitle, exact: true }).check();
    await page.locator(".ws-pick-row").filter({ hasText: "task103-browser-material.md" }).getByRole("checkbox").check();
    const responseWait = page.waitForResponse(r => new URL(r.url()).pathname === "/api/activities" && r.request().method() === "POST");
    await page.getByRole("button", { name: "创建活动", exact: true }).click();
    const created = await responseWait; assert(created.status() === 200, "selected activity create failed");
    const actual = (await created.json()).activity;
    assert(actual.memory_selection && actual.memory_selection.entries.length === 1, "selection not persisted");
    ok("real UI fixed memory selection with activity", { activity_id: actual.activity_id, selected: 1 });
    await page.screenshot({ path: path.join(out, "02-final.png"), fullPage: true });
    assert(errors.length === 0, "page errors: " + errors.join(","));
    fs.writeFileSync(path.join(out, "result.json"), JSON.stringify({ status: "PASS", cases, network, page_errors: errors }, null, 2));
  } catch (error) {
    if (browser) {
      const pages = browser.contexts().flatMap(c => c.pages());
      if (activePage) { await activePage.screenshot({ path: path.join(out, "failure.png"), fullPage: true }).catch(() => {});
        fs.writeFileSync(path.join(out, "failure-dom.txt"), await activePage.locator("body").innerText().catch(() => "")); }
    }
    fs.writeFileSync(path.join(out, "result.json"), JSON.stringify({ status: "FAIL", cases, network, error: String(error.stack || error) }, null, 2));
    process.exitCode = 1;
  } finally { if (browser) await browser.close(); }
})();

