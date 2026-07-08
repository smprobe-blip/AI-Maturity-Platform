export interface CompanyProfile {
  industry: string;
  company_size: string;
  region: string;
  ai_experience_years?: number;
  annual_it_budget_millions?: number;
}

export interface ContactInfo {
  email: string;
  name?: string;
  position?: string;
  phone?: string;
  consent_to_process_data: boolean;
}

export interface RawResponse {
  dimension_id: number;
  question_id: number;
  score: number;
  time_to_answer_sec?: number;
  confidence_level?: number;
}

export interface CalculatedIndices {
  dimension_scores: Record<string, number>;
  composite_score: number;
  maturity_level: string;
  roi_estimate_percent?: number;
  tco_estimate_millions?: number;
}

export interface AuditExpressCreate {
  company_profile: CompanyProfile;
  contact: ContactInfo;
  raw_responses: RawResponse[];
}

export interface AuditExpressResponse {
  audit_id: string;
  created_at: string;
  calculated_indices: CalculatedIndices;
  report_url?: string;
  message: string;
}

export interface Dimension {
  id: number;
  name: string;
  description: string;
  questions: Question[];
}

export interface Question {
  id: number;
  text: string;
  description?: string;
}

export interface RadarChartData {
  dimension: string;
  score: number;
  max_score: number;
}