import { useAuth } from "@/hooks/useAuth";

export function Settings() {
  const { user } = useAuth();

  return (
    <div className="max-w-lg space-y-4">
      <div className="rounded-md border border-border bg-panel p-4">
        <h3 className="mb-3 text-sm font-medium">Account</h3>
        <dl className="space-y-2 text-xs">
          <Row label="Name" value={user?.name ?? "—"} />
          <Row label="Email" value={user?.email ?? "—"} mono />
          <Row label="Role" value={user?.role ?? "—"} />
        </dl>
      </div>

      <div className="rounded-md border border-border bg-panel p-4">
        <h3 className="mb-3 text-sm font-medium">Environment</h3>
        <dl className="space-y-2 text-xs">
          <Row label="API base URL" value={import.meta.env.VITE_API_BASE_URL} mono />
          <Row label="WebSocket URL" value={import.meta.env.VITE_WS_BASE_URL} mono />
          <Row label="Database" value="SQLite (dev) — see docs/ARCHITECTURE.md §9 for PostGIS upgrade" />
        </dl>
      </div>

      <p className="text-[11px] text-muted">
        Retention settings, plate/face-blur configuration, and notification
        preferences are documented as future improvements in the README rather
        than implemented here without real enforcement behind them.
      </p>
    </div>
  );
}

function Row({ label, value, mono }: { label: string; value: string; mono?: boolean }) {
  return (
    <div className="flex items-center justify-between border-t border-border/60 pt-2 first:border-t-0 first:pt-0">
      <dt className="text-muted">{label}</dt>
      <dd className={mono ? "font-mono" : ""}>{value}</dd>
    </div>
  );
}
