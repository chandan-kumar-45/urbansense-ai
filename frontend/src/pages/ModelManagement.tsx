import { useEffect, useState } from "react";
import { activateModel, getModels, type ModelVersion } from "@/services/ai";
import { useAuth } from "@/hooks/useAuth";

const STATUS_COLOR: Record<string, string> = {
  ACTIVE: "text-signal-good border-signal-good/40",
  TESTING: "text-signal-medium border-signal-medium/40",
  INACTIVE: "text-muted border-border",
};

export function ModelManagement() {
  const { user } = useAuth();
  const [models, setModels] = useState<ModelVersion[]>([]);
  const [error, setError] = useState<string | null>(null);

  function load() {
    getModels().then(setModels).catch((e) => setError(e.message));
  }

  useEffect(load, []);

  const grouped = models.reduce<Record<string, ModelVersion[]>>((acc, m) => {
    (acc[m.model_name] ??= []).push(m);
    return acc;
  }, {});

  async function handleActivate(id: string) {
    await activateModel(id);
    load();
  }

  return (
    <div className="space-y-6">
      {error && (
        <p className="rounded border border-signal-high/30 bg-signal-high/10 px-3 py-2 text-xs text-signal-high">
          {error}
        </p>
      )}
      {Object.entries(grouped).map(([name, versions]) => (
        <div key={name} className="rounded-md border border-border bg-panel">
          <div className="border-b border-border px-4 py-3">
            <h3 className="text-sm font-medium capitalize">{name.replace("_", " ")}</h3>
          </div>
          <table className="w-full text-left text-xs">
            <thead className="text-muted">
              <tr>
                <th className="px-4 py-2 font-normal">Version</th>
                <th className="px-4 py-2 font-normal">Type</th>
                <th className="px-4 py-2 font-normal">Framework</th>
                <th className="px-4 py-2 font-normal">Demo</th>
                <th className="px-4 py-2 font-normal">Status</th>
                <th className="px-4 py-2 font-normal" />
              </tr>
            </thead>
            <tbody>
              {versions.map((v) => (
                <tr key={v.id} className="border-t border-border/60">
                  <td className="px-4 py-2 font-mono">{v.version}</td>
                  <td className="px-4 py-2">{v.model_type}</td>
                  <td className="px-4 py-2">{v.framework ?? "—"}</td>
                  <td className="px-4 py-2">{v.is_demo ? "Yes" : "No"}</td>
                  <td className="px-4 py-2">
                    <span className={`rounded border px-1.5 py-0.5 text-[11px] ${STATUS_COLOR[v.status]}`}>
                      {v.status}
                    </span>
                  </td>
                  <td className="px-4 py-2">
                    {v.status !== "ACTIVE" && user?.role === "ADMIN" && (
                      <button
                        onClick={() => handleActivate(v.id)}
                        className="rounded border border-border px-2 py-1 text-[11px] hover:bg-card"
                      >
                        Activate
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ))}
      <p className="text-[11px] text-muted">
        Registering new model versions is available via{" "}
        <code className="font-mono">POST /api/models/register</code> (Admin
        only) — see docs/AI_MODEL_INTEGRATION.md for the full workflow of
        promoting a newly trained model to Active.
      </p>
    </div>
  );
}
