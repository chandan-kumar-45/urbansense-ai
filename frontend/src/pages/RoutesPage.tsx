import { useEffect, useState } from "react";
import { getRouteDelays, type RouteDelay } from "@/services/reports";

function delayColor(delay: number) {
  if (delay <= 0) return "text-signal-good";
  if (delay <= 10) return "text-signal-medium";
  return "text-signal-high";
}

export function RoutesPage() {
  const [routes, setRoutes] = useState<RouteDelay[]>([]);

  useEffect(() => {
    getRouteDelays().then(setRoutes);
  }, []);

  return (
    <div className="space-y-4">
      <p className="text-xs text-muted">
        Scheduled durations are illustrative reference values for this
        prototype (see docs) — current duration is derived from observed
        average speed on each route.
      </p>
      <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
        {routes.map((r) => (
          <div key={r.route} className="rounded-md border border-border bg-panel p-4">
            <div className="flex items-center justify-between">
              <p className="text-sm font-medium">{r.route}</p>
              {r.is_demo && <span className="text-[10px] text-muted">no live samples yet</span>}
            </div>
            <div className="mt-3 grid grid-cols-3 gap-3 text-center">
              <div>
                <p className="font-mono text-lg">{r.scheduled_minutes}m</p>
                <p className="text-[11px] text-muted">Scheduled</p>
              </div>
              <div>
                <p className="font-mono text-lg">{r.current_estimated_minutes}m</p>
                <p className="text-[11px] text-muted">Current</p>
              </div>
              <div>
                <p className={`font-mono text-lg ${delayColor(r.delay_minutes)}`}>
                  {r.delay_minutes > 0 ? "+" : ""}
                  {r.delay_minutes}m
                </p>
                <p className="text-[11px] text-muted">Delay</p>
              </div>
            </div>
            {r.average_speed_kmph && (
              <p className="mt-3 text-center text-[11px] text-muted">
                avg speed {r.average_speed_kmph} km/h · {r.sample_size} samples
              </p>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
