import { useState, useCallback } from 'react';
import apiClient from '@/lib/api';

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
  apiMethod: (...args: any[]) => Promise<any>,
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
  return useApi(apiClient.healthCheck);
}

export function useSources(page = 1, perPage = 10) {
  return useApi(() => apiClient.getSources({ page, perPage }));
}

export function useSource(id: number) {
  return useApi(() => apiClient.getSources({ id }));
}

export function useContent(page = 1, perPage = 10, sourceId?: number, riskLevel?: string) {
  return useApi(() => apiClient.getContent({ page, perPage, sourceId, riskLevel }));
}

export function useContentById(id: number) {
  return useApi(() => apiClient.getContent({ id }));
}

export function useOSINTInfo() {
  return useApi(apiClient.getOSINTInfo);
}

export function useOSINTResults(page = 1, perPage = 10) {
  return useApi(() => apiClient.getOSINTInfo());
}

export function useOSINTResult(id: number) {
  return useApi(() => apiClient.getOSINTInfo());
}

export function useDashboardInfo() {
  return useApi(apiClient.getDashboardInfo);
}

export function useDashboardStats(days = 30) {
  return useApi(() => apiClient.getDashboardInfo());
}

export function useRecentContent(limit = 10) {
  return useApi(() => apiClient.getDashboardInfo());
}

export function useHighRiskContent(limit = 10) {
  return useApi(() => apiClient.getDashboardInfo());
}

export function useTrends(days = 30) {
  return useApi(() => apiClient.getDashboardInfo());
}

export function useAlerts() {
  return useApi(() => apiClient.getDashboardInfo());
} 