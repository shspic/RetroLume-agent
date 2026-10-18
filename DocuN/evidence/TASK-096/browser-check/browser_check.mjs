// TASK-096 审计专项：最终 bundle 的前端显示行为最小取证。
// 所有 /api 请求由 Playwright route 合成截获；仅静态资源来自本卡 127.0.0.1:18096；
// 外网/未知请求拒绝并留证；不启动 PG、不触真实后端、不发任何真实模型调用。
import { createRequire } from "module";
import http from "http";
import fs from "fs";
import path from "path";

const require2 = createRequire("D:/shspic/project_NO3_RetroLume-agent/frontend/package.json");
const { chromium } = require2("playwright");

const DIST = "D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-096/browser-check/dist-audit";
const OUT = "D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-096/browser-check";
const PORT = 18096;
const HOST = `http://127.0.0.1:${PORT}`;
const summary = { ok: false, steps: [], requests: [], blocked: [], posts_after_refresh: null, checks: {}, console_errors: [], page_errors: [] };
const consoleErrors = [];
const pageErrors = [];
const mime = { ".html": "text/html", ".js": "text/javascript", ".css": "text/css", ".mjs": "text/javascript", ".svg": "image/svg+xml" };

const server = http.createServer((req, res) => {
  const rel = req.url.split("?")[0] === "/" ? "/index.html" : req.url.split("?")[0];
  const file = path.resolve(DIST, "." + rel);
  if (path.relative(DIST, file).startsWith("..") || !fs.existsSync(file) || fs.statSync(file).isDirectory()) {
    res.writeHead(404); res.end("not found"); summary.blocked.push(`static-404:${req.url}`);
    return;
  }
  res.writeHead(200, { "Content-Type": mime[path.extname(file)] ?? "application/octet-stream" });
  res.end(fs.readFileSync(file));
});

const bodies = {
  A: "合成正文A-096：<script>window.__xss_marker=true</script> & \"引号\" 反斜杠\\ 换行\n多字节 Chinese ✓",
  C: "合成正文C-096（慢回包专属标记）：绝不允许出现在A的面板里",
};

function json(route, payload, status = 200) {
  return route.fulfill({ status, contentType: "application/json", body: JSON.stringify(payload) });
}
function opRow(id, kind, state, disposition, read_status, extra = {}) {
  return {
    operation_id: id, kind, state, disposition, error_code: null,
    reserved_at: "2026-10-01T10:00:00Z", dispatch_started_at: "2026-10-01T10:00:01Z",
    recorded_at: "2026-10-01T10:00:05Z", prompt_tokens: 5, completion_tokens: 3,
    finish_reason: "stop", returned_model: "synthetic-model-095", committed_at: "2026-10-01T10:00:06Z",
    read_status, payload_available: read_status === "committed_current", payload: null, ...extra,
  };
}
const activity = {
  activity_id: "1f0e6d2c-0000-4000-8000-000000000001", status: "running",
  created_at: "2026-10-01T09:00:00Z", updated_at: "2026-10-01T10:00:06Z",
  deadline_at: "2026-10-02T09:00:00Z", cancelled_at: null, scope_revision: 1,
  max_requests: 8, requests_reserved: 2, max_cost_microunits: 800000, cost_reserved_microunits: 200000,
  reserve_cost_microunits: 100000, max_running_seconds: 600, running_reserved_seconds: 0,
  running_settled_seconds: 7, max_tool_calls: null, tools_reserved: 0,
  source_count: 1, source_titles: ["TASK096-合成资料"],
  last_settled_generation: 2, last_settled_seconds: 7,
  allowed_models: [{ provider: "deepseek_chat_completions", model: "synthetic-model-095" }],
  sources: [{ source_id: "aaaa0000-0000-4000-8000-00000000000a", title: "TASK096-合成资料", valid: true }],
};
const ops = {
  A: opRow("ui-a-096", "model", "received", "received", "committed_current"),
  B: opRow("ui-b-096", "model", "received", "received", "invalidated_source"),
  C: opRow("ui-c-096", "model", "received", "received", "committed_current"),
};

await new Promise(resolve => server.listen(PORT, "127.0.0.1", resolve));

const browser = await chromium.launch({ headless: true });
try {
  const page = await browser.newPage();
  page.on("pageerror", e => pageErrors.push(String(e)));
  page.on("console", m => { if (m.type() === "error") consoleErrors.push(m.text()); });

  let slowC = false;
  await page.route("**/*", async route => {
    const req = route.request();
    const url = new URL(req.url());
    summary.requests.push({ method: req.method(), url: req.url() });
    if (url.hostname !== "127.0.0.1" || url.port !== String(PORT)) {
      summary.blocked.push(`${req.method()}:${req.url()}`);
      return route.abort();
    }
    if (!url.pathname.startsWith("/api/")) return route.continue();
    if (req.method() !== "GET") { summary.requests.push({ intercepted_write: req.method(), url: req.url() }); }
    if (url.pathname === "/api/session") return json(route, { token: "synthetic-token-096", storage_configured: true, max_bytes: 100 });
    if (url.pathname === "/api/activities/capabilities") return json(route, {
      storage_ready: true, storage_reason: null,
      create: { available: true, reason: null }, continue: { available: true, reason: null },
      quota_preview: { deadline_hours: 24, max_requests: 8, max_cost_microunits: 800000, reserve_cost_microunits: 100000, max_request_bytes: 65536, max_output_tokens: 256, max_running_seconds: 600, allowed_tools: [], max_tool_calls: null },
      provider: { provider: "deepseek_chat_completions", model: "synthetic-model-095" },
      supervision_management_budget_seconds: 120, window_seconds: 90, followup_max_chars: 4096,
    });
    if (url.pathname === "/api/activities" && req.method() === "GET") return json(route, { items: [activity], next_cursor: null });
    if (url.pathname === "/api/activities/1f0e6d2c-0000-4000-8000-000000000001" && req.method() === "GET") return json(route, { activity });
    if (url.pathname.endsWith("/operations") && req.method() === "GET") {
      return json(route, { items: [ops.A, ops.B, ops.C], next_cursor: null });
    }
    const single = url.pathname.match(/\/operations\/(ui-[abc]-096)$/);
    if (single && req.method() === "GET") {
      const id = single[1];
      if (id === "ui-c-096" && slowC) await new Promise(r => setTimeout(r, 1500));
      if (id === "ui-a-096") return json(route, { operation: { ...ops.A, payload: { format: "text", value: bodies.A } } });
      if (id === "ui-c-096") return json(route, { operation: { ...ops.C, payload: { format: "json", value: { reply: bodies.C } } } });
      return json(route, { operation: ops.B });
    }
    if (url.pathname.endsWith("/cancel") && req.method() === "POST") {
      activity.status = "cancelled"; activity.cancelled_at = "2026-10-01T10:05:00Z";
      return json(route, { activity });
    }
    summary.blocked.push(`unmatched-api:${req.method()}:${req.url()}`);
    return json(route, { detail: { code: "synthetic_unmatched", message: "审计夹具未匹配该请求" } }, 404);
  });

  const clicked = id => page.locator(".ws-op", { hasText: id }).first().click();

  // s1 加载与能力分层（合成）。
  await page.goto(HOST, { waitUntil: "domcontentloaded" });
  await page.locator("nav div", { hasText: "学习活动" }).click();
  await page.getByText("读取与取消：可用").waitFor({ timeout: 10000 });
  await page.getByText("显式继续：可用").waitFor({ timeout: 10000 });
  summary.steps.push("capabilities-ok");

  // s2 列表 → 详情 → 操作列表（列表行不带正文）。
  await page.locator("button.material").first().click();
  await page.locator(".ws-op").first().waitFor({ timeout: 10000 });
  const listBodyLeak = await page.locator(".ws-operations").innerText();
  summary.checks.list_no_payload = !listBodyLeak.includes("合成正文A-096") && !listBodyLeak.includes("合成正文C-096");
  summary.steps.push("list-shown");

  // s3 展开A：单操作读取补全正文；低信任字符串转义显示；XSS marker 不得置位。
  await clicked("ui-a-096");
  await page.locator(".ws-op-detail pre").first().waitFor({ timeout: 10000 });
  const aText = await page.locator(".ws-op-detail pre").first().innerText();
  summary.checks.a_body_shown = aText.includes("合成正文A-096") && aText.includes("多字节 Chinese ✓") && aText.includes("\\");
  summary.checks.a_no_c_body = !aText.includes("合成正文C-096");
  summary.checks.xss_not_executed = await page.evaluate(() => window.__xss_marker !== true);
  summary.checks.a_continue_open = await page.getByRole("button", { name: "从该成果继续…" }).first().isVisible();
  await page.screenshot({ path: `${OUT}/audit-detail-a.png`, fullPage: true });
  summary.steps.push("detail-a-ok");

  // s4 慢回包C与切换：C响应延迟期间A正文保持；C到达后C面板显示C正文；互不串。
  slowC = true;
  await clicked("ui-c-096");
  await page.waitForTimeout(300);
  const duringPending = await page.locator(".ws-operations").innerText();
  summary.checks.pending_no_early_c = !duringPending.includes("合成正文C-096");
  await page.locator(".ws-op-detail pre", { hasText: "合成正文C-096" }).waitFor({ timeout: 10000 });
  const cText = await page.locator(".ws-op-detail pre").first().innerText();
  summary.checks.c_body_json = cText.includes("合成正文C-096") && !cText.includes("合成正文A-096");
  slowC = false;
  await clicked("ui-a-096");
  await page.locator(".ws-op-detail pre", { hasText: "合成正文A-096" }).waitFor({ timeout: 10000 });
  const aAgain = await page.locator(".ws-op-detail pre").first().innerText();
  summary.checks.a_again_no_c = aAgain.includes("合成正文A-096") && !aAgain.includes("合成正文C-096");
  summary.steps.push("switch-no-cross-contamination");

  // s5 失效操作B：无正文、显示失效原因、无继续入口。
  await clicked("ui-b-096");
  await page.locator(".ws-op-detail", { hasText: "正文已失效" }).waitFor({ timeout: 10000 });
  const bPanel = await page.locator(".ws-op-detail").last().innerText();
  summary.checks.b_suppressed = bPanel.includes("正文已失效") && !bPanel.includes("合成正文A-096") && !bPanel.includes("合成正文C-096");
  summary.checks.b_no_continue = !(await page.locator(".ws-op-detail").last().getByRole("button", { name: "从该成果继续…" }).count());
  await page.screenshot({ path: `${OUT}/audit-detail-b-invalidated.png`, fullPage: true });
  summary.steps.push("invalidated-suppressed");

  // s6 陈旧running前端取消（仅前端行为）：两步确认 → 合成取消 → 只读更新。
  await page.getByRole("button", { name: "取消活动" }).click();
  await page.getByText("取消后不会开始新的动作").waitFor({ timeout: 5000 });
  await page.getByRole("button", { name: "确认取消" }).click();
  await page.getByText("已取消：不会再开始新动作").waitFor({ timeout: 5000 });
  summary.checks.cancel_frontend_two_step = true;
  await page.screenshot({ path: `${OUT}/audit-cancelled.png`, fullPage: true });
  summary.steps.push("stale-running-cancel-frontend");

  // s7 刷新只GET：清点刷新后全部请求，不得出现任何写入动作。
  const seen = summary.requests.length;
  await page.reload({ waitUntil: "domcontentloaded" });
  await page.locator("nav div", { hasText: "学习活动" }).click();
  await page.locator(".ws-op").first().waitFor({ timeout: 10000 });
  await page.waitForTimeout(500);
  const after = summary.requests.slice(seen);
  summary.posts_after_refresh = after.filter(r => r.method && r.method !== "GET").length;
  summary.steps.push("refresh-get-only");

  summary.ok =
    summary.checks.list_no_payload && summary.checks.a_body_shown && summary.checks.a_no_c_body &&
    summary.checks.xss_not_executed && summary.checks.a_continue_open && summary.checks.pending_no_early_c &&
    summary.checks.c_body_json && summary.checks.a_again_no_c && summary.checks.b_suppressed &&
    summary.checks.b_no_continue && summary.checks.cancel_frontend_two_step && summary.posts_after_refresh === 0 &&
    consoleErrors.length === 0 && pageErrors.length === 0 && summary.blocked.length === 0;
  summary.console_errors = consoleErrors;
  summary.page_errors = pageErrors;
} catch (reason) {
  summary.error = String(reason);
  summary.console_errors = consoleErrors;
  summary.page_errors = pageErrors;
} finally {
  await browser.close();
  server.close();
}
fs.writeFileSync(`${OUT}/audit-browser-summary.json`, JSON.stringify(summary, null, 2) + "\n", "utf-8");
console.log(JSON.stringify({ ok: summary.ok, steps: summary.steps, checks: summary.checks, blocked: summary.blocked, error: summary.error ?? null }));
process.exit(summary.ok ? 0 : 1);
