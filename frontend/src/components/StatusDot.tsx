import clsx from "clsx";

type Status = "ACTIVE" | "DELAYED" | "INCIDENT" | "OFFLINE" | "ONLINE" | "FAULT";

const COLORS: Record<Status, string> = {
  ACTIVE: "bg-signal-good",
  ONLINE: "bg-signal-good",
  DELAYED: "bg-signal-medium",
  INCIDENT: "bg-signal-high",
  FAULT: "bg-signal-high",
  OFFLINE: "bg-muted",
};

export function StatusDot({ status, label }: { status: Status; label?: string }) {
  return (
    <span className="inline-flex items-center gap-1.5 text-xs text-muted">
      <span className={clsx("h-1.5 w-1.5 rounded-full", COLORS[status])} />
      {label ?? status}
    </span>
  );
}
