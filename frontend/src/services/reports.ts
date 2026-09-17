import { apiRequest, ApiError } from "./api";

export interface RouteDelay {
  route: string;
  scheduled_minutes: number;
  current_estimated_minutes: number;
  delay_minutes: number;
  average_speed_kmph: number | null;
  sample_size: number;
  is_demo: boolean;
}

export interface RoadHealth {
  route: string;
  defect_count: number;
  road_health_score: number;
  is_analytical_score: boolean;
  note: string;
}

export interface CongestionSummary {
  low: number;
  medium: number;
  high: number;
  total_samples: number;
  is_demo: boolean;
}

export const getCongestionSummary = () => apiRequest<CongestionSummary>("/api/analytics/congestion");
export const getRouteDelays = () => apiRequest<RouteDelay[]>("/api/analytics/routes");
export const getRoadHealth = () => apiRequest<RoadHealth[]>("/api/analytics/road-health");
export const getOriginDestination = () => apiRequest("/api/analytics/origin-destination");

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

/** Reports are downloaded as CSV via a direct authenticated fetch (not JSON). */
export async function downloadReportCsv(reportPath: string, filename: string) {
  const token = localStorage.getItem("urbansense_token");
  const res = await fetch(`${API_BASE_URL}${reportPath}?format=csv`, {
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  });
  if (!res.ok) throw new ApiError(res.status, "Failed to generate report.");
  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

export const getReportSummary = (path: string) => apiRequest<Record<string, unknown>>(path);
