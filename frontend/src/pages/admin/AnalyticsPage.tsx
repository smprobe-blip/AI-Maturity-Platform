import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  FlaskConical,
  BarChart3,
  TrendingUp,
  Users,
  FileText,
  Play,
} from 'lucide-react';
import { toast } from 'sonner';
import { Tabs } from '@/components/ui/Tabs';
import { Button } from '@/components/ui/Button';
import { KpiCard } from '@/components/ui/KpiCard';
import { Badge } from '@/components/ui/Badge';
import { analyticsApi } from '@/services/analyticsApi';

const dimensionNames: Record<string, string> = {
  '1': 'Strategy & Vision',
  '2': 'Data & Analytics',
  '3': 'Technology',
  '4': 'Processes',
  '5': 'People & Skills',
  '6': 'Culture & Change',
  '7': 'Ethics & Governance',
};

export default function AnalyticsPage() {
  const queryClient = useQueryClient();
  const [activeTab, setActiveTab] = useState('descriptive');

  const { data: descriptive, isLoading: descLoading } = useQuery({
    queryKey: ['analytics', 'descriptive'],
    queryFn: analyticsApi.getSampleCharacteristics,
    enabled: activeTab === 'descriptive',
  });

  const { data: reliability, isLoading: relLoading } = useQuery({
    queryKey: ['analytics', 'reliability'],
    queryFn: analyticsApi.getFullReliability,
    enabled: activeTab === 'reliability',
  });

  const { data: efa, isLoading: efaLoading } = useQuery({
    queryKey: ['analytics', 'efa'],
    queryFn: () => analyticsApi.runEFA(7),
    enabled: activeTab === 'factor',
  });

  const { data: regression, isLoading: regLoading } = useQuery({
    queryKey: ['analytics', 'regression'],
    queryFn: analyticsApi.maturityToROI,
    enabled: activeTab === 'regression',
  });

  const { data: cluster, isLoading: clustLoading } = useQuery({
    queryKey: ['analytics', 'cluster'],
    queryFn: () => analyticsApi.kmeansClustering(4),
    enabled: activeTab === 'cluster',
  });

  const fullAnalysisMutation = useMutation({
    mutationFn: analyticsApi.runFullAnalysis,
    onSuccess: () => {
      toast.success('Полный анализ завершён');
      queryClient.invalidateQueries({ queryKey: ['analytics'] });
    },
    onError: () => toast.error('Ошибка анализа'),
  });

  const reportMutation = useMutation({
    mutationFn: analyticsApi.generateReport,
    onSuccess: () => toast.success('Отчёт сгенерирован'),
    onError: () => toast.error('Ошибка генерации отчёта'),
  });

  const tabs = [
    { id: 'descriptive', label: 'Описательные', icon: <BarChart3 className="w-4 h-4" /> },
    { id: 'reliability', label: 'Надёжность', icon: <FlaskConical className="w-4 h-4" /> },
    { id: 'factor', label: 'Факторный', icon: <TrendingUp className="w-4 h-4" /> },
    { id: 'regression', label: 'Регрессия', icon: <TrendingUp className="w-4 h-4" /> },
    { id: 'cluster', label: 'Кластеры', icon: <Users className="w-4 h-4" /> },
  ];

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Аналитика</h1>
          <p className="text-gray-600 mt-1">Статистический анализ для диссертации</p>
        </div>
        <div className="flex gap-3">
          <Button
            variant="secondary"
            onClick={() => fullAnalysisMutation.mutate()}
            disabled={fullAnalysisMutation.isPending}
          >
            <Play className="w-4 h-4 mr-2" />
            {fullAnalysisMutation.isPending ? 'Анализ...' : 'Полный анализ'}
          </Button>
          <Button
            onClick={() => reportMutation.mutate()}
            disabled={reportMutation.isPending}
          >
            <FileText className="w-4 h-4 mr-2" />
            {reportMutation.isPending ? 'Генерация...' : 'PDF отчёт'}
          </Button>
        </div>
      </div>

      <Tabs tabs={tabs} activeTab={activeTab} onChange={setActiveTab} />

      <div className="mt-6">
        {activeTab === 'descriptive' && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <KpiCard
                title="Размер выборки"
                value={descriptive?.total_sample_size ?? 0}
                icon={<Users className="w-5 h-5 text-primary-600" />}
              />
              <KpiCard
                title="Отраслей"
                value={Object.keys(descriptive?.industry_distribution || {}).length}
                icon={<BarChart3 className="w-5 h-5 text-primary-600" />}
              />
              <KpiCard
                title="Регионов"
                value={Object.keys(descriptive?.region_distribution || {}).length}
                icon={<Users className="w-5 h-5 text-primary-600" />}
              />
              <KpiCard
                title="Уровней зрелости"
                value={Object.keys(descriptive?.maturity_level_distribution || {}).length}
                icon={<TrendingUp className="w-5 h-5 text-primary-600" />}
              />
            </div>

            <div className="card">
              <h3 className="text-lg font-semibold mb-4">Распределение по отраслям</h3>
              <div className="space-y-2">
                {Object.entries(descriptive?.industry_distribution || {}).map(
                  ([industry, count]) => (
                    <div key={industry} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                      <span className="font-medium">{industry}</span>
                      <Badge variant="info">{count as number}</Badge>
                    </div>
                  )
                )}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'reliability' && (
          <div className="space-y-6">
            {reliability?.summary && (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <KpiCard
                  title="Средний α Кронбаха"
                  value={reliability.summary.mean_alpha?.toFixed(3)}
                  icon={<FlaskConical className="w-5 h-5 text-primary-600" />}
                />
                <KpiCard
                  title="Минимальный α"
                  value={reliability.summary.min_alpha?.toFixed(3)}
                  icon={<FlaskConical className="w-5 h-5 text-primary-600" />}
                />
                <KpiCard
                  title="Все ≥ 0.7"
                  value={reliability.summary.all_acceptable ? '✓ Да' : '✗ Нет'}
                  icon={<FlaskConical className="w-5 h-5 text-primary-600" />}
                />
              </div>
            )}

            <div className="card">
              <h3 className="text-lg font-semibold mb-4">Надёжность по осям</h3>
              <div className="space-y-3">
                {Object.entries(reliability?.dimensions || {}).map(([dimId, dimData]: [string, any]) => {
                  const alpha = dimData.cronbach_alpha;
                  if (alpha?.status !== 'completed') return null;

                  return (
                    <div key={dimId} className="p-4 bg-gray-50 rounded-lg">
                      <div className="flex items-center justify-between mb-2">
                        <span className="font-semibold">
                          Ось {dimId}: {dimensionNames[dimId]}
                        </span>
                        <Badge
                          variant={
                            alpha.alpha >= 0.8
                              ? 'success'
                              : alpha.alpha >= 0.7
                              ? 'info'
                              : 'warning'
                          }
                        >
                          α = {alpha.alpha.toFixed(3)}
                        </Badge>
                      </div>
                      <div className="text-sm text-gray-600">
                        95% CI: [{alpha.ci_95[0].toFixed(3)}, {alpha.ci_95[1].toFixed(3)}]
                      </div>
                      <div className="text-sm text-gray-600">
                        Интерпретация: {alpha.interpretation}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'factor' && (
          <div className="space-y-6">
            {efa?.status === 'completed' ? (
              <>
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                  <KpiCard
                    title="Размер выборки"
                    value={efa.sample_size}
                    icon={<Users className="w-5 h-5 text-primary-600" />}
                  />
                  <KpiCard
                    title="KMO"
                    value={efa.assumptions?.kmo?.overall?.toFixed(3)}
                    icon={<FlaskConical className="w-5 h-5 text-primary-600" />}
                  />
                  <KpiCard
                    title="Bartlett p"
                    value={efa.assumptions?.bartlett_sphericity?.p_value?.toFixed(4)}
                    icon={<FlaskConical className="w-5 h-5 text-primary-600" />}
                  />
                  <KpiCard
                    title="Объяснённая дисперсия"
                    value={`${(efa.cumulative_variance?.slice(-1)[0] * 100)?.toFixed(1)}%`}
                    icon={<TrendingUp className="w-5 h-5 text-primary-600" />}
                  />
                </div>

                <div className="card">
                  <h3 className="text-lg font-semibold mb-4">Собственные значения</h3>
                  <div className="space-y-2">
                    {efa.eigenvalues?.map((ev: number, i: number) => (
                      <div key={i} className="flex items-center gap-3">
                        <span className="w-20 text-sm">Factor {i + 1}</span>
                        <div className="flex-1 bg-gray-200 rounded-full h-3">
                          <div
                            className="bg-primary-600 h-3 rounded-full"
                            style={{ width: `${(ev / Math.max(...efa.eigenvalues)) * 100}%` }}
                          />
                        </div>
                        <span className="w-20 text-right font-mono text-sm">
                          {ev.toFixed(3)}
                        </span>
                        {ev > 1 && <Badge variant="success">{'>'}1</Badge>}
                      </div>
                    ))}
                  </div>
                </div>

                <div className="card">
                  <h3 className="text-lg font-semibold mb-4">Интерпретация факторов</h3>
                  <div className="space-y-3">
                    {efa.interpretation?.map((interp: any) => (
                      <div key={interp.factor} className="p-4 bg-gray-50 rounded-lg">
                        <div className="font-semibold mb-2">Factor {interp.factor}</div>
                        <div className="text-sm text-gray-600">
                          Доминирующая ось: {interp.dominant_dimension || 'N/A'}
                        </div>
                        <div className="text-sm text-gray-600">
                          Топ-загрузок: {interp.items_count}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </>
            ) : (
              <div className="card text-center py-12 text-gray-500">
                {efa?.message || 'Недостаточно данных для факторного анализа'}
              </div>
            )}
          </div>
        )}

        {activeTab === 'regression' && (
          <div className="space-y-6">
            {regression?.status === 'completed' ? (
              <>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <KpiCard
                    title="R²"
                    value={regression.r_squared?.toFixed(3)}
                    icon={<TrendingUp className="w-5 h-5 text-primary-600" />}
                  />
                  <KpiCard
                    title="Adj R²"
                    value={regression.adjusted_r_squared?.toFixed(3)}
                    icon={<TrendingUp className="w-5 h-5 text-primary-600" />}
                  />
                  <KpiCard
                    title="F-statistic"
                    value={regression.f_statistic?.toFixed(2)}
                    icon={<TrendingUp className="w-5 h-5 text-primary-600" />}
                  />
                </div>

                <div className="card">
                  <h3 className="text-lg font-semibold mb-4">Коэффициенты</h3>
                  <div className="space-y-3">
                    {Object.entries(regression.coefficients || {}).map(([name, coef]: [string, any]) => (
                      <div key={name} className="p-4 bg-gray-50 rounded-lg">
                        <div className="flex items-center justify-between mb-2">
                          <span className="font-semibold">{name}</span>
                          <Badge variant={coef.p_value < 0.05 ? 'success' : 'warning'}>
                            p = {coef.p_value?.toFixed(4)}
                          </Badge>
                        </div>
                        <div className="text-sm text-gray-600">
                          β = {coef.value?.toFixed(3)}
                        </div>
                        <div className="text-sm text-gray-600">
                          95% CI: [{coef.ci_95?.[0]?.toFixed(3)}, {coef.ci_95?.[1]?.toFixed(3)}]
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="card">
                  <h3 className="text-lg font-semibold mb-4">Интерпретация</h3>
                  <p className="text-gray-700">{regression.interpretation}</p>
                </div>
              </>
            ) : (
              <div className="card text-center py-12 text-gray-500">
                Недостаточно данных для регрессионного анализа
              </div>
            )}
          </div>
        )}

        {activeTab === 'cluster' && (
          <div className="space-y-6">
            {cluster?.status === 'completed' ? (
              <>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <KpiCard
                    title="Кластеров"
                    value={cluster.n_clusters}
                    icon={<Users className="w-5 h-5 text-primary-600" />}
                  />
                  <KpiCard
                    title="Silhouette"
                    value={cluster.silhouette_score?.toFixed(3)}
                    icon={<FlaskConical className="w-5 h-5 text-primary-600" />}
                  />
                  <KpiCard
                    title="Размер выборки"
                    value={cluster.sample_size}
                    icon={<Users className="w-5 h-5 text-primary-600" />}
                  />
                </div>

                <div className="card">
                  <h3 className="text-lg font-semibold mb-4">Профили кластеров</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {cluster.cluster_profiles?.map((profile: any) => (
                      <div key={profile.cluster_id} className="p-4 border border-gray-200 rounded-lg">
                        <div className="flex items-center justify-between mb-3">
                          <h4 className="font-bold text-lg">Кластер {profile.cluster_id + 1}</h4>
                          <Badge variant="info">n={profile.size}</Badge>
                        </div>
                        <div className="space-y-2 text-sm">
                          <div>
                            <span className="text-gray-600">Средняя зрелость:</span>{' '}
                            <span className="font-semibold">{profile.composite_mean?.toFixed(2)}</span>
                          </div>
                          <div>
                            <span className="text-gray-600">Характеристики:</span>
                            <div className="mt-1 flex flex-wrap gap-1">
                              {profile.characteristics?.map((c: string, i: number) => (
                                <Badge key={i} variant="neutral">{c}</Badge>
                              ))}
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </>
            ) : (
              <div className="card text-center py-12 text-gray-500">
                Недостаточно данных для кластерного анализа
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}