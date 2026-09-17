import { useEffect, useMemo, useState } from "react";
import { CommandMap, coloredDivIcon, type MapMarker } from "@/maps/CommandMap";
import { SeverityBadge } from "@/components/SeverityBadge";
import { getBuses, getIncidents, getRoadDefects, getTrafficEvents } from "@/services/data";
import type { Bus, Incident, RoadDefect, Severity, TrafficEvent } from "@/types";

type LayerKey = "defects" | "incidents" | "traffic" | "buses";

const SEVERITY_COLOR: Record<Severity, string> = {
  LOW: "#3ED598",
  MEDIUM: "#F2B84B",
  HIGH: "#FF6B5E",
  CRITICAL: "#FF3B3B",
};

export function GisIntelligence() {
  const [buses, setBuses] = useState<Bus[]>([]);
  const [defects, setDefects] = useState<RoadDefect[]>([]);
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [traffic, setTraffic] = useState<TrafficEvent[]>([]);
  const [layers, setLayers] = useState<Record<LayerKey, boolean>>({
    defects: true,
    incidents: true,
    traffic: true,
    buses: true,
  });
  const [severityFilter, setSeverityFilter] = useState<Severity | "ALL">("ALL");
  const [selected, setSelected] = useState<RoadDefect | Incident | null>(null);

  useEffect(() => {
    Promise.all([
      getBuses(),
      getRoadDefects(),
      getIncidents().catch(() => []),
      getTrafficEvents(),
    ]).then(([b, d, i, t]) => {
      setBuses(b);
      setDefects(d);
      setIncidents(i as Incident[]);
      setTraffic(t);
    });
  }, []);

  const markers: MapMarker[] = useMemo(() => {
    const out: MapMarker[] = [];

    if (layers.buses) {
      for (const b of buses) {
        if (!b.latitude || !b.longitude) continue;
        out.push({
          id: `bus-${b.id}`,
          lat: b.latitude,
          lng: b.longitude,
          icon: coloredDivIcon("#4FA8F7", "B"),
          popup: <div className="text-xs">{b.bus_number} — {b.route}</div>,
        });
      }
    }

    if (layers.defects) {
      for (const d of defects) {
        if (severityFilter !== "ALL" && d.severity !== severityFilter) continue;
        out.push({
          id: `defect-${d.id}`,
          lat: d.latitude,
          lng: d.longitude,
          icon: coloredDivIcon(SEVERITY_COLOR[d.severity], "!"),
          popup: (
            <button className="text-left text-xs underline" onClick={() => setSelected(d)}>
              {d.defect_type.replace("_", " ")} — click for details
            </button>
          ),
        });
      }
    }

    if (layers.incidents) {
      for (const i of incidents) {
        if (severityFilter !== "ALL" && i.severity !== severityFilter) continue;
        out.push({
          id: `incident-${i.id}`,
          lat: i.latitude,
          lng: i.longitude,
          icon: coloredDivIcon(SEVERITY_COLOR[i.severity], "⚠"),
          popup: (
            <button className="text-left text-xs underline" onClick={() => setSelected(i)}>
              {i.incident_type.replace(/_/g, " ").toLowerCase()} — click for details
            </button>
          ),
        });
      }
    }

    if (layers.traffic) {
      const congestionColor = { LOW: "#3ED598", MEDIUM: "#F2B84B", HIGH: "#FF6B5E" };
      for (const t of traffic) {
        if (!t.latitude || !t.longitude) continue;
        out.push({
          id: `traffic-${t.id}`,
          lat: t.latitude,
          lng: t.longitude,
          icon: coloredDivIcon(congestionColor[t.congestion_level], "T"),
          popup: (
            <div className="text-xs">
              {t.location} — {t.vehicle_count} vehicles, {t.congestion_level}
            </div>
          ),
        });
      }
    }

    return out;
  }, [buses, defects, incidents, traffic, layers, severityFilter]);

  function toggleLayer(key: LayerKey) {
    setLayers((prev) => ({ ...prev, [key]: !prev[key] }));
  }

  return (
    <div className="grid grid-cols-1 gap-4 lg:grid-cols-4">
      <div className="space-y-4 lg:col-span-3">
        <div className="flex flex-wrap items-center gap-4 rounded-md border border-border bg-panel p-3">
          {(["defects", "incidents", "traffic", "buses"] as LayerKey[]).map((key) => (
            <label key={key} className="flex items-center gap-1.5 text-xs capitalize">
              <input
                type="checkbox"
                checked={layers[key]}
                onChange={() => toggleLayer(key)}
                className="accent-signal-info"
              />
              {key}
            </label>
          ))}
          <div className="ml-auto flex items-center gap-2">
            <span className="text-xs text-muted">Severity</span>
            <select
              value={severityFilter}
              onChange={(e) => setSeverityFilter(e.target.value as Severity | "ALL")}
              className="rounded border border-border bg-card px-2 py-1 text-xs"
            >
              <option value="ALL">All</option>
              <option value="LOW">Low</option>
              <option value="MEDIUM">Medium</option>
              <option value="HIGH">High</option>
              <option value="CRITICAL">Critical</option>
            </select>
          </div>
        </div>

        <CommandMap markers={markers} heightClassName="h-[600px]" />
      </div>

      <div className="rounded-md border border-border bg-panel p-4 lg:col-span-1">
        <h3 className="mb-3 text-sm font-medium">Event Details</h3>
        {!selected && (
          <p className="text-xs text-muted">
            Click a road-defect or incident marker on the map to see its full
            detection record here.
          </p>
        )}
        {selected && (
          <div className="space-y-2 text-xs">
            <div className="flex items-center justify-between">
              <span className="font-medium capitalize">
                {"defect_type" in selected
                  ? selected.defect_type.replace("_", " ")
                  : selected.incident_type.replace(/_/g, " ").toLowerCase()}
              </span>
              <SeverityBadge severity={selected.severity} />
            </div>
            <DetailRow label="Confidence" value={`${((selected.confidence ?? 0) * 100).toFixed(0)}%`} />
            <DetailRow
              label="GPS"
              value={`${selected.latitude.toFixed(5)}, ${selected.longitude.toFixed(5)}`}
              mono
            />
            <DetailRow
              label="Timestamp"
              value={new Date(
                "detected_at" in selected ? selected.detected_at : selected.timestamp
              ).toLocaleString()}
              mono
            />
            <DetailRow label="Bus" value={selected.bus_id ?? "—"} mono />
            {"camera_id" in selected && (
              <DetailRow label="Camera" value={selected.camera_id ?? "—"} mono />
            )}
            {"model_name" in selected && (
              <DetailRow
                label="Model"
                value={`${selected.model_name ?? "—"} ${selected.model_version ?? ""}`}
                mono
              />
            )}
            <DetailRow label="Demo data" value={selected.is_demo ? "Yes" : "No"} />
            <DetailRow label="Status" value={selected.status} />
          </div>
        )}
      </div>
    </div>
  );
}

function DetailRow({ label, value, mono }: { label: string; value: string; mono?: boolean }) {
  return (
    <div className="flex items-center justify-between border-t border-border/60 py-1.5">
      <span className="text-muted">{label}</span>
      <span className={mono ? "font-mono" : ""}>{value}</span>
    </div>
  );
}
