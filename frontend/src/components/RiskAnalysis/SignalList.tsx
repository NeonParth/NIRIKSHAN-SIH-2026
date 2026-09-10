import type { RiskSignalRead } from "../../types/api";

export function SignalList({ signals }: { signals: RiskSignalRead[] }) {
  if (!signals.length) {
    return <p className="text-sm text-slate-600">No contributing signals were triggered.</p>;
  }
  return (
    <ul className="divide-y divide-slate-200 border border-slate-200 bg-white">
      {signals.map((signal) => (
        <li key={signal.id} className="px-4 py-3">
          <div className="flex items-start justify-between gap-3">
            <div>
              <p className="font-medium text-navy-900">
                +{Number(signal.contribution)} {signal.signal_name}
              </p>
              <p className="mt-1 text-sm text-slate-600">{signal.explanation}</p>
              <p className="mt-1 text-xs text-slate-500">
                Module: {signal.source_module}
                {signal.observed_value ? ` · Observed: ${signal.observed_value}` : ""}
                {signal.threshold ? ` · Threshold: ${signal.threshold}` : ""}
              </p>
            </div>
          </div>
        </li>
      ))}
    </ul>
  );
}
