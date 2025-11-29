import api from './client';
import type { LetterResponse } from '@/types';

export interface LetterInput {
  content: string;
  subject?: string;
}

export const processLetter = async (data: LetterInput): Promise<LetterResponse> => {
  const response = await api.post<LetterResponse>('/api/letters/process', data);
  return response.data;
};
