import { apiRequest } from "./api";

export interface SimulationStatus {
  running: boolean;
  ticks: number;
  events_generated: number;
  bandwidth_saved_percent: number;
  is_demo: boolean;
  note: string;
}

export const getSimulationStatus = () => apiRequest<SimulationStatus>("/api/simulation/status");
export const startSimulation = () =>
  apiRequest<SimulationStatus>("/api/simulation/start", { method: "POST" });
export const stopSimulation = () =>
  apiRequest<SimulationStatus>("/api/simulation/stop", { method: "POST" });
