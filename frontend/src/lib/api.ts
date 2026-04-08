/**
 * API client for Data Analytics Dashboard
 */

import axios, { AxiosError } from 'axios';
import type {
  SummaryStats,
  RevenueTrendResponse,
  TopProductsResponse,
  SalesByCategoryResponse,
  RegionalPerformanceResponse,
  DateRangeFilter,
} from '@/types';

const API_BASE_URL = import.meta.env.VITE_API_URL || '';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.response.use(
  (response) => response,
  (error: AxiosError<{ detail?: string }>) => {
    const message = error.response?.data?.detail ?? error.message ?? 'Request failed';
    return Promise.reject(new Error(message));
  },
);

// Analytics API
export const analyticsApi = {
  async getSummary(filters?: DateRangeFilter): Promise<SummaryStats> {
    const { data } = await api.get('/api/v1/analytics/summary', { params: filters });
    return data;
  },

  async getRevenueTrend(filters?: DateRangeFilter): Promise<RevenueTrendResponse> {
    const { data } = await api.get('/api/v1/analytics/revenue-trend', { params: filters });
    return data;
  },

  async getTopProducts(limit: number = 10, filters?: DateRangeFilter): Promise<TopProductsResponse> {
    const { data } = await api.get('/api/v1/analytics/top-products', {
      params: { limit, ...filters },
    });
    return data;
  },

  async getSalesByCategory(filters?: DateRangeFilter): Promise<SalesByCategoryResponse> {
    const { data } = await api.get('/api/v1/analytics/sales-by-category', { params: filters });
    return data;
  },

  async getRegionalPerformance(filters?: DateRangeFilter): Promise<RegionalPerformanceResponse> {
    const { data } = await api.get('/api/v1/analytics/regional-performance', { params: filters });
    return data;
  },
};

// Export API
export const exportApi = {
  async exportCSV(filters?: DateRangeFilter): Promise<Blob> {
    const { data } = await api.get('/api/v1/exports/csv', {
      params: filters,
      responseType: 'blob',
    });
    return data;
  },
};

// Health Check API
export const healthApi = {
  async check(): Promise<{ status: string; database: string; cache: string; timestamp: string }> {
    const { data } = await api.get('/health/db');
    return data;
  },
};

export default api;
