import api from './client';
import type { Draft } from '@/types';

export const generationApi = {
  // Генерировать ответ на письмо
  generate: async (letterId: number): Promise<Draft> => {
    const response = await api.post<Draft>(`/generation/generate/${letterId}`);
    return response.data;
  },
};

