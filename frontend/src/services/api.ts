import type {
  ContractorRead,
  Paginated,
  ProjectDetail,
  ProjectSummary,
  RiskAssessmentRead,
  TenderRead,
  VerificationStatus,
} from "../types/api";

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
  });
  if (!response.ok) {
    throw new Error(`Request failed (${response.status})`);
  }
  return response.json() as Promise<T>;
}

export const api = {
  health: () => request<{ status: string; database: string }>("/health"),
  projects: (params?: URLSearchParams) =>
    request<Paginated<ProjectSummary>>(`/api/v1/projects${params ? `?${params}` : ""}`),
  project: (id: string) => request<ProjectDetail>(`/api/v1/projects/${id}`),
  projectRisks: (id: string) => request<RiskAssessmentRead[]>(`/api/v1/projects/${id}/risks`),
  projectEvidence: (id: string) => request<unknown[]>(`/api/v1/projects/${id}/evidence`),
  risks: (params?: URLSearchParams) =>
    request<Paginated<RiskAssessmentRead>>(`/api/v1/risks${params ? `?${params}` : ""}`),
  assess: (id: string) =>
    request<RiskAssessmentRead>(`/api/v1/risks/assess/${id}`, { method: "POST" }),
  review: (id: string, verification_status: VerificationStatus, remarks?: string) =>
    request<RiskAssessmentRead>(`/api/v1/risks/${id}/review`, {
      method: "POST",
      body: JSON.stringify({ verification_status, remarks, reviewed_by: "phase1-reviewer" }),
    }),
  contractors: () => request<Paginated<ContractorRead>>("/api/v1/contractors"),
  tenders: () => request<Paginated<TenderRead>>("/api/v1/tenders"),
};
