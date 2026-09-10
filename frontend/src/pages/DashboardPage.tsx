import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { ProvenanceBanner } from "../components/Dashboard/ProvenanceBanner";
import { RiskDonutChart } from "../components/Dashboard/RiskDonutChart";
import { StatCard } from "../components/Dashboard/StatCard";
import { MapView } from "../components/ProjectMap/MapView";
import { RiskBadge, VerificationBadge } from "../components/RiskAnalysis/Badges";
import { api } from "../services/api";
import type { ProjectSummary, RiskAssessmentRead, RiskLevel } from "../types/api";

export function DashboardPage() {
  const [projects, setProjects] = useState<ProjectSummary[]>([]);
  const [risks, setRisks] = useState<RiskAssessmentRead[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([
      api.projects(new URLSearchParams({ page_size: "100" })),
      api.risks(new URLSearchParams({ page_size: "10" })),
    ])
      .then(([projectPage, riskPage]) => {
        setProjects(projectPage.items);
        setRisks(riskPage.items);
      })
      .catch(() => setError("Unable to load dashboard data. Confirm the backend API is running."));
  }, []);

  const totalProjects = projects.length;
  const totalValue = projects.reduce((sum, p) => sum + (p.allocated_amount || 0), 0);

  const highCriticalCount = projects.filter((p) => {
    const level = p.latest_risk?.risk_level;
    return level === "HIGH" || level === "CRITICAL";
  }).length;

  const underReviewCount = projects.filter((p) => {
    return p.latest_risk?.verification_status === "UNDER_REVIEW";
  }).length;

  const countsByLevel: Record<RiskLevel, number> = {
    LOW: projects.filter((p) => p.latest_risk?.risk_level === "LOW").length,
    MEDIUM: projects.filter((p) => p.latest_risk?.risk_level === "MEDIUM").length,
    HIGH: projects.filter((p) => p.latest_risk?.risk_level === "HIGH").length,
    CRITICAL: projects.filter((p) => p.latest_risk?.risk_level === "CRITICAL").length,
  };

  const assessedTotal = Object.values(countsByLevel).reduce((a, b) => a + b, 0);

  const formatCurrency = (val: number) => {
    if (val >= 10000000) {
      return `₹${(val / 10000000).toFixed(2)} Cr`;
    } else if (val >= 100000) {
      return `₹${(val / 100000).toFixed(2)} Lakh`;
    }
    return `₹${val.toLocaleString()}`;
  };

  return (
    <div className="space-y-8">
      {/* Header Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-200 pb-5">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-slate-900">
            MPLADS Risk Intelligence Dashboard
          </h2>
          <p className="text-sm text-slate-600">
            Continuous project monitoring, spatial analysis, and anomaly verification.
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Link
            to="/investigation"
            className="inline-flex items-center space-x-2 bg-blue-600 hover:bg-blue-700 text-white font-medium text-xs px-4 py-2 rounded-lg transition-colors shadow-xs"
          >
            <span>Open Investigator Workspace</span>
            <span>→</span>
          </Link>
        </div>
      </div>

      {error ? (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-900 font-medium">
          {error}
        </div>
      ) : null}

      {/* Metric Cards */}
      <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard label="Total Projects" value={totalProjects} hint="Active MPLADS Works" />
        <StatCard
          label="Total Project Value"
          value={formatCurrency(totalValue)}
          hint="Allocated Outlay"
        />
        <StatCard
          label="High / Critical Risk"
          value={highCriticalCount}
          hint="Requires Priority Verification"
        />
        <StatCard
          label="Projects Under Review"
          value={underReviewCount}
          hint="Active Investigations"
        />
      </section>

      {/* Risk Distribution & Geospatial Overview */}
      <section className="grid gap-6 lg:grid-cols-12">
        <div className="lg:col-span-5">
          <RiskDonutChart counts={countsByLevel} total={assessedTotal} />
        </div>
        <div className="lg:col-span-7 bg-white border border-slate-200 rounded-xl p-5 shadow-sm space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="text-base font-semibold text-slate-900">Project Risk Map Preview</h3>
            <Link to="/map" className="text-xs text-blue-600 hover:text-blue-800 font-semibold">
              Full Map View →
            </Link>
          </div>
          <MapView projects={projects} height={320} />
        </div>
      </section>

      {/* Recent Alerts & Investigation Queue */}
      <section className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-base font-semibold text-slate-900">Recent Anomaly Assessments</h3>
            <p className="text-xs text-slate-500">
              Latest automated rule & spatial proximity risk findings requiring reviewer attention.
            </p>
          </div>
          <Link to="/risks" className="text-xs font-semibold text-blue-600 hover:text-blue-800">
            View All Risk Signals →
          </Link>
        </div>

        <div className="overflow-x-auto rounded-lg border border-slate-200">
          <table className="min-w-full text-left text-xs">
            <thead className="bg-slate-50 text-slate-500 font-semibold uppercase tracking-wider border-b border-slate-200">
              <tr>
                <th className="px-4 py-3">Project Code</th>
                <th className="px-4 py-3">Project Name</th>
                <th className="px-4 py-3">Risk Score</th>
                <th className="px-4 py-3">Analysis Type</th>
                <th className="px-4 py-3">Verification Status</th>
                <th className="px-4 py-3 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {risks.map((risk) => {
                const project = projects.find((p) => p.id === risk.project_id);
                return (
                  <tr key={risk.id} className="hover:bg-slate-50 transition-colors">
                    <td className="px-4 py-3 font-bold font-mono text-slate-800">
                      {project?.code ?? risk.project_id.substring(0, 8)}
                    </td>
                    <td className="px-4 py-3 text-slate-700 max-w-xs truncate">
                      {project?.name ?? "MPLADS Project Record"}
                    </td>
                    <td className="px-4 py-3">
                      <RiskBadge level={risk.risk_level} score={risk.risk_score} />
                    </td>
                    <td className="px-4 py-3 font-mono text-slate-500">{risk.analysis_type}</td>
                    <td className="px-4 py-3">
                      <VerificationBadge status={risk.verification_status} />
                    </td>
                    <td className="px-4 py-3 text-right">
                      <Link
                        to={`/investigation?project=${risk.project_id}`}
                        className="text-xs font-semibold text-blue-600 hover:text-blue-800 bg-blue-50 px-2.5 py-1 rounded border border-blue-200"
                      >
                        Investigate
                      </Link>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </section>

      {/* Disclaimer below dashboard */}
      <ProvenanceBanner />
    </div>
  );
}
