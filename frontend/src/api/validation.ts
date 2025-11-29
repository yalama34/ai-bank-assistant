import api from './client';
import type { ValidationResult } from '@/types';

export const validationApi = {
  // Валидировать черновик
  validate: async (draftId: number): Promise<ValidationResult> => {
    const response = await api.post<ValidationResult>(`/validation/validate/${draftId}`);
    return response.data;
  },
};

