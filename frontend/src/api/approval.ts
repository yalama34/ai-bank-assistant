import api from './client';
import type { Approval } from '@/types';

export const approvalApi = {
  // Направить письмо на согласование
  route: async (letterId: number): Promise<Approval> => {
    const response = await api.post<Approval>(`/approval/route/${letterId}`);
    return response.data;
  },

  // Получить статус согласования
  getStatus: async (approvalId: number): Promise<Approval> => {
    const response = await api.get<Approval>(`/approval/status/${approvalId}`);
    return response.data;
  },
};

