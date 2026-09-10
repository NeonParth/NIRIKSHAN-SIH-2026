import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { RiskBadge, SourceBadge, VerificationBadge } from "../components/RiskAnalysis/Badges";
import { RiskContributionBars } from "../components/RiskAnalysis/RiskContributionBars";
import { api } from "../services/api";
import type { ProjectSummary, RiskAssessmentRead } from "../types/api";

export function RiskAnalysisPage() {
  const [assessments, setAssessments] = useState<RiskAssessmentRead[]>([]);
  const [projectsMap, setProjectsMap] = useState<Record<string, ProjectSummary>>({});
  const [selected, setSelected] = useState<RiskAssessmentRead | null>(null);

  useEffect(() => {
    Promise.all([
      api.risks(new URLSearchParams({ page_size: "100" })),
      api.projects(new URLSearchParams({ page_size: "100" })),
    ]).then(([riskPage, projectPage]) => {
      // Order assessments by risk score descending
      const sorted = [...riskPage.items].sort((a, b) => b.risk_score - a.risk_score);
      setAssessments(sorted);
      setSelected(sorted[0] ?? null);

      const pMap: Record<string, ProjectSummary> = {};
      projectPage.items.forEach((p) => {
        pMap[p.id] = p;
      });
      setProjectsMap(pMap);
    });
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-900 tracking-tight">Risk Priority Analysis Queue</h2>
        <p className="text-sm text-slate-600">
          Prioritized list of MPLADS project anomaly indicators requiring official verification.
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-12">
        {/* Left Column: Prioritized Assessment Table/List */}
        <section className="lg:col-span-5 space-y-3">
          <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
            <div className="bg-slate-900 text-white px-4 py-3 flex items-center justify-between text-xs font-semibold uppercase tracking-wider">
              <span>Risk Priority Queue</span>
              <span>{assessments.length} Records</span>
            </div>

            <div className="divide-y divide-slate-100 max-h-[620px] overflow-y-auto">
              {assessments.map((item) => {
                const project = projectsMap[item.project_id];
                const isSelected = selected?.id === item.id;
                const isHighOrCritical = item.risk_level === "HIGH" || item.risk_level === "CRITICAL";

                return (
                  <button
                    key={item.id}
                    type="button"
                    onClick={() => setSelected(item)}
                    className={`w-full p-3.5 text-left transition-all flex flex-col space-y-2 ${
                      isSelected
                        ? "bg-blue-50/90 border-l-4 border-l-blue-600"
                        : "hover:bg-slate-50 border-l-4 border-l-transparent"
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-xs font-mono text-slate-800">
                        {project?.code ?? item.project_id.substring(0, 8)}
                      </span>
                      <RiskBadge level={item.risk_level} score={item.risk_score} />
                    </div>

                    <p className="text-xs font-medium text-slate-900 line-clamp-1">
                      {project?.name ?? "MPLADS Project Record"}
                    </p>

                    <div className="flex items-center justify-between text-[11px] text-slate-500">
                      <div className="flex items-center space-x-2">
                        <SourceBadge source={item.data_source} />
                        {isHighOrCritical && (
                          <span className="bg-rose-100 text-rose-800 font-bold px-1.5 py-0.5 rounded text-[10px]">
                            Requires Verification
                          </span>
                        )}
                      </div>
                      <VerificationBadge status={item.verification_status} />
                    </div>
                  </button>
                );
              })}
            </div>
          </div>
        </section>

        {/* Right Column: Selected Assessment Details & Horizontal Signal Bars */}
        <section className="lg:col-span-7 space-y-6">
          {selected ? (
            <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm space-y-6">
              {/* Selected Header */}
              <div className="flex flex-wrap items-start justify-between gap-4 border-b border-slate-100 pb-4">
                <div>
                  <span className="text-xs font-mono font-bold text-slate-400 uppercase tracking-wider">
                    {projectsMap[selected.project_id]?.code ?? selected.project_id}
                  </span>
                  <h3 className="text-xl font-bold text-slate-900 leading-snug">
                    {projectsMap[selected.project_id]?.name ?? "Selected Project Anomaly Record"}
                  </h3>
                  <div className="mt-2 flex flex-wrap items-center gap-2">
                    <RiskBadge level={selected.risk_level} score={selected.risk_score} />
                    <VerificationBadge status={selected.verification_status} />
                    <SourceBadge source={selected.data_source} />
                  </div>
                </div>

                <Link
                  to={`/investigation?project=${selected.project_id}`}
                  className="bg-blue-600 hover:bg-blue-700 text-white font-semibold text-xs py-2 px-4 rounded-lg shadow-xs transition-colors"
                >
                  Investigate Project →
                </Link>
              </div>

              {/* Summary explanation */}
              <div className="space-y-2">
                <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400">Reason Text Summary</h4>
                <p className="text-sm text-slate-800 bg-slate-50 p-3 rounded-lg border border-slate-200 font-medium">
                  {selected.reason_text}
                </p>
              </div>

              {/* Horizontal Contribution Bars */}
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400">
                    Contributing Risk Signals
                  </h4>
                  <span className="text-xs text-slate-500 font-mono">Module: {selected.source_module}</span>
                </div>
                <RiskContributionBars signals={selected.contributing_signals} />
              </div>

              {/* Metadata details */}
              <div className="grid grid-cols-2 gap-4 text-xs text-slate-500 pt-3 border-t border-slate-100">
                <div>
                  <span className="font-semibold text-slate-700">Analysis Type:</span> {selected.analysis_type}
                </div>
                <div>
                  <span className="font-semibold text-slate-700">Assessed Timestamp:</span>{" "}
                  {new Date(selected.created_at).toLocaleString()}
                </div>
              </div>
            </div>
          ) : (
            <div className="bg-white rounded-xl border border-slate-200 p-8 text-center text-slate-500">
              Select an assessment record from the priority queue to inspect signal details.
            </div>
          )}
        </section>
      </div>
    </div>
  );
}
