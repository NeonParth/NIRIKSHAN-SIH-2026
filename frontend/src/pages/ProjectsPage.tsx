import { FormEvent, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { RiskBadge, SourceBadge } from "../components/RiskAnalysis/Badges";
import { api } from "../services/api";
import type { ProjectSummary } from "../types/api";

export function ProjectsPage() {
  const [items, setItems] = useState<ProjectSummary[]>([]);
  const [q, setQ] = useState("");
  const [riskLevel, setRiskLevel] = useState("");
  const [dataSource, setDataSource] = useState("");
  const [status, setStatus] = useState("");
  const [error, setError] = useState<string | null>(null);

  function load(event?: FormEvent) {
    event?.preventDefault();
    const params = new URLSearchParams({ page_size: "50" });
    if (q) params.set("q", q);
    if (riskLevel) params.set("risk_level", riskLevel);
    if (dataSource) params.set("data_source", dataSource);
    if (status) params.set("completion_status", status);
    api
      .projects(params)
      .then((page) => setItems(page.items))
      .catch(() => setError("Unable to load projects."));
  }

  useEffect(() => {
    load();
  }, []);

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-semibold text-navy-900">Projects</h2>
      <form onSubmit={load} className="grid gap-3 rounded border border-slate-200 bg-white p-4 md:grid-cols-5">
        <input
          className="rounded border border-slate-300 px-3 py-2 text-sm"
          placeholder="Search name or code"
          value={q}
          onChange={(event) => setQ(event.target.value)}
          aria-label="Search projects"
        />
        <select className="rounded border border-slate-300 px-3 py-2 text-sm" value={riskLevel} onChange={(e) => setRiskLevel(e.target.value)} aria-label="Risk level">
          <option value="">All risk levels</option>
          <option>LOW</option>
          <option>MEDIUM</option>
          <option>HIGH</option>
          <option>CRITICAL</option>
        </select>
        <select className="rounded border border-slate-300 px-3 py-2 text-sm" value={dataSource} onChange={(e) => setDataSource(e.target.value)} aria-label="Data source">
          <option value="">All sources</option>
          <option>SYNTHETIC</option>
          <option>PUBLIC</option>
          <option>REAL</option>
        </select>
        <select className="rounded border border-slate-300 px-3 py-2 text-sm" value={status} onChange={(e) => setStatus(e.target.value)} aria-label="Completion status">
          <option value="">All statuses</option>
          <option>PROPOSED</option>
          <option>SANCTIONED</option>
          <option>IN_PROGRESS</option>
          <option>COMPLETED</option>
          <option>DELAYED</option>
        </select>
        <button type="submit" className="rounded bg-navy-800 px-3 py-2 text-sm font-medium text-white">
          Apply filters
        </button>
      </form>
      {error ? <p className="text-sm text-red-800">{error}</p> : null}
      <div className="overflow-x-auto rounded border border-slate-200 bg-white">
        <table className="min-w-full text-left text-sm">
          <thead className="bg-slate-50 text-xs uppercase text-slate-500">
            <tr>
              <th className="px-3 py-2">Code</th>
              <th className="px-3 py-2">Name</th>
              <th className="px-3 py-2">Status</th>
              <th className="px-3 py-2">Source</th>
              <th className="px-3 py-2">Risk</th>
            </tr>
          </thead>
          <tbody>
            {items.map((project) => (
              <tr key={project.id} className="border-t border-slate-100">
                <td className="px-3 py-2 font-medium">
                  <Link className="text-navy-700 underline" to={`/projects/${project.id}`}>
                    {project.code}
                  </Link>
                </td>
                <td className="px-3 py-2">{project.name}</td>
                <td className="px-3 py-2">{project.completion_status}</td>
                <td className="px-3 py-2">
                  <SourceBadge source={project.data_source} />
                </td>
                <td className="px-3 py-2">
                  {project.latest_risk ? (
                    <RiskBadge level={project.latest_risk.risk_level} score={project.latest_risk.risk_score} />
                  ) : (
                    "—"
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
