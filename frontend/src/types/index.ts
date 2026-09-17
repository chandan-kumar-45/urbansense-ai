export type UserRole =
  | "ADMIN"
  | "TRANSPORT_AUTHORITY"
  | "TRAFFIC_OFFICER"
  | "MAINTENANCE_OFFICER"
  | "ANALYST";

export interface User {
  id: string;
  name: string;
  email: string;
  role: UserRole;
  is_active: boolean;
  created_at: string;
}

export interface AuthToken {
  access_token: string;
  token_type: string;
  user: User;
}

export type BusStatus = "ACTIVE" | "DELAYED" | "INCIDENT" | "OFFLINE";
export type CameraType = "FRONT" | "REAR" | "LEFT" | "RIGHT" | "CABIN";
export type CameraStatus = "ONLINE" | "OFFLINE" | "FAULT";

export interface Camera {
  id: string;
  bus_id: string;
  camera_type: CameraType;
  status: CameraStatus;
}

export interface Bus {
  id: string;
  bus_number: string;
  registration_number: string;
  route: string | null;
  status: BusStatus;
  latitude: number | null;
  longitude: number | null;
  speed_kmph: number;
  heading_deg: number;
  last_seen: string | null;
  is_simulated: boolean;
  cameras: Camera[];
}

export type Severity = "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
export type EventStatus =
  | "NEW"
  | "ACKNOWLEDGED"
  | "INVESTIGATING"
  | "RESOLVED"
  | "FALSE_POSITIVE";

export interface DetectionEvent {
  id: string;
  event_type: string;
  bus_id: string | null;
  camera_id: string | null;
  latitude: number;
  longitude: number;
  timestamp: string;
  confidence: number;
  severity: Severity;
  image_path: string | null;
  video_path: string | null;
  vehicle_id: string | null;
  license_plate: string | null;
  model_name: string;
  model_version: string;
  is_demo: boolean;
  status: EventStatus;
}

export interface RoadDefect {
  id: string;
  defect_type: string;
  severity: Severity;
  confidence: number;
  latitude: number;
  longitude: number;
  detected_at: string;
  bus_id: string | null;
  camera_id: string | null;
  image: string | null;
  model_name: string;
  model_version: string | null;
  is_demo: boolean;
  status: EventStatus;
}

export interface TrafficEvent {
  id: string;
  location: string;
  latitude: number | null;
  longitude: number | null;
  vehicle_count: number;
  density: number;
  congestion_level: "LOW" | "MEDIUM" | "HIGH";
  average_speed_kmph: number | null;
  timestamp: string;
  is_demo: boolean;
}

export type IncidentType =
  | "HIT_AND_RUN"
  | "RASH_DRIVING"
  | "ACCIDENT"
  | "PEDESTRIAN_RISK"
  | "ROAD_HAZARD"
  | "WATERLOGGING"
  | "TRAFFIC_CONGESTION";

export interface Incident {
  id: string;
  incident_type: IncidentType;
  severity: Severity;
  vehicle_number: string | null;
  confidence: number | null;
  latitude: number;
  longitude: number;
  timestamp: string;
  evidence_image: string | null;
  evidence_video: string | null;
  bus_id: string | null;
  camera_id: string | null;
  model_name: string | null;
  model_version: string | null;
  is_demo: boolean;
  assigned_officer_id: string | null;
  status: EventStatus;
}

export interface WsMessage<T = unknown> {
  channel:
    | "detection_event"
    | "road_defect"
    | "traffic_event"
    | "incident"
    | "bus_position";
  data: T;
}
