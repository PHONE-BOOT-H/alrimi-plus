"use client";

import { ShieldAlert } from "lucide-react";

import { Button } from "@/components/ui/button";
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from "@/components/ui/sheet";
import { ALLERGENS } from "@/lib/allergens";

export function AllergyPicker({
  value,
  onChange,
}: {
  value: string[];
  onChange: (v: string[]) => void;
}) {
  const toggle = (name: string) => {
    onChange(value.includes(name) ? value.filter((a) => a !== name) : [...value, name]);
  };

  return (
    <Sheet>
      <SheetTrigger asChild>
        <Button variant="outline" size="sm" className="gap-1.5">
          <ShieldAlert className="h-4 w-4 text-destructive" />
          {value.length > 0 ? `내 알레르기 ${value.length}` : "알레르기 설정"}
        </Button>
      </SheetTrigger>
      <SheetContent side="right" className="w-[320px] sm:w-[380px]">
        <SheetHeader>
          <SheetTitle>내 아이 알레르기 설정</SheetTitle>
          <SheetDescription>
            해당하는 항목을 고르면, 급식 답변에 <strong>내 아이가 주의할 식품</strong>을 강조해
            드려요. 이 정보는 <strong>이 기기에만 저장</strong>되고 서버로 보내 저장하지 않습니다.
          </SheetDescription>
        </SheetHeader>

        <div className="mt-6 flex flex-wrap gap-2">
          {ALLERGENS.map((name) => {
            const on = value.includes(name);
            return (
              <button
                key={name}
                type="button"
                onClick={() => toggle(name)}
                className={
                  on
                    ? "rounded-full border border-destructive bg-destructive/10 px-3 py-1.5 text-sm font-medium text-destructive"
                    : "rounded-full border px-3 py-1.5 text-sm text-muted-foreground hover:bg-muted"
                }
                aria-pressed={on}
              >
                {name}
              </button>
            );
          })}
        </div>

        {value.length > 0 && (
          <div className="mt-6 flex items-center justify-between rounded-lg bg-muted/50 p-3 text-sm">
            <span>
              선택: <strong className="text-destructive">{value.join(", ")}</strong>
            </span>
            <Button variant="ghost" size="sm" onClick={() => onChange([])}>
              초기화
            </Button>
          </div>
        )}
      </SheetContent>
    </Sheet>
  );
}
