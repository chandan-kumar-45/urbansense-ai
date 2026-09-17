import { useEffect, useMemo, useState } from "react";
import {
  AlertTriangle,
  Bus,
  CloudRain,
  Construction,
  Gauge,
  ShieldAlert,
  Users,
} from "lucide-react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { KpiCard } from "@/components/KpiCard";
import { LiveEventFeed } from "@/components/LiveEventFeed";
import { getBuses, getIncidents, getRoadDefects, getTrafficEvents } from "@/services/data";
import type { Bus as BusT, Incident, RoadDefect, TrafficEvent } from "@/types";

function groupDefectsByDay(defects: RoadDefect[]) {
  const counts = new Map<string, number>();
  for (const d of defects) {
    const day = new Date(d.detected_at).toLocaleDateString("en-IN", {
      month: "short",
      day: "numeric",
    });
    counts.set(day, (counts.get(day) ?? 0) + 1);
  }
  return Array.from(counts.entries()).map(([day, count]) => ({ day, count }));
}

function confidenceHistogram(defects: RoadDefect[]) {
  const buckets = [0, 0, 0, 0, 0]; // 0-20,20-40,40-60,60-80,80-100
  for (const d of defects) {
    const idx = Math.min(4, Math.floor(d.confidence * 5));
    buckets[idx] += 1;
  }
  return buckets.map((count, i) => ({ bucket: `${i * 20}-${i * 20 + 20}%`, count }));
}

export function Dashboard() {
  const [buses, setBuses] = useState<BusT[]>([]);
  const [defects, setDefects] = useState<RoadDefect[]>([]);
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [traffic, setTraffic] = useState<TrafficEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([getBuses(), getRoadDefects(), getTrafficEvents(), getIncidents().catch(() => [])])
      .then(([b, d, t, i]) => {
        setBuses(b);
        setDefects(d);
        setTraffic(t);
        setIncidents(i as Incident[]);
      })
      .catch((e) => setError(e.message ?? "Failed to load dashboard data."))
      .finally(() => setLoading(false));
  }, []);

  const activeBuses = useMemo(() => buses.filter((b) => b.status === "ACTIVE").length, [buses]);
  const activeIncidents = useMemo(
    () => incidents.filter((i) => i.status !== "RESOLVED" && i.status !== "FALSE_POSITIVE").length,
    [incidents]
  );
  const avgCongestion = useMemo(() => {
    if (traffic.length === 0) return "—";
    const order = { LOW: 0, MEDIUM: 1, HIGH: 2 };
    const avg =
      traffic.reduce((sum, t) => sum + order[t.congestion_level], 0) / traffic.length;
    return avg < 0.5 ? "LOW" : avg < 1.5 ? "MEDIUM" : "HIGH";
  }, [traffic]);
  const waterloggingAlerts = useMemo(
    () => incidents.filter((i) => i.incident_type === "WATERLOGGING").length,
    [incidents]
  );
  const pedestrianAlerts = useMemo(
    () => incidents.filter((i) => i.incident_type === "PEDESTRIAN_RISK").length,
    [incidents]
  );
  const infrastructureIssues = useMemo(
    () => defects.filter((d) => d.defect_type !== "pothole").length,
    [defects]
  );

  if (loading) {
    return <p className="text-sm text-muted">Loading command center data…</p>;
  }

  if (error) {
    return (
      <div className="rounded-md border border-signal-high/30 bg-signal-high/10 p-4 text-sm text-signal-high">
        Couldn't reach the backend at the configured API URL: {error}. Confirm the
        FastAPI server is running (see backend/README) and that VITE_API_BASE_URL
        points at it.
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 gap-3 md:grid-cols-4 xl:grid-cols-7">
        <KpiCard label="Active Buses" value={activeBuses} icon={Bus} tone="good" />
        <KpiCard
          label="Road Defects"
          value={defects.length}
          icon={Construction}
          tone={defects.length > 0 ? "medium" : "default"}
        />
        <KpiCard
          label="Active Incidents"
          value={activeIncidents}
          icon={AlertTriangle}
          tone={activeIncidents > 0 ? "high" : "default"}
        />
        <KpiCard label="Congestion Level" value={avgCongestion} icon={Gauge} />
        <KpiCard label="Waterlogging Alerts" value={waterloggingAlerts} icon={CloudRain} />
        <KpiCard label="Pedestrian Alerts" value={pedestrianAlerts} icon={Users} />
        <KpiCard label="Infrastructure Issues" value={infrastructureIssues} icon={ShieldAlert} />
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        <div className="space-y-4 lg:col-span-2">
          <div className="rounded-md border border-border bg-panel p-4">
            <h3 className="mb-4 text-sm font-medium">Road Defects Over Time</h3>
            {defects.length === 0 ? (
              <EmptyChart note="No road-damage detections yet. Run inference via the AI Detection Lab or POST /api/road-damage." />
            ) : (
              <ResponsiveContainer width="100%" height={220}>
                <LineChart data={groupDefectsByDay(defects)}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#2C3A52" />
                  <XAxis dataKey="day" stroke="#7C8AA5" fontSize={11} />
                  <YAxis stroke="#7C8AA5" fontSize={11} allowDecimals={false} />
                  <Tooltip
                    contentStyle={{
                      background: "#1A2436",
                      border: "1px solid #2C3A52",
                      fontSize: 12,
                    }}
                  />
                  <Line type="monotone" dataKey="count" stroke="#4FA8F7" strokeWidth={2} dot={false} />
                </LineChart>
              </ResponsiveContainer>
            )}
          </div>

          <div className="rounded-md border border-border bg-panel p-4">
            <h3 className="mb-4 text-sm font-medium">Detection Confidence Distribution</h3>
            {defects.length === 0 ? (
              <EmptyChart note="Confidence distribution appears once detections start coming in." />
            ) : (
              <ResponsiveContainer width="100%" height={220}>
                <BarChart data={confidenceHistogram(defects)}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#2C3A52" />
                  <XAxis dataKey="bucket" stroke="#7C8AA5" fontSize={11} />
                  <YAxis stroke="#7C8AA5" fontSize={11} allowDecimals={false} />
                  <Tooltip
                    contentStyle={{
                      background: "#1A2436",
                      border: "1px solid #2C3A52",
                      fontSize: 12,
                    }}
                  />
                  <Bar dataKey="count" fill="#3ED598" radius={[3, 3, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>

        <div className="lg:col-span-1">
          <LiveEventFeed />
        </div>
      </div>
    </div>
  );
}

function EmptyChart({ note }: { note: string }) {
  return (
    <div className="flex h-[220px] items-center justify-center rounded border border-dashed border-border/60 px-6 text-center text-xs text-muted">
      {note}
    </div>
  );
}
