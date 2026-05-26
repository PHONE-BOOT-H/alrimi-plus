import { Badge } from "@/components/ui/badge";
import type { Source } from "@/lib/types";

const SOURCE_LABELS: Record<string, string> = {
  neis_meal: "급식",
  neis_schedule: "학사일정",
  neis_timetable: "시간표",
  schoolinfo: "학교알리미",
  homepage: "학교 홈페이지",
};

export function SourceCitation({ sources }: { sources: Source[] }) {
  if (!sources?.length) return null;
  return (
    <div className="mt-3 border-t pt-2">
      <p className="mb-1.5 text-xs font-medium text-muted-foreground">출처</p>
      <div className="flex flex-col gap-1">
        {sources.map((s) => {
          const label = SOURCE_LABELS[s.source_type] ?? s.source_type;
          const inner = (
            <span className="flex items-start gap-1.5 text-xs">
              <Badge variant="secondary" className="shrink-0">
                [{s.n}] {label}
              </Badge>
              <span className="text-muted-foreground">{s.title}</span>
            </span>
          );
          return s.source_url && s.source_url.startsWith("http") ? (
            <a
              key={s.n}
              href={s.source_url}
              target="_blank"
              rel="noopener noreferrer"
              className="hover:underline"
            >
              {inner}
            </a>
          ) : (
            <div key={s.n}>{inner}</div>
          );
        })}
      </div>
    </div>
  );
}
