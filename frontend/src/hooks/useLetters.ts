import { useQuery, useMutation, useQueryClient } from 'react-query';
import { lettersApi } from '@/api/letters';
import type { LetterCreate, LetterResponse } from '@/types';

export const useLetters = () => {
  return useQuery('letters', lettersApi.getAll, {
    refetchInterval: 30000, // Обновление каждые 30 секунд
  });
};

export const useLetter = (id: number | null) => {
  return useQuery(
    ['letter', id],
    () => lettersApi.getById(id!),
    {
      enabled: !!id,
    }
  );
};

export const useCreateLetter = () => {
  const queryClient = useQueryClient();

  return useMutation(
    (data: LetterCreate) => lettersApi.create(data),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('letters');
      },
    }
  );
};
