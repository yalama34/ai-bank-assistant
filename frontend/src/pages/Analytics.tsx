import { useMetrics, useSLA } from '@/hooks/useAnalytics';
import Loading from '@/components/Loading';
import Error from '@/components/Error';
import {
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899'];

export default function Analytics() {
  const { data: metrics, isLoading: metricsLoading, error: metricsError } = useMetrics();
  const { data: sla, isLoading: slaLoading, error: slaError } = useSLA();

  if (metricsLoading || slaLoading) return <Loading />;
  if (metricsError || slaError) {
    return <Error message="Не удалось загрузить аналитику" />;
  }

  const letterTypesData = metrics
    ? Object.entries(metrics.letter_types_statistics).map(([name, value]) => ({
        name,
        value,
      }))
    : [];

  const statusData = metrics
    ? Object.entries(metrics.status_distribution).map(([name, value]) => ({
        name,
        value,
      }))
    : [];

  const slaData = sla
    ? [
        { name: 'Соблюдено', value: sla.sla_compliant_count, color: '#10b981' },
        { name: 'Нарушено', value: sla.sla_violated_count, color: '#ef4444' },
      ]
    : [];

  return (
    <div className="px-4 py-6 sm:px-0">
      <h2 className="text-2xl font-bold text-gray-900 mb-6">Аналитика</h2>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-sm font-medium text-gray-500">Всего писем</div>
          <div className="mt-2 text-3xl font-bold text-gray-900">
            {metrics?.total_letters || 0}
          </div>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-sm font-medium text-gray-500">Всего черновиков</div>
          <div className="mt-2 text-3xl font-bold text-gray-900">
            {metrics?.total_drafts || 0}
          </div>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-sm font-medium text-gray-500">Среднее время обработки</div>
          <div className="mt-2 text-3xl font-bold text-gray-900">
            {metrics?.average_processing_time_hours.toFixed(1) || '0.0'} ч
          </div>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-sm font-medium text-gray-500">SLA соблюдение</div>
          <div className="mt-2 text-3xl font-bold text-gray-900">
            {sla?.sla_compliance_rate_percent.toFixed(1) || '0.0'}%
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Распределение по типам запросов
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={letterTypesData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="value" fill="#3b82f6" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Распределение по статусам
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={statusData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {statusData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">SLA мониторинг</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={slaData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {slaData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
          <div className="mt-4 text-sm text-gray-600">
            <div>Соблюдено: {sla?.sla_compliant_count || 0}</div>
            <div>Нарушено: {sla?.sla_violated_count || 0}</div>
            <div>Всего проверено: {sla?.total_checked || 0}</div>
          </div>
        </div>

        {sla && sla.violated_letters.length > 0 && (
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Письма с нарушением SLA
            </h3>
            <div className="space-y-2 max-h-80 overflow-y-auto">
              {sla.violated_letters.map((letter) => (
                <div
                  key={letter.letter_id}
                  className="border rounded-lg p-3 hover:bg-gray-50"
                >
                  <div className="font-medium text-sm text-gray-900">
                    {letter.subject}
                  </div>
                  <div className="text-xs text-gray-600 mt-1">
                    Нарушение: {letter.violation_hours.toFixed(1)} ч
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

