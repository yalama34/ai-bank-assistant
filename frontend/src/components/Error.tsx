interface ErrorProps {
  message?: string;
  onRetry?: () => void;
}

export default function Error({ message = 'Произошла ошибка', onRetry }: ErrorProps) {
  return (
    <div className="bg-red-50 border border-red-200 rounded-lg p-4">
      <div className="flex">
        <div className="flex-shrink-0">
          <span className="text-red-400 text-xl">⚠️</span>
        </div>
        <div className="ml-3 flex-1">
          <h3 className="text-sm font-medium text-red-800">Ошибка</h3>
          <p className="mt-1 text-sm text-red-700">{message}</p>
          {onRetry && (
            <button
              onClick={onRetry}
              className="mt-2 text-sm font-medium text-red-800 hover:text-red-900 underline"
            >
              Попробовать снова
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

