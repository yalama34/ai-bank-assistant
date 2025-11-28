import { useParams, useNavigate } from 'react-router-dom';
import { useLetter } from '@/hooks/useLetters';
import { useGenerateResponse } from '@/hooks/useGeneration';
import { useValidateDraft } from '@/hooks/useValidation';
import { useRouteLetter } from '@/hooks/useApproval';
import { format } from 'date-fns';
import { ru } from 'date-fns/locale';
import Loading from '@/components/Loading';
import Error from '@/components/Error';
import StatusBadge from '@/components/StatusBadge';
import { useState } from 'react';

export default function LetterDetails() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const letterId = id ? parseInt(id) : null;

  const { data: letter, isLoading, error, refetch } = useLetter(letterId);
  const generateMutation = useGenerateResponse();
  const validateMutation = useValidateDraft();
  const routeMutation = useRouteLetter();

  const [activeTab, setActiveTab] = useState<'content' | 'params' | 'drafts'>('content');

  const drafts = letter.drafts || [];

  if (isLoading) return <Loading />;
  if (error || !letter) return <Error message="Письмо не найдено" />;

  const handleGenerate = async () => {
    if (!letterId) return;
    try {
      const draft = await generateMutation.mutateAsync(letterId);
      alert(`Черновик создан! ID: ${draft.id}`);
      refetch();
    } catch (err) {
      alert('Ошибка при генерации');
    }
  };

  const handleValidate = async (draftId: number) => {
    try {
      const result = await validateMutation.mutateAsync(draftId);
      alert(`Валидация завершена. Оценка: ${result.score}`);
      refetch();
    } catch (err) {
      alert('Ошибка при валидации');
    }
  };

  const handleRoute = async () => {
    if (!letterId) return;
    try {
      const approval = await routeMutation.mutateAsync(letterId);
      alert(`Письмо направлено на согласование. ID: ${approval.id}`);
      navigate('/approvals');
    } catch (err) {
      alert('Ошибка при направлении на согласование');
    }
  };


  return (
    <div className="px-4 py-6 sm:px-0">
      <div className="mb-4">
        <button
          onClick={() => navigate(-1)}
          className="text-sm text-primary-600 hover:text-primary-800 mb-4"
        >
          ← Назад
        </button>
      </div>

      <div className="bg-white shadow rounded-lg">
        <div className="px-6 py-4 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <h2 className="text-2xl font-bold text-gray-900">{letter.subject}</h2>
            {letter.request_category && (
              <StatusBadge status={letter.request_category} />
            )}
          </div>
          <div className="mt-2 text-sm text-gray-600">
            <span>От: {letter.sender} ({letter.sender_email})</span>
            <span className="ml-4">
              {format(new Date(letter.received_at), 'dd MMM yyyy, HH:mm', { locale: ru })}
            </span>
          </div>
        </div>

        <div className="px-6 py-4">
          <div className="border-b border-gray-200 mb-4">
            <nav className="-mb-px flex space-x-8">
              <button
                onClick={() => setActiveTab('content')}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'content'
                    ? 'border-primary-500 text-primary-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                Содержание
              </button>
              <button
                onClick={() => setActiveTab('params')}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'params'
                    ? 'border-primary-500 text-primary-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                Параметры анализа
              </button>
              <button
                onClick={() => setActiveTab('drafts')}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'drafts'
                    ? 'border-primary-500 text-primary-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                Черновики ({drafts.length})
              </button>
            </nav>
          </div>

          {activeTab === 'content' && (
            <div className="prose max-w-none">
              <div className="bg-gray-50 rounded-lg p-4 whitespace-pre-wrap">
                {letter.content}
              </div>
            </div>
          )}

          {activeTab === 'params' && (
            <div>
              {letter.processing_params ? (
                <div className="bg-gray-50 rounded-lg p-4">
                  <pre className="text-sm overflow-auto">
                    {JSON.stringify(letter.processing_params, null, 2)}
                  </pre>
                </div>
              ) : (
                <p className="text-gray-500">Параметры анализа отсутствуют</p>
              )}
            </div>
          )}

          {activeTab === 'drafts' && (
            <div>
              {drafts.length === 0 ? (
                <p className="text-gray-500">Черновиков пока нет</p>
              ) : (
                <div className="space-y-4">
                  {drafts.map((draft) => (
                    <div key={draft.id} className="border rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <StatusBadge status={draft.status} />
                        {draft.validation_score !== null && (
                          <span className="text-sm text-gray-600">
                            Оценка: {draft.validation_score}
                          </span>
                        )}
                      </div>
                      <div className="bg-gray-50 rounded p-3 mb-2 whitespace-pre-wrap text-sm">
                        {draft.content}
                      </div>
                      <div className="flex space-x-2">
                        {draft.status === 'draft' && (
                          <button
                            onClick={() => handleValidate(draft.id)}
                            disabled={validateMutation.isLoading}
                            className="px-3 py-1 bg-blue-600 text-white rounded text-sm hover:bg-blue-700 disabled:opacity-50"
                          >
                            Валидировать
                          </button>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>

        <div className="px-6 py-4 bg-gray-50 border-t border-gray-200">
          <div className="flex space-x-3">
            <button
              onClick={handleGenerate}
              disabled={generateMutation.isLoading}
              className="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 disabled:opacity-50"
            >
              {generateMutation.isLoading ? 'Генерация...' : 'Сгенерировать ответ'}
            </button>
            {drafts.length > 0 && (
              <button
                onClick={handleRoute}
                disabled={routeMutation.isLoading}
                className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50"
              >
                {routeMutation.isLoading ? 'Отправка...' : 'Направить на согласование'}
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

