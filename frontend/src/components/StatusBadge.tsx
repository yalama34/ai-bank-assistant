import { clsx } from 'clsx';
import type { DraftStatus } from '@/types';

interface StatusBadgeProps {
  status: DraftStatus | string;
}

export default function StatusBadge({ status }: StatusBadgeProps) {
  const statusConfig: Record<string, { label: string; className: string }> = {
    draft: { label: 'Черновик', className: 'bg-gray-100 text-gray-800' },
    validated: { label: 'Проверен', className: 'bg-blue-100 text-blue-800' },
    approved: { label: 'Одобрен', className: 'bg-green-100 text-green-800' },
    sent: { label: 'Отправлен', className: 'bg-emerald-100 text-emerald-800' },
    rejected: { label: 'Отклонен', className: 'bg-red-100 text-red-800' },
    pending: { label: 'На согласовании', className: 'bg-yellow-100 text-yellow-800' },
    auto_sent: { label: 'Автоотправка', className: 'bg-purple-100 text-purple-800' },
  };

  const config = statusConfig[status] || { label: status, className: 'bg-gray-100 text-gray-800' };

  return (
    <span
      className={clsx(
        'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium',
        config.className
      )}
    >
      {config.label}
    </span>
  );
}

