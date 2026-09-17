import clsx from "clsx";
import type { Severity } from "@/types";

const STYLES: Record<Severity, string> = {
  LOW: "bg-signal-good/10 text-signal-good border-signal-good/30",
  MEDIUM: "bg-signal-medium/10 text-signal-medium border-signal-medium/30",
  HIGH: "bg-signal-high/10 text-signal-high border-signal-high/30",
  CRITICAL: "bg-signal-critical/15 text-signal-critical border-signal-critical/40",
};

export function SeverityBadge({ severity }: { severity: Severity }) {
  return (
    <span
      className={clsx(
        "inline-flex items-center rounded border px-1.5 py-0.5 text-[11px] font-medium tracking-wide",
        STYLES[severity]
      )}
    >
      {severity}
    </span>
  );
}
