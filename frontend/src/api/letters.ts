import api from './client';
import type { Letter, LetterCreate, LetterResponse } from '@/types';

export const lettersApi = {
  // Создать письмо
  create: async (data: LetterCreate): Promise<LetterResponse> => {
    const response = await api.post<LetterResponse>('/letters/', data);
    return response.data;
  },

  // Получить письмо по ID
  getById: async (id: number): Promise<LetterResponse> => {
    const response = await api.get<LetterResponse>(`/letters/${id}`);
    return response.data;
  },

  // Получить все письма
  getAll: async (): Promise<LetterResponse[]> => {
    const response = await api.get<LetterResponse[]>('/letters/');
    return response.data;
  },
};

