/**
 * API client for AI Maturity Platform.
 * v1.1 — Priority 1: nested responses, report_type, target_scores, pdn_consent.
 */
import axios from 'axios';
import type { AuditRequest, AuditResponse, BenchmarkResponse } from '@/types';

const client = axios.create({
  baseURL: '/api/v1',
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' },
});

// ============================================================
// Public API (Entry calculator)
// ============================================================

export const publicApi = {
  /**
   * Create express audit (35 questions, nested format).
   * POST /api/v1/public/audits/express
   */
  createAudit: async (data: AuditRequest): Promise<AuditResponse> => {
    const res = await client.post<AuditResponse>('/public/audits/express', data);
    return res.data;
  },

  /**
   * Get audit by ID.
   * GET /api/v1/public/audits/{auditId}
   */
  getAudit: async (auditId: string): Promise<AuditResponse> => {
    const res = await client.get<AuditResponse>(`/public/audits/${auditId}`);
    return res.data;
  },

  /**
   * Send audit report to email.
   * POST /api/v1/public/audits/{auditId}/email
   */
  sendAuditReport: async (auditId: string, email: string): Promise<void> => {
    await client.post(`/public/audits/${auditId}/email`, { email });
  },

  /**
   * Get industry benchmark data.
   * GET /api/v1/public/benchmarks/{industry}
   */
  getBenchmark: async (industry: string): Promise<BenchmarkResponse> => {
    const res = await client.get<BenchmarkResponse>(`/public/benchmarks/${industry}`);
    return res.data;
  },
};

// ============================================================
// Admin API (back-office) — stub for future use
// ============================================================

export const adminApi = {
  /**
   * List all audits with filters.
   * GET /api/v1/admin/audits
   */
  listAudits: async (params?: {
    industry?: string;
    company_size?: string;
    limit?: number;
    offset?: number;
  }): Promise<any> => {
    const res = await client.get('/admin/audits', { params });
    return res.data;
  },

  /**
   * Get audit details.
   * GET /api/v1/admin/audits/{auditId}
   */
  getAuditDetail: async (auditId: string): Promise<any> => {
    const res = await client.get(`/admin/audits/${auditId}`);
    return res.data;
  },

  /**
   * Business dashboard metrics.
   * GET /api/v1/admin/dashboard/business
   */
  getBusinessDashboard: async (): Promise<any> => {
    const res = await client.get('/admin/dashboard/business');
    return res.data;
  },

  /**
   * Scientific dashboard metrics (for dissertation).
   * GET /api/v1/admin/dashboard/scientific
   */
  getScientificDashboard: async (): Promise<any> => {
    const res = await client.get('/admin/dashboard/scientific');
    return res.data;
  },

  /**
   * Download PDF report.
   * GET /api/v1/admin/audits/{auditId}/report/pdf
   */
  downloadPdfReport: async (auditId: string): Promise<Blob> => {
    const res = await client.get(`/admin/audits/${auditId}/report/pdf`, {
      responseType: 'blob',
    });
    return res.data;
  },
};

// ============================================================
// Error handling
// ============================================================

export interface ApiError {
  code: string;
  message: string;
  details?: Record<string, any>;
}

export function extractApiError(error: any): ApiError {
  if (error.response?.data?.error) {
    return error.response.data.error;
  }
  if (error.response?.data?.detail) {
    const detail = error.response.data.detail;
    if (typeof detail === 'string') {
      return { code: 'UNKNOWN', message: detail };
    }
    return detail;
  }
  return {
    code: 'NETWORK_ERROR',
    message: error.message || 'Network error',
  };
}