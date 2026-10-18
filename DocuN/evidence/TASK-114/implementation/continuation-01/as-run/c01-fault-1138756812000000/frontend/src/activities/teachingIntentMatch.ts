// 教学意图核对：只确认匹配的持久命令；其他内容不抹去本机意图。

export function compareTeachingIntent(
  summary: { request_sha?: string; action: string; key: string },
  value: unknown,
): "matching" | "conflict" | "unconfirmed" {
  if (typeof value !== "object" || value === null) return "unconfirmed";
  const stored = value as Record<string, unknown>;
  if (typeof stored.request_sha256 !== "string") return "unconfirmed";
  if (String(stored.business_key) !== summary.key || String(stored.action) !== summary.action) {
    return "conflict";
  }
  if (summary.request_sha && stored.request_sha256 === summary.request_sha) return "matching";
  if (summary.request_sha && stored.request_sha256 !== summary.request_sha) return "conflict";
  return "unconfirmed";
}
