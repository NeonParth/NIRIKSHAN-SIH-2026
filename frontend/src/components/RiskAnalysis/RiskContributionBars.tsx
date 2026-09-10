import type { RiskSignalRead } from "../../types/api";

interface RiskContributionBarsProps {
  signals: RiskSignalRead[];
}

export function RiskContributionBars({ signals }: RiskContributionBarsProps) {
  if (!signals || signals.length === 0) {
    return (
      <div className="text-xs text-slate-500 italic p-3 bg-slate-50 rounded-lg border border-slate-200">
        No active risk signals triggered.
      </div>
    );
  }

  // Find max contribution for proportional bar scaling (min max scale of 30 for clear display)
  const maxContribution = Math.max(30, ...signals.map((s) => Math.abs(s.contribution)));

  return (
    <div className="space-y-4">
      {signals.map((signal) => {
        const widthPct = Math.min(100, Math.round((Math.abs(signal.contribution) / maxContribution) * 100));

        return (
          <div key={signal.id || signal.signal_code} className="space-y-1.5 bg-slate-50/80 p-3 rounded-lg border border-slate-200/80">
            <div className="flex items-center justify-between text-xs">
              <div className="flex items-center space-x-2">
                <span className="font-semibold text-slate-900">{signal.signal_name}</span>
                {signal.observed_value && (
                  <span className="text-[11px] text-slate-500 bg-slate-200/70 px-2 py-0.5 rounded font-mono">
                    Observed: {signal.observed_value}
                  </span>
                )}
              </div>
              <span className="font-bold text-amber-700 bg-amber-100/80 border border-amber-300 px-2 py-0.5 rounded">
                +{signal.contribution}
              </span>
            </div>

            {/* Horizontal Bar */}
            <div className="w-full bg-slate-200 rounded-full h-2.5 overflow-hidden">
              <div
                className="bg-amber-600 h-2.5 rounded-full transition-all duration-500 ease-out"
                style={{ width: `${widthPct}%` }}
              />
            </div>

            <p className="text-[11px] text-slate-600 leading-snug">{signal.explanation}</p>
          </div>
        );
      })}
    </div>
  );
}
