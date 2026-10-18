// TASK-095 最终批次浏览器步骤（只读查看）：真实浏览器打开工作区，查看既有 Windows 链
// 提交的继续成果（正文按单操作读取补全）与预算事实，不触发任何新监督。
// 环境：APP_URL、TITLE_MATCH、OP_ID、SHOT_DIR。
import { chromium } from "playwright";

const APP = process.env.APP_URL ?? "http://127.0.0.1:18095";
const PARENT = process.env.OP_ID ?? "ui-cont-b2-1";
const TITLE = process.env.TITLE_MATCH ?? "TASK095";
const SHOTS = process.env.SHOT_DIR ?? ".";
const summary = { ok: false, console_errors: [], steps: [] };
const errors = [];

try {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  page.on("pageerror", error => errors.push(String(error)));
  page.on("console", message => { if (message.type() === "error") errors.push(message.text()); });

  await page.goto(APP, { waitUntil: "domcontentloaded" });
  await page.locator("nav div", { hasText: "学习活动" }).click();
  await page.locator("button.material", { hasText: TITLE }).first().waitFor({ timeout: 15000 });
  summary.steps.push("workspace-list-visible");

  await page.locator("button.material", { hasText: TITLE }).first().click();
  await page.locator(".ws-op", { hasText: PARENT }).first().waitFor({ timeout: 15000 });
  await page.screenshot({ path: `${SHOTS}/continue-detail.png`, fullPage: true });

  // 展开既有操作：列表不携正文，展开时按单操作读取补全（仅读取）。
  await page.locator(".ws-op", { hasText: PARENT }).first().click();
  await page.locator(".ws-op-detail pre").first().waitFor({ timeout: 15000 });
  const payloadText = await page.locator(".ws-op-detail pre").first().innerText();
  if (!payloadText.includes("synthetic-continue-095")) throw new Error("committed payload not visible");
  summary.steps.push("committed-payload-visible");
  const statusLine = await page.locator(".ws-op", { hasText: PARENT }).first().innerText();
  summary.operation_status_line = statusLine;
  await page.screenshot({ path: `${SHOTS}/continue-payload.png`, fullPage: true });

  await browser.close();
  summary.ok = errors.length === 0;
  summary.console_errors = errors;
} catch (reason) {
  summary.error = String(reason);
  summary.console_errors = errors;
}
console.log(JSON.stringify(summary));
process.exit(summary.ok ? 0 : 1);
