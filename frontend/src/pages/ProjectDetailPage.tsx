import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { EvidenceList } from "../components/Evidence/EvidenceList";
import { MapView } from "../components/ProjectMap/MapView";
import { RiskBadge, SourceBadge, VerificationBadge } from "../components/RiskAnalysis/Badges";
import { RiskContributionBars } from "../components/RiskAnalysis/RiskContributionBars";
import { api } from "../services/api";
import type { ContractorRead, ProjectDetail, TenderRead } from "../types/api";

export function ProjectDetailPage() {
  const { projectId } = useParams();
  const [project, setProject] = useState<ProjectDetail | null>(null);
  const [tenders, setTenders] = useState<TenderRead[]>([]);
  const [contractors, setContractors] = useState<ContractorRead[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  function refresh() {
    if (!projectId) return;
    Promise.all([api.project(projectId), api.tenders(), api.contractors()])
      .then(([detail, tenderPage, contractorPage]) => {
        setProject(detail);
        setTenders(tenderPage.items.filter((item) => item.project_id === projectId));
        setContractors(contractorPage.items);
      })
      .catch(() => setError("Unable to load project details."));
  }

  useEffect(() => {
    refresh();
  }, [projectId]);

  async function runAssessment() {
    if (!projectId) return;
    setBusy(true);
    try {
      await api.assess(projectId);
      refresh();
    } finally {
      setBusy(false);
    }
  }

  if (error) return <p className="text-sm text-red-800">{error}</p>;
  if (!project) return <p className="text-sm text-slate-600">Loading project details…</p>;

  const assessment = project.latest_assessment;
  const isSynthetic = project.data_source === "SYNTHETIC";

  return (
    <div className="space-y-6">
      {/* Top Banner for Synthetic Demo Data (Displayed ONLY ONCE near top) */}
      {isSynthetic && (
        <div className="bg-amber-500/10 border border-amber-500/30 text-amber-900 px-4 py-2 rounded-lg text-xs font-semibold flex items-center space-x-2">
          <span className="bg-amber-600 text-white px-2 py-0.5 rounded text-[10px] tracking-wider uppercase font-bold">
            SYNTHETIC DEMO DATA
          </span>
          <span>This project record is generated synthetic data for demonstration purposes.</span>
        </div>
      )}

      {/* Header Area */}
      <div className="flex flex-wrap items-start justify-between gap-4 border-b border-slate-200 pb-4">
        <div>
          <div className="flex items-center space-x-2">
            <span className="text-xs font-mono font-bold text-slate-500 bg-slate-100 px-2 py-0.5 rounded">
              {project.code}
            </span>
            <SourceBadge source={project.data_source} />
          </div>
          <h2 className="text-2xl font-bold text-slate-900 tracking-tight mt-1">{project.name}</h2>
          <p className="mt-1 text-sm text-slate-600 max-w-3xl">{project.description}</p>

          <div className="mt-3 flex flex-wrap items-center gap-2">
            {assessment ? <RiskBadge level={assessment.risk_level} score={assessment.risk_score} /> : null}
            {assessment ? <VerificationBadge status={assessment.verification_status} /> : null}
            {project.completion_status && (
              <span className="text-xs font-medium text-slate-600 bg-slate-100 px-2.5 py-0.5 rounded">
                Status: {project.completion_status}
              </span>
            )}
          </div>
        </div>

        <div className="flex items-center space-x-3">
          <button
            type="button"
            onClick={runAssessment}
            disabled={busy}
            className="rounded-lg bg-slate-900 hover:bg-slate-800 px-4 py-2 text-xs font-semibold text-white disabled:opacity-60 transition-colors shadow-xs"
          >
            {busy ? "Assessing…" : "Re-run Risk Assessment"}
          </button>
          <Link
            to={`/investigation?project=${project.id}`}
            className="rounded-lg bg-blue-600 hover:bg-blue-700 px-4 py-2 text-xs font-semibold text-white transition-colors shadow-xs"
          >
            Open Investigation →
          </Link>
        </div>
      </div>

      {/* Risk Score & Geospatial Grid */}
      <section className="grid gap-6 lg:grid-cols-2">
        <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm space-y-4">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400">Risk Assessment Overview</h3>
          {assessment ? (
            <div className="space-y-3">
              <div className="flex items-baseline space-x-3">
                <span className="text-4xl font-extrabold text-slate-900">{assessment.risk_score}</span>
                <span className="text-sm font-semibold text-slate-500">/ 100 Risk Score</span>
                <RiskBadge level={assessment.risk_level} />
              </div>
              <p className="text-sm text-slate-700 font-medium leading-relaxed">{assessment.reason_text}</p>
              
              <div className="pt-3 border-t border-slate-100 grid grid-cols-2 gap-2 text-xs text-slate-500">
                <div>
                  <span className="font-semibold text-slate-700">Source Module:</span> {assessment.source_module}
                </div>
                <div>
                  <span className="font-semibold text-slate-700">Analysis Type:</span> {assessment.analysis_type}
                </div>
              </div>
            </div>
          ) : (
            <p className="text-sm text-slate-500">No assessment recorded yet.</p>
          )}
        </div>

        <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm space-y-2">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400">Project Geographic Location</h3>
          <MapView projects={[project]} height={220} />
        </div>
      </section>

      {/* Contributing Signals - HORIZONTAL CONTRIBUTION BARS */}
      <section className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm space-y-4">
        <div className="flex items-center justify-between border-b border-slate-100 pb-3">
          <h3 className="text-sm font-bold uppercase tracking-wider text-slate-800">
            Active Risk Contributing Signals
          </h3>
          <span className="text-xs text-slate-500 font-medium">Additive Score Breakdown</span>
        </div>
        <RiskContributionBars signals={assessment?.contributing_signals ?? []} />
      </section>

      {/* Evidence & Provenance */}
      <section className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm space-y-4">
        <div className="border-b border-slate-100 pb-3">
          <h3 className="text-sm font-bold uppercase tracking-wider text-slate-800">Evidence & Provenance</h3>
          <p className="text-xs text-slate-500">Audit trail files, photographs, geotags, and verification sources.</p>
        </div>
        <EvidenceList evidence={project.evidence} links={assessment?.evidence_references} />
      </section>

      {/* Tenders & Contractors Grid */}
      <section className="grid gap-6 md:grid-cols-2">
        <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm space-y-3">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400">Linked Tender Records</h3>
          <ul className="space-y-2 text-xs divide-y divide-slate-100">
            {tenders.map((tender) => (
              <li key={tender.id} className="pt-2 flex justify-between items-start">
                <div>
                  <p className="font-semibold font-mono text-slate-800">{tender.official_tender_id}</p>
                  <p className="text-slate-500">Bidders: {tender.bidder_count ?? "N/A"}</p>
                </div>
                <div className="text-right">
                  <p className="font-semibold text-slate-900">
                    {tender.winning_amount ? `₹${tender.winning_amount.toLocaleString()}` : "N/A"}
                  </p>
                  <SourceBadge source={tender.data_source} />
                </div>
              </li>
            ))}
            {!tenders.length && <p className="text-xs text-slate-500 italic py-2">No tenders linked.</p>}
          </ul>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm space-y-3">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400">Contractors in Dataset</h3>
          <ul className="space-y-2 text-xs divide-y divide-slate-100">
            {contractors.map((contractor) => (
              <li key={contractor.id} className="pt-2 flex justify-between items-center">
                <div>
                  <p className="font-semibold text-slate-800">{contractor.name}</p>
                  <p className="text-slate-500">Awards: {contractor.award_count}</p>
                </div>
                <SourceBadge source={contractor.data_source} />
              </li>
            ))}
          </ul>
        </div>
      </section>
    </div>
  );
}
