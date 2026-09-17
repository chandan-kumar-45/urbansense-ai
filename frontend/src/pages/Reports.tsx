import { useState } from "react";
import { Download, FileText } from "lucide-react";
import { downloadReportCsv, getReportSummary } from "@/services/reports";

const REPORTS = [
  { key: "road-damage", label: "Daily Road Damage Report", path: "/api/reports/road-damage" },
  { key: "traffic-congestion", label: "Traffic Congestion Report", path: "/api/reports/traffic-congestion" },
  { key: "incidents", label: "Incident Report", path: "/api/reports/incidents" },
  { key: "fleet", label: "Bus Fleet Report", path: "/api/reports/fleet" },
  { key: "infrastructure", label: "Infrastructure Deficiency Report", path: "/api/reports/infrastructure" },
];

export function Reports() {
  const [summaries, setSummaries] = useState<Record<string, Record<string, unknown>>>({});
  const [loadingKey, setLoadingKey] = useState<string | null>(null);

  async function generate(key: string, path: string) {
    setLoadingKey(key);
    try {
      const summary = await getReportSummary(path);
      setSummaries((prev) => ({ ...prev, [key]: summary }));
    } finally {
      setLoadingKey(null);
    }
  }

  return (
    <div className="space-y-4">
      {REPORTS.map(({ key, label, path }) => (
        <div key={key} className="rounded-md border border-border bg-panel p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2.5">
              <FileText className="h-4 w-4 text-muted" strokeWidth={1.75} />
              <p className="text-sm font-medium">{label}</p>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={() => generate(key, path)}
                disabled={loadingKey === key}
                className="rounded border border-border px-3 py-1.5 text-xs hover:bg-card disabled:opacity-50"
              >
                {loadingKey === key ? "Generating…" : "Generate"}
              </button>
              <button
                onClick={() => downloadReportCsv(path, `${key}.csv`)}
                className="flex items-center gap-1.5 rounded border border-border px-3 py-1.5 text-xs hover:bg-card"
              >
                <Download className="h-3 w-3" /> CSV
              </button>
              <button
                onClick={() => window.print()}
                className="rounded border border-border px-3 py-1.5 text-xs hover:bg-card"
                title="Use your browser's Print dialog to save as PDF"
              >
                Print / PDF
              </button>
            </div>
          </div>
          {summaries[key] && (
            <pre className="mt-3 max-h-56 overflow-auto rounded bg-card p-3 text-[11px] text-muted">
              {JSON.stringify(summaries[key], null, 2)}
            </pre>
          )}
        </div>
      ))}
      <p className="text-[11px] text-muted">
        PDF export in this prototype uses the browser's native Print dialog
        (Save as PDF) rather than a server-side PDF renderer — documented as a
        future improvement in the README rather than adding an unverified
        dependency.
      </p>
    </div>
  );
}
