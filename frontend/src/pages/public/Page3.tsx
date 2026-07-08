import { useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/Button';
import { RadarChart } from '@/components/charts/RadarChart';
import { useAuditStore } from '@/store/auditStore';
import { publicApi } from '@/services/api';

export default function Page3() {
  const { auditId } = useParams<{ auditId: string }>();
  const navigate = useNavigate();
  const { calculatedIndices, auditId: storedAuditId } = useAuditStore();

  useEffect(() => {
    if (!auditId || (!calculatedIndices && auditId !== storedAuditId)) {
      navigate('/');
    }
  }, [auditId, calculatedIndices, storedAuditId, navigate]);

  if (!calculatedIndices) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Загрузка результатов...</p>
        </div>
      </div>
    );
  }

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

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-secondary-50 py-12 px-4">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-3">
            Ваши результаты
          </h1>
          <p className="text-lg text-gray-600">
            ID аудита: <span className="font-mono text-sm">{auditId?.slice(0, 8)}...</span>
          </p>
        </div>

        {/* Main results card */}
        <div className="card mb-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {/* Radar chart */}
            <div>
              <RadarChart dimensionScores={calculatedIndices.dimension_scores} />
            </div>

            {/* Key metrics */}
            <div className="space-y-6">
              <div>
                <div className="text-sm text-gray-600 mb-1">Комплексная оценка</div>
                <div className="text-5xl font-bold text-primary-600">
                  {calculatedIndices.composite_score.toFixed(2)}
                  <span className="text-2xl text-gray-400"> / 5.00</span>
                </div>
              </div>

              <div>
                <div className="text-sm text-gray-600 mb-1">Уровень зрелости</div>
                <div className="text-2xl font-bold text-gray-900">
                  {calculatedIndices.maturity_level}
                </div>
              </div>

	      {calculatedIndices.roi_estimate_percent && (
                <div>
                  <div className="text-sm text-gray-600 mb-1">Оценка ROI</div>
                  <div className="text-3xl font-bold text-success-600">
                    +{calculatedIndices.roi_estimate_percent.toFixed(0)}%
                  </div>
                </div>
              )}

              {calculatedIndices.tco_estimate_millions && (
                <div>
                  <div className="text-sm text-gray-600 mb-1">Оценка TCO</div>
                  <div className="text-2xl font-bold text-gray-900">
                    {calculatedIndices.tco_estimate_millions.toFixed(1)} млн ₽
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Dimension breakdown */}
        <div className="card mb-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Детализация по осям</h2>
          <div className="space-y-4">
            {Object.entries(calculatedIndices.dimension_scores).map(([dimId, score]) => {
              const dimensionNames: Record<string, string> = {
                '1': 'Strategy & Vision',
                '2': 'Data & Analytics',
                '3': 'Technology & Infrastructure',
                '4': 'Processes & Operations',
                '5': 'People & Skills',
                '6': 'Culture & Change',
                '7': 'Ethics & Governance',
              };

              return (
                <div key={dimId}>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="font-medium text-gray-700">
                      {dimensionNames[dimId] || `Dimension ${dimId}`}
                    </span>
                    <span className="font-bold text-gray-900">{score.toFixed(2)}</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-primary-600 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${(score / 5) * 100}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Action buttons */}
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