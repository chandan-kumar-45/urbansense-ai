import { NavLink } from "react-router-dom";
import {
  AlertTriangle,
  BarChart3,
  Bus,
  Camera,
  FileText,
  LayoutDashboard,
  MapPinned,
  Route,
  Settings,
  ShieldAlert,
  Sparkles,
  UserCog,
  Wrench,
} from "lucide-react";
import clsx from "clsx";
import { useAuth } from "@/hooks/useAuth";
import { canAccess } from "@/config/roleAccess";

const NAV_ITEMS = [
  { to: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { to: "/fleet", label: "Live Fleet", icon: Bus },
  { to: "/gis", label: "GIS Intelligence", icon: MapPinned },
  { to: "/road-conditions", label: "Road Conditions", icon: Wrench },
  { to: "/traffic", label: "Traffic Analytics", icon: BarChart3 },
  { to: "/incidents", label: "Incident Center", icon: AlertTriangle },
  { to: "/infrastructure", label: "Infrastructure", icon: ShieldAlert },
  { to: "/detection-lab", label: "AI Detection Lab", icon: Sparkles },
  { to: "/video-analysis", label: "Video Analysis", icon: Camera },
  { to: "/models", label: "AI Model Management", icon: Settings },
  { to: "/routes", label: "Routes", icon: Route },
  { to: "/reports", label: "Reports", icon: FileText },
  { to: "/settings", label: "Settings", icon: UserCog },
];

export function Sidebar() {
  const { user } = useAuth();
  const visibleItems = NAV_ITEMS.filter((item) => canAccess(user?.role, item.to));

  return (
    <aside className="flex w-60 shrink-0 flex-col border-r border-border bg-panel">
      <div className="flex items-center gap-2 border-b border-border px-4 py-4">
        <div className="flex h-7 w-7 items-center justify-center rounded bg-signal-info/15">
          <span className="font-mono text-xs font-semibold text-signal-info">US</span>
        </div>
        <div className="leading-tight">
          <p className="text-sm font-semibold">UrbanSense AI</p>
          <p className="text-[10px] text-muted">Command Center</p>
        </div>
      </div>

      <nav className="flex-1 space-y-0.5 overflow-y-auto px-2 py-3">
        {visibleItems.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              clsx(
                "flex items-center gap-2.5 rounded px-2.5 py-2 text-sm transition-colors",
                isActive
                  ? "bg-card text-ink"
                  : "text-muted hover:bg-card/60 hover:text-ink"
              )
            }
          >
            <Icon className="h-4 w-4" strokeWidth={1.75} />
            {label}
          </NavLink>
        ))}
      </nav>

      <div className="border-t border-border px-4 py-3 text-[11px] text-muted">
        SIH 2026 · PS 26124 · BEL
      </div>
    </aside>
  );
}
