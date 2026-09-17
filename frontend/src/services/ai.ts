import { apiRequest } from "./api";

export interface Detection {
  class: string;
  confidence: number;
  bbox: [number, number, number, number];
  severity: string;
}

export interface InferenceResult {
  model: string;
  model_version: string;
  is_demo: boolean;
  processing_time_ms: number;
  detections: Detection[];
}

export function runInference(capability: string, file: File) {
  const form = new FormData();
  form.append("capability", capability);
  form.append("file", file);
  return apiRequest<InferenceResult>("/api/inference", { method: "POST", body: form, isForm: true });
}

export interface VideoFrameResult {
  frame_index: number;
  timestamp_s: number;
  detections: Detection[];
}

export interface VideoAnalysisResult {
  model: string;
  model_version: string;
  is_demo: boolean;
  source_fps: number;
  sampled_fps: number;
  frames_analyzed: number;
  frames_capped_at: number;
  total_processing_time_ms: number;
  total_detections: number;
  frames: VideoFrameResult[];
}

export function analyzeVideo(capability: string, file: File) {
  const form = new FormData();
  form.append("capability", capability);
  form.append("file", file);
  return apiRequest<VideoAnalysisResult>("/api/video/analyze", {
    method: "POST",
    body: form,
    isForm: true,
  });
}

export interface ModelVersion {
  id: string;
  model_name: string;
  version: string;
  model_type: string;
  supported_classes: string[];
  framework: string | null;
  accuracy_metrics: Record<string, unknown>;
  is_demo: boolean;
  status: "ACTIVE" | "TESTING" | "INACTIVE";
  created_at: string;
}

export const getModels = (modelName?: string) =>
  apiRequest<ModelVersion[]>(`/api/models${modelName ? `?model_name=${modelName}` : ""}`);

export const registerModel = (payload: Record<string, unknown>) =>
  apiRequest<ModelVersion>("/api/models/register", { method: "POST", body: payload });

export const activateModel = (id: string) =>
  apiRequest<ModelVersion>(`/api/models/${id}/activate`, { method: "POST" });
