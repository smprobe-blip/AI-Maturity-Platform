import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  Users,
  TrendingUp,
  Activity,
  CheckCircle2,
  FlaskConical,
  Server,
  ShieldCheck,
} from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend,
} from 'recharts';
import { Tabs } from '@/components/ui/Tabs';
import { KpiCard } from '@/components/ui/KpiCard';
import { adminApi } from '@/services/adminApi';

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#14b8a6'];

export default function DashboardPage() {
  const [activeTab, setActiveTab] = useState('business');

  const { data: business, isLoading: bLoading } = useQuery({
    queryKey: ['dashboard', 'business'],
    queryFn: adminApi.getBusinessMetrics,
  });

  const { data: scientific } = useQuery({
    queryKey: ['dashboard', 'scientific'],
    queryFn: adminApi.getScientificMetrics,
    enabled: activeTab === 'scientific',
  });

  const { data: operations } = useQuery({
    queryKey: ['dashboard', 'operations'],
    queryFn: adminApi.getOperationsMetrics,
    enabled: activeTab === 'operations',
  });

  const { data: quality } = useQuery({
    queryKey: ['dashboard', 'quality'],
    queryFn: adminApi.getQualityMetrics,
    enabled: activeTab === 'quality',
  });

  const industryData = business?.industry_distribution
    ? Object.entries(business.industry_distribution).map(([name, value]) => ({
        name,
        value,
      }))
    : [];

  const maturityData = business?.maturity_level_distribution
    ? Object.entries(business.maturity_level_distribution).map(([name, value]) => ({
        name,
        value,
      }))
    : [];

  const tabs = [
    { id: 'business', label: 'Бизнес', icon: <TrendingUp className="w-4 h-4" /> },
    { id: 'scientific', label: 'Наука', icon: <FlaskConical className="w-4 h-4" /> },
    { id: 'operations', label: 'Операции', icon: <Server className="w-4 h-4" /> },
    { id: 'quality', label: 'Качество', icon: <ShieldCheck className="w-4 h-4" /> },
  ];

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600 mt-1">Обзор ключевых метрик платформы</p>
      </div>

      <Tabs tabs={tabs} activeTab={activeTab} onChange={setActiveTab} />

      <div className="mt-6">
        {activeTab === 'business' && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <KpiCard
                title="Всего аудитов"
                value={business?.total_audits ?? 0}
                icon={<Users className="w-5 h-5 text-primary-600" />}
              />
              <KpiCard
                title="За этот месяц"
                value={business?.audits_this_month ?? 0}
                delta={business?.growth_rate_percent}
                trend={
                  (business?.growth_rate_percent || 0) > 0
                    ? 'up'
                    : (business?.growth_rate_percent || 0) < 0
                    ? 'down'
                    : 'neutral'
                }
                icon={<Activity className="w-5 h-5 text-primary-600" />}
              />
              <KpiCard
                title="Средняя зрелость"
                value={(business?.average_maturity_score ?? 0).toFixed(2)}
                icon={<CheckCircle2 className="w-5 h-5 text-primary-600" />}
              />
              <KpiCard
                title="Конверсия"
                value="68%"
                delta={4.2}
                trend="up"
                icon={<TrendingUp className="w-5 h-5 text-primary-600" />}
              />
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="card">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  Распределение по отраслям
                </h3>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={industryData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" angle={-20} textAnchor="end" height={80} />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="value" fill="#3b82f6" radius={[8, 8, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>

              <div className="card">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  Уровни зрелости
                </h3>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={maturityData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      outerRadius={100}
                      fill="#8884d8"
                      dataKey="value"
                      label={({ name, percent }) =>
                        `${name}: ${(percent * 100).toFixed(0)}%`
                      }
                    >
                      {maturityData.map((_, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Legend />
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'scientific' && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <KpiCard
                title="Размер выборки"
                value={scientific?.sample_size ?? 0}
                icon={<Users className="w-5 h-5 text-primary-600" />}
              />
              <KpiCard
                title="Всего ответов"
                value={scientific?.total_responses ?? 0}
                icon={<CheckCircle2 className="w-5 h-5 text-primary-600" />}
              />
              <KpiCard
                title="Средний ответ"
                value={(scientific?.mean_response ?? 0).toFixed(2)}
                icon={<Activity className="w-5 h-5 text-primary-600" />}
              />
            </div>

            <div className="card">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Alpha Кронбаха по осям
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                {Object.entries(scientific?.cronbach_alpha || {}).map(
                  ([dim, alpha]) => (
                    <div key={dim} className="p-4 bg-gray-50 rounded-lg">
                      <div className="text-xs text-gray-600 mb-1">Ось {dim}</div>
                      <div className="text-2xl font-bold text-gray-900">
                        {(alpha as number).toFixed(3)}
                      </div>
                      <div
                        className={`text-xs mt-1 ${
                          (alpha as number) >= 0.7
                            ? 'text-green-600'
                            : (alpha as number) >= 0.5
                            ? 'text-yellow-600'
                            : 'text-red-600'
                        }`}
                      >
                        {(alpha as number) >= 0.7
                          ? '✓ Отличная надёжность'
                          : (alpha as number) >= 0.5
                          ? '⚠ Приемлемо'
                          : '✗ Низкая'}
                      </div>
                    </div>
                  )
                )}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'operations' && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <KpiCard
              title="Аудитов в хранилище"
              value={operations?.total_audits_stored ?? 0}
              icon={<Users className="w-5 h-5 text-primary-600" />}
            />
            <KpiCard
              title="Среднее время ответа"
              value={`${operations?.avg_response_time_sec ?? 0}с`}
              icon={<Activity className="w-5 h-5 text-primary-600" />}
            />
            <KpiCard
              title="Статус хранилища"
              value={operations?.storage_status ?? 'N/A'}
              icon={<Server className="w-5 h-5 text-primary-600" />}
            />
            <KpiCard
              title="Последний бэкап"
              value="Сегодня"
              icon={<CheckCircle2 className="w-5 h-5 text-primary-600" />}
            />
          </div>
        )}

        {activeTab === 'quality' && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <KpiCard
                title="Всего записей"
                value={quality?.total_records ?? 0}
                icon={<Users className="w-5 h-5 text-primary-600" />}
              />
              <KpiCard
                title="Полных записей"
                value={quality?.complete_records ?? 0}
                icon={<CheckCircle2 className="w-5 h-5 text-primary-600" />}
              />
              <KpiCard
                title="Полнота данных"
                value={`${quality?.completeness_rate ?? 0}%`}
                icon={<Activity className="w-5 h-5 text-primary-600" />}
              />
              <KpiCard
                title="Архивировано"
                value={quality?.archived_records ?? 0}
                icon={<Server className="w-5 h-5 text-primary-600" />}
              />
            </div>

            <div className="card">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Индикатор качества
              </h3>
              <div className="w-full bg-gray-200 rounded-full h-4">
                <div
                  className="bg-green-500 h-4 rounded-full transition-all"
                  style={{ width: `${quality?.completeness_rate ?? 0}%` }}
                />
              </div>
              <div className="text-sm text-gray-600 mt-2">
                {(quality?.completeness_rate ?? 0).toFixed(1)}% данных полностью заполнены
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}