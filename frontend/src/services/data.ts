import { apiRequest } from "./api";
import type { Bus, DetectionEvent, Incident, RoadDefect, TrafficEvent } from "@/types";

export const getBuses = () => apiRequest<Bus[]>("/api/buses");

export const getRoadDefects = (params: Record<string, string> = {}) =>
  apiRequest<RoadDefect[]>(`/api/road-damage?${new URLSearchParams(params)}`);

export const getTrafficEvents = (params: Record<string, string> = {}) =>
  apiRequest<TrafficEvent[]>(`/api/traffic?${new URLSearchParams(params)}`);

export const getIncidents = (params: Record<string, string> = {}) =>
  apiRequest<Incident[]>(`/api/incidents?${new URLSearchParams(params)}`);

export const getEvents = (params: Record<string, string> = {}) =>
  apiRequest<DetectionEvent[]>(`/api/events?${new URLSearchParams(params)}`);

export const updateIncident = (id: string, body: Record<string, unknown>) =>
  apiRequest(`/api/incidents/${id}`, { method: "PATCH", body });

export const updateDefectStatus = (id: string, status: string) =>
  apiRequest(`/api/road-damage/${id}/status`, { method: "PATCH", body: { status } });

/** Manually trigger one capture-and-detect cycle on a specific bus camera —
 * runs through the real app/services/capture.py pipeline (see backend). */
export const captureCamera = (busId: string, cameraId: string) =>
  apiRequest<RoadDefect[]>(`/api/buses/${busId}/cameras/${cameraId}/capture`, { method: "POST" });
