import { useState, useCallback } from 'react';
import { apiService, ApiResponse } from '@/lib/api';

interface UseApiState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
}

interface UseApiReturn<T> extends UseApiState<T> {
  execute: (...args: any[]) => Promise<void>;
  reset: () => void;
}

export function useApi<T = any>(
  apiMethod: (...args: any[]) => Promise<ApiResponse<T>>,
  immediate = false
): UseApiReturn<T> {
  const [state, setState] = useState<UseApiState<T>>({
    data: null,
    loading: false,
    error: null,
  });

  const execute = useCallback(
    async (...args: any[]) => {
      setState(prev => ({ ...prev, loading: true, error: null }));
      
      try {
        const response = await apiMethod(...args);
        setState({
          data: response.data,
          loading: false,
          error: null,
        });
      } catch (error) {
        setState({
          data: null,
          loading: false,
          error: error instanceof Error ? error.message : 'An error occurred',
        });
      }
    },
    [apiMethod]
  );

  const reset = useCallback(() => {
    setState({
      data: null,
      loading: false,
      error: null,
    });
  }, []);

  return {
    ...state,
    execute,
    reset,
  };
}

// Specific hooks for different API endpoints
export function useHealthCheck() {
  return useApi(apiService.healthCheck);
}

export function useSources(page = 1, perPage = 10) {
  return useApi(() => apiService.getSources(page, perPage));
}

export function useSource(id: number) {
  return useApi(() => apiService.getSource(id));
}

export function useContent(page = 1, perPage = 10, sourceId?: number, riskLevel?: string) {
  return useApi(() => apiService.getContent(page, perPage, sourceId, riskLevel));
}

export function useContentById(id: number) {
  return useApi(() => apiService.getContentById(id));
}

export function useOSINTInfo() {
  return useApi(apiService.getOSINTInfo);
}

export function useOSINTResults(page = 1, perPage = 10) {
  return useApi(() => apiService.getOSINTResults(page, perPage));
}

export function useOSINTResult(id: number) {
  return useApi(() => apiService.getOSINTResult(id));
}

export function useDashboardInfo() {
  return useApi(apiService.getDashboardInfo);
}

export function useDashboardStats(days = 30) {
  return useApi(() => apiService.getDashboardStats(days));
}

export function useRecentContent(limit = 10) {
  return useApi(() => apiService.getRecentContent(limit));
}

export function useHighRiskContent(limit = 10) {
  return useApi(() => apiService.getHighRiskContent(limit));
}

export function useTrends(days = 30) {
  return useApi(() => apiService.getTrends(days));
}

export function useAlerts() {
  return useApi(apiService.getAlerts);
} 