import axios from 'axios';
import { keycloak } from '@/auth/keycloak';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const analyticsClient = axios.create({
  baseURL: `${API_BASE_URL}/api/v1/analytics`,
  headers: { 'Content-Type': 'application/json' },
});

analyticsClient.interceptors.request.use((config) => {
  const token = keycloak.token;
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

export const analyticsApi = {
  // Descriptive
  getSampleCharacteristics: async () => {
    const { data } = await analyticsClient.get('/descriptive/sample');
    return data;
  },

  getCentralTendency: async () => {
    const { data } = await analyticsClient.get('/descriptive/central-tendency');
    return data;
  },

  getCorrelationAnalysis: async () => {
    const { data } = await analyticsClient.get('/descriptive/correlation');
    return data;
  },

  // Reliability
  getFullReliability: async () => {
    const { data } = await analyticsClient.get('/reliability/full');
    return data;
  },

  getDimensionReliability: async (dimensionId: number) => {
    const { data } = await analyticsClient.get(`/reliability/dimension/${dimensionId}`);
    return data;
  },

  // Factor Analysis
  runEFA: async (nFactors = 7) => {
    const { data } = await analyticsClient.get(`/factor-analysis/efa?n_factors=${nFactors}`);
    return data;
  },

  runPCA: async (nComponents = 7) => {
    const { data } = await analyticsClient.get(`/factor-analysis/pca?n_components=${nComponents}`);
    return data;
  },

  determineOptimalFactors: async () => {
    const { data } = await analyticsClient.get('/factor-analysis/optimal-factors');
    return data;
  },

  // Regression
  maturityToROI: async () => {
    const { data } = await analyticsClient.get('/regression/maturity-to-roi');
    return data;
  },

  dimensionContribution: async () => {
    const { data } = await analyticsClient.get('/regression/dimension-contribution');
    return data;
  },

  // Cluster
  kmeansClustering: async (nClusters = 4) => {
    const { data } = await analyticsClient.get(`/cluster/kmeans?n_clusters=${nClusters}`);
    return data;
  },

  industryComparison: async () => {
    const { data } = await analyticsClient.get('/cluster/industry-comparison');
    return data;
  },

  // Full analysis
  runFullAnalysis: async () => {
    const { data } = await analyticsClient.post('/full-analysis');
    return data;
  },

  generateReport: async () => {
    const { data } = await analyticsClient.post('/generate-report');
    return data;
  },

  exportForDissertation: async (format = 'all') => {
    const { data } = await analyticsClient.post(`/export?format=${format}`);
    return data;
  },
};