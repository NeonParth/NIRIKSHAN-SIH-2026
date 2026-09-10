import type { DataSource, RiskLevel, VerificationStatus } from "../../types/api";

const riskStyles: Record<RiskLevel, string> = {
  LOW: "bg-emerald-50 text-emerald-800 border-emerald-200",
  MEDIUM: "bg-amber-50 text-amber-900 border-amber-200",
  HIGH: "bg-orange-50 text-orange-900 border-orange-200",
  CRITICAL: "bg-red-50 text-red-900 border-red-200",
};

export function RiskBadge({ level, score }: { level: RiskLevel; score?: number }) {
  return (
    <span className={`inline-flex items-center gap-1 rounded border px-2 py-0.5 text-xs font-semibold ${riskStyles[level]}`}>
      {level}
      {score !== undefined ? <span>{score}/100</span> : null}
    </span>
  );
}

export function SourceBadge({ source }: { source: DataSource }) {
  const styles =
    source === "SYNTHETIC"
      ? "bg-slate-800 text-white"
      : source === "PUBLIC"
        ? "bg-sky-100 text-sky-900 border border-sky-200"
        : "bg-white text-navy-900 border border-slate-300";
  return <span className={`rounded px-2 py-0.5 text-[11px] font-semibold tracking-wide ${styles}`}>{source}</span>;
}

export function VerificationBadge({ status }: { status: VerificationStatus }) {
  return (
    <span className="rounded border border-slate-300 bg-white px-2 py-0.5 text-[11px] font-medium text-slate-700">
      {status.replace("_", " ")}
    </span>
  );
}
