import { useEffect, useRef } from "react";
import type { Detection } from "@/services/ai";

const SEVERITY_COLOR: Record<string, string> = {
  LOW: "#3ED598",
  MEDIUM: "#F2B84B",
  HIGH: "#FF6B5E",
  CRITICAL: "#FF3B3B",
};

export function DetectionOverlay({
  imageUrl,
  detections,
}: {
  imageUrl: string;
  detections: Detection[];
}) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const img = new Image();
    img.onload = () => {
      canvas.width = img.width;
      canvas.height = img.height;
      ctx.drawImage(img, 0, 0);

      for (const d of detections) {
        const [x1, y1, x2, y2] = d.bbox;
        const color = SEVERITY_COLOR[d.severity] ?? "#4FA8F7";
        ctx.strokeStyle = color;
        ctx.lineWidth = Math.max(2, img.width / 300);
        ctx.strokeRect(x1, y1, x2 - x1, y2 - y1);

        const label = `${d.class} ${(d.confidence * 100).toFixed(0)}%`;
        ctx.font = `${Math.max(12, img.width / 40)}px 'IBM Plex Mono', monospace`;
        const metrics = ctx.measureText(label);
        const padding = 4;
        ctx.fillStyle = color;
        ctx.fillRect(
          x1,
          Math.max(0, y1 - 20),
          metrics.width + padding * 2,
          20
        );
        ctx.fillStyle = "#0A0E17";
        ctx.fillText(label, x1 + padding, Math.max(14, y1 - 5));
      }
    };
    img.src = imageUrl;
  }, [imageUrl, detections]);

  return <canvas ref={canvasRef} className="w-full rounded border border-border" />;
}
