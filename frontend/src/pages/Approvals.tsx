import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useLetters } from '@/hooks/useLetters';
import { format } from 'date-fns';
import { ru } from 'date-fns/locale';
import Loading from '@/components/Loading';
import Error from '@/components/Error';
import StatusBadge from '@/components/StatusBadge';

export default function Approvals() {
  const navigate = useNavigate();
  const { data: letters, isLoading, error, refetch } = useLetters();
  const [filter, setFilter] = useState<'all' | 'pending' | 'approved' | 'rejected'>('all');

  // Фильтруем письма с согласованиями
  const approvals = letters?.flatMap((letter) =>
    (letter.approvals || []).map((approval) => ({
      ...approval,
      letter,
    }))
  ) || [];

  const filteredApprovals = approvals.filter((approval) => {
    if (filter === 'all') return true;
    return approval.approval_status === filter;
  });

  if (isLoading) return <Loading />;
  if (error) return <Error message="Не удалось загрузить согласования" onRetry={() => refetch()} />;

  return (
    <div className="px-4 py-6 sm:px-0">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Согласования</h2>

        <div className="flex items-center space-x-4 mb-4">
          <label className="text-sm font-medium text-gray-700">Статус:</label>
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value as typeof filter)}
            className="rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
          >
            <option value="all">Все</option>
            <option value="pending">На согласовании</option>
            <option value="approved">Одобрено</option>
            <option value="rejected">Отклонено</option>
          </select>
          <div className="text-sm text-gray-600">
            Всего: {filteredApprovals.length}
          </div>
        </div>
      </div>

      <div className="bg-white shadow overflow-hidden sm:rounded-md">
        <ul className="divide-y divide-gray-200">
          {filteredApprovals.length === 0 ? (
            <li className="px-6 py-8 text-center text-gray-500">
              Согласований не найдено
            </li>
          ) : (
            filteredApprovals.map((approval) => (
              <li
                key={approval.id}
                className="px-6 py-4 hover:bg-gray-50 cursor-pointer transition-colors"
                onClick={() => navigate(`/letters/${approval.letter_id}`)}
              >
                <div className="flex items-center justify-between">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center space-x-3 mb-2">
                      <p className="text-sm font-medium text-gray-900">
                        {approval.letter.subject}
                      </p>
                      <StatusBadge status={approval.approval_status || 'pending'} />
                    </div>
                    <div className="text-sm text-gray-600 space-y-1">
                      {approval.current_approver && (
                        <div>Текущий согласующий: {approval.current_approver}</div>
                      )}
                      {approval.department && (
                        <div>Отдел: {approval.department}</div>
                      )}
                      {approval.risk_level && (
                        <div>Уровень риска: {approval.risk_level}</div>
                      )}
                      <div>
                        Создано: {format(new Date(approval.created_at), 'dd MMM yyyy, HH:mm', { locale: ru })}
                      </div>
                      {approval.route && (
                        <div className="mt-2">
                          <span className="text-xs font-medium text-gray-500">Маршрут:</span>
                          <div className="flex flex-wrap gap-1 mt-1">
                            {Array.isArray(approval.route) ? (
                              approval.route.map((step, idx) => (
                                <span
                                  key={idx}
                                  className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-800"
                                >
                                  {step}
                                </span>
                              ))
                            ) : (
                              <span className="text-xs text-gray-600">
                                {JSON.stringify(approval.route)}
                              </span>
                            )}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                  <div className="ml-4 flex-shrink-0">
                    <svg
                      className="h-5 w-5 text-gray-400"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M9 5l7 7-7 7"
                      />
                    </svg>
                  </div>
                </div>
              </li>
            ))
          )}
        </ul>
      </div>
    </div>
  );
}

