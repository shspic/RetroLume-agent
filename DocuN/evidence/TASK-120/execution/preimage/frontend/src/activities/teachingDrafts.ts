// 教学命令的完整待发正文构造与本地 canonical 化。
// 客户端按与服务端相同的规范对象计算 request 摘要，核对时重算比对。

import type { TeachingCommandInput } from "./teachingApi";

async function sha256Hex(text: string): Promise<string> {
  const bytes = new TextEncoder().encode(text);
  const digest = await crypto.subtle.digest("SHA-256", bytes);
  return Array.from(new Uint8Array(digest)).map(b => b.toString(16).padStart(2, "0")).join("");
}

function canonical(value: unknown): string {
  const keys: string[] = [];
  const collect = (item: unknown) => {
    if (Array.isArray(item)) { item.forEach(collect); return; }
    if (typeof item === "object" && item !== null) {
      Object.keys(item as Record<string, unknown>).sort().forEach(k => keys.push(k));
      Object.values(item as Record<string, unknown>).forEach(collect);
    }
  };
  collect(value);
  // 直接用 JSON.stringify 的稳定实现：服务端 sort_keys + 紧凑分隔符。
  return stableStringify(value);
}

function stableStringify(value: unknown): string {
  if (value === null || typeof value !== "object") return JSON.stringify(value);
  if (Array.isArray(value)) return `[${value.map(stableStringify).join(",")}]`;
  const entries = Object.entries(value as Record<string, unknown>)
    .filter(([, v]) => v !== undefined)
    .sort(([a], [b]) => (a < b ? -1 : a > b ? 1 : 0));
  return `{${entries.map(([k, v]) => `${JSON.stringify(k)}:${stableStringify(v)}`).join(",")}}`;
}

export async function buildTeachingCommand(
  activityId: string,
  input: Omit<TeachingCommandInput, "body"> & { body: Record<string, unknown> },
): Promise<{ command: TeachingCommandInput; request_sha256: string; request_body: string }> {
  const requestBody = {
    activity_id: activityId,
    action: input.action,
    expected_revision: input.expected_revision,
    expected_goal_version: input.expected_goal_version,
    expected_scope_revision: input.expected_scope_revision,
    body: input.body,
    ...(input.retrieval_ref?{retrieval_ref:input.retrieval_ref}:{}),
  };
  const request_body = canonical(requestBody);
  const request_sha256 = await sha256Hex(request_body);
  return { command: input, request_sha256, request_body };
}

export function newTeachingKey(): string {
  return crypto.randomUUID();
}
