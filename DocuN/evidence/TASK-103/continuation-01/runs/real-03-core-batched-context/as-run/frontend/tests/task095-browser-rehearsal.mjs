// TASK-095 离线彩排：验证浏览器可启动、工作区渲染与存储未就绪文案（不触碰 PG/容器）。
import { chromium } from "playwright";

const APP = process.env.APP_URL ?? "http://127.0.0.1:18095";
const summary = { ok: false, console_errors: [], steps: [] };
const errors = [];
try {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  page.on("pageerror", error => errors.push(String(error)));
  page.on("console", message => { if (message.type() === "error") errors.push(message.text()); });
  await page.goto(APP, { waitUntil: "domcontentloaded" });
  await page.locator("nav div", { hasText: "学习活动" }).click();
  await page.getByText("读取与取消：").waitFor({ timeout: 10000 });
  await page.getByText("新建活动：").waitFor({ timeout: 10000 });
  summary.steps.push("workspace-rendered");
  const storage = await page.locator(".ws-cap").first().innerText();
  summary.storage_line = storage;
  await page.locator("nav div", { hasText: "我的资料" }).click();
  await page.getByText("我的资料").first().waitFor({ timeout: 10000 });
  summary.steps.push("materials-view-ok");
  await page.screenshot({ path: process.env.SHOT ?? "rehearsal.png" });
  await browser.close();
  summary.ok = errors.length === 0;
  summary.console_errors = errors;
} catch (reason) {
  summary.error = String(reason);
  summary.console_errors = errors;
}
console.log(JSON.stringify(summary));
process.exit(summary.ok ? 0 : 1);
