import { useEffect, useState } from "react";
import { LogOut } from "lucide-react";
import { useAuth } from "@/hooks/useAuth";

const ROLE_LABEL: Record<string, string> = {
  ADMIN: "Administrator",
  TRANSPORT_AUTHORITY: "Transport Authority",
  TRAFFIC_OFFICER: "Traffic Officer",
  MAINTENANCE_OFFICER: "Maintenance Officer",
  ANALYST: "Analyst",
};

export function TopBar({ title }: { title: string }) {
  const { user, logout } = useAuth();
  const [now, setNow] = useState(new Date());

  useEffect(() => {
    const id = setInterval(() => setNow(new Date()), 1000);
    return () => clearInterval(id);
  }, []);

  return (
    <header className="flex h-14 shrink-0 items-center justify-between border-b border-border bg-panel px-6">
      <h1 className="text-sm font-medium text-ink">{title}</h1>

      <div className="flex items-center gap-5">
        <span className="font-mono text-xs text-muted">
          {now.toLocaleTimeString("en-IN", { hour12: false })}
        </span>

        {user && (
          <div className="flex items-center gap-3 border-l border-border pl-5">
            <div className="text-right leading-tight">
              <p className="text-xs font-medium">{user.name}</p>
              <p className="text-[11px] text-muted">{ROLE_LABEL[user.role] ?? user.role}</p>
            </div>
            <button
              onClick={logout}
              className="rounded p-1.5 text-muted transition-colors hover:bg-card hover:text-ink"
              title="Sign out"
            >
              <LogOut className="h-4 w-4" strokeWidth={1.75} />
            </button>
          </div>
        )}
      </div>
    </header>
  );
}
