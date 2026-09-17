import { useEffect, useState } from "react";
import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";
import { getCongestionSummary, type CongestionSummary } from "@/services/reports";
import { getTrafficEvents } from "@/services/data";
import type { TrafficEvent } from "@/types";

const COLORS = { low: "#3ED598", medium: "#F2B84B", high: "#FF6B5E" };

export function TrafficAnalytics() {
  const [summary, setSummary] = useState<CongestionSummary | null>(null);
  const [events, setEvents] = useState<TrafficEvent[]>([]);

  useEffect(() => {
    getCongestionSummary().then(setSummary);
    getTrafficEvents({ limit: "50" }).then(setEvents);
  }, []);

  const pieData = summary
    ? [
        { name: "Low", value: summary.low, color: COLORS.low },
        { name: "Medium", value: summary.medium, color: COLORS.medium },
        { name: "High", value: summary.high, color: COLORS.high },
      ]
    : [];

  return (
    <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
      <div className="rounded-md border border-border bg-panel p-4 lg:col-span-1">
        <h3 className="mb-1 text-sm font-medium">Congestion Breakdown</h3>
        {summary?.is_demo && (
          <p className="mb-3 text-[11px] text-muted">Includes simulated samples.</p>
        )}
        {!summary || summary.total_samples === 0 ? (
          <p className="mt-8 text-center text-xs text-muted">
            No traffic samples yet — start the fleet simulation on Live Fleet.
          </p>
        ) : (
          <ResponsiveContainer width="100%" height={220}>
            <PieChart>
              <Pie data={pieData} dataKey="value" nameKey="name" innerRadius={50} outerRadius={80}>
                {pieData.map((d) => (
                  <Cell key={d.name} fill={d.color} />
                ))}
              </Pie>
              <Tooltip contentStyle={{ background: "#1A2436", border: "1px solid #2C3A52", fontSize: 12 }} />
            </PieChart>
          </ResponsiveContainer>
        )}
      </div>

      <div className="rounded-md border border-border bg-panel lg:col-span-2">
        <div className="border-b border-border px-4 py-3">
          <h3 className="text-sm font-medium">Recent Traffic Samples</h3>
        </div>
        <table className="w-full text-left text-xs">
          <thead className="text-muted">
            <tr>
              <th className="px-4 py-2 font-normal">Location</th>
              <th className="px-4 py-2 font-normal">Vehicles</th>
              <th className="px-4 py-2 font-normal">Congestion</th>
              <th className="px-4 py-2 font-normal">Avg Speed</th>
              <th className="px-4 py-2 font-normal">Time</th>
            </tr>
          </thead>
          <tbody>
            {events.map((e) => (
              <tr key={e.id} className="border-t border-border/60">
                <td className="px-4 py-2">{e.location}</td>
                <td className="px-4 py-2 font-mono">{e.vehicle_count}</td>
                <td className="px-4 py-2">{e.congestion_level}</td>
                <td className="px-4 py-2 font-mono">{e.average_speed_kmph ?? "—"} km/h</td>
                <td className="px-4 py-2 font-mono text-muted">
                  {new Date(e.timestamp).toLocaleTimeString()}
                </td>
              </tr>
            ))}
            {events.length === 0 && (
              <tr>
                <td colSpan={5} className="px-4 py-6 text-center text-muted">
                  No traffic events yet.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
