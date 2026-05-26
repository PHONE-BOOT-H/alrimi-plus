"use client";

import { useEffect, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import { Send, School as SchoolIcon, Loader2 } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { SourceCitation } from "@/components/SourceCitation";
import { fetchSchools, streamChat } from "@/lib/api";
import type { ChatMessage, School } from "@/lib/types";

// 시작 화면 추천 질문
const SUGGESTIONS = [
  "이번 주 급식 메뉴 알려줘",
  "급식에 우유 들어간 메뉴 있어?",
  "다가오는 학사일정이나 행사 있어?",
  "5월 급식 중에 알레르기 조심할 메뉴는?",
];

// 답변 후 "이어서 물어보기" 추천 질문 (사용자가 막히지 않도록)
const FOLLOWUPS = [
  "다른 날 급식도 알려줘",
  "이 메뉴 열량은 얼마야?",
  "땅콩·견과류 알레르기 메뉴 있어?",
  "시험이나 방학 일정 알려줘",
  "이번 달 학교 행사 정리해줘",
];

export function ChatInterface() {
  const [schools, setSchools] = useState<School[]>([]);
  const [school, setSchool] = useState<School | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [streaming, setStreaming] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    fetchSchools().then((data) => {
      setSchools(data);
      if (data.length) setSchool(data[0]);
    });
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function send(question: string) {
    const q = question.trim();
    if (!q || !school || streaming) return;
    setInput("");
    setMessages((m) => [...m, { role: "user", content: q }, { role: "assistant", content: "" }]);
    setStreaming(true);

    try {
      for await (const ev of streamChat(school.school_code, q)) {
        if (ev.type === "sources") {
          setMessages((m) => {
            const next = [...m];
            next[next.length - 1] = { ...next[next.length - 1], sources: ev.sources };
            return next;
          });
        } else if (ev.type === "delta") {
          setMessages((m) => {
            const next = [...m];
            const last = next[next.length - 1];
            next[next.length - 1] = { ...last, content: last.content + ev.text };
            return next;
          });
        } else if (ev.type === "done") {
          setMessages((m) => {
            const next = [...m];
            next[next.length - 1] = { ...next[next.length - 1], model: ev.model };
            return next;
          });
        } else if (ev.type === "error") {
          setMessages((m) => {
            const next = [...m];
            next[next.length - 1] = {
              ...next[next.length - 1],
              content: `⚠️ ${ev.message}`,
            };
            return next;
          });
        }
      }
    } catch {
      setMessages((m) => {
        const next = [...m];
        next[next.length - 1] = {
          ...next[next.length - 1],
          content: "⚠️ 백엔드에 연결하지 못했어요. 잠시 후 다시 시도해 주세요.",
        };
        return next;
      });
    } finally {
      setStreaming(false);
    }
  }

  return (
    <div className="mx-auto flex h-[calc(100vh-2rem)] max-w-2xl flex-col gap-3 p-4">
      {/* 헤더 + 학교 선택 */}
      <div className="flex items-center gap-2">
        <SchoolIcon className="h-5 w-5 text-primary" />
        <Select
          value={school?.school_code}
          onValueChange={(code) =>
            setSchool(schools.find((s) => s.school_code === code) ?? null)
          }
        >
          <SelectTrigger className="w-full">
            <SelectValue placeholder="학교를 선택하세요" />
          </SelectTrigger>
          <SelectContent>
            {schools.map((s) => (
              <SelectItem key={s.school_code} value={s.school_code}>
                {s.school_name} {s.region ? `· ${s.region}` : ""}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* 메시지 영역 */}
      <div className="flex-1 overflow-y-auto rounded-lg border bg-muted/30 p-4">
        {messages.length === 0 ? (
          <div className="flex h-full flex-col items-center justify-center gap-4 text-center">
            <p className="text-lg font-semibold">알리미+에게 물어보세요</p>
            <p className="max-w-sm text-sm text-muted-foreground">
              선택한 학교의 급식·학사일정·공지를 출처와 함께 알려드려요.
            </p>
            <div className="flex flex-wrap justify-center gap-2">
              {SUGGESTIONS.map((s) => (
                <Button key={s} variant="outline" size="sm" onClick={() => send(s)}>
                  {s}
                </Button>
              ))}
            </div>
          </div>
        ) : (
          <div className="flex flex-col gap-4">
            {messages.map((m, i) => (
              <div
                key={i}
                className={m.role === "user" ? "flex justify-end" : "flex justify-start"}
              >
                <div
                  className={
                    m.role === "user"
                      ? "max-w-[85%] rounded-2xl bg-primary px-4 py-2 text-primary-foreground"
                      : "max-w-[90%] rounded-2xl bg-background px-4 py-3 shadow-sm"
                  }
                >
                  {m.role === "assistant" && !m.content ? (
                    <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />
                  ) : (
                    <div className="prose prose-sm max-w-none break-words dark:prose-invert">
                      <ReactMarkdown>{m.content}</ReactMarkdown>
                    </div>
                  )}
                  {m.role === "assistant" && m.sources && (
                    <SourceCitation sources={m.sources} />
                  )}
                </div>
              </div>
            ))}
            {!streaming &&
              messages[messages.length - 1]?.role === "assistant" &&
              messages[messages.length - 1]?.content && (
                <div className="flex flex-col gap-2 pt-1">
                  <p className="text-xs text-muted-foreground">💡 이어서 물어보기</p>
                  <div className="flex flex-wrap gap-2">
                    {FOLLOWUPS.map((s) => (
                      <Button
                        key={s}
                        variant="outline"
                        size="sm"
                        className="h-auto whitespace-normal py-1.5 text-left"
                        onClick={() => send(s)}
                      >
                        {s}
                      </Button>
                    ))}
                  </div>
                </div>
              )}
            <div ref={bottomRef} />
          </div>
        )}
      </div>

      {/* 입력 */}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          send(input);
        }}
        className="flex items-end gap-2"
      >
        <Textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              send(input);
            }
          }}
          placeholder={school ? "급식·학사일정·공지를 물어보세요…" : "먼저 학교를 선택하세요"}
          disabled={!school || streaming}
          rows={1}
          className="max-h-32 min-h-[44px] resize-none"
        />
        <Button type="submit" size="icon" disabled={!school || streaming || !input.trim()}>
          {streaming ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
        </Button>
      </form>
    </div>
  );
}
