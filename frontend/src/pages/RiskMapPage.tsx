import { useEffect, useState } from "react";
import { ProvenanceBanner } from "../components/Dashboard/ProvenanceBanner";
import { MapView } from "../components/ProjectMap/MapView";
import { api } from "../services/api";
import type { ProjectSummary } from "../types/api";

export function RiskMapPage() {
  const [projects, setProjects] = useState<ProjectSummary[]>([]);

  useEffect(() => {
    api.projects(new URLSearchParams({ page_size: "100" })).then((page) => setProjects(page.items));
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-900 tracking-tight">Geospatial Risk Map</h2>
        <p className="text-sm text-slate-600">
          Geographic spatial distribution of project sites and assessed risk levels.
        </p>
      </div>

      <MapView projects={projects} height={580} />

      {/* Disclaimer placed below map area */}
      <ProvenanceBanner />
    </div>
  );
}
