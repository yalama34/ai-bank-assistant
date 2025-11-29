import { useQuery } from 'react-query';
import { analyticsApi } from '@/api/analytics';
import type { Metrics, SLAMonitoring } from '@/types';

export const useMetrics = () => {
  return useQuery<Metrics>('metrics', analyticsApi.getMetrics, {
    refetchInterval: 60000, // Обновление каждую минуту
  });
};

export const useSLA = () => {
  return useQuery<SLAMonitoring>('sla', analyticsApi.getSLA, {
    refetchInterval: 60000, // Обновление каждую минуту
  });
};