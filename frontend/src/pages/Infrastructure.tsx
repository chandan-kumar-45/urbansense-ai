import { useEffect, useState } from "react";
import { SeverityBadge } from "@/components/SeverityBadge";
import { updateDefectStatus } from "@/services/data";
import { getRoadDefects } from "@/services/data";
import type { RoadDefect } from "@/types";

export function Infrastructure() {
  const [defects, setDefects] = useState<RoadDefect[]>([]);

  function load() {
    getRoadDefects().then((all) => setDefects(all.filter((d) => d.defect_type !== "pothole")));
  }

  useEffect(load, []);

  return (
    <div className="rounded-md border border-border bg-panel">
      <div className="border-b border-border px-4 py-3">
        <h3 className="text-sm font-medium">Infrastructure Deficiencies</h3>
        <p className="text-[11px] text-muted">
          Non-pothole road defects — cracked road, damaged asphalt, depressions,
          debris.
        </p>
      </div>
      <table className="w-full text-left text-xs">
        <thead className="text-muted">
          <tr>
            <th className="px-4 py-2 font-normal">Type</th>
            <th className="px-4 py-2 font-normal">Severity</th>
            <th className="px-4 py-2 font-normal">Confidence</th>
            <th className="px-4 py-2 font-normal">Detected</th>
            <th className="px-4 py-2 font-normal">Status</th>
            <th className="px-4 py-2 font-normal" />
          </tr>
        </thead>
        <tbody>
          {defects.map((d) => (
            <tr key={d.id} className="border-t border-border/60">
              <td className="px-4 py-2 capitalize">{d.defect_type.replace("_", " ")}</td>
              <td className="px-4 py-2">
                <SeverityBadge severity={d.severity} />
              </td>
              <td className="px-4 py-2 font-mono">{(d.confidence * 100).toFixed(0)}%</td>
              <td className="px-4 py-2 font-mono text-muted">
                {new Date(d.detected_at).toLocaleDateString()}
              </td>
              <td className="px-4 py-2">{d.status}</td>
              <td className="px-4 py-2">
                {d.status !== "RESOLVED" && (
                  <button
                    onClick={async () => {
                      await updateDefectStatus(d.id, "RESOLVED");
                      load();
                    }}
                    className="rounded border border-border px-2 py-1 text-[11px] hover:bg-card"
                  >
                    Mark Resolved
                  </button>
                )}
              </td>
            </tr>
          ))}
          {defects.length === 0 && (
            <tr>
              <td colSpan={6} className="px-4 py-6 text-center text-muted">
                No infrastructure issues recorded.
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}
