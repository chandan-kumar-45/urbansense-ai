import type { LucideIcon } from "lucide-react";
import clsx from "clsx";

interface Props {
  label: string;
  value: string | number;
  icon: LucideIcon;
  tone?: "default" | "good" | "medium" | "high";
  hint?: string;
}

const TONE_STYLES: Record<NonNullable<Props["tone"]>, string> = {
  default: "text-ink",
  good: "text-signal-good",
  medium: "text-signal-medium",
  high: "text-signal-high",
};

export function KpiCard({ label, value, icon: Icon, tone = "default", hint }: Props) {
  return (
    <div className="flex flex-col justify-between rounded-md border border-border bg-panel p-4">
      <div className="flex items-start justify-between">
        <span className="text-xs text-muted">{label}</span>
        <Icon className="h-4 w-4 text-muted" strokeWidth={1.75} />
      </div>
      <div className="mt-3 flex items-baseline gap-2">
        <span className={clsx("font-mono text-2xl font-semibold", TONE_STYLES[tone])}>
          {value}
        </span>
        {hint && <span className="text-[11px] text-muted">{hint}</span>}
      </div>
    </div>
  );
}
