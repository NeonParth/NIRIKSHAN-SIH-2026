export type DataSource = "REAL" | "PUBLIC" | "SYNTHETIC";
export type AnalysisType = "RAW_DATA" | "RULE_BASED" | "MODEL_PREDICTION";
export type VerificationStatus = "UNVERIFIED" | "UNDER_REVIEW" | "HUMAN_VERIFIED" | "HUMAN_REJECTED";
export type RiskLevel = "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
export type CompletionStatus = "PROPOSED" | "SANCTIONED" | "IN_PROGRESS" | "COMPLETED" | "DELAYED";

export interface GeoPoint {
  longitude: number;
  latitude: number;
}

export interface LatestRiskSummary {
  id: string;
  risk_score: number;
  risk_level: RiskLevel;
  verification_status: VerificationStatus;
  analysis_type: AnalysisType;
  created_at: string;
}

export interface ProjectSummary {
  id: string;
  code: string;
  name: string;
  description?: string | null;
  location?: GeoPoint | null;
  allocated_amount?: number | null;
  benchmark_amount?: number | null;
  sanctioned_date?: string | null;
  completion_status: CompletionStatus;
  data_source: DataSource;
  created_at: string;
  updated_at: string;
  latest_risk?: LatestRiskSummary | null;
}

export interface EvidenceRead {
  id: string;
  project_id: string;
  evidence_type: string;
  storage_uri: string;
  captured_at?: string | null;
  extra_metadata?: Record<string, unknown> | null;
  data_source: DataSource;
  verification_status: VerificationStatus;
  created_at: string;
  updated_at: string;
}

export interface RiskSignalRead {
  id: string;
  signal_code: string;
  signal_name: string;
  contribution: number;
  observed_value?: string | null;
  threshold?: string | null;
  explanation: string;
  source_reference?: string | null;
  source_module: string;
}

export interface RiskEvidenceRead {
  evidence_id: string;
  relevance: string;
  explanation: string;
  evidence?: EvidenceRead | null;
}

export interface RiskAssessmentRead {
  id: string;
  project_id: string;
  risk_score: number;
  risk_level: RiskLevel;
  reason_text: string;
  source_module: string;
  analysis_type: AnalysisType;
  data_source: DataSource;
  verification_status: VerificationStatus;
  reviewer_remarks?: string | null;
  reviewed_by?: string | null;
  reviewed_at?: string | null;
  created_at: string;
  updated_at: string;
  contributing_signals: RiskSignalRead[];
  evidence_references: RiskEvidenceRead[];
}

export interface ProjectDetail extends ProjectSummary {
  evidence: EvidenceRead[];
  latest_assessment?: RiskAssessmentRead | null;
}

export interface Paginated<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
}

export interface ContractorRead {
  id: string;
  name: string;
  registration_no?: string | null;
  location_text?: string | null;
  data_source: DataSource;
  award_count: number;
  created_at: string;
  updated_at: string;
}

export interface TenderRead {
  id: string;
  project_id: string;
  official_tender_id: string;
  bidder_count?: number | null;
  winning_amount?: number | null;
  data_source: DataSource;
  created_at: string;
  updated_at: string;
}
