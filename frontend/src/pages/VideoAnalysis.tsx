import { useState } from "react";
import { Film, UploadCloud } from "lucide-react";
import { analyzeVideo, type VideoAnalysisResult } from "@/services/ai";
import { ApiError } from "@/services/api";

export function VideoAnalysis() {
  const [file, setFile] = useState<File | null>(null);
  const [result, setResult] = useState<VideoAnalysisResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleAnalyze() {
    if (!file) return;
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const res = await analyzeVideo("road_damage", file);
      setResult(res);
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Video analysis failed.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-4">
      <div className="rounded-md border border-border bg-panel p-4">
        <label className="flex cursor-pointer flex-col items-center justify-center gap-2 rounded border border-dashed border-border py-10 text-center hover:border-signal-info/50">
          <UploadCloud className="h-6 w-6 text-muted" strokeWidth={1.5} />
          <span className="text-xs text-muted">
            {file ? file.name : "Click to upload a road video (MP4)"}
          </span>
          <input
            type="file"
            accept="video/mp4,video/quicktime,video/webm"
            className="hidden"
            onChange={(e) => setFile(e.target.files?.[0] ?? null)}
          />
        </label>
        <button
          onClick={handleAnalyze}
          disabled={!file || loading}
          className="mt-4 flex w-full items-center justify-center gap-2 rounded bg-signal-info px-4 py-2 text-sm font-medium text-base transition-opacity hover:opacity-90 disabled:opacity-50"
        >
          <Film className="h-4 w-4" />
          {loading ? "Analyzing video…" : "Analyze Video"}
        </button>
        {error && (
          <p className="mt-3 rounded border border-signal-high/30 bg-signal-high/10 px-3 py-2 text-xs text-signal-high">
            {error}
          </p>
        )}
        <p className="mt-3 text-[11px] text-muted">
          Frames are sampled at {result?.sampled_fps ?? 2} fps (not every frame)
          — this is the same rate an edge node would use, which is what gives
          the bandwidth savings described on the Live Fleet page. Capped at{" "}
          {result?.frames_capped_at ?? 40} frames for this prototype.
        </p>
      </div>

      {result && (
        <div className="rounded-md border border-border bg-panel">
          <div className="flex items-center justify-between border-b border-border px-4 py-3">
            <h3 className="text-sm font-medium">Analysis Result</h3>
            <span className="text-[11px] text-muted">
              {result.frames_analyzed} frames · {result.total_detections} detections ·{" "}
              {result.total_processing_time_ms}ms
            </span>
          </div>
          <table className="w-full text-left text-xs">
            <thead className="text-muted">
              <tr>
                <th className="px-4 py-2 font-normal">Frame</th>
                <th className="px-4 py-2 font-normal">Time</th>
                <th className="px-4 py-2 font-normal">Detections</th>
              </tr>
            </thead>
            <tbody>
              {result.frames.map((f) => (
                <tr key={f.frame_index} className="border-t border-border/60">
                  <td className="px-4 py-2 font-mono">#{f.frame_index}</td>
                  <td className="px-4 py-2 font-mono">{f.timestamp_s}s</td>
                  <td className="px-4 py-2">
                    {f.detections.length === 0
                      ? "—"
                      : f.detections
                          .map((d) => `${d.class} (${(d.confidence * 100).toFixed(0)}%)`)
                          .join(", ")}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
