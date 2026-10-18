// 题干和暴露正文只消费同一 workspace 快照，刷新即恢复合法参考。
import type { TeachingWorkspace } from "./teachingApi";

export function TeachingExercise({workspace,onExpose,busy}: {
  workspace: TeachingWorkspace | null; token: string;
  onExpose: (part: "hint" | "reference") => void; busy: boolean;
}) {
  const body=workspace?.exercise;
  if (!body) return <p className="quiet">当前没有练习题。接受路径后可显式获取练习。</p>;
  if (body.qualification!=="current") return <p role="alert">当前题目不可核对：{body.qualification}</p>;
  const dimensions=Array.isArray(body.dimensions)?body.dimensions as {id:string;description:string}[]:[];
  const points=Array.isArray(body.reference_points)?body.reference_points as {point_id:string;text:string}[]:[];
  const disabled=busy||Boolean(workspace?.overlay.cancelled||workspace?.overlay.expired||workspace?.overlay.source_invalid);
  return <div className="ws-exercise" aria-label="当前练习">
    <p className="quiet">题型：{String(body.exercise_type)}</p>
    <p className="ws-exercise-stem">{String(body.stem??"")}</p>
    <ul>{dimensions.map(d=><li key={d.id}>{d.id}：{d.description}</li>)}</ul>
    <button className="secondary" disabled={disabled||Boolean(body.hint_available)} onClick={()=>onExpose("hint")}>查看提示（零费）</button>
    <button className="secondary" disabled={disabled||Boolean(body.reference_available)} onClick={()=>onExpose("reference")}>查看参考要点（零费）</button>
    <p className="quiet">参考与提示单独记录暴露；看过后的同题作答属于辅助观察。</p>
    {Boolean(body.hint_available)&&<p>提示：{String(body.hint??"")}</p>}
    {Boolean(body.reference_available)&&<div aria-label="参考要点"><ul>{points.map(p=><li key={p.point_id}>{p.point_id}：{p.text}</li>)}</ul><p>{String(body.reference_explanation??"")}</p></div>}
  </div>;
}
