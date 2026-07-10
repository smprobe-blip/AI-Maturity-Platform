import { useEffect, useState, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/Button';
import { RadarChart } from '@/components/charts/RadarChart';
import { useAuditStore } from '@/store/auditStore';
import { publicApi } from '@/services/api';
import { REPORT_TYPES } from '@/types';

export default function Page3() {
  const { auditId } = useParams<{ auditId: string }>();
  const navigate = useNavigate();
  const { calculatedIndices, setResults } = useAuditStore();
  const [auditData, setAuditData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  
  // Ref для предотвращения повторной загрузки
  const loadedAuditIdRef = useRef<string | null>(null);

  useEffect(() => {
    // Если уже загрузили этот аудит - не загружаем снова
    if (!auditId || loadedAuditIdRef.current === auditId) {
      return;
    }

    const loadResults = async () => {
      try {
        setLoading(true);
        setError('');
        
        const data = await publicApi.getAudit(auditId);
        setAuditData(data);
        
        // Сохраняем в store
        if (data.calculated_indices) {
          setResults(auditId, data.calculated_indices);
        }
        
        // Помечаем как загруженный
        loadedAuditIdRef.current = auditId;
        setLoading(false);
      } catch (err) {
        console.error('Failed to load audit:', err);
        setError('Не удалось загрузить результаты аудита');
        setLoading(false);
        
        // Если ошибка - редирект через 3 сек
        setTimeout(() => navigate('/'), 3000);
      }
    };

    loadResults();
    
    // Cleanup
    return () => {
      // Можно добавить очистку если нужно
    };
  }, [auditId]); // ТОЛЬКО auditId в зависимостях!

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

  if (error && !calculatedIndices) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="text-danger-600 text-xl mb-4">{error}</div>
          <Button onClick={() => navigate('/')}>
            На главную
          </Button>
        </div>
      </div>
    );
  }

  // Используем данные из API или из store
  const indices = auditData?.calculated_indices || calculatedIndices;
  if (!indices) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="text-gray-600 mb-4">Нет данных для отображения</div>
          <Button onClick={() => navigate('/')}>
            Начать оценку
          </Button>
        </div>
      </div>
    );
  }

  const reportType = auditData?.report_type || 'express';
  const selectedReport = REPORT_TYPES.find((r) => r.value === reportType) || REPORT_TYPES[0];

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-secondary-50 py-12 px-4">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-3">
            Ваши результаты
          </h1>
          <p className="text-lg text-gray-600">
            ID аудита: <span className="font-mono text-sm">{auditId?.slice(0, 8)}...</span>
            {' · '}
            Вариант: <strong>{selectedReport.label}</strong>
          </p>
        </div>

        {/* Main results card */}
        <div className="card mb-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {/* Radar chart */}
            <div>
              <RadarChart dimensionScores={indices.dimension_scores} />
            </div>
            
            {/* Key metrics */}
            <div className="space-y-6">
              <div>
                <div className="text-sm text-gray-600 mb-1">Комплексная оценка</div>
                <div className="text-5xl font-bold text-primary-600">
                  {indices.composite_score.toFixed(2)}
                  <span className="text-2xl text-gray-400"> / 5.00</span>
                </div>
              </div>
              
              <div>
                <div className="text-sm text-gray-600 mb-1">Уровень зрелости</div>
                <div className="text-2xl font-bold text-gray-900">
                  {indices.maturity_level}
                </div>
              </div>
              
              {indices.roi_estimate_percent && (
                <div>
                  <div className="text-sm text-gray-600 mb-1">Оценка ROI</div>
                  <div className="text-3xl font-bold text-success-600">
                    +{indices.roi_estimate_percent.toFixed(0)}%
                  </div>
                </div>
              )}
              
              {indices.tco_estimate_millions && (
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

        {/* Dimension breakdown */}
        <div className="card mb-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Детализация по осям</h2>
          <div className="space-y-4">
            {Object.entries(indices.dimension_scores).map(([dimId, score]) => {
              const dimensionNames: Record<string, string> = {
                '1': 'Стратегия и управление',
                '2': 'Данные и аналитика',
                '3': 'Технологии и инфраструктура',
                '4': 'Процессы и операции',
                '5': 'Люди и навыки',
                '6': 'Культура и изменения',
                '7': 'Этика и управление',
              };
              const scoreNum = typeof score === 'number' ? score : parseFloat(score);
              return (
                <div key={dimId}>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="font-medium text-gray-700">
                      {dimensionNames[dimId] || `Ось ${dimId}`}
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

        {/* Recommendations */}
        {auditData?.recommendations && auditData.recommendations.length > 0 && (
          <div className="card mb-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">💡 Рекомендации</h2>
            <ul className="space-y-2">
              {auditData.recommendations.map((r: string, i: number) => (
                <li key={i} className="flex gap-2 text-gray-700">
                  <span className="text-primary-600">•</span>
                  <span>{r}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

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