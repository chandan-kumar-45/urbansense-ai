import { Fragment, useEffect, useState } from "react";
import { Bus as BusIcon, Camera as CameraIcon, Gauge, Play, Radio, Square } from "lucide-react";
import { CommandMap, coloredDivIcon, type MapMarker } from "@/maps/CommandMap";
import { KpiCard } from "@/components/KpiCard";
import { StatusDot } from "@/components/StatusDot";
import { captureCamera, getBuses } from "@/services/data";
import { getSimulationStatus, startSimulation, stopSimulation, type SimulationStatus } from "@/services/simulation";
import { useLiveEvents } from "@/hooks/useLiveEvents";
import type { Bus } from "@/types";

const STATUS_COLOR: Record<string, string> = {
  ACTIVE: "#3ED598",
  DELAYED: "#F2B84B",
  INCIDENT: "#FF6B5E",
  OFFLINE: "#7C8AA5",
};

export function LiveFleet() {
  const [buses, setBuses] = useState<Bus[]>([]);
  const [sim, setSim] = useState<SimulationStatus | null>(null);
  const [busy, setBusy] = useState(false);
  const [expanded, setExpanded] = useState<string | null>(null);
  const [captureResult, setCaptureResult] = useState<Record<string, string>>({});
  const { messages } = useLiveEvents(200);

  async function refresh() {
    const [b, s] = await Promise.all([getBuses(), getSimulationStatus()]);
    setBuses(b);
    setSim(s);
  }

  useEffect(() => {
    refresh();
    const id = setInterval(refresh, 4000);
    return () => clearInterval(id);
  }, []);

  // Apply live bus_position messages on top of the polled snapshot for smoother movement.
  const positions = new Map(buses.map((b) => [b.id, b]));
  for (const msg of [...messages].reverse()) {
    if (msg.channel === "bus_position") {
      const d = msg.data as Bus;
      const existing = positions.get(d.id);
      if (existing) positions.set(d.id, { ...existing, ...d });
    }
  }
  const liveBuses = Array.from(positions.values());

  const markers: MapMarker[] = liveBuses
    .filter((b) => b.latitude && b.longitude)
    .map((b) => ({
      id: b.id,
      lat: b.latitude!,
      lng: b.longitude!,
      icon: coloredDivIcon(STATUS_COLOR[b.status] ?? "#7C8AA5", "B"),
      popup: (
        <div className="font-sans text-xs">
          <p className="font-medium">{b.bus_number}</p>
          <p className="text-muted">{b.route}</p>
          <p className="mt-1 font-mono">{b.speed_kmph} km/h · {b.status}</p>
        </div>
      ),
    }));

  async function toggleSimulation() {
    setBusy(true);
    try {
      if (sim?.running) await stopSimulation();
      else await startSimulation();
      await refresh();
    } finally {
      setBusy(false);
    }
  }

  async function handleCapture(busId: string, cameraId: string, label: string) {
    const key = `${busId}:${cameraId}`;
    setCaptureResult((prev) => ({ ...prev, [key]: "Capturing…" }));
    try {
      const defects = await captureCamera(busId, cameraId);
      setCaptureResult((prev) => ({
        ...prev,
        [key]:
          defects.length === 0
            ? `${label}: clean — no defect found`
            : `${label}: ${defects.length} detection(s) — ${defects[0].defect_type} (${(defects[0].confidence * 100).toFixed(0)}%)`,
      }));
    } catch {
      setCaptureResult((prev) => ({ ...prev, [key]: `${label}: capture failed` }));
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between rounded-md border border-border bg-panel p-4">
        <div className="flex items-center gap-3">
          <Radio className={`h-4 w-4 ${sim?.running ? "text-signal-good" : "text-muted"}`} />
          <div>
            <p className="text-sm font-medium">
              {sim?.running ? "Live simulation running" : "Simulation stopped"}
            </p>
            <p className="text-[11px] text-muted">
              DEMO / SIMULATED DATA — moves buses along fixed routes. Each bus's
              4 cameras periodically capture and run through the real
              road-damage model via the AI Model Registry (see docs).
            </p>
          </div>
        </div>
        <button
          onClick={toggleSimulation}
          disabled={busy}
          className="flex items-center gap-2 rounded bg-signal-info px-4 py-2 text-sm font-medium text-base transition-opacity hover:opacity-90 disabled:opacity-50"
        >
          {sim?.running ? <Square className="h-3.5 w-3.5" /> : <Play className="h-3.5 w-3.5" />}
          {sim?.running ? "Stop Live Simulation" : "Start Live Simulation"}
        </button>
      </div>

      <div className="grid grid-cols-3 gap-3">
        <KpiCard label="Buses Tracked" value={liveBuses.length} icon={BusIcon} tone="good" />
        <KpiCard
          label="Events Generated (session)"
          value={sim?.events_generated ?? 0}
          icon={Radio}
        />
        <KpiCard
          label="Bandwidth Saved"
          value={`${sim?.bandwidth_saved_percent ?? 0}%`}
          icon={Gauge}
          tone="good"
          hint="simulated estimate"
        />
      </div>

      <CommandMap markers={markers} />

      <div className="rounded-md border border-border bg-panel">
        <div className="border-b border-border px-4 py-3">
          <h3 className="text-sm font-medium">Fleet Status</h3>
          <p className="text-[11px] text-muted">
            Click a bus to open its 4 cameras and trigger a manual capture.
          </p>
        </div>
        <table className="w-full text-left text-xs">
          <thead className="text-muted">
            <tr>
              <th className="px-4 py-2 font-normal">Bus</th>
              <th className="px-4 py-2 font-normal">Route</th>
              <th className="px-4 py-2 font-normal">Speed</th>
              <th className="px-4 py-2 font-normal">Status</th>
              <th className="px-4 py-2 font-normal">Last Update</th>
              <th className="px-4 py-2 font-normal">Cameras</th>
            </tr>
          </thead>
          <tbody>
            {liveBuses.map((b) => (
              <Fragment key={b.id}>
                <tr
                  className="cursor-pointer border-t border-border/60 hover:bg-card/40"
                  onClick={() => setExpanded(expanded === b.id ? null : b.id)}
                >
                  <td className="px-4 py-2 font-mono">{b.bus_number}</td>
                  <td className="px-4 py-2">{b.route}</td>
                  <td className="px-4 py-2 font-mono">{b.speed_kmph} km/h</td>
                  <td className="px-4 py-2">
                    <StatusDot status={b.status as "ACTIVE"} />
                  </td>
                  <td className="px-4 py-2 font-mono text-muted">
                    {b.last_seen ? new Date(b.last_seen).toLocaleTimeString() : "—"}
                  </td>
                  <td className="px-4 py-2 text-muted">{b.cameras?.length ?? 0} onboard</td>
                </tr>
                {expanded === b.id && (
                  <tr className="border-t border-border/40 bg-card/30">
                    <td colSpan={6} className="px-4 py-3">
                      <div className="grid grid-cols-2 gap-2 md:grid-cols-4">
                        {(b.cameras ?? []).map((cam) => {
                          const key = `${b.id}:${cam.id}`;
                          return (
                            <div
                              key={cam.id}
                              className="rounded border border-border bg-panel p-2.5"
                            >
                              <div className="flex items-center justify-between">
                                <span className="flex items-center gap-1.5 font-mono text-[11px]">
                                  <CameraIcon className="h-3 w-3 text-muted" />
                                  {cam.camera_type}
                                </span>
                                <StatusDot status={cam.status as "ONLINE"} />
                              </div>
                              <button
                                onClick={(e) => {
                                  e.stopPropagation();
                                  handleCapture(b.id, cam.id, cam.camera_type);
                                }}
                                className="mt-2 w-full rounded border border-border py-1 text-[11px] hover:bg-card"
                              >
                                Capture Now
                              </button>
                              {captureResult[key] && (
                                <p className="mt-1.5 text-[10px] leading-tight text-muted">
                                  {captureResult[key]}
                                </p>
                              )}
                            </div>
                          );
                        })}
                      </div>
                    </td>
                  </tr>
                )}
              </Fragment>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
