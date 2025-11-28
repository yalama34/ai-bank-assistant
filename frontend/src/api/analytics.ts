import api from './client';
import type { Metrics, SLAMonitoring } from '@/types';

export const analyticsApi = {
  // Получить метрики
  getMetrics: async (): Promise<Metrics> => {
    const response = await api.get<Metrics>('/analytics/metrics');
    return response.data;
  },

  // Получить SLA мониторинг
  getSLA: async (): Promise<SLAMonitoring> => {
    const response = await api.get<SLAMonitoring>('/analytics/sla');
    return response.data;
  },
};

