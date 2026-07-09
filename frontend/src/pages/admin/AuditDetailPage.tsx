import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { format } from 'date-fns';
import { ArrowLeft, Archive, Mail } from 'lucide-react';
import { toast } from 'sonner';
import { Tabs } from '@/components/ui/Tabs';
import { Button } from '@/components/ui/Button';
import { Badge, getMaturityBadgeVariant } from '@/components/ui/Badge';
import { RadarChartWithBenchmark } from '@/components/charts/RadarChartWithBenchmark';
import { adminApi } from '@/services/adminApi';

export default function AuditDetailPage() {
  const { auditId } = useParams<{ auditId: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [activeTab, setActiveTab] = useState('metadata');

  const { data: audit, isLoading } = useQuery({
    queryKey: ['audit', auditId],
    queryFn: () => adminApi.getAudit(auditId!),
    enabled: !!auditId,
  });

  const archiveMutation = useMutation({
    mutationFn: () => adminApi.archiveAudit(auditId!),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['audit', auditId] });
      toast.success('Аудит архивирован');
    },
  });

  if (isLoading) {
    return (
      <div className="flex justify-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600" />
      </div>
    );
  }

  if (!audit) {
    return <div className="text-center py-12">Аудит не найден</div>;
  }

  const tabs = [
    { id: 'metadata', label: 'Метаданные' },
    { id: 'responses', label: 'Ответы' },
    { id: 'radar', label: 'Радар' },
    { id: 'financial', label: 'Финансы' },
    { id: 'qualitative', label: 'Качественные' },
  ];

  return (
    <div>
      <div className="flex items-center gap-4 mb-6">
        <button
          onClick={() => navigate('/admin/audits')}
          className="p-2 rounded-lg hover:bg-gray-100"
        >
          <ArrowLeft className="w-5 h-5" />
        </button>
        <div className="flex-1">
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold text-gray-900">
              Аудит {audit.audit_id.slice(0, 8)}...
            </h1>
            <Badge variant={getMaturityBadgeVariant(audit.calculated_indices?.maturity_level || '')}>
              {audit.calculated_indices?.maturity_level}
            </Badge>
          </div>
          <p className="text-sm text-gray-500 mt-1">
            {format(new Date(audit.created_at), 'dd.MM.yyyy HH:mm')}
          </p>
        </div>
        <Button
          variant="secondary"
          onClick={() => archiveMutation.mutate()}
          disabled={audit.status === 'archived'}
        >
          <Archive className="w-4 h-4 mr-2" />
          Архивировать
        </Button>
      </div>

      <div className="card">
        <Tabs tabs={tabs} activeTab={activeTab} onChange={setActiveTab} />
        <div className="mt-6">
          {activeTab === 'metadata' && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h3 className="text-sm font-semibold text-gray-500 uppercase mb-3">
                  Профиль компании
                </h3>
                <dl className="space-y-2">
                  <div>
                    <dt className="text-xs text-gray-500">Отрасль</dt>
                    <dd className="text-sm font-medium">
                      {audit.company_profile?.industry}
                    </dd>
                  </div>
                  <div>
                    <dt className="text-xs text-gray-500">Размер</dt>
                    <dd className="text-sm font-medium">
                      {audit.company_profile?.company_size}
                    </dd>
                  </div>
                  <div>
                    <dt className="text-xs text-gray-500">Регион</dt>
                    <dd className="text-sm font-medium">
                      {audit.company_profile?.region}
                    </dd>
                  </div>
                </dl>
              </div>
              <div>
                <h3 className="text-sm font-semibold text-gray-500 uppercase mb-3">
                  Контакты
                </h3>
                <dl className="space-y-2">
                  <div>
                    <dt className="text-xs text-gray-500">Email</dt>
                    <dd className="text-sm font-medium flex items-center gap-2">
                      {audit.contact?.email}
                      <button
                        onClick={() => {
                          navigator.clipboard.writeText(audit.contact?.email || '');
                          toast.success('Email скопирован');
                        }}
                        className="text-primary-600 hover:text-primary-700"
                      >
                        <Mail className="w-4 h-4" />
                      </button>
                    </dd>
                  </div>
                  <div>
                    <dt className="text-xs text-gray-500">Имя</dt>
                    <dd className="text-sm font-medium">{audit.contact?.name || '—'}</dd>
                  </div>
                  <div>
                    <dt className="text-xs text-gray-500">Должность</dt>
                    <dd className="text-sm font-medium">
                      {audit.contact?.position || '—'}
                    </dd>
                  </div>
                </dl>
              </div>
              <div className="md:col-span-2 bg-primary-50 rounded-lg p-4">
                <div className="grid grid-cols-3 gap-4 text-center">
                  <div>
                    <div className="text-xs text-gray-600 mb-1">Комплексная оценка</div>
                    <div className="text-3xl font-bold text-primary-700">
                      {audit.calculated_indices?.composite_score?.toFixed(2)}
                    </div>
                  </div>
                  <div>
                    <div className="text-xs text-gray-600 mb-1">ROI</div>
                    <div className="text-3xl font-bold text-green-600">
                      +{audit.calculated_indices?.roi_estimate_percent?.toFixed(0)}%
                    </div>
                  </div>
                  <div>
                    <div className="text-xs text-gray-600 mb-1">TCO</div>
                    <div className="text-3xl font-bold text-gray-900">
                      {audit.calculated_indices?.tco_estimate_millions?.toFixed(1)}M ₽
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'responses' && (
            <div>
              <h3 className="text-lg font-semibold mb-4">Сырые ответы (35 вопросов)</h3>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-3 py-2 text-left">Ось</th>
                      <th className="px-3 py-2 text-left">Вопрос</th>
                      <th className="px-3 py-2 text-center">Оценка</th>
                      <th className="px-3 py-2 text-center">Время (сек)</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    {audit.raw_responses?.map((r: any, i: number) => (
                      <tr key={i}>
                        <td className="px-3 py-2">D{r.dimension_id}</td>
                        <td className="px-3 py-2">Q{r.question_id}</td>
                        <td className="px-3 py-2 text-center font-bold">
                          {r.score}
                        </td>
                        <td className="px-3 py-2 text-center text-gray-600">
                          {r.time_to_answer_sec?.toFixed(1) || '—'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {activeTab === 'radar' && (
            <div className="space-y-6">
              {/* Legend */}
              <div className="flex justify-center gap-6">
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 bg-blue-500 rounded" style={{ opacity: 0.3 }} />
                  <span className="text-sm text-gray-700">Текущее состояние</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 bg-yellow-500 rounded" style={{ opacity: 0.2 }} />
                  <span className="text-sm text-gray-700">Целевое состояние</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 bg-green-500 rounded" style={{ opacity: 0.15 }} />
                  <span className="text-sm text-gray-700">Отраслевой бенчмарк</span>
                </div>
              </div>
              
              {/* Radar Chart */}
              <div className="flex justify-center py-6">
                <RadarChartWithBenchmark audit={audit} />
              </div>
            </div>
          )}

          {activeTab === 'financial' && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="p-6 bg-green-50 rounded-lg">
                <div className="text-sm text-gray-600 mb-1">ROI</div>
                <div className="text-3xl font-bold text-green-700">
                  +{audit.calculated_indices?.roi_estimate_percent?.toFixed(0)}%
                </div>
              </div>
              <div className="p-6 bg-blue-50 rounded-lg">
                <div className="text-sm text-gray-600 mb-1">TCO</div>
                <div className="text-3xl font-bold text-blue-700">
                  {audit.calculated_indices?.tco_estimate_millions?.toFixed(1)}M ₽
                </div>
              </div>
              <div className="p-6 bg-purple-50 rounded-lg">
                <div className="text-sm text-gray-600 mb-1">Уровень зрелости</div>
                <div className="text-xl font-bold text-purple-700">
                  {audit.calculated_indices?.maturity_level}
                </div>
              </div>
            </div>
          )}

          {activeTab === 'qualitative' && (
            <div className="text-center py-12 text-gray-500">
              Качественные инсайты доступны для полных аудитов
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
