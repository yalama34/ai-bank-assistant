import { useQuery, useMutation, useQueryClient } from 'react-query';
import { approvalApi } from '@/api/approval';

export const useApprovalStatus = (approvalId: number | null) => {
  return useQuery(
    ['approval', approvalId],
    () => approvalApi.getStatus(approvalId!),
    {
      enabled: !!approvalId,
      refetchInterval: 10000, // Обновление каждые 10 секунд
    }
  );
};

export const useRouteLetter = () => {
  const queryClient = useQueryClient();

  return useMutation(
    (letterId: number) => approvalApi.route(letterId),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('letters');
        queryClient.invalidateQueries('letter');
      },
    }
  );
};
