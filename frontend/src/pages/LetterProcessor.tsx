import { useState } from 'react';
import { processLetter } from '@/api/letters';
import Loading from '@/components/Loading';
import Error from '@/components/Error';
import type { LetterResponse } from '@/types';

export default function LetterProcessor() {
  const [inputText, setInputText] = useState('');
  const [subject, setSubject] = useState('');
  const [result, setResult] = useState<LetterResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputText.trim()) {
      setError('Введите текст письма');
      return;
    }

    setIsLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await processLetter({
        content: inputText,
        subject: subject || 'Входящее письмо',
      });
      setResult(response);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Произошла ошибка при обработке письма');
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    setInputText('');
    setSubject('');
    setResult(null);
    setError(null);
  };

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      <div className="bg-white rounded-lg shadow-lg">
        <div className="px-6 py-4 border-b border-gray-200">
          <h1 className="text-2xl font-bold text-gray-900">AI Bank Assistant</h1>
          <p className="text-sm text-gray-600 mt-1">Обработка входящих писем и генерация ответов</p>
        </div>

        <div className="p-6">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label htmlFor="subject" className="block text-sm font-medium text-gray-700 mb-2">
                Тема письма (необязательно)
              </label>
              <input
                type="text"
                id="subject"
                value={subject}
                onChange={(e) => setSubject(e.target.value)}
                placeholder="Введите тему письма"
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500"
              />
            </div>

            <div>
              <label htmlFor="content" className="block text-sm font-medium text-gray-700 mb-2">
                Текст письма *
              </label>
              <textarea
                id="content"
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                placeholder="Вставьте текст входящего письма..."
                rows={10}
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500"
                required
              />
            </div>

            <div className="flex space-x-3">
              <button
                type="submit"
                disabled={isLoading || !inputText.trim()}
                className="px-6 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isLoading ? 'Обработка...' : 'Обработать письмо'}
              </button>
              {result && (
                <button
                  type="button"
                  onClick={handleReset}
                  className="px-6 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300"
                >
                  Очистить
                </button>
              )}
            </div>
          </form>

          {isLoading && (
            <div className="mt-6">
              <Loading />
            </div>
          )}

          {error && (
            <div className="mt-6">
              <Error message={error} />
            </div>
          )}

          {result && (
            <div className="mt-6 space-y-6">
              {/* Оригинальное письмо */}
              <div className="border rounded-lg p-4 bg-gray-50">
                <h2 className="text-lg font-semibold text-gray-900 mb-2">Оригинальное письмо</h2>
                <div className="text-sm text-gray-700 whitespace-pre-wrap">{result.original_letter}</div>
              </div>

              {/* Сгенерированный ответ */}
              <div className="border rounded-lg p-4 bg-green-50">
                <div className="flex items-center justify-between mb-2">
                  <h2 className="text-lg font-semibold text-gray-900">Сгенерированный ответ</h2>
                  <div className="flex items-center space-x-2">
                    <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                      result.auto_send_eligible
                        ? 'bg-green-100 text-green-800'
                        : 'bg-yellow-100 text-yellow-800'
                    }`}>
                      {result.auto_send_eligible ? 'Готов к отправке' : 'Требует проверки'}
                    </span>
                    <span className="px-3 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                      Оценка: {result.validation_score}/100
                    </span>
                  </div>
                </div>
                <div className="text-sm text-gray-700 whitespace-pre-wrap bg-white p-3 rounded border">
                  {result.generated_response}
                </div>
              </div>

              {/* Параметры анализа */}
              {result.processing_params && Object.keys(result.processing_params).length > 0 && (
                <div className="border rounded-lg p-4 bg-blue-50">
                  <h2 className="text-lg font-semibold text-gray-900 mb-2">Параметры анализа</h2>
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                    {Object.entries(result.processing_params).map(([key, value]) => (
                      <div key={key} className="bg-white p-2 rounded border">
                        <div className="text-xs font-medium text-gray-500 uppercase">{key}</div>
                        <div className="text-sm font-semibold text-gray-900 mt-1">
                          {String(value)}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Результаты валидации */}
              {result.validation_result && (
                <div className="border rounded-lg p-4 bg-yellow-50">
                  <h2 className="text-lg font-semibold text-gray-900 mb-2">Результаты валидации</h2>
                  <div className="space-y-2">
                    {result.validation_result.issues && result.validation_result.issues.length > 0 && (
                      <div>
                        <div className="text-sm font-medium text-red-700 mb-1">Замечания:</div>
                        <ul className="list-disc list-inside text-sm text-red-600 space-y-1">
                          {result.validation_result.issues.map((issue, idx) => (
                            <li key={idx}>{issue}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                    {result.validation_result.recommendations && result.validation_result.recommendations.length > 0 && (
                      <div>
                        <div className="text-sm font-medium text-blue-700 mb-1">Рекомендации:</div>
                        <ul className="list-disc list-inside text-sm text-blue-600 space-y-1">
                          {result.validation_result.recommendations.map((rec, idx) => (
                            <li key={idx}>{rec}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Категория запроса */}
              {result.request_category && (
                <div className="border rounded-lg p-4 bg-purple-50">
                  <h2 className="text-lg font-semibold text-gray-900 mb-2">Категория запроса</h2>
                  <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-purple-100 text-purple-800">
                    {result.request_category}
                  </span>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

