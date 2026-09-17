import { Outlet, useLocation } from "react-router-dom";
import { Sidebar } from "@/components/Sidebar";
import { TopBar } from "@/components/TopBar";

/**
 * Maps the current path to a page title for the top bar. We use useLocation()
 * rather than React Router's useMatches()/handle system because this app uses
 * the declarative <Routes>/<Route> API (BrowserRouter), not a data router
 * (createBrowserRouter + RouterProvider) — useMatches() only works with the
 * latter and throws at runtime otherwise (this was a real bug — thanks for
 * catching it).
 */
const PAGE_TITLES: Record<string, string> = {
  "/dashboard": "Dashboard",
  "/fleet": "Live Fleet",
  "/gis": "GIS Intelligence",
  "/road-conditions": "Road Conditions",
  "/traffic": "Traffic Analytics",
  "/incidents": "Incident Center",
  "/infrastructure": "Infrastructure",
  "/detection-lab": "AI Detection Lab",
  "/video-analysis": "Video Analysis",
  "/models": "AI Model Management",
  "/routes": "Routes",
  "/reports": "Reports",
  "/settings": "Settings",
};

export function CommandLayout() {
  const location = useLocation();
  const title = PAGE_TITLES[location.pathname] ?? "UrbanSense AI";

  return (
    <div className="flex h-screen">
      <Sidebar />
      <div className="flex min-w-0 flex-1 flex-col">
        <TopBar title={title} />
        <main className="flex-1 overflow-y-auto bg-base p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
