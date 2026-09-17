import { AlertTriangle, Car, Construction, Droplets, Radio } from "lucide-react";
import { useLiveEvents } from "@/hooks/useLiveEvents";
import { SeverityBadge } from "./SeverityBadge";
import type { Severity, WsMessage } from "@/types";

const CHANNEL_ICON: Record<WsMessage["channel"], typeof AlertTriangle> = {
  detection_event: Radio,
  road_defect: Construction,
  traffic_event: Car,
  incident: AlertTriangle,
  bus_position: Radio,
};

function describe(msg: WsMessage): { title: string; meta: string; severity?: Severity } {
  const d = msg.data as Record<string, unknown>;
  switch (msg.channel) {
    case "road_defect":
      return {
        title: `${String(d.defect_type).replace("_", " ")} detected`,
        meta: `confidence ${(Number(d.confidence) * 100).toFixed(0)}%`,
        severity: d.severity as Severity,
      };
    case "incident":
      return {
        title: `${String(d.incident_type).replace(/_/g, " ").toLowerCase()}`,
        meta: d.vehicle_number ? `vehicle ${d.vehicle_number}` : "no vehicle identified",
        severity: d.severity as Severity,
      };
    case "traffic_event":
      return {
        title: `Traffic update — ${d.location}`,
        meta: `${d.vehicle_count} vehicles, ${d.congestion_level} congestion`,
      };
    case "bus_position":
      return { title: `Bus ${d.bus_number} position update`, meta: `${d.speed_kmph} km/h` };
    default:
      return {
        title: String(d.event_type ?? "Detection event"),
        meta: `confidence ${(Number(d.confidence ?? 0) * 100).toFixed(0)}%`,
        severity: d.severity as Severity | undefined,
      };
  }
}

export function LiveEventFeed() {
  const { messages, connected } = useLiveEvents(40);

  return (
    <div className="flex h-full flex-col rounded-md border border-border bg-panel">
      <div className="flex items-center justify-between border-b border-border px-4 py-3">
        <h3 className="text-sm font-medium">Live Event Feed</h3>
        <span
          className={`flex items-center gap-1.5 text-[11px] ${
            connected ? "text-signal-good" : "text-muted"
          }`}
        >
          <span
            className={`h-1.5 w-1.5 rounded-full ${
              connected ? "bg-signal-good" : "bg-muted"
            }`}
          />
          {connected ? "Live" : "Reconnecting…"}
        </span>
      </div>

      <div className="flex-1 space-y-2 overflow-y-auto p-3">
        {messages.length === 0 && (
          <p className="mt-6 text-center text-xs text-muted">
            No events yet. Events appear here the instant they're detected —
            try running the demo simulation (Phase 8) or posting to{" "}
            <code className="font-mono">/api/events</code>.
          </p>
        )}
        {messages.map((msg, i) => {
          const Icon = CHANNEL_ICON[msg.channel] ?? Radio;
          const { title, meta, severity } = describe(msg);
          return (
            <div
              key={i}
              className="feed-item-enter flex items-start gap-2.5 rounded border border-border/60 bg-card px-3 py-2"
            >
              <Icon className="mt-0.5 h-3.5 w-3.5 shrink-0 text-signal-info" strokeWidth={1.75} />
              <div className="min-w-0 flex-1">
                <div className="flex items-center justify-between gap-2">
                  <p className="truncate text-xs font-medium capitalize">{title}</p>
                  {severity && <SeverityBadge severity={severity} />}
                </div>
                <p className="mt-0.5 truncate font-mono text-[11px] text-muted">{meta}</p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
