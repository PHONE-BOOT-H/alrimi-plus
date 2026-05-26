import Link from "next/link";
import { MessageSquareText, Quote, ShieldAlert, Languages } from "lucide-react";

import { Button } from "@/components/ui/button";

const FEATURES = [
  {
    icon: MessageSquareText,
    title: "학교별 맞춤 답변",
    desc: "우리 학교를 골라 급식·학사일정·공지를 대화로 물어보세요. NEIS 공공데이터를 학교 단위로 검색합니다.",
  },
  {
    icon: Quote,
    title: "출처를 보여주는 AI",
    desc: "지어내지 않습니다. 답변마다 어떤 자료를 근거로 했는지 출처를 함께 표시해요.",
  },
  {
    icon: ShieldAlert,
    title: "알레르기 자동 안내",
    desc: "급식 메뉴의 알레르기 유발 식품을 함께 알려드려요. 알레르기 자녀를 둔 학부모를 위해.",
  },
  {
    icon: Languages,
    title: "한국어·영어 지원",
    desc: "영어로 물으면 영어로 답합니다. 다문화 가정도 우리 학교 정보를 모국어로.",
  },
];

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center">
      {/* Hero */}
      <section className="flex w-full max-w-3xl flex-col items-center gap-6 px-6 pt-24 pb-16 text-center">
        <span className="rounded-full border px-3 py-1 text-xs text-muted-foreground">
          제8회 교육 공공데이터 AI 활용대회 출품작
        </span>
        <h1 className="text-5xl font-bold tracking-tight sm:text-6xl">알리미+</h1>
        <p className="text-xl font-medium text-muted-foreground sm:text-2xl">
          학교알리미가 진짜 <strong className="text-foreground">답하는</strong> 시대
        </p>
        <p className="max-w-xl text-balance text-muted-foreground">
          NEIS·학교알리미·학교 공지를 한 챗봇이 모국어로 답하고, 출처와 알레르기 정보까지
          함께 보여드립니다.
        </p>
        <Link href="/chat">
          <Button size="lg" className="mt-2">
            학교에 물어보기 →
          </Button>
        </Link>
      </section>

      {/* Features */}
      <section className="grid w-full max-w-3xl grid-cols-1 gap-4 px-6 pb-24 sm:grid-cols-2">
        {FEATURES.map(({ icon: Icon, title, desc }) => (
          <div key={title} className="rounded-xl border bg-card p-5 text-left">
            <Icon className="mb-3 h-6 w-6 text-primary" />
            <h3 className="mb-1 font-semibold">{title}</h3>
            <p className="text-sm text-muted-foreground">{desc}</p>
          </div>
        ))}
      </section>

      <footer className="pb-10 text-center text-xs text-muted-foreground">
        공공데이터(NEIS·학교알리미) 기반 · 정확한 정보는 학교에 확인하세요
      </footer>
    </main>
  );
}
