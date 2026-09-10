import { FormEvent, useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { EvidenceList } from "../components/Evidence/EvidenceList";
import { RiskBadge, SourceBadge, VerificationBadge } from "../components/RiskAnalysis/Badges";
import { RiskContributionBars } from "../components/RiskAnalysis/RiskContributionBars";
import { api } from "../services/api";
import type { ProjectSummary, RiskAssessmentRead, VerificationStatus } from "../types/api";

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "";

export function InvestigationPage() {
  const [searchParams] = useSearchParams();
  const targetProjectId = searchParams.get("project");

  const [items, setItems] = useState<RiskAssessmentRead[]>([]);
  const [projectsMap, setProjectsMap] = useState<Record<string, ProjectSummary>>({});
  const [selected, setSelected] = useState<RiskAssessmentRead | null>(null);
  const [statusInput, setStatusInput] = useState<VerificationStatus>("UNDER_REVIEW");
  const [remarks, setRemarks] = useState("");
  const [saving, setSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState<string | null>(null);

  function load() {
    Promise.all([
      api.risks(new URLSearchParams({ page_size: "100" })),
      api.projects(new URLSearchParams({ page_size: "100" })),
    ]).then(([riskPage, projectPage]) => {
      setItems(riskPage.items);

      const pMap: Record<string, ProjectSummary> = {};
      projectPage.items.forEach((p) => {
        pMap[p.id] = p;
      });
      setProjectsMap(pMap);

      let targetItem: RiskAssessmentRead | null = null;
      if (targetProjectId) {
        targetItem = riskPage.items.find((item) => item.project_id === targetProjectId) || null;
      }
      if (!targetItem) {
        targetItem = riskPage.items[0] ?? null;
      }

      setSelected(targetItem);
      if (targetItem) {
        setStatusInput(targetItem.verification_status);
        setRemarks(targetItem.reviewer_remarks || "");
      }
    });
  }

  useEffect(() => {
    load();
  }, [targetProjectId]);

  const handleSelect = (item: RiskAssessmentRead) => {
    setSelected(item);
    setStatusInput(item.verification_status);
    setRemarks(item.reviewer_remarks || "");
    setSaveSuccess(null);
  };

  async function submit(event: FormEvent) {
    event.preventDefault();
    if (!selected) return;
    setSaving(true);
    setSaveSuccess(null);
    try {
      const updated = await api.review(selected.id, statusInput, remarks);
      setSelected(updated);
      setSaveSuccess(`Verification decision updated to ${statusInput.replace("_", " ")}.`);
      load();
    } catch (err) {
      alert("Failed to submit review.");
    } finally {
      setSaving(false);
    }
  }

  const handleDownloadReport = () => {
    if (!selected) return;
    const downloadUrl = `${API_BASE}/api/v1/projects/${selected.project_id}/investigation-report.docx`;
    window.open(downloadUrl, "_blank");
  };

  const project = selected ? projectsMap[selected.project_id] : null;

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-900 tracking-tight">
          Authority Investigator Workspace
        </h2>
        <p className="text-sm text-slate-600">
          Official reviewer workspace for inspecting evidence, recording audit observations, and exporting formal investigation reports.
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-12">
        {/* Left Column: Assessment Selection Sidebar */}
        <section className="lg:col-span-4 space-y-3">
          <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
            <div className="bg-slate-900 text-white px-4 py-3 text-xs font-semibold uppercase tracking-wider flex justify-between items-center">
              <span>Investigation Queue</span>
              <span>{items.length} Items</span>
            </div>
            <div className="divide-y divide-slate-100 max-h-[640px] overflow-y-auto">
              {items.map((item) => {
                const p = projectsMap[item.project_id];
                const isSelected = selected?.id === item.id;
                return (
                  <button
                    key={item.id}
                    type="button"
                    onClick={() => handleSelect(item)}
                    className={`w-full p-3.5 text-left transition-all flex flex-col space-y-2 ${
                      isSelected
                        ? "bg-blue-50 border-l-4 border-l-blue-600"
                        : "hover:bg-slate-50 border-l-4 border-l-transparent"
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-xs font-mono text-slate-800">
                        {p?.code ?? item.project_id.substring(0, 8)}
                      </span>
                      <RiskBadge level={item.risk_level} score={item.risk_score} />
                    </div>
                    <p className="text-xs text-slate-700 font-medium line-clamp-1">{p?.name ?? "Project Record"}</p>
                    <div className="flex items-center justify-between">
                      <SourceBadge source={item.data_source} />
                      <VerificationBadge status={item.verification_status} />
                    </div>
                  </button>
                );
              })}
            </div>
          </div>
        </section>

        {/* Right Column: Review Workspace & Action Tools */}
        <section className="lg:col-span-8 space-y-6">
          {selected ? (
            <div className="space-y-6">
              {/* Project Summary Header */}
              <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm space-y-4">
                <div className="flex flex-wrap items-start justify-between gap-4 border-b border-slate-100 pb-4">
                  <div>
                    <div className="flex items-center space-x-2">
                      <span className="text-xs font-mono font-bold text-slate-400 uppercase">
                        {project?.code ?? selected.project_id}
                      </span>
                      <SourceBadge source={selected.data_source} />
                      {project?.data_source === "SYNTHETIC" && (
                        <span className="bg-amber-100 text-amber-900 text-[10px] font-bold px-2 py-0.5 rounded">
                          SYNTHETIC DEMO DATA
                        </span>
                      )}
                    </div>
                    <h3 className="text-xl font-bold text-slate-900 mt-1">{project?.name ?? "MPLADS Project Record"}</h3>
                    <p className="text-xs text-slate-500 mt-1">{project?.description}</p>
                  </div>

                  {/* Download DOCX Investigation Report */}
                  <button
                    onClick={handleDownloadReport}
                    className="inline-flex items-center space-x-2 bg-emerald-700 hover:bg-emerald-800 text-white font-semibold text-xs py-2.5 px-4 rounded-lg shadow-xs transition-colors"
                  >
                    <span>📄 Download DOCX Report</span>
                  </button>
                </div>

                <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs">
                  <div className="bg-slate-50 p-3 rounded-lg border border-slate-100">
                    <span className="text-slate-400 block uppercase text-[10px] font-bold">Risk Score</span>
                    <div className="mt-1">
                      <RiskBadge level={selected.risk_level} score={selected.risk_score} />
                    </div>
                  </div>

                  <div className="bg-slate-50 p-3 rounded-lg border border-slate-100">
                    <span className="text-slate-400 block uppercase text-[10px] font-bold">Verification</span>
                    <div className="mt-1">
                      <VerificationBadge status={selected.verification_status} />
                    </div>
                  </div>

                  <div className="bg-slate-50 p-3 rounded-lg border border-slate-100">
                    <span className="text-slate-400 block uppercase text-[10px] font-bold">Analysis Type</span>
                    <span className="font-mono font-semibold text-slate-700 mt-1 block">
                      {selected.analysis_type}
                    </span>
                  </div>

                  <div className="bg-slate-50 p-3 rounded-lg border border-slate-100">
                    <span className="text-slate-400 block uppercase text-[10px] font-bold">Data Source</span>
                    <span className="font-mono font-semibold text-slate-700 mt-1 block">
                      {selected.data_source}
                    </span>
                  </div>
                </div>
              </div>

              {/* Contributing Risk Signals (Horizontal Contribution Bars) */}
              <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm space-y-4">
                <div className="border-b border-slate-100 pb-2">
                  <h4 className="text-sm font-bold uppercase tracking-wider text-slate-800">
                    Contributing Risk Signals
                  </h4>
                  <p className="text-xs text-slate-500">Additive anomaly signals calculated by rule engine.</p>
                </div>
                <RiskContributionBars signals={selected.contributing_signals} />
              </div>

              {/* Evidence & Provenance */}
              <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm space-y-4">
                <div className="border-b border-slate-100 pb-2">
                  <h4 className="text-sm font-bold uppercase tracking-wider text-slate-800">
                    Linked Evidence & Provenance
                  </h4>
                  <p className="text-xs text-slate-500">Documentary and spatial evidence references.</p>
                </div>
                <EvidenceList links={selected.evidence_references} />
              </div>

              {/* Reviewer Action Form */}
              <form onSubmit={submit} className="bg-slate-900 text-white rounded-xl p-6 shadow-md space-y-4">
                <div className="border-b border-slate-800 pb-3 flex justify-between items-center">
                  <h4 className="text-sm font-bold uppercase tracking-wider text-slate-200">
                    Record Authority Reviewer Decision
                  </h4>
                  <span className="text-[11px] text-slate-400">Phase 1 Human Verification</span>
                </div>

                {saveSuccess && (
                  <div className="bg-emerald-950 border border-emerald-700 text-emerald-300 p-3 rounded-lg text-xs font-medium">
                    ✓ {saveSuccess}
                  </div>
                )}

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-semibold uppercase text-slate-300 mb-1">
                      Verification Status
                    </label>
                    <select
                      value={statusInput}
                      onChange={(e) => setStatusInput(e.target.value as VerificationStatus)}
                      className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:ring-2 focus:ring-blue-500 font-medium"
                    >
                      <option value="UNDER_REVIEW">UNDER REVIEW</option>
                      <option value="HUMAN_VERIFIED">HUMAN VERIFIED</option>
                      <option value="HUMAN_REJECTED">HUMAN REJECTED</option>
                    </select>
                  </div>
                </div>

                <div>
                  <label htmlFor="remarks" className="block text-xs font-semibold uppercase text-slate-300 mb-1">
                    Reviewer Findings & Remarks
                  </label>
                  <textarea
                    id="remarks"
                    className="w-full bg-slate-800 border border-slate-700 rounded-lg p-3 text-xs text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500 font-sans"
                    rows={4}
                    value={remarks}
                    onChange={(e) => setRemarks(e.target.value)}
                    placeholder="Record the verification findings, evidence reviewed, discrepancies observed, and recommended follow-up actions."
                  />
                </div>

                <div className="flex justify-end space-x-3 pt-2">
                  <button
                    type="submit"
                    disabled={saving}
                    className="bg-blue-600 hover:bg-blue-500 text-white font-semibold text-xs py-2.5 px-6 rounded-lg transition-colors shadow-xs disabled:opacity-60"
                  >
                    {saving ? "Saving Decision…" : "Save Review Decision"}
                  </button>
                </div>
              </form>
            </div>
          ) : (
            <div className="bg-white rounded-xl border border-slate-200 p-8 text-center text-slate-500">
              Select an investigation item from the queue to conduct review.
            </div>
          )}
        </section>
      </div>
    </div>
  );
}
