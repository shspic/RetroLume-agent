"use strict";
// 真实关口反例固定源码；任何关键反证即停止后续场景。
const host = require("/opt/preview/host.cjs");
const pageHtml = `<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><style>button,a{display:inline-block;margin:8px;padding:8px}</style></head><body>
<p id="h0_ready">关口合成页</p><button id="h0_open">新页</button><a id="h0_blank" href="about:blank" target="_blank">空白新页</a><a id="h0_named" href="about:blank" target="h0_new_target">新命名页</a>
<form action="about:blank" target="_blank"><button id="h0_form">表单新页</button></form>
<button id="h0_data">自身data</button><button id="h0_blob">自身blob</button><button id="h0_hash">同文档导航</button><button id="h0_child">动态frame</button>
<script>window.h0_gestures=[];document.addEventListener('click',e=>window.h0_gestures.push({id:e.target.id,trusted:e.isTrusted,active:navigator.userActivation.isActive}),true);
document.getElementById('h0_open').onclick=()=>{window.h0_opened=window.open('about:blank','_blank')!==null};
document.getElementById('h0_data').onclick=()=>{location.href='data:text/html,<p id="h0_nav_marker">H0_DATA_COMMITTED</p>'};
document.getElementById('h0_blob').onclick=()=>{location.href=URL.createObjectURL(new Blob(['<p id="h0_nav_marker">H0_BLOB_COMMITTED</p>'],{type:'text/html'}))};
document.getElementById('h0_hash').onclick=()=>{location.hash='H0_SAME_DOCUMENT_COMMITTED'};
document.getElementById('h0_child').onclick=()=>{const f=document.createElement('iframe');f.id='H0_NEW_CHILD';document.body.appendChild(f)};
<\/script></body></html>`;
async function main() {
  host.emit("processes_before_launch", host.processFacts());
  const { browser, cdp, targetEvents } = await host.launch();
  const diagnostic = await host.context(browser);
  const diagnosticPage = await diagnostic.newPage();
  await diagnosticPage.goto("chrome://sandbox", { timeout: 2000 });
  host.emit("sandbox_status", { text: (await diagnosticPage.locator("body").innerText()).slice(0, 3000) });
  await diagnostic.close();
  host.emit("processes_with_browser", host.processFacts());
  const control = await host.context(browser);
  const positive = await host.loadFrame(control, pageHtml, true);
  const controlBefore = await host.snapshot(control, cdp);
  const popup = positive.page.waitForEvent("popup", { timeout: 2000 }).catch(() => null);
  await host.trustedClick(positive.page, positive.frame, "h0_open");
  await popup;
  const controlAfter = await host.snapshot(control, cdp);
  const gesture = await positive.frame.evaluate(() => ({ gestures: window.h0_gestures, opened: window.h0_opened }));
  const controlOk = controlAfter.pages.length === controlBefore.pages.length + 1 && gesture.opened === true && gesture.gestures.some(row => row.id === "h0_open" && row.trusted && row.active);
  host.emit("H0_B01_CONTROL", { verdict: controlOk ? "PASS_SUBFACT" : "FAIL", before: controlBefore, after: controlAfter, gesture });
  await control.close();
  if (!controlOk) throw new Error("可信手势成功对照未成立");
  const restricted = await host.context(browser);
  const { page, frame } = await host.loadFrame(restricted, pageHtml);
  for (const id of ["h0_open", "h0_blank", "h0_named", "h0_form"]) {
    const before = await host.snapshot(restricted, cdp); const index = targetEvents.length;
    await host.trustedClick(page, frame, id);
    const after = await host.snapshot(restricted, cdp);
    const delta = targetEvents.slice(index);
    const failed = delta.some(row => row.kind === "created" && ["page", "iframe"].includes(row.type)) || after.pages.length !== before.pages.length || after.targets.length !== before.targets.length;
    host.emit("H0_B01_RESTRICTED", { id, verdict: failed ? "FAIL" : "PASS_SUBFACT", before, after, events: delta });
    if (failed) return { verdict: "FAIL", blocking: id };
  }
  for (const id of ["h0_data", "h0_blob", "h0_hash", "h0_child"]) {
    const before = await host.snapshot(restricted, cdp); const index = targetEvents.length;
    await host.trustedClick(page, frame, id);
    const after = await host.snapshot(restricted, cdp);
    const marker = await page.frames()[1].locator("#h0_nav_marker").textContent({ timeout: 300 }).catch(() => null);
    const failed = JSON.stringify(before.pages) !== JSON.stringify(after.pages) || before.targets.length !== after.targets.length || targetEvents.slice(index).some(row => row.kind === "created" && ["page", "iframe"].includes(row.type));
    host.emit("H0_NAVIGATION", { id, verdict: failed ? "FAIL" : "BLOCKED_IN_THIS_PROBE", before, after, marker, events: targetEvents.slice(index) });
    if (failed) return { verdict: "FAIL", blocking: id, stop_remaining: true };
  }
  return { verdict: "NOT_FULL_H0", blocking: "还须完整关口与同步锚，不能凭此反例批签通过" };
}
main().then(result => {
  host.emit("terminal", result);
  // 留待容器外精确kill；独立控制器固定截止，不等待人工stdin。
  setInterval(() => {}, 1000);
}).catch(error => {
  host.emit("terminal", { verdict: "ERROR", message: String(error.message).slice(0, 2000) });
  setInterval(() => {}, 1000);
});
