import { useState, type FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import { AlertCircle } from "lucide-react";
import { useAuth } from "@/hooks/useAuth";
import { ApiError } from "@/services/api";

const DEMO_ACCOUNTS = [
  { role: "Admin", email: "admin@urbansense.ai" },
  { role: "Transport Authority", email: "authority@urbansense.ai" },
  { role: "Traffic Officer", email: "traffic@urbansense.ai" },
  { role: "Maintenance Officer", email: "maintenance@urbansense.ai" },
  { role: "Analyst", email: "analyst@urbansense.ai" },
];

export function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      await login(email, password);
      navigate("/dashboard");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not sign in. Try again.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-base px-4">
      <div className="w-full max-w-sm">
        <div className="mb-8 flex items-center gap-2.5">
          <div className="flex h-9 w-9 items-center justify-center rounded bg-signal-info/15">
            <span className="font-mono text-sm font-semibold text-signal-info">US</span>
          </div>
          <div className="leading-tight">
            <p className="text-base font-semibold">UrbanSense AI</p>
            <p className="text-xs text-muted">Command Center Access</p>
          </div>
        </div>

        <form
          onSubmit={handleSubmit}
          className="rounded-md border border-border bg-panel p-6"
        >
          <div className="space-y-4">
            <div>
              <label className="mb-1.5 block text-xs text-muted" htmlFor="email">
                Email
              </label>
              <input
                id="email"
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full rounded border border-border bg-card px-3 py-2 text-sm text-ink outline-none focus:border-signal-info"
                placeholder="you@urbansense.ai"
              />
            </div>
            <div>
              <label className="mb-1.5 block text-xs text-muted" htmlFor="password">
                Password
              </label>
              <input
                id="password"
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full rounded border border-border bg-card px-3 py-2 text-sm text-ink outline-none focus:border-signal-info"
                placeholder="••••••••"
              />
            </div>
          </div>

          {error && (
            <div className="mt-4 flex items-start gap-2 rounded border border-signal-high/30 bg-signal-high/10 px-3 py-2 text-xs text-signal-high">
              <AlertCircle className="mt-0.5 h-3.5 w-3.5 shrink-0" strokeWidth={1.75} />
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={submitting}
            className="mt-5 w-full rounded bg-signal-info px-4 py-2 text-sm font-medium text-base transition-opacity hover:opacity-90 disabled:opacity-50"
          >
            {submitting ? "Signing in…" : "Sign in"}
          </button>
        </form>

        <div className="mt-5 rounded-md border border-border/60 bg-panel/50 p-4">
          <p className="mb-2 text-[11px] font-medium text-muted">
            Demo accounts — password <span className="font-mono text-ink">Demo@123</span>
          </p>
          <ul className="space-y-1">
            {DEMO_ACCOUNTS.map((acc) => (
              <li
                key={acc.email}
                className="flex items-center justify-between text-[11px]"
              >
                <span className="text-muted">{acc.role}</span>
                <button
                  type="button"
                  onClick={() => setEmail(acc.email)}
                  className="font-mono text-signal-info hover:underline"
                >
                  {acc.email}
                </button>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}
