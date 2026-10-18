// TASK-095 续作01 G1 浏览器补证：最终 bundle 上刷新只 GET（普通状态 +
// 持久 unconfirmed/submitted 意图各一例）、慢响应轮询不重叠、隐藏暂停/恢复、
// 卸载清理、切换与展开迟到结果不串、失效分支与展开正文、显式动作后读取。
// 全合成 API 回放，不需要生产应用、PG 或 key；未知 /api 路径拒绝并记为失败。
// 环境：APP_PORT、SHOT_DIR、REPORT_PATH、DIST_DIR。
import { chromium } from "playwright";
import { createServer } from "node:http";
import { readFile, stat, mkdir, writeFile } from "node:fs/promises";
import { extname, join, normalize } from "node:path";

const PORT = Number(process.env.APP_PORT ?? 18095);
const SHOTS = process.env.SHOT_DIR ?? ".";
const REPORT = process.env.REPORT_PATH ?? "report.json";
const DIST = process.env.DIST_DIR ?? "../dist";
const APP = `http://127.0.0.1:${PORT}`;

const summary = {
  ok: false, steps: [], checks: {}, blocked: [], console_errors: [], page_errors: [],
  post_total: 0, bundle: {}, timeline_note: "", failures: [],
};
const consoleErrors = [];
const pageErrors = [];

// ---------- 静态服务（正式 dist） ----------
const MIME = {
  ".html": "text/html; charset=utf-8", ".js": "text/javascript", ".mjs": "text/javascript",
  ".css": "text/css", ".svg": "image/svg+xml", ".png": "image/png", ".json": "application/json",
  ".woff2": "font/woff2", ".map": "application/json",
};
const staticServer = createServer(async (request, response) => {
  try {
    const url = new URL(request.url, APP);
    let relative = decodeURIComponent(url.pathname);
    if (relative === "/") relative = "/index.html";
    const target = normalize(join(DIST, relative));
    if (!target.startsWith(normalize(DIST))) { response.writeHead(403).end(); return; }
    const body = await readFile(target);
    response.writeHead(200, { "content-type": MIME[extname(target)] ?? "application/octet-stream", "cache-control": "no-store" });
    response.end(body);
  } catch {
    response.writeHead(404).end("not found");
  }
});
await new Promise((resolve, reject) => {
  staticServer.once("error", reject);
  staticServer.listen(PORT, "127.0.0.1", resolve);
});

// ---------- 合成数据 ----------
const SA = "6b1f9c1e-0000-4000-8000-00000000aaa1";
const AID = "11111111-1111-4111-8111-111111111111";
const BID = "22222222-2222-4222-8222-222222222222";
const XID = "33333333-3333-4333-8333-333333333333";
const now = new Date().toISOString();
const budgetFields = {
  scope_revision: 1, max_requests: 8, requests_reserved: 0,
  max_cost_microunits: 800000, cost_reserved_microunits: 0, reserve_cost_microunits: 100000,
  max_running_seconds: 600, running_reserved_seconds: 0, running_settled_seconds: 0,
  last_settled_generation: null, last_settled_seconds: null, max_tool_calls: null, tools_reserved: 0,
};
const activity = (id, status, title) => ({
  activity_id: id, status, created_at: now, updated_at: now,
  deadline_at: new Date(Date.now() + 86400000).toISOString(), cancelled_at: null,
  ...budgetFields,
  source_count: 1, source_titles: [title],
  allowed_models: [["deepseek_chat_completions", "synthetic-model-095"]],
  sources: [{ source_id: SA, title, valid: true }],
});
const listRow = (operation_id, read_status, payload_available) => ({
  operation_id, kind: "model", state: "received", disposition: "received",
  error_code: null, reserved_at: now, dispatch_started_at: now, recorded_at: now,
  prompt_tokens: 12, completion_tokens: 34, finish_reason: "stop",
  returned_model: "synthetic-model-095", committed_at: now,
  read_status, payload_available, payload: null, // 列表行不携正文
});
const singleRow = (operation_id, payloadText) => ({
  ...listRow(operation_id, "committed_current", true),
  payload: payloadText === null ? null : { format: "text", value: payloadText },
});
const DATA = {
  [AID]: { opRows: [listRow("OP-A1", "committed_current", true), listRow("OP-INVALID", "invalidated_source", false)] },
  [BID]: { opRows: [listRow("OP-B-SLOW", "committed_current", true), listRow("OP-B-FAST", "committed_current", true)] },
  [XID]: { opRows: [] },
};
const SINGLE = {
  "OP-A1": singleRow("OP-A1", '继续正文标记ⓒ "引号" 反斜杠\\ 中文✓'),
  "OP-INVALID": { ...listRow("OP-INVALID", "invalidated_source", false), payload: null },
  "OP-B-SLOW": singleRow("OP-B-SLOW", "SLOW-正文标记ⓐ"),
  "OP-B-FAST": singleRow("OP-B-FAST", "FAST-正文标记ⓑ"),
};

// ---------- 合成路由控制与请求日志 ----------
const control = { slowList: false, slowOpsFor: {}, slowSingle: {} };
const log = [];         // {phase, group, method, path, t_start, t_end, inflight_at_start, duration_ms}
const inflightStack = [];
let inflightPeak = 0;
let phase = "s0-mount";
let postTotal = 0;
const setPhase = value => { phase = value; };

function classify(method, pathname) {
  if (pathname === "/api/session") return "session";
  if (pathname === "/api/materials") return "materials";
  if (pathname === "/api/pdf-candidates") return "pdf-candidates";
  if (pathname === "/api/activities/capabilities") return "capabilities";
  if (pathname === "/api/activities") return method === "POST" ? "create" : "list";
  let match = pathname.match(/^\/api\/activities\/([0-9a-f-]{36})\/operations\/([^/]+)$/);
  if (match) return `single:${match[1]}:${match[2]}`;
  match = pathname.match(/^\/api\/activities\/([0-9a-f-]{36})\/operations$/);
  if (match) return `ops:${match[1]}`;
  match = pathname.match(/^\/api\/activities\/([0-9a-f-]{36})$/);
  if (match) return `detail:${match[1]}`;
  return `unknown:${pathname}`;
}

const json = (body, status = 200) => ({ status, contentType: "application/json", body: JSON.stringify(body) });

await stat(join(DIST, "index.html")); // 首启前静态核：dist 必须存在
const indexHtml = await readFile(join(DIST, "index.html"), "utf-8");
const bundleName = indexHtml.match(/assets\/(index-[^"]+\.js)/)?.[1] ?? "";
summary.bundle = { index_js: bundleName };

async function safeFulfill(route, payload) {
  try { await route.fulfill(payload); } catch { /* 页面已导航或关闭：响应丢弃 */ }
}

async function fulfillAfter(route, payload, delayMs) {
  if (delayMs > 0) await new Promise(resolve => setTimeout(resolve, delayMs));
  await safeFulfill(route, payload);
}

// 轮询周期 3s；等待一个完整周期让在途自动请求完成，避免切片被 reload 前的
// 在途请求污染（合成响应均 <100ms，3.5s 足够）。
const settle = page => page.waitForTimeout(3500);

async function apiHandler(route) {
  const request = route.request();
  const url = new URL(request.url());
  const group = classify(request.method(), url.pathname);
  const tStart = Date.now();
  inflightStack.push(group);
  inflightPeak = Math.max(inflightPeak, inflightStack.length);
  const entry = { phase, group, method: request.method(), path: url.pathname, t_start: tStart, inflight_at_start: inflightStack.length - 1 };
  try {
    if (group.startsWith("unknown:")) {
      summary.blocked.push({ phase, path: url.pathname, method: request.method() });
      await safeFulfill(route, json({ detail: "unknown-route" }, 500));
    } else if (group === "session") {
      await safeFulfill(route, json({ token: "synthetic-token-continuation01", storage_configured: true, max_bytes: 5242880 }));
    } else if (group === "materials") {
      await safeFulfill(route, json({ items: [{ id: SA, title: "合成资料甲", version_id: "v-1", revision: 1, size: 1024, format: "md", created_at: now }], next_offset: null }));
    } else if (group === "pdf-candidates") {
      await safeFulfill(route, json({ items: [] }));
    } else if (group === "capabilities") {
      await safeFulfill(route, json({
        storage_ready: true, storage_reason: null,
        create: { available: true, reason: null }, continue: { available: true, reason: null },
        quota_preview: { deadline_hours: 24, max_requests: 8, max_cost_microunits: 800000, reserve_cost_microunits: 100000, max_running_seconds: 600, max_output_tokens: 256 },
        provider: { provider: "deepseek_chat_completions", model: "synthetic-model-095" },
        supervision_management_budget_seconds: 120, window_seconds: 90, followup_max_chars: 4096,
      }));
    } else if (group === "list") {
      const slow = control.slowList;
      const payload = json({ items: [activity(AID, "running", "活动甲专属资料"), activity(BID, "pending", "活动乙专属资料")], next_cursor: null });
      if (slow) {
        await fulfillAfter(route, payload, 3200);
      } else {
        await safeFulfill(route, payload);
      }
      entry.t_end = Date.now();
      entry.duration_ms = entry.t_end - tStart;
      log.push(entry);
      return;
    } else if (group === "create") {
      postTotal += 1;
      await safeFulfill(route, json({ activity: activity(XID, "pending", "活动甲专属资料") }));
    } else if (group.startsWith("detail:")) {
      const id = group.slice("detail:".length);
      await safeFulfill(route, json({ activity: activity(id, id === AID ? "running" : "pending", "活动甲专属资料") }));
    } else if (group.startsWith("ops:")) {
      const id = group.slice("ops:".length);
      const rows = DATA[id]?.opRows ?? [];
      const delay = control.slowOpsFor[id] ? 2500 : 0;
      const payload = json({ items: rows, next_cursor: null });
      await fulfillAfter(route, payload, delay);
      entry.t_end = Date.now(); entry.duration_ms = entry.t_end - tStart; log.push(entry);
      return;
    } else if (group.startsWith("single:")) {
      const [, , opId] = group.split(":");
      const delay = control.slowSingle[opId] ? 2500 : 0;
      const payload = json({ operation: SINGLE[opId] ?? listRow(opId, "unresolved", false) });
      await fulfillAfter(route, payload, delay);
      entry.t_end = Date.now(); entry.duration_ms = entry.t_end - tStart; log.push(entry);
      return;
    } else {
      // 已知但不预期的写路径：拒绝并记为失败（本轮不应发生）。
      summary.blocked.push({ phase, path: url.pathname, method: request.method() });
      await safeFulfill(route, json({ detail: "not-synthesized" }, 500));
    }
    entry.t_end = Date.now();
    entry.duration_ms = entry.t_end - tStart;
    log.push(entry);
  } finally {
    inflightStack.splice(inflightStack.indexOf(group), 1);
  }
}

// ---------- 场景执行 ----------
await mkdir(SHOTS, { recursive: true });
const browser = await chromium.launch({ headless: true });
try {
  const page = await browser.newPage();
  page.on("pageerror", error => pageErrors.push(String(error)));
  page.on("console", message => { if (message.type() === "error") consoleErrors.push(message.text()); });
  await page.route("**/api/**", apiHandler);
  const apiCount = () => log.length;

  // s0 挂载与默认视图路由覆盖（materials 视图为默认）。
  await page.goto(APP, { waitUntil: "domcontentloaded" });
  const nav = page.locator("nav div", { hasText: "学习活动" });
  await nav.click();
  await page.getByText("读取与取消：可用").waitFor({ timeout: 15000 });
  summary.blocked.length === 0 || summary.failures.push(`s0 blocked non-empty: ${JSON.stringify(summary.blocked)}`);
  summary.steps.push("s0-mount-route-coverage");
  await page.screenshot({ path: `${SHOTS}/c01-s0-capabilities.png`, fullPage: true });

  // s1 普通状态：显式选择 → 刷新只 GET，且不自动恢复旧选择面板。
  await page.locator("button.material", { hasText: "活动甲专属资料" }).first().click();
  await page.getByText("OP-A1").waitFor({ timeout: 15000 });
  setPhase("s1-reload");
  await settle(page);
  const beforeS1 = apiCount();
  await page.reload({ waitUntil: "domcontentloaded" });
  await page.locator("nav div", { hasText: "学习活动" }).click();
  await page.getByText("读取与取消：可用").waitFor({ timeout: 15000 });
  await page.waitForTimeout(2000); // 稳定期窗口：给任何可能的自动请求留观察时间
  const slice1 = log.slice(beforeS1);
  summary.checks.s1_refresh_get_only = slice1.length > 0 && slice1.every(item => item.method === "GET");
  summary.checks.s1_no_ops_without_explicit_pick = slice1.every(item =>
    !item.group.startsWith("ops:") && !item.group.startsWith("single:") && !item.group.startsWith("detail:"));
  summary.checks.s1_detail_not_auto_restored = (await page.getByText("选择一个活动").count()) > 0;
  slice1.length > 0 && slice1.every(item => item.method === "GET") || summary.failures.push(`s1 refresh slice has non-GET: ${JSON.stringify(slice1.filter(i => i.method !== "GET"))}`);
  summary.steps.push("s1-refresh-get-only-normal");

  // s2 持久 unconfirmed 意图：刷新后横幅可见，稳定期只 GET。
  await page.evaluate(() => localStorage.setItem("retrolume.pending-intents.v1", JSON.stringify([
    { intent_id: "i-u1", kind: "create", state: "unconfirmed", created_at: new Date().toISOString(), activity_id: "44444444-4444-4444-8444-444444444444", source_ids: ["6b1f9c1e-0000-4000-8000-00000000aaa1"] },
  ])));
  setPhase("s2-reload");
  await settle(page);
  const beforeS2 = apiCount();
  await page.reload({ waitUntil: "domcontentloaded" });
  await page.locator("nav div", { hasText: "学习活动" }).click();
  await page.getByText("上次动作未确认").waitFor({ timeout: 15000 });
  await page.waitForTimeout(2000);
  const slice2 = log.slice(beforeS2);
  summary.checks.s2_unconfirmed_intent_no_post = slice2.length > 0 && slice2.every(item => item.method === "GET");
  summary.checks.s2_banner_visible = (await page.getByText("上次动作未确认").count()) > 0;
  slice2.some(item => item.method !== "GET") && summary.failures.push("s2 unconfirmed slice has non-GET");
  summary.steps.push("s2-unconfirmed-intent-get-only");
  await page.screenshot({ path: `${SHOTS}/c01-s2-unconfirmed-banner.png`, fullPage: true });

  // s3 持久 submitted 意图：刷新无自动 POST；显式"重新提交同一意图"才产生唯一 POST，且动作后只读重读触发。
  await page.evaluate(() => localStorage.setItem("retrolume.pending-intents.v1", JSON.stringify([
    { intent_id: "i-s1", kind: "create", state: "submitted", created_at: new Date().toISOString(), activity_id: "33333333-3333-4333-8333-333333333333", source_ids: ["6b1f9c1e-0000-4000-8000-00000000aaa1"] },
  ])));
  setPhase("s3-reload");
  await settle(page);
  const beforeS3 = apiCount();
  await page.reload({ waitUntil: "domcontentloaded" });
  await page.locator("nav div", { hasText: "学习活动" }).click();
  await page.getByText("上次动作未确认").waitFor({ timeout: 15000 });
  await page.waitForTimeout(2000);
  const slice3 = log.slice(beforeS3);
  summary.checks.s3_submitted_intent_no_auto_post = slice3.every(item => item.method === "GET");
  slice3.some(item => item.method !== "GET") && summary.failures.push("s3 submitted slice has non-GET");
  const postBefore = postTotal;
  const beforeS3b = apiCount();
  await page.getByRole("button", { name: "重新提交同一意图" }).first().click();
  await page.getByText("活动已创建").waitFor({ timeout: 15000 });
  await page.waitForTimeout(2000); // 显式动作后的重读窗口
  const slice3b = log.slice(beforeS3b);
  summary.checks.s3_explicit_post_exactly_one = postTotal - postBefore === 1;
  summary.checks.s3_read_after_explicit_action = slice3b.some(item => item.group === "list" && item.method === "GET");
  (postTotal - postBefore === 1) || summary.failures.push(`s3 explicit POST count ${postTotal - postBefore}`);
  slice3b.some(item => item.method === "POST") && summary.failures.push("s3 after-action slice contains POST");
  summary.checks.s3_detail_after_success = (await page.getByText("尚无操作。此版本等待学习入口接入").count()) > 0;
  summary.steps.push("s3-submitted-intent-explicit-post");
  await page.screenshot({ path: `${SHOTS}/c01-s3-explicit-post.png`, fullPage: true });
  await page.evaluate(() => localStorage.removeItem("retrolume.pending-intents.v1"));

  // s4 慢响应超过 3 秒调度的轮询不重叠：A running 使轮询活跃；列表响应慢 3.2s。
  setPhase("s4-poll");
  const peakBeforeS4 = inflightPeak; // 只统计本观察窗（显式动作场景不在本窗内）
  control.slowList = true;
  const beforeS4 = apiCount();
  await page.waitForTimeout(11500); // 观察窗：覆盖慢响应 + 多个 3s tick
  const slice4 = log.slice(beforeS4).filter(item => item.group === "list");
  const sorted = [...slice4].sort((a, b) => a.t_start - b.t_start);
  summary.checks.s4_lists_observed = sorted.length >= 2;
  summary.checks.s4_no_overlap = sorted.every((item, index) => index === 0 || sorted[index - 1].t_end <= item.t_start);
  const slowOne = sorted.find(item => (item.duration_ms ?? 0) > 3000);
  const afterSlow = slowOne ? sorted.filter(item => item.t_start > slowOne.t_start) : [];
  summary.checks.s4_slow_request_seen = Boolean(slowOne);
  summary.checks.s4_tick_skipped_while_inflight = afterSlow.length > 0 && afterSlow.every(item => item.t_start >= (slowOne.t_end ?? 0));
  summary.checks.s4_window_inflight_delta_le_2 = inflightPeak - peakBeforeS4 <= 2;
  (sorted.length >= 2) || summary.failures.push(`s4 list count ${sorted.length}`);
  sorted.every((item, index) => index === 0 || sorted[index - 1].t_end <= item.t_start) || summary.failures.push("s4 overlapping list requests");
  Boolean(slowOne) || summary.failures.push("s4 no slow list request observed");
  (inflightPeak - peakBeforeS4 <= 2) || summary.failures.push(`s4 window inflight delta ${inflightPeak - peakBeforeS4}`);
  summary.timeline_note = JSON.stringify(sorted.map(item => ({ start: item.t_start, end: item.t_end, dur: item.duration_ms })));
  summary.steps.push("s4-poll-no-overlap-slow");
  control.slowList = false;

  // s5 隐藏暂停 / 恢复只 GET。计数按请求发起时刻（t_start）过滤，避免
  // 前序场景在途请求的完成记录污染切片。
  setPhase("s5-visibility");
  await settle(page);
  const s5Start = Date.now();
  await page.evaluate(() => {
    Object.defineProperty(document, "hidden", { configurable: true, get: () => true });
    document.dispatchEvent(new Event("visibilitychange"));
  });
  await page.waitForTimeout(5000); // > 1 个完整轮询周期，证明暂停而非巧合
  const hiddenSlice = log.filter(item => item.t_start >= s5Start);
  summary.checks.s5_hidden_pauses_polling = hiddenSlice.length === 0;
  hiddenSlice.length !== 0 && summary.failures.push(`s5 hidden slice has ${hiddenSlice.length} requests`);
  const resumeStart = Date.now();
  await page.evaluate(() => {
    Object.defineProperty(document, "hidden", { configurable: true, get: () => false });
    document.dispatchEvent(new Event("visibilitychange"));
  });
  await page.waitForTimeout(3000);
  const resumeSlice = log.filter(item => item.t_start >= resumeStart);
  summary.checks.s5_resume_get_only = resumeSlice.length >= 2 && resumeSlice.every(item => item.method === "GET");
  resumeSlice.length < 2 && summary.failures.push(`s5 resume slice only ${resumeSlice.length} requests`);
  summary.steps.push("s5-visibility-pause-resume");

  // s6 迟到结果不串：活动切换 + 展开切换两个上下文。
  // 迟到响应的到达用 waitForResponse 精确锚定，不凭 sleep 猜。
  setPhase("s6-late");
  control.slowOpsFor[AID] = true;
  control.slowSingle["OP-B-SLOW"] = true;
  const aOpsResponse = page.waitForResponse(response => response.url().includes(`/api/activities/${AID}/operations`));
  await page.locator("button.material", { hasText: "活动甲专属资料" }).first().click();
  await page.locator("button.material", { hasText: "活动乙专属资料" }).first().click(); // A 仍在途时切换
  await page.getByText("OP-B-SLOW").waitFor({ timeout: 15000 });
  await aOpsResponse; // A 的迟到 operations 响应已真实派发
  await page.waitForTimeout(300); // 渲染缓冲（非判定依据）
  summary.checks.s6_late_activity_does_not_override = (await page.locator(".ws-operations", { hasText: "OP-A1" }).count()) === 0
    && (await page.locator(".ws-operations", { hasText: "OP-B-SLOW" }).count()) > 0;
  ((await page.locator(".ws-operations", { hasText: "OP-A1" }).count()) === 0) || summary.failures.push("s6 late A ops overrode B panel");
  // 展开迟到：SLOW 展开 → 快速切 FAST → SLOW 迟到正文不覆盖。
  const slowSingleResponse = page.waitForResponse(response => response.url().includes("/operations/OP-B-SLOW"));
  await page.locator("button.ws-op", { hasText: "OP-B-SLOW" }).click();
  await page.locator("button.ws-op", { hasText: "OP-B-FAST" }).click();
  await page.getByText("FAST-正文标记ⓑ").waitFor({ timeout: 15000 });
  await slowSingleResponse; // SLOW 的迟到正文已真实派发
  await page.waitForTimeout(300);
  const detailText = await page.locator(".ws-op-detail").innerText();
  summary.checks.s6_late_payload_does_not_override = detailText.includes("FAST-正文标记ⓑ") && !detailText.includes("SLOW-正文标记ⓐ");
  detailText.includes("SLOW-正文标记ⓐ") && summary.failures.push("s6 slow payload overrode fast panel");
  summary.steps.push("s6-late-result-isolation");
  control.slowOpsFor[AID] = false;
  control.slowSingle["OP-B-SLOW"] = false;
  await page.screenshot({ path: `${SHOTS}/c01-s6-late-isolation.png`, fullPage: true });

  // s7 本次改动直接影响分支：展开取回正文（含转义/多字节）、失效抑制与继续入口。
  setPhase("s7-branches");
  await page.locator("button.material", { hasText: "活动甲专属资料" }).first().click();
  await page.getByText("OP-INVALID").waitFor({ timeout: 15000 });
  await page.locator("button.ws-op", { hasText: "OP-INVALID" }).click();
  await page.getByText("正文已失效").waitFor({ timeout: 15000 });
  summary.checks.s7_invalidated_no_continue_entry = (await page.getByRole("button", { name: "从该成果继续…" }).count()) === 0;
  await page.locator("button.ws-op", { hasText: "OP-A1" }).click();
  await page.getByText("继续正文标记ⓒ").waitFor({ timeout: 15000 });
  summary.checks.s7_expanded_payload_rendered = true;
  summary.checks.s7_committed_has_continue_entry = (await page.getByRole("button", { name: "从该成果继续…" }).count()) > 0;
  ((await page.getByRole("button", { name: "从该成果继续…" }).count()) > 0) || summary.failures.push("s7 continue entry missing");
  summary.steps.push("s7-branches-expanded-invalid");
  await page.screenshot({ path: `${SHOTS}/c01-s7-branches.png`, fullPage: true });

  // s8 卸载清理：轮询活跃时离开页面，卸载后不再发出自动请求。
  setPhase("s8-unmount");
  await settle(page);
  const s8Start = Date.now();
  await page.goto("about:blank");
  await page.waitForTimeout(5000);
  const afterClose = log.filter(item => item.t_start >= s8Start);
  summary.checks.s8_no_requests_after_unmount = afterClose.length === 0;
  afterClose.length !== 0 && summary.failures.push(`s8 unmount slice has ${afterClose.length} requests`);
  summary.steps.push("s8-unmount-cleanup");
  await page.close();

  summary.checks.blocked_empty = summary.blocked.length === 0;
  summary.checks.post_total_is_one = postTotal === 1;
  summary.checks.console_errors_empty = consoleErrors.length === 0 && pageErrors.length === 0;
  (postTotal === 1) || summary.failures.push(`post total ${postTotal}`);
  (summary.blocked.length === 0) || summary.failures.push(`blocked ${JSON.stringify(summary.blocked)}`);
  summary.console_errors = consoleErrors;
  summary.page_errors = pageErrors;
  summary.inflight_peak = inflightPeak;
  summary.ok = summary.failures.length === 0;
} catch (error) {
  summary.failures.push(`exception: ${error && error.stack ? String(error.stack).slice(0, 800) : String(error)}`);
  summary.ok = false;
} finally {
  await browser.close();
  staticServer.close();
  summary.log = log;
  await writeFile(REPORT, JSON.stringify(summary, null, 2) + "\n", "utf-8");
  console.log(JSON.stringify({ ok: summary.ok, steps: summary.steps, checks: summary.checks, failures: summary.failures, inflight_peak: summary.inflightPeak }));
}
