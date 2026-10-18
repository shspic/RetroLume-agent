// 当前练习呈现：题干、维度与参考/提示显示状态。参考未暴露时绝不显示正文。
import { useEffect, useRef, useState } from "react";
import { getTeachingRecord, TeachingApiError, type TeachingWorkspace } from "./teachingApi";

export type ExerciseView = {
  recordId: string;
  stem: string;
  exerciseType: string;
  dimensions: { id: string; description: string; point_ids: string[] }[];
  referenceAvailable: boolean;
  hintAvailable: boolean;
  hint?: string;
};

export function TeachingExercise({
  workspace, token, onExpose, busy,
}: {
  workspace: TeachingWorkspace | null;
  token: string;
  onExpose: (part: "hint" | "reference") => void;
  busy: boolean;
}) {
  const [view, setView] = useState<ExerciseView | null>(null);
  const [error, setError] = useState("");
  const seq = useRef(0);

  const exerciseId = workspace?.head.exercise_record_id ?? null;

  useEffect(() => {
    const current = ++seq.current;
    if (!exerciseId) { setView(null); return; }
    setError("");
    void (async () => {
      try {
        const record = await getTeachingRecord(workspace!.activity_id, exerciseId, token);
        if (current !== seq.current) return;
        const body = (record.public_body ?? {}) as Record<string, unknown>;
        setView({
          recordId: exerciseId,
          stem: String(body.stem ?? "（题目正文由受控评价材料装配）"),
          exerciseType: String(body.exercise_type ?? "calculation"),
          dimensions: Array.isArray(body.dimensions)
            ? body.dimensions as ExerciseView["dimensions"] : [],
          referenceAvailable: Boolean(body.reference_available),
          hintAvailable: Boolean(body.hint_available),
          hint: typeof body.hint === "string" ? body.hint : undefined,
        });
      } catch (reason) {
        if (current !== seq.current) return;
        setError(reason instanceof TeachingApiError ? reason.message : "题目读取失败");
      }
    })();
    return () => { /* 切换/卸载后迟到响应不作更新 */ };
  }, [exerciseId, token, workspace?.activity_id]);

  if (!workspace || !exerciseId) {
    return <p className="quiet">当前没有练习题。接受路径后可显式获取练习。</p>;
  }
  return (
    <div className="ws-exercise" aria-label="当前练习">
      <p className="ws-exercise-stem">{view?.stem ?? "正在读取题目…"}</p>
      {view && view.dimensions.length > 0 && (
        <ul className="ws-dimensions">
          {view.dimensions.map(dimension => (
            <li key={dimension.id}>{dimension.id}：{dimension.description}</li>
          ))}
        </ul>
      )}
      {error && <p role="alert" className="failure">{error}</p>}
      <div className="ws-exercise-actions">
        <button
          className="secondary"
          disabled={busy || !view?.hintAvailable}
          onClick={() => onExpose("hint")}
        >查看提示（零费）</button>
        <button
          className="secondary"
          disabled={busy || !view?.referenceAvailable}
          onClick={() => onExpose("reference")}
        >查看参考要点（零费）</button>
      </div>
      <p className="quiet">
        参考与提示单独记录暴露；看过参考后的同题作答只算辅助，不构成独立复测。
      </p>
      {view?.hint && <p className="ws-hint">提示：{view.hint}</p>}
    </div>
  );
}
