import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useLetters } from '@/hooks/useLetters';
import { format } from 'date-fns';
import { ru } from 'date-fns/locale';
import Loading from '@/components/Loading';
import Error from '@/components/Error';
import StatusBadge from '@/components/StatusBadge';
import type { Letter } from '@/types';

export default function Dashboard() {
  const navigate = useNavigate();
  const { data: letters, isLoading, error, refetch } = useLetters();
  const [filter, setFilter] = useState<string>('all');

  const filteredLetters = letters?.filter((letter) => {
    if (filter === 'all') return true;
    return letter.request_category === filter;
  }) || [];

  const categories = Array.from(new Set(letters?.map((l) => l.request_category).filter(Boolean) || []));

  const getLatestDraftStatus = (letter: Letter) => {
    // В реальном приложении нужно получать drafts из API
    return 'draft';
  };

  if (isLoading) return <Loading />;
  if (error) return <Error message="Не удалось загрузить письма" onRetry={() => refetch()} />;

  return (
    <div className="px-4 py-6 sm:px-0">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Входящие письма</h2>

        <div className="flex items-center space-x-4 mb-4">
          <label className="text-sm font-medium text-gray-700">Фильтр:</label>
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
          >
            <option value="all">Все</option>
            {categories.map((cat) => (
              <option key={cat} value={cat}>
                {cat}
              </option>
            ))}
          </select>
          <div className="text-sm text-gray-600">
            Всего: {filteredLetters.length}
          </div>
        </div>
      </div>

      <div className="bg-white shadow overflow-hidden sm:rounded-md">
        <ul className="divide-y divide-gray-200">
          {filteredLetters.length === 0 ? (
            <li className="px-6 py-8 text-center text-gray-500">
              Писем не найдено
            </li>
          ) : (
            filteredLetters.map((letter) => (
              <li
                key={letter.id}
                className="px-6 py-4 hover:bg-gray-50 cursor-pointer transition-colors"
                onClick={() => navigate(`/letters/${letter.id}`)}
              >
                <div className="flex items-center justify-between">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center space-x-3">
                      <p className="text-sm font-medium text-gray-900 truncate">
                        {letter.subject}
                      </p>
                      <StatusBadge status={getLatestDraftStatus(letter)} />
                    </div>
                    <div className="mt-2 flex items-center text-sm text-gray-500">
                      <span className="mr-4">От: {letter.sender}</span>
                      <span className="mr-4">{letter.sender_email}</span>
                      <span>
                        {format(new Date(letter.received_at), 'dd MMM yyyy, HH:mm', { locale: ru })}
                      </span>
                    </div>
                    {letter.request_category && (
                      <div className="mt-1">
                        <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800">
                          {letter.request_category}
                        </span>
                      </div>
                    )}
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

