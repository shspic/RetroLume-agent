// 四类反馈分开展示：正确部分 / 实际错误 / 缺证据 / 原因假设，
// 逐维度观察与下一步建议；不显示长期掌握，不把假设写成确定缺陷。
import type { TeachingWorkspace } from "./teachingApi";
import { TeachingCitations } from "./TeachingCitations";

export type FeedbackView = {
  correctParts: { answer_excerpt: string; explanation: string; citations: string[] }[];
  errors: { answer_excerpt: string; explanation: string; citations: string[] }[];
  evidenceGaps: { answer_excerpt: string; explanation: string; citations: string[] }[];
  causeHypotheses: { hypothesis: string; evidence_for: string; confidence: string }[];
  observations: { id: string; observation: string; reason: string }[];
  nextFocus: { focus_dimension: string; reason: string; suggested_mode: string } | null;
};

const EMPTY: FeedbackView = {
  correctParts: [], errors: [], evidenceGaps: [], causeHypotheses: [],
  observations: [], nextFocus: null,
};

export function TeachingFeedback({
  workspace, feedback, token,
}: {
  workspace: TeachingWorkspace | null;
  feedback: FeedbackView | null;
  token: string;
}) {
  if (!workspace || !feedback) {
    return <p className="quiet">当前没有评价结果。保存作答后可显式请求评价（1 次模型）。</p>;
  }
  const groups: { title: string; items: FeedbackView["correctParts"]; tone: string }[] = [
    { title: "正确部分", items: feedback.correctParts, tone: "ok" },
    { title: "实际错误", items: feedback.errors, tone: "failure" },
    { title: "证据不足", items: feedback.evidenceGaps, tone: "quiet" },
  ];
  return (
    <div className="ws-feedback" aria-label="评价结果">
      {groups.map(group => (
        <div key={group.title} className={`ws-feedback-group ws-${group.tone}`}>
          <h5>{group.title}</h5>
          {group.items.length === 0 && <p className="quiet">本次未记录。</p>}
          {group.items.map((item, index) => (
            <div key={`${group.title}-${index}`}>
              <p>「{item.answer_excerpt}」——{item.explanation}</p>
              <TeachingCitations activityId={workspace.activity_id} recordId={workspace.feedback?.record_id}
                ids={item.citations} token={token} label={`${group.title} ${index + 1}`} />
            </div>
          ))}
        </div>
      ))}
      <div className="ws-feedback-group ws-quiet">
        <h5>原因假设（用户/模型补充，不是已验证事实）</h5>
        {feedback.causeHypotheses.length === 0 && <p className="quiet">本次未记录。</p>}
        {feedback.causeHypotheses.map((item, index) => (
          <p key={`hyp-${index}`}>
            {item.hypothesis}（{item.confidence === "tentative" ? "待验证" : "未知"}）——依据：{item.evidence_for}
          </p>
        ))}
      </div>
      <div className="ws-feedback-group">
        <h5>逐维度观察</h5>
        {feedback.observations.map(item => (
          <p key={item.id}>
            {item.id}：{observationText(item.observation)}——{item.reason}
          </p>
        ))}
      </div>
      {feedback.nextFocus && (
        <p className="quiet">
          下一步建议：{feedback.nextFocus.focus_dimension}（{modeText(feedback.nextFocus.suggested_mode)}）——{feedback.nextFocus.reason}
        </p>
      )}
      <p className="quiet">
        反馈只表达"按当前评价已有有限证据"，不代表长期掌握；两个不同练习的未暴露独立作答都满足才可能前进。
      </p>
    </div>
  );
}

function observationText(value: string): string {
  switch (value) {
    case "met": return "本次有据满足";
    case "partial": return "部分满足";
    case "not_met": return "不满足";
    case "unknown": return "未知";
    default: return value;
  }
}

function modeText(value: string): string {
  switch (value) {
    case "continuation": return "针对续答";
    case "retest": return "新实例复测";
    case "review": return "复习";
    default: return value;
  }
}
