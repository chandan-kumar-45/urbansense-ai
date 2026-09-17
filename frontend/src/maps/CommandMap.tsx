import { MapContainer, Marker, Popup, TileLayer } from "react-leaflet";
import L from "leaflet";
import type { ReactNode } from "react";

/**
 * Default react-leaflet marker icons reference image paths that break under
 * Vite's bundler. Rather than patch that global, every marker on this map
 * uses a custom colored SVG divIcon instead — which also lets severity/status
 * drive marker color directly, per the GIS spec's "different markers/icons"
 * requirement.
 */
export function coloredDivIcon(color: string, glyph = "●"): L.DivIcon {
  return L.divIcon({
    className: "",
    html: `<div style="
        width: 22px; height: 22px; border-radius: 50%;
        background: ${color}; border: 2px solid #0A0E17;
        display: flex; align-items: center; justify-content: center;
        font-size: 10px; color: #0A0E17; font-weight: 700;
        box-shadow: 0 0 0 1px ${color}55;
      ">${glyph}</div>`,
    iconSize: [22, 22],
    iconAnchor: [11, 11],
    popupAnchor: [0, -12],
  });
}

export interface MapMarker {
  id: string;
  lat: number;
  lng: number;
  icon: L.DivIcon;
  popup: ReactNode;
}

interface Props {
  markers: MapMarker[];
  center?: [number, number];
  zoom?: number;
  heightClassName?: string;
}

const JAIPUR_CENTER: [number, number] = [26.9124, 75.7873];

export function CommandMap({ markers, center = JAIPUR_CENTER, zoom = 12, heightClassName = "h-[520px]" }: Props) {
  return (
    <div className={`overflow-hidden rounded-md border border-border ${heightClassName}`}>
      <MapContainer
        center={center}
        zoom={zoom}
        scrollWheelZoom
        style={{ height: "100%", width: "100%", background: "#111826" }}
      >
        <TileLayer
          attribution='&copy; OpenStreetMap contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        {markers.map((m) => (
          <Marker key={m.id} position={[m.lat, m.lng]} icon={m.icon}>
            <Popup>{m.popup}</Popup>
          </Marker>
        ))}
      </MapContainer>
    </div>
  );
}
