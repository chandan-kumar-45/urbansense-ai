import { useEffect, useState } from "react";
import { CommandMap, coloredDivIcon, type MapMarker } from "@/maps/CommandMap";
import { getRoadHealth, type RoadHealth } from "@/services/reports";
import { getRoadDefects } from "@/services/data";
import type { RoadDefect, Severity } from "@/types";

const SEVERITY_COLOR: Record<Severity, string> = {
  LOW: "#3ED598",
  MEDIUM: "#F2B84B",
  HIGH: "#FF6B5E",
  CRITICAL: "#FF3B3B",
};

function scoreColor(score: number) {
  if (score >= 80) return "text-signal-good";
  if (score >= 50) return "text-signal-medium";
  return "text-signal-high";
}

export function RoadConditions() {
  const [health, setHealth] = useState<RoadHealth[]>([]);
  const [defects, setDefects] = useState<RoadDefect[]>([]);

  useEffect(() => {
    getRoadHealth().then(setHealth);
    getRoadDefects().then(setDefects);
  }, []);

  const markers: MapMarker[] = defects.map((d) => ({
    id: d.id,
    lat: d.latitude,
    lng: d.longitude,
    icon: coloredDivIcon(SEVERITY_COLOR[d.severity], "!"),
    popup: (
      <div className="text-xs">
        <p className="font-medium capitalize">{d.defect_type.replace("_", " ")}</p>
        <p className="text-muted">confidence {(d.confidence * 100).toFixed(0)}%</p>
      </div>
    ),
  }));

  return (
    <div className="space-y-4">
      <div className="rounded-md border border-border/60 bg-panel/50 p-3 text-[11px] text-muted">
        Road Health Score is an analytical score derived from detected-defect
        count and severity in this system — not an official government road
        rating.
      </div>

      <div className="grid grid-cols-1 gap-3 md:grid-cols-3">
        {health.length === 0 && (
          <p className="text-xs text-muted">
            No road defects recorded yet for any route — scores will appear as
            detections come in.
          </p>
        )}
        {health.map((h) => (
          <div key={h.route} className="rounded-md border border-border bg-panel p-4">
            <p className="text-xs text-muted">{h.route}</p>
            <p className={`mt-2 font-mono text-3xl font-semibold ${scoreColor(h.road_health_score)}`}>
              {h.road_health_score}
              <span className="text-sm text-muted">/100</span>
            </p>
            <p className="mt-1 text-[11px] text-muted">{h.defect_count} defects detected</p>
          </div>
        ))}
      </div>

      <CommandMap markers={markers} heightClassName="h-[520px]" />
    </div>
  );
}
