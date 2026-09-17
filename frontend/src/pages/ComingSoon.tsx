import { Construction } from "lucide-react";

export function ComingSoon({ page, phase }: { page: string; phase: string }) {
  return (
    <div className="flex h-[70vh] flex-col items-center justify-center text-center">
      <Construction className="mb-3 h-8 w-8 text-muted" strokeWidth={1.5} />
      <h2 className="text-sm font-medium text-ink">{page}</h2>
      <p className="mt-1 max-w-sm text-xs text-muted">
        Not built yet — scheduled for {phase}. See the README build-status table
        for where this stands.
      </p>
    </div>
  );
}
