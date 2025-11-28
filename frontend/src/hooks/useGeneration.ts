import { useMutation, useQueryClient } from 'react-query';
import { generationApi } from '@/api/generation';

export const useGenerateResponse = () => {
  const queryClient = useQueryClient();

  return useMutation(
    (letterId: number) => generationApi.generate(letterId),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('letters');
        queryClient.invalidateQueries('letter');
      },
    }
  );
};
