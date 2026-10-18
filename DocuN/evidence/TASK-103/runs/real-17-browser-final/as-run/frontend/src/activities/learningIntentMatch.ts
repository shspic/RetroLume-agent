// 核对只能确认匹配的持久输入；发现其他目标不抹去本机意图。
import type { PendingIntent } from "./pendingIntents";

export function compareLearningIntent(intent: PendingIntent, value: unknown): "matching" | "conflict" | "unconfirmed" {
  if (typeof value !== "object" || value === null) return "unconfirmed";
  const stored = value as Record<string, unknown>;
  if (stored.profile !== "learning.v1") return "unconfirmed";
  if (intent.kind === "learning_first") {
    return stored.action === "first" && stored.goal === intent.goal?.trim() ? "matching" : "conflict";
  }
  if (intent.kind === "learning_followup") {
    return stored.action === "followup" && stored.question === intent.followup?.trim()
      && stored.parent_operation_id === intent.parent_operation_id ? "matching" : "conflict";
  }
  return "unconfirmed";
}
