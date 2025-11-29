import { QueryClient, QueryClientProvider } from 'react-query';
import LetterProcessor from './pages/LetterProcessor';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <div className="min-h-screen bg-gray-50">
        <LetterProcessor />
      </div>
    </QueryClientProvider>
  );
}

export default App;
