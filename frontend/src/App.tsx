import { Navigate, Route, Routes } from "react-router-dom";
import { AuthProvider } from "@/hooks/useAuth";
import { ProtectedRoute } from "@/components/ProtectedRoute";
import { RoleRoute } from "@/components/RoleRoute";
import { CommandLayout } from "@/layouts/CommandLayout";
import { Login } from "@/pages/Login";
import { Dashboard } from "@/pages/Dashboard";
import { LiveFleet } from "@/pages/LiveFleet";
import { GisIntelligence } from "@/pages/GisIntelligence";
import { RoadConditions } from "@/pages/RoadConditions";
import { TrafficAnalytics } from "@/pages/TrafficAnalytics";
import { IncidentCenter } from "@/pages/IncidentCenter";
import { Infrastructure } from "@/pages/Infrastructure";
import { DetectionLab } from "@/pages/DetectionLab";
import { VideoAnalysis } from "@/pages/VideoAnalysis";
import { ModelManagement } from "@/pages/ModelManagement";
import { RoutesPage } from "@/pages/RoutesPage";
import { Reports } from "@/pages/Reports";
import { Settings } from "@/pages/Settings";

// Dashboard has no RoleRoute wrapper — it's the shared landing page every
// authenticated role can see. Every other page is role-gated per
// src/config/roleAccess.ts, both here (direct-URL protection) and in
// Sidebar.tsx (hides links the role can't use).
const ROLE_GATED_ROUTES: { path: string; element: JSX.Element }[] = [
  { path: "/fleet", element: <LiveFleet /> },
  { path: "/gis", element: <GisIntelligence /> },
  { path: "/road-conditions", element: <RoadConditions /> },
  { path: "/traffic", element: <TrafficAnalytics /> },
  { path: "/incidents", element: <IncidentCenter /> },
  { path: "/infrastructure", element: <Infrastructure /> },
  { path: "/detection-lab", element: <DetectionLab /> },
  { path: "/video-analysis", element: <VideoAnalysis /> },
  { path: "/models", element: <ModelManagement /> },
  { path: "/routes", element: <RoutesPage /> },
  { path: "/reports", element: <Reports /> },
];

export default function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route path="/login" element={<Login />} />

        <Route
          element={
            <ProtectedRoute>
              <CommandLayout />
            </ProtectedRoute>
          }
        >
          <Route path="/dashboard" element={<Dashboard />} />

          {ROLE_GATED_ROUTES.map(({ path, element }) => (
            <Route key={path} path={path} element={<RoleRoute>{element}</RoleRoute>} />
          ))}

          {/* Settings is available to every authenticated role, like Dashboard. */}
          <Route path="/settings" element={<Settings />} />
        </Route>

        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </AuthProvider>
  );
}
