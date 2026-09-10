import type { RiskLevel } from "../../types/api";

interface RiskDistributionProps {
  counts: Record<RiskLevel, number>;
  total: number;
}

const COLORS: Record<RiskLevel, { stroke: string; bg: string; text: string }> = {
  LOW: { stroke: "#16a34a", bg: "bg-emerald-500", text: "text-emerald-700" },
  MEDIUM: { stroke: "#d97706", bg: "bg-amber-500", text: "text-amber-700" },
  HIGH: { stroke: "#dc2626", bg: "bg-red-500", text: "text-red-700" },
  CRITICAL: { stroke: "#991b1b", bg: "bg-rose-900", text: "text-rose-900" },
};

export function RiskDonutChart({ counts, total }: RiskDistributionProps) {
  const levels: RiskLevel[] = ["LOW", "MEDIUM", "HIGH", "CRITICAL"];

  // Calculate SVG arc paths
  const radius = 40;
  const circumference = 2 * Math.PI * radius;
  let accumulatedPercent = 0;

  const slices = levels.map((level) => {
    const count = counts[level] || 0;
    const percent = total > 0 ? count / total : 0;
    const strokeDasharray = `${percent * circumference} ${circumference}`;
    const strokeDashoffset = -accumulatedPercent * circumference;
    accumulatedPercent += percent;

    return {
      level,
      count,
      percent: Math.round(percent * 100),
      strokeDasharray,
      strokeDashoffset,
      color: COLORS[level].stroke,
    };
  });

  return (
    <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-base font-semibold text-slate-900">Risk Level Distribution</h3>
        <span className="text-xs font-medium text-slate-500 bg-slate-100 px-2.5 py-1 rounded-full">
          Total Assessed: {total}
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 items-center">
        {/* SVG Donut */}
        <div className="relative flex items-center justify-center py-2">
          <svg className="w-48 h-48 transform -rotate-90" viewBox="0 0 100 100">
            {/* Base Background Track */}
            <circle
              cx="50"
              cy="50"
              r={radius}
              fill="transparent"
              stroke="#e2e8f0"
              strokeWidth="12"
            />
            {total > 0 ? (
              slices.map((slice) =>
                slice.count > 0 ? (
                  <circle
                    key={slice.level}
                    cx="50"
                    cy="50"
                    r={radius}
                    fill="transparent"
                    stroke={slice.color}
                    strokeWidth="12"
                    strokeDasharray={slice.strokeDasharray}
                    strokeDashoffset={slice.strokeDashoffset}
                    className="transition-all duration-500 ease-out hover:opacity-90"
                  />
                ) : null
              )
            ) : null}
          </svg>
          <div className="absolute flex flex-col items-center justify-center text-center">
            <span className="text-2xl font-bold text-slate-900">{total}</span>
            <span className="text-[11px] font-medium uppercase text-slate-500">Projects</span>
          </div>
        </div>

        {/* Legend & Breakdown */}
        <div className="space-y-3">
          {levels.map((level) => {
            const count = counts[level] || 0;
            const pct = total > 0 ? Math.round((count / total) * 100) : 0;
            return (
              <div key={level} className="flex items-center justify-between text-xs">
                <div className="flex items-center space-x-2">
                  <span className={`w-3 h-3 rounded-sm ${COLORS[level].bg}`} />
                  <span className="font-medium text-slate-700">{level}</span>
                </div>
                <div className="flex items-center space-x-3">
                  <span className="font-semibold text-slate-900">{count}</span>
                  <span className="text-slate-400 w-9 text-right">{pct}%</span>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
