import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/Button';
import { RadarChartWithBenchmark } from '@/components/charts/RadarChartWithBenchmark';
import { useAuditStore } from '@/store/auditStore';
import { publicApi } from '@/services/api';

export default function Page3() {
  const { auditId } = useParams<{ auditId: string }>();
  const navigate = useNavigate();
  const { calculatedIndices, companyProfile, auditId: storedAuditId } = useAuditStore();
  const [auditData, setAuditData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadResults = async () => {
      if (!auditId) {
        navigate('/');
        return;
      }

      try {
        const data = await publicApi.getAudit(auditId);
        setAuditData(data);
        setLoading(false);
      } catch (error) {
        console.error('Failed to load audit:', error);
        if (calculatedIndices || auditId === storedAuditId) {
          setLoading(false);
        } else {
          navigate('/');
        }
      }
    };

    loadResults();
  }, [auditId, calculatedIndices, storedAuditId, navigate]);

  const getAuditForRadar = () => {
    const indices = auditData?.calculated_indices || calculatedIndices;
    const industry = auditData?.company_profile?.industry || companyProfile?.industry || 'CrossIndustry';
    
    if (!indices || !indices.dimension_scores) return null;
    
    return {
      company_profile: {
        industry: industry,
      },
      calculated_indices: {
        dimension_scores: indices.dimension_scores,
      },
    };
  };

  const handleSendEmail = async () => {
    if (!auditId) return;
    const email = prompt('Введите ваш email для получения отчёта:');
    if (!email) return;
    try {
      await publicApi.sendAuditReport(auditId, email);
      alert('Отчёт отправлен на вашу почту!');
    } catch (error) {
      alert('Ошибка при отправке отчёта');
    }
  };

  const handleRestart = () => {
    if (confirm('Начать новую оценку? Текущие данные будут потеряны.')) {
      navigate('/');
      window.location.reload();
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Загрузка результатов...</p>
        </div>
      </div>
    );
  }

  const indices = auditData?.calculated_indices || calculatedIndices;
  const auditForRadar = getAuditForRadar();

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-secondary-50 py-12 px-4">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-3">
            Ваши результаты
          </h1>
          <p className="text-lg text-gray-600">
            ID аудита: <span className="font-mono text-sm">{auditId?.slice(0, 8)}...</span>
          </p>
        </div>

        <div className="card mb-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <div>
              <div className="mb-4">
                <h3 className="text-lg font-semibold text-gray-900 mb-3">
                  Профиль зрелости
                </h3>
                <div className="flex flex-wrap gap-3 mb-4">
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full bg-blue-500" style={{ opacity: 0.6 }} />
                    <span className="text-sm text-gray-700">Текущее</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full bg-yellow-500" style={{ opacity: 0.4 }} />
                    <span className="text-sm text-gray-700">Целевое</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full bg-green-500" style={{ opacity: 0.3 }} />
                    <span className="text-sm text-gray-700">Бенчмарк</span>
                  </div>
                </div>
              </div>
              {auditForRadar ? (
                <RadarChartWithBenchmark audit={auditForRadar} />
              ) : (
                <div className="flex justify-center items-center h-[400px]">
                  <p className="text-gray-400">Нет данных для отображения</p>
                </div>
              )}
            </div>

            <div className="space-y-6">
              <div>
                <div className="text-sm text-gray-600 mb-1">Комплексная оценка</div>
                <div className="text-5xl font-bold text-primary-600">
                  {indices?.composite_score?.toFixed(2)}
                  <span className="text-2xl text-gray-400"> / 5.00</span>
                </div>
              </div>
              <div>
                <div className="text-sm text-gray-600 mb-1">Уровень зрелости</div>
                <div className="text-2xl font-bold text-gray-900">
                  {indices?.maturity_level}
                </div>
              </div>
              {indices?.roi_estimate_percent && (
                <div>
                  <div className="text-sm text-gray-600 mb-1">Оценка ROI</div>
                  <div className="text-3xl font-bold text-success-600">
                    +{indices.roi_estimate_percent.toFixed(0)}%
                  </div>
                </div>
              )}
              {indices?.tco_estimate_millions && (
                <div>
                  <div className="text-sm text-gray-600 mb-1">Оценка TCO</div>
                  <div className="text-2xl font-bold text-gray-900">
                    {indices.tco_estimate_millions.toFixed(1)} млн ₽
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        <div className="card mb-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Детализация по осям</h2>
          <div className="space-y-4">
            {Object.entries(indices?.dimension_scores || {}).map(([dimId, score]: [string, any]) => {
              const dimensionNames: Record<string, string> = {
                '1': 'Strategy & Vision',
                '2': 'Data & Analytics',
                '3': 'Technology & Infrastructure',
                '4': 'Processes & Operations',
                '5': 'People & Skills',
                '6': 'Culture & Change',
                '7': 'Ethics & Governance',
              };
              const scoreNum = typeof score === 'number' ? score : parseFloat(score);
              return (
                <div key={dimId}>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="font-medium text-gray-700">
                      {dimensionNames[dimId] || `Dimension ${dimId}`}
                    </span>
                    <span className="font-bold text-gray-900">{scoreNum.toFixed(2)}</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-primary-600 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${(scoreNum / 5) * 100}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Button onClick={handleSendEmail} variant="secondary">
            📧 Получить отчёт на email
          </Button>
          <Button onClick={handleRestart}>
            🔄 Начать заново
          </Button>
        </div>

        <p className="text-center text-sm text-gray-500 mt-8">
          ✨ Спасибо за участие! Ваши данные анонимизированы и используются только для бенчмаркинга.
        </p>
      </div>
    </div>
  );
}