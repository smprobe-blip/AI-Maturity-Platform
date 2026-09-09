import axios, { AxiosInstance } from 'axios';
import { keycloak } from '@/auth/keycloak';

const API_BASE_URL = import.meta.env.VITE_API_URL || '';

const adminClient: AxiosInstance = axios.create({
  baseURL: `${API_BASE_URL}/api/v1/admin`,
  headers: { 'Content-Type': 'application/json' },
});

// Attach token to every request
adminClient.interceptors.request.use((config) => {
  const token = keycloak.token;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle 401 globally
adminClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      keycloak.login();
    }
    return Promise.reject(error);
  }
);

// ──────────────────────────────────────────────────
// TYPES
// ──────────────────────────────────────────────────

export interface Audit {
  audit_id: string;
  created_at: string;
  status: string;
  source?: string;
  audit_type: string;
  company_profile: {
    industry: string;
    company_size: string;
    region: string;
  };
  contact: {
    email: string;
    name?: string;
    position?: string;
  };
  calculated_indices: {
    composite_score: number;
    maturity_level: string;
    dimension_scores: Record<string, number>;
  };
}

export interface Benchmark {
  industry: string;
  sample_size: number;
  mean_score: number;
  median_score: number;
  std_dev: number;
  percentile_25: number;
  percentile_75: number;
  dimension_breakdown: Record<string, { mean: number; median: number }>;
}

export interface ExportRecord {
  export_id: string;
  created_at: string;
  export_type: string;
  format: string;
  filename: string;
  row_count: number;
  status: string;
  user_id: string;
}

export interface DashboardMetrics {
  total_audits: number;
  audits_this_month: number;
  growth_rate_percent: number;
  average_maturity_score: number;
  industry_distribution?: Record<string, number>;
  maturity_level_distribution?: Record<string, number>;
}

export interface User {
  email: string;
  name: string;
  audits_count: number;
  test_audits: number;
  first_seen: string;
  last_seen: string;
  sources: string[];
}

export interface PlatformSettings {
  platform: { name: string };
  integrations: {
    keycloak: { realm: string; client_id: string; configured: boolean };
    baserow: { url: string; leads_table_id: number; configured: boolean };
    email: {
      provider: 'smtp' | 'postbox';
      configured: boolean;
      host: string;
      port: number;
      use_tls: boolean;
      from_email: string;
      from_name: string;
      auth_enabled: boolean;
      postbox?: {
        endpoint: string;
        region: string;
        configured: boolean;
        from_email: string;
      };
    };
  };
  data: {
    audits_total: number;
    audits_active: number;
    audits_archived: number;
    audits_test_manual: number;
    reports_pdf: number;
  };
}

export interface Methodology {
  version: string;
  weights: Record<string, number>;
  maturity_levels: Record<string, { min: number; max: number; label: string }>;
}

// ──────────────────────────────────────────────────
// ENDPOINTS
// ──────────────────────────────────────────────────

export const adminApi = {
  // AUDITS
  listAudits: async (params?: {
    industry?: string;
    company_size?: string;
    status?: string;
    search?: string;
    limit?: number;
    offset?: number;
  }) => {
    const { data } = await adminClient.get('/audits', { params });
    return data;
  },

  getAudit: async (auditId: string) => {
    const { data } = await adminClient.get(`/audits/${auditId}`);
    return data as Audit;
  },

  archiveAudit: async (auditId: string) => {
    // Архивация с сохранением данных (не удаление): важно для исследовательской базы
    const { data } = await adminClient.post(`/audits/${auditId}/archive`);
    return data;
  },

  deleteAudit: async (auditId: string) => {
    // Безвозвратное удаление (для тестовых аудитов): JSON + связанный лид CRM
    const { data } = await adminClient.delete(`/audits/${auditId}`);
    return data as { status: string; audit_id: string; source?: string; lead_deleted: boolean };
  },

  // BENCHMARKS
  listBenchmarks: async () => {
    const { data } = await adminClient.get('/benchmarks');
    return data.items as Benchmark[];
  },

  getBenchmark: async (industry: string) => {
    const { data } = await adminClient.get(`/benchmarks/${industry}`);
    return data as Benchmark;
  },

  recalculateBenchmarks: async () => {
    const { data } = await adminClient.post('/benchmarks/recalculate');
    return data;
  },

  getPercentile: async (industry: string, score: number) => {
    const { data } = await adminClient.get(
      `/benchmarks/${industry}/percentile?score=${score}`
    );
    return data;
  },

  // EXPORTS
  createExport: async (payload: {
    export_type: string;
    format: string;
    filters?: Record<string, any>;
    columns?: string[];
    nda_signed: boolean;
  }) => {
    const { data } = await adminClient.post('/exports', payload);
    return data as ExportRecord;
  },

  getExportHistory: async (limit = 50) => {
    const { data } = await adminClient.get(`/exports/history?limit=${limit}`);
    return data.items as ExportRecord[];
  },

  downloadExport: async (exportId: string) => {
    const { data } = await adminClient.get(`/exports/${exportId}/download`, {
      responseType: 'blob',
    });
    return data;
  },

  // DASHBOARD
  getBusinessMetrics: async () => {
    const { data } = await adminClient.get('/dashboard/business');
    return data as DashboardMetrics;
  },

  getScientificMetrics: async () => {
    const { data } = await adminClient.get('/dashboard/scientific');
    return data;
  },

  getOperationsMetrics: async () => {
    const { data } = await adminClient.get('/dashboard/operations');
    return data;
  },

  getQualityMetrics: async () => {
    const { data } = await adminClient.get('/dashboard/quality');
    return data;
  },


  // SETTINGS
  getSettings: async () => {
    const { data } = await adminClient.get('/settings');
    return data as PlatformSettings;
  },

  // EMAIL
  getEmailStatus: async () => {
    const { data } = await adminClient.get('/email/status');
    return data as PlatformSettings['integrations']['email'];
  },
  sendTestEmail: async (email: string) => {
    const { data } = await adminClient.post(
      `/email/send-test?to_email=${encodeURIComponent(email)}`
    );
    return data;
  },

  // LEADS
listLeads: async (params?: { limit?: number; offset?: number }) => {
  const { data } = await adminClient.get('/leads', { params });
  return data;
},
updateLeadStatus: async (leadId: number, status: string) => {
  const { data } = await adminClient.patch(`/leads/${leadId}/status`, { status });
  return data;
},

  getReports: async () => {
    const { data } = await adminClient.get('/reports');
    return data;
  },
  downloadReport: async (filename: string) => {
    const { data } = await adminClient.get(`/reports/download/${encodeURIComponent(filename)}`, {
      responseType: 'blob',
    });
    return data as Blob;
  },
  generateDissertationReport: async () => {
    const { data } = await adminClient.post('/reports/generate-dissertation');
    return data;
  },
// USERS
listUsers: async () => {
    const { data } = await adminClient.get('/users');
    return data.items as User[];
  },

  // SETTINGS
  getMethodology: async () => {
    const { data } = await adminClient.get('/settings/methodology');
    return data as Methodology;
  },

  updateMethodology: async (payload: Partial<Methodology>) => {
    const { data } = await adminClient.put('/settings/methodology', payload);
    return data;
  },

  getIntegrations: async () => {
    const { data } = await adminClient.get('/settings/integrations');
    return data;
  },

  updateIntegrations: async (payload: Record<string, any>) => {
    const { data } = await adminClient.put('/settings/integrations', payload);
    return data;
  },

  // AUDIT LOG
  getAuditLog: async (params?: { user_id?: string; action?: string; limit?: number }) => {
    const { data } = await adminClient.get('/audit-log', { params });
    return data.items;
  },
};
