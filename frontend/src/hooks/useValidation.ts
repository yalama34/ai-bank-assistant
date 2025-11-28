import { useMutation, useQueryClient } from 'react-query';
import { validationApi } from '@/api/validation';

export const useValidateDraft = () => {
  const queryClient = useQueryClient();

  return useMutation(
    (draftId: number) => validationApi.validate(draftId),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('letters');
        queryClient.invalidateQueries('letter');
      },
    }
  );
};