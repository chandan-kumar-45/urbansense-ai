import { useEffect, useState } from "react";
import { SeverityBadge } from "@/components/SeverityBadge";
import { getIncidents, updateIncident } from "@/services/data";
import type { EventStatus, Incident } from "@/types";

const STATUS_FLOW: EventStatus[] = ["NEW", "ACKNOWLEDGED", "INVESTIGATING", "RESOLVED"];

export function IncidentCenter() {
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [statusFilter, setStatusFilter] = useState<string>("ALL");
  const [error, setError] = useState<string | null>(null);

  function load() {
    getIncidents(statusFilter === "ALL" ? {} : { status: statusFilter })
      .then(setIncidents)
      .catch((e) => setError(e.message));
  }

  useEffect(load, [statusFilter]);

  async function advanceStatus(incident: Incident) {
    const idx = STATUS_FLOW.indexOf(incident.status);
    const next = STATUS_FLOW[Math.min(idx + 1, STATUS_FLOW.length - 1)];
    await updateIncident(incident.id, { status: next });
    load();
  }

  if (error) {
    return (
      <div className="rounded-md border border-signal-high/30 bg-signal-high/10 p-4 text-sm text-signal-high">
        {error}. This page requires an Admin, Traffic Officer, or Transport
        Authority role.
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2">
        {["ALL", ...STATUS_FLOW].map((s) => (
          <button
            key={s}
            onClick={() => setStatusFilter(s)}
            className={`rounded px-3 py-1.5 text-xs ${
              statusFilter === s ? "bg-card text-ink" : "text-muted hover:text-ink"
            }`}
          >
            {s}
          </button>
        ))}
      </div>

      <div className="space-y-2">
        {incidents.length === 0 && (
          <p className="py-10 text-center text-xs text-muted">
            No incidents in this status. Try starting the fleet simulation.
          </p>
        )}
        {incidents.map((i) => (
          <div
            key={i.id}
            className="flex items-center justify-between rounded-md border border-border bg-panel px-4 py-3"
          >
            <div className="flex items-center gap-3">
              <SeverityBadge severity={i.severity} />
              <div>
                <p className="text-sm capitalize">{i.incident_type.replace(/_/g, " ").toLowerCase()}</p>
                <p className="font-mono text-[11px] text-muted">
                  {new Date(i.timestamp).toLocaleString()} · {i.latitude.toFixed(4)}, {i.longitude.toFixed(4)}
                  {i.vehicle_number ? ` · ${i.vehicle_number}` : ""}
                  {i.is_demo ? " · DEMO" : ""}
                </p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <span className="text-xs text-muted">{i.status}</span>
              {i.status !== "RESOLVED" && (
                <button
                  onClick={() => advanceStatus(i)}
                  className="rounded border border-border px-3 py-1.5 text-xs hover:bg-card"
                >
                  Advance
                </button>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
