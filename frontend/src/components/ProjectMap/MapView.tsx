import { useState } from "react";
import L from "leaflet";
import { MapContainer, Marker, Popup, TileLayer } from "react-leaflet";
import { Link } from "react-router-dom";
import type { ProjectSummary, RiskLevel } from "../../types/api";
import { RiskBadge, VerificationBadge } from "../RiskAnalysis/Badges";

const RISK_COLORS: Record<RiskLevel | "UNKNOWN", string> = {
  LOW: "#16a34a",
  MEDIUM: "#d97706",
  HIGH: "#dc2626",
  CRITICAL: "#991b1b",
  UNKNOWN: "#64748b",
};

const createCustomIcon = (level: RiskLevel | "UNKNOWN", score?: number) => {
  const color = RISK_COLORS[level];
  const scoreText = score !== undefined ? score : "?";
  
  return L.divIcon({
    className: "custom-leaflet-pin",
    html: `
      <div style="
        background-color: ${color};
        width: 32px;
        height: 32px;
        border-radius: 50%;
        border: 2px solid white;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: 700;
        font-size: 11px;
        font-family: sans-serif;
      ">
        ${scoreText}
      </div>
    `,
    iconSize: [32, 32],
    iconAnchor: [16, 16],
    popupAnchor: [0, -16],
  });
};

const DEFAULT_CENTER: [number, number] = [21.15, 79.08];

export function MapView({ projects, height = 480 }: { projects: ProjectSummary[]; height?: number }) {
  const [selectedRiskFilter, setSelectedRiskFilter] = useState<string>("ALL");

  const points = projects.filter((project) => project.location);

  const filteredPoints = points.filter((project) => {
    if (selectedRiskFilter === "ALL") return true;
    return project.latest_risk?.risk_level === selectedRiskFilter;
  });

  const center: [number, number] = points[0]
    ? [points[0].location!.latitude, points[0].location!.longitude]
    : DEFAULT_CENTER;

  return (
    <div className="space-y-3">
      {/* Map Header & Filter Controls */}
      <div className="flex flex-wrap items-center justify-between gap-3 bg-white p-3 rounded-lg border border-slate-200 shadow-sm">
        <div className="flex items-center space-x-2">
          <span className="text-xs font-semibold uppercase text-slate-500 tracking-wider">Filter by Risk:</span>
          {["ALL", "LOW", "MEDIUM", "HIGH", "CRITICAL"].map((level) => (
            <button
              key={level}
              onClick={() => setSelectedRiskFilter(level)}
              className={`px-2.5 py-1 rounded text-xs font-medium transition-all ${
                selectedRiskFilter === level
                  ? "bg-slate-900 text-white shadow-xs"
                  : "bg-slate-100 text-slate-600 hover:bg-slate-200"
              }`}
            >
              {level}
            </button>
          ))}
        </div>

        {/* Legend */}
        <div className="flex items-center space-x-4 text-xs font-medium text-slate-600">
          {(["LOW", "MEDIUM", "HIGH", "CRITICAL"] as RiskLevel[]).map((level) => (
            <div key={level} className="flex items-center space-x-1.5">
              <span
                className="w-3 h-3 rounded-full border border-white shadow-xs"
                style={{ backgroundColor: RISK_COLORS[level] }}
              />
              <span>{level}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Leaflet Map */}
      <div className="overflow-hidden rounded-xl border border-slate-200 shadow-sm relative" style={{ height }}>
        <MapContainer center={center} zoom={8} scrollWheelZoom={false} style={{ height: "100%" }}>
          <TileLayer
            attribution='&copy; OpenStreetMap contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          {filteredPoints.map((project) => {
            const riskLevel = project.latest_risk?.risk_level || "UNKNOWN";
            const score = project.latest_risk?.risk_score;
            const icon = createCustomIcon(riskLevel, score);

            return (
              <Marker
                key={project.id}
                position={[project.location!.latitude, project.location!.longitude]}
                icon={icon}
              >
                <Popup>
                  <div className="space-y-2 p-1 min-w-[200px]">
                    <div>
                      <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">
                        {project.code}
                      </span>
                      <h4 className="font-semibold text-sm text-slate-900 leading-snug">{project.name}</h4>
                    </div>

                    <div className="flex items-center justify-between pt-1 border-t border-slate-100">
                      <span className="text-xs text-slate-500">Risk Score:</span>
                      {project.latest_risk ? (
                        <RiskBadge level={project.latest_risk.risk_level} score={project.latest_risk.risk_score} />
                      ) : (
                        <span className="text-xs text-slate-400">Unassessed</span>
                      )}
                    </div>

                    {project.latest_risk && (
                      <div className="flex items-center justify-between">
                        <span className="text-xs text-slate-500">Status:</span>
                        <VerificationBadge status={project.latest_risk.verification_status} />
                      </div>
                    )}

                    <div className="pt-2">
                      <Link
                        to={`/investigation?project=${project.id}`}
                        className="block text-center bg-blue-600 hover:bg-blue-700 text-white font-medium text-xs py-1.5 px-3 rounded transition-colors"
                      >
                        Investigate Project →
                      </Link>
                    </div>
                  </div>
                </Popup>
              </Marker>
            );
          })}
        </MapContainer>
      </div>
    </div>
  );
}
