// TASK-095 批次最终浏览器工作区检查：能力分层、界面新建/取消、响应丢失恢复、
// 409 核验、同键显式重试、无自动重发、损坏台账闸门、原资料与PDF分支最小回归。
// 环境：APP_URL、SHOT_DIR、WS_TITLE、UPLOAD_MD、UPLOAD_BAD_PDF。
import { chromium } from "playwright";

const APP = process.env.APP_URL ?? "http://127.0.0.1:18095";
const SHOTS = process.env.SHOT_DIR ?? ".";
const WS = process.env.WS_TITLE ?? "TASK095-WS";
const UPLOAD_MD = process.env.UPLOAD_MD ?? "";
const UPLOAD_BAD_PDF = process.env.UPLOAD_BAD_PDF ?? "";
const summary = { ok: false, steps: [], console_errors: [], expected_network_errors: [], counts: {} };
const consoleErrors = [];
const pageErrors = [];

try {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  page.on("pageerror", error => pageErrors.push(String(error)));
  page.on("console", message => { if (message.type() === "error") consoleErrors.push(message.text()); });

  // 单一路由槽位：mode 控制每段行为；hits 记录 POST 命中，证明无自动重发。
  let mode = "off";
  let hits = 0;
  await page.route("**/api/activities", async route => {
    if (route.request().method() !== "POST") return route.continue();
    hits += 1;
    if (mode === "hold" && hits === 1) {
      const response = await route.fetch();
      await new Promise(resolve => setTimeout(resolve, 4000));
      try { await route.fulfill({ response }); } catch { /* 页面已刷新，响应丢弃 */ }
    } else if (mode === "abort" && hits === 1) {
      await route.abort("failed");
    } else {
      await route.continue();
    }
  });

  const pick = async () => page.locator(".ws-pick-row", { hasText: WS }).locator("input").check();

  // s1 能力分层。
  await page.goto(APP, { waitUntil: "domcontentloaded" });
  await page.locator("nav div", { hasText: "学习活动" }).click();
  await page.getByText("读取与取消：可用").waitFor({ timeout: 15000 });
  await page.getByText("新建活动：可用").waitFor({ timeout: 15000 });
  await page.getByText("显式继续：可用").waitFor({ timeout: 15000 });
  summary.steps.push("capabilities-layers");
  await page.screenshot({ path: `${SHOTS}/workspace-capabilities.png`, fullPage: true });

  // s2 界面新建。
  await page.locator(".ws-pick-row", { hasText: WS }).first().waitFor({ timeout: 15000 });
  await pick();
  await page.getByRole("button", { name: "创建活动" }).click();
  await page.getByText("活动已创建").waitFor({ timeout: 20000 });
  await page.getByText("尚无操作。此版本等待学习入口接入").waitFor({ timeout: 15000 });
  await page.screenshot({ path: `${SHOTS}/workspace-created.png`, fullPage: true });
  summary.steps.push("ui-create");

  // s3 响应丢失（服务端已成功、浏览器未收到）→ 刷新横幅 → 同键重试触发 409 核验。
  mode = "hold"; hits = 0;
  await pick();
  await page.getByRole("button", { name: "创建活动" }).click();
  await page.waitForTimeout(1000);
  await page.reload({ waitUntil: "domcontentloaded" });
  await page.locator("nav div", { hasText: "学习活动" }).click();
  await page.getByText("上次动作未确认").waitFor({ timeout: 15000 });
  await page.screenshot({ path: `${SHOTS}/workspace-lost-response-banner.png`, fullPage: true });
  summary.steps.push("lost-response-banner");
  await page.getByRole("button", { name: "重新提交同一意图" }).first().click();
  await page.getByText("已核对该活动与意图的资料范围一致").waitFor({ timeout: 30000 });
  await page.screenshot({ path: `${SHOTS}/workspace-conflict-verified.png`, fullPage: true });
  summary.counts.hold_flow_posts = hits;
  summary.steps.push("409-verify-after-lost-response");
  mode = "off"; hits = 0;

  // s4 请求未到达（网络失败）→ 核对（只读）404 提示 → 显式同键重试成功。
  mode = "abort"; hits = 0;
  await pick();
  await page.getByRole("button", { name: "创建活动" }).click();
  await page.getByText("动作结果未确认").waitFor({ timeout: 20000 });
  await page.screenshot({ path: `${SHOTS}/workspace-unconfirmed.png`, fullPage: true });
  await page.getByRole("button", { name: "核对（只读）" }).first().click();
  await page.getByText("尚未发现该动作已开始的记录").waitFor({ timeout: 20000 });
  await page.getByRole("button", { name: "重新提交同一意图" }).first().click();
  await page.getByText("活动已创建").waitFor({ timeout: 20000 });
  summary.counts.abort_flow_posts = hits;
  summary.steps.push("explicit-same-key-retry");
  mode = "off"; hits = 0;
  if (summary.counts.abort_flow_posts !== 2 || summary.counts.hold_flow_posts !== 2) {
    throw new Error(`unexpected POST counts: ${JSON.stringify(summary.counts)}`);
  }

  // s5 取消（当前选中活动，两步确认）。
  await page.getByRole("button", { name: "取消活动" }).click();
  await page.getByRole("button", { name: "确认取消" }).click();
  await page.getByText("已取消：不会再开始新动作").waitFor({ timeout: 20000 });
  await page.screenshot({ path: `${SHOTS}/workspace-cancelled.png`, fullPage: true });
  summary.steps.push("cancel-two-step");

  // s6 台账损坏闸门：阻止依赖恢复的新写动作；可清除恢复；读取不受影响。
  await page.evaluate(() => localStorage.setItem("retrolume.pending-intents.v1", "{{{"));
  await page.reload({ waitUntil: "domcontentloaded" });
  await page.locator("nav div", { hasText: "学习活动" }).click();
  await page.getByText("本机恢复记录不可用或已损坏").waitFor({ timeout: 15000 });
  await pick();
  await page.getByRole("button", { name: "创建活动" }).click();
  await page.getByText("恢复记录不可用：为避免出现无法核对的重复动作，新建已暂停").waitFor({ timeout: 15000 });
  await page.screenshot({ path: `${SHOTS}/workspace-corrupt-ledger-gate.png`, fullPage: true });
  await page.getByRole("button", { name: "清除恢复记录" }).click();
  await page.getByText("本机恢复记录不可用或已损坏").waitFor({ state: "hidden", timeout: 15000 });
  summary.steps.push("corrupt-ledger-gate");

  // s7 原资料与 PDF 分支最小回归（上传成功、正文可读、坏 PDF 得到具体原因）。
  await page.locator("nav div", { hasText: "我的资料" }).click();
  await page.locator('input[type="file"]').first().setInputFiles(UPLOAD_MD);
  await page.getByText("已保存").first().waitFor({ timeout: 30000 });
  await page.locator("button.material", { hasText: "task095-upload" }).first().click();
  await page.getByText("回归正文内容-095").waitFor({ timeout: 20000 });
  summary.steps.push("materials-upload-read");
  await page.locator('input[type="file"]').first().setInputFiles(UPLOAD_BAD_PDF);
  await page.getByText("PDF损坏或格式无效").first().waitFor({ timeout: 40000 });
  summary.steps.push("pdf-branch-reason");
  await page.screenshot({ path: `${SHOTS}/materials-regression.png`, fullPage: true });

  await browser.close();
  const expected = consoleErrors.filter(text => /Failed to load resource|ERR_FAILED|Failed to fetch/i.test(text));
  const unexpected = consoleErrors.filter(text => !expected.includes(text));
  summary.expected_network_errors = expected;
  summary.console_errors = unexpected;
  summary.page_errors = pageErrors;
  summary.ok = unexpected.length === 0 && pageErrors.length === 0;
} catch (reason) {
  summary.error = String(reason);
  summary.console_errors = consoleErrors;
  summary.page_errors = pageErrors;
}
console.log(JSON.stringify(summary));
process.exit(summary.ok ? 0 : 1);
