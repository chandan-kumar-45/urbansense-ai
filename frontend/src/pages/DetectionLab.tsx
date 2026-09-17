import { useState } from "react";
import { Sparkles, UploadCloud } from "lucide-react";
import { DetectionOverlay } from "@/components/DetectionOverlay";
import { runInference, type InferenceResult } from "@/services/ai";
import { ApiError } from "@/services/api";

const CAPABILITIES = [{ value: "road_damage", label: "Road Damage Detection" }];

export function DetectionLab() {
  const [capability, setCapability] = useState("road_damage");
  const [file, setFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [result, setResult] = useState<InferenceResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  function handleFile(f: File | null) {
    setFile(f);
    setResult(null);
    setError(null);
    if (f) setPreviewUrl(URL.createObjectURL(f));
  }

  async function runDetection() {
    if (!file) return;
    setLoading(true);
    setError(null);
    try {
      const res = await runInference(capability, file);
      setResult(res);
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Inference failed.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
      <div className="space-y-4">
        <div className="rounded-md border border-border bg-panel p-4">
          <label className="mb-1.5 block text-xs text-muted">Model</label>
          <select
            value={capability}
            onChange={(e) => setCapability(e.target.value)}
            className="w-full rounded border border-border bg-card px-3 py-2 text-sm"
          >
            {CAPABILITIES.map((c) => (
              <option key={c.value} value={c.value}>
                {c.label}
              </option>
            ))}
          </select>

          <label className="mt-4 flex cursor-pointer flex-col items-center justify-center gap-2 rounded border border-dashed border-border py-10 text-center hover:border-signal-info/50">
            <UploadCloud className="h-6 w-6 text-muted" strokeWidth={1.5} />
            <span className="text-xs text-muted">
              {file ? file.name : "Click to upload a road image (JPG/PNG)"}
            </span>
            <input
              type="file"
              accept="image/jpeg,image/png,image/webp"
              className="hidden"
              onChange={(e) => handleFile(e.target.files?.[0] ?? null)}
            />
          </label>

          <button
            onClick={runDetection}
            disabled={!file || loading}
            className="mt-4 flex w-full items-center justify-center gap-2 rounded bg-signal-info px-4 py-2 text-sm font-medium text-base transition-opacity hover:opacity-90 disabled:opacity-50"
          >
            <Sparkles className="h-4 w-4" />
            {loading ? "Running detection…" : "Run Detection"}
          </button>

          {error && (
            <p className="mt-3 rounded border border-signal-high/30 bg-signal-high/10 px-3 py-2 text-xs text-signal-high">
              {error}
            </p>
          )}
        </div>

        {result && (
          <div className="rounded-md border border-border bg-panel p-4">
            <div className="mb-2 flex items-center justify-between">
              <h3 className="text-sm font-medium">Result</h3>
              <span
                className={`rounded border px-2 py-0.5 text-[11px] ${
                  result.is_demo
                    ? "border-signal-medium/40 text-signal-medium"
                    : "border-signal-good/40 text-signal-good"
                }`}
              >
                {result.is_demo ? "DEMO MODEL" : "TRAINED MODEL"}
              </span>
            </div>
            <dl className="grid grid-cols-2 gap-y-1.5 text-xs">
              <dt className="text-muted">Model version</dt>
              <dd className="font-mono">{result.model_version}</dd>
              <dt className="text-muted">Processing time</dt>
              <dd className="font-mono">{result.processing_time_ms} ms</dd>
              <dt className="text-muted">Detections</dt>
              <dd className="font-mono">{result.detections.length}</dd>
            </dl>
            <pre className="mt-3 max-h-48 overflow-auto rounded bg-card p-3 text-[11px] text-muted">
              {JSON.stringify(result, null, 2)}
            </pre>
          </div>
        )}
      </div>

      <div className="rounded-md border border-border bg-panel p-4">
        <h3 className="mb-3 text-sm font-medium">Preview</h3>
        {!previewUrl && (
          <div className="flex h-64 items-center justify-center text-xs text-muted">
            Upload an image to see it here.
          </div>
        )}
        {previewUrl && (
          <DetectionOverlay imageUrl={previewUrl} detections={result?.detections ?? []} />
        )}
      </div>
    </div>
  );
}
