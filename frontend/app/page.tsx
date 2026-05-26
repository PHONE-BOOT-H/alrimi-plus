import Link from "next/link";
import { Button } from "@/components/ui/button";

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center gap-8 p-8">
      <h1 className="text-5xl font-bold">알리미+</h1>
      <p className="text-xl text-muted-foreground">
        학교알리미가 진짜 <strong>답하는</strong> 시대
      </p>
      <p className="max-w-xl text-center text-muted-foreground">
        NEIS·학교알리미·학교 공지를 한 챗봇이 모국어로 답하고, 출처까지 보여드립니다.
      </p>
      <Link href="/chat">
        <Button size="lg">학교에 물어보기 →</Button>
      </Link>
    </main>
  );
}
