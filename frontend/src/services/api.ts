import axios from 'axios';
import type { AuditExpressCreate, AuditExpressResponse } from '@/types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: `${API_BASE_URL}/api/v1/public`,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const publicApi = {
  createExpressAudit: async (data: AuditExpressCreate): Promise<AuditExpressResponse> => {
    const response = await apiClient.post<AuditExpressResponse>('/audits/express', data);
    return response.data;
  },

  getAudit: async (auditId: string): Promise<any> => {
    const response = await apiClient.get(`/audits/${auditId}`);
    return response.data;
  },

  sendAuditReport: async (auditId: string, email: string): Promise<{ message: string }> => {
    const response = await apiClient.post(`/audits/${auditId}/email`, { email });
    return response.data;
  },

  getIndustryBenchmark: async (industry: string): Promise<any> => {
    const response = await apiClient.get(`/benchmarks/${industry}`);
    return response.data;
  },
};