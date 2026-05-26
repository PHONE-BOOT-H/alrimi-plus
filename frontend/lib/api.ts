import type { Source } from "./types";

export type ChatEvent =
  | { type: "sources"; sources: Source[] }
  | { type: "delta"; text: string }
  | { type: "done"; model: string }
  | { type: "error"; message: string };

const BACKEND = process.env.NEXT_PUBLIC_BACKEND_URL ?? "";

/** 백엔드 /api/chat NDJSON 스트림을 파싱해 이벤트를 yield. */
export async function* streamChat(
  schoolCode: string,
  question: string,
  language = "ko",
): AsyncGenerator<ChatEvent> {
  const res = await fetch(`${BACKEND}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ school_code: schoolCode, question, language }),
  });

  if (!res.ok || !res.body) {
    yield { type: "error", message: `요청 실패 (HTTP ${res.status})` };
    return;
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buf = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buf += decoder.decode(value, { stream: true });
    let nl: number;
    while ((nl = buf.indexOf("\n")) >= 0) {
      const line = buf.slice(0, nl).trim();
      buf = buf.slice(nl + 1);
      if (line) {
        try {
          yield JSON.parse(line) as ChatEvent;
        } catch {
          /* 부분 라인 무시 */
        }
      }
    }
  }
  const rest = buf.trim();
  if (rest) {
    try {
      yield JSON.parse(rest) as ChatEvent;
    } catch {
      /* ignore */
    }
  }
}
