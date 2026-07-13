import { useEffect, useState, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/Button';
import { RadarChart } from '@/components/charts/RadarChart';
import { Speedometer } from '@/components/charts/Speedometer';
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
  const loadedRef = useRef<string | null>(null);

  useEffect(() => {
    if (!auditId) {
      navigate('/');
      return;
    }

    if (loadedRef.current === auditId) {
      return;
    }

    let cancelled = false;

    const loadResults = async () => {
      setLoading(true);
      setError('');

      try {
        const data = await publicApi.getAudit(auditId);

        if (cancelled) return;

        setAuditData(data);

        if (data.calculated_indices) {
          setResults(auditId, data.calculated_indices);
        }

        loadedRef.current = auditId;
        setLoading(false);
      } catch (err) {
        if (cancelled) return;

        console.error('Failed to load audit:', err);
        setError('Не удалось загрузить результаты аудита');
        setLoading(false);

        if (!calculatedIndices) {
          setTimeout(() => navigate('/'), 3000);
        }
      }
    };

    loadResults();

    return () => {
      cancelled = true;
    };
  }, [auditId]);

  const handleSendEmail = async () => {
    if (!auditId) return;
    const email = prompt('Введите ваш email для получения отчёта:');
    if (!email) return;
    try {
      await publicApi.sendAuditReport(auditId, email);
      alert('Отчёт отправлен на вашу почту!');
    } catch (err) {
      alert('Ошибка при отправке отчёта');
    }
  };

  const handleRestart = () => {
    if (confirm('Начать новую оценку? Текущие данные будут потеряны.')) {
      useAuditStore.getState().reset();
      navigate('/');
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

  if (error && !calculatedIndices && !auditData) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="text-red-600 text-xl mb-4">{error}</div>
          <Button onClick={() => navigate('/')}>На главную</Button>
        </div>
      </div>
    );
  }

  const indices = auditData?.calculated_indices || calculatedIndices;
  if (!indices) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="text-gray-600 mb-4">Нет данных для отображения</div>
          <Button onClick={() => navigate('/')}>Начать оценку</Button>
        </div>
      </div>
    );
  }

  const reportType = auditData?.report_type || 'express';
  const selectedReport = REPORT_TYPES.find((r) => r.value === reportType) || REPORT_TYPES[0];
  const pattern = indices.pattern;
  const top3Bottlenecks = indices.top3_bottlenecks || [];
  const top3Anchors = indices.top3_anchors || [];
  const upsellTriggers = auditData?.upsell_triggers || [];

  const patternSeverityColors: Record<string, string> = {
    critical: 'bg-red-50 border-red-300 text-red-900',
    warning: 'bg-yellow-50 border-yellow-300 text-yellow-900',
    info: 'bg-blue-50 border-blue-300 text-blue-900',
    success: 'bg-green-50 border-green-300 text-green-900',
  };

  const patternIcons: Record<string, string> = {
    critical: '🚨',
    warning: '⚠️',
    info: 'ℹ️',
    success: '✅',
  };

  const targetScores = indices.gap_analysis
    ? Object.fromEntries(
        Object.entries(indices.gap_analysis.dimension_gaps).map(([k, v]: [string, any]) => [k, v.target])
      )
    : undefined;

  const benchmarkScores = indices.benchmark_scores || undefined;

  const financialMetrics = indices.financial_metrics || {
    roi_percent: indices.roi_estimate_percent || 0,
    npv_millions: 0,
    payback_months: 0,
    confidence: 'medium',
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50 py-8 px-4">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="text-center mb-6">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Ваши результаты</h1>
          <p className="text-sm text-gray-600">
            ID аудита: <span className="font-mono">{auditId?.slice(0, 8)}...</span>
            {' · '}
            Вариант отчёта: <strong>{selectedReport.label}</strong>
          </p>
        </div>

        {/* Main radar + metrics card */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Radar Chart — легенда внутри SVG (в левом верхнем углу) */}
            <div>
              <h2 className="text-lg font-bold text-gray-900 mb-3">🎯 Радар зрелости</h2>
              <RadarChart
                dimensionScores={indices.dimension_scores}
                targetScores={targetScores}
                benchmarkScores={benchmarkScores}
                showGap={!!indices.gap_analysis}
              />
            </div>

            {/* Key metrics */}
            <div className="space-y-4">
              <div>
                <div className="text-sm text-gray-600 mb-1">Комплексная оценка</div>
                <div className="text-5xl font-bold text-blue-600">
                  {indices.composite_score.toFixed(2)}
                  <span className="text-2xl text-gray-400"> / 5.00</span>
                </div>
              </div>
              <div>
                <div className="text-sm text-gray-600 mb-1">Уровень зрелости</div>
                <div className="text-2xl font-bold text-gray-900">{indices.maturity_level}</div>
              </div>
              {indices.roi_estimate_percent !== undefined && indices.roi_estimate_percent !== null && (
                <div className="bg-green-50 border border-green-200 rounded-lg p-3">
                  <div className="text-sm text-gray-600 mb-1">Потенциал роста ROI</div>
                  <div className="text-3xl font-bold text-green-600">
                    +{indices.roi_estimate_percent.toFixed(0)}%
                  </div>
                  <div className="text-xs text-gray-500">при достижении целевого состояния</div>
                </div>
              )}
              {indices.tco_estimate_millions !== undefined && indices.tco_estimate_millions !== null && (
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

        {/* Financial Speedometer */}
        {(financialMetrics.npv_millions > 0 || financialMetrics.payback_months > 0) && (
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-6">
            <h2 className="text-lg font-bold text-gray-900 mb-3"> Финансовый потенциал</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <Speedometer
                roiPercent={financialMetrics.roi_percent}
                npvMillions={financialMetrics.npv_millions}
                paybackMonths={financialMetrics.payback_months}
                confidence={financialMetrics.confidence}
              />
              <div className="space-y-4">
                <div>
                  <div className="text-sm text-gray-600 mb-1">Чистая приведённая стоимость (NPV)</div>
                  <div className="text-3xl font-bold text-green-600">
                    +{financialMetrics.npv_millions.toFixed(1)} млн ₽
                  </div>
                  <div className="text-xs text-gray-500">за 3 года (ставка дисконтирования 15%)</div>
                </div>
                <div>
                  <div className="text-sm text-gray-600 mb-1">Срок окупаемости</div>
                  <div className="text-2xl font-bold text-gray-900">
                    {financialMetrics.payback_months} месяцев
                  </div>
                </div>
                <div>
                  <div className="text-sm text-gray-600 mb-1">Годовая выгода</div>
                  <div className="text-xl font-bold text-gray-900">
                    {financialMetrics.annual_benefit_millions?.toFixed(1) || '0'} млн ₽
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Pattern diagnosis */}
        {pattern && (
          <div className={'bg-white rounded-xl shadow-sm border-2 p-6 mb-6 ' + (patternSeverityColors[pattern.severity] || '')}>
            <div className="flex items-start gap-3">
              <div className="text-3xl">{patternIcons[pattern.severity] || '📊'}</div>
              <div className="flex-1">
                <h2 className="text-xl font-bold mb-2">Диагноз: {pattern.diagnosis}</h2>
                <p className="text-sm">{pattern.recommendation}</p>
              </div>
            </div>
          </div>
        )}

        {/* Top-3 bottlenecks & anchors */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h2 className="text-lg font-bold text-gray-900 mb-3 flex items-center gap-2">
              <span className="text-red-600">🔻</span>
              Топ-3 горлышка
            </h2>
            <div className="space-y-2">
              {top3Bottlenecks.length === 0 && (
                <p className="text-sm text-gray-500 italic">Нет критичных зон</p>
              )}
              {top3Bottlenecks.map((b: any, i: number) => (
                <div key={i} className="flex items-center gap-3 p-2 bg-gray-50 rounded">
                  <div className="text-2xl font-bold text-gray-400">#{i + 1}</div>
                  <div className="flex-1">
                    <div className="font-medium text-gray-900">{b.dimension_name}</div>
                    <div className="text-xs text-gray-500">вес {Math.round(b.weight * 100)}%</div>
                  </div>
                  <div className={
                    'text-xl font-bold ' + (
                      b.severity === 'critical' ? 'text-red-600' :
                      b.severity === 'warning' ? 'text-yellow-600' :
                      'text-gray-600'
                    )
                  }>
                    {b.score.toFixed(1)}
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h2 className="text-lg font-bold text-gray-900 mb-3 flex items-center gap-2">
              <span className="text-green-600">🔺</span>
              Топ-3 якоря
            </h2>
            <div className="space-y-2">
              {top3Anchors.length === 0 && (
                <p className="text-sm text-gray-500 italic">Нет опорных точек</p>
              )}
              {top3Anchors.map((a: any, i: number) => (
                <div key={i} className="flex items-center gap-3 p-2 bg-gray-50 rounded">
                  <div className="text-2xl font-bold text-gray-400">#{i + 1}</div>
                  <div className="flex-1">
                    <div className="font-medium text-gray-900">{a.dimension_name}</div>
                    <div className="text-xs text-gray-500">вес {Math.round(a.weight * 100)}%</div>
                  </div>
                  <div className={
                    'text-xl font-bold ' + (
                      a.strength === 'strong' ? 'text-green-600' :
                      a.strength === 'moderate' ? 'text-blue-600' :
                      'text-gray-600'
                    )
                  }>
                    {a.score.toFixed(1)}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Upsell triggers */}
        {upsellTriggers.length > 0 && (
          <div className="bg-yellow-50 border border-yellow-200 rounded-xl shadow-sm p-6 mb-6">
            <h2 className="text-lg font-bold text-yellow-900 mb-3">💼 Рекомендуемые услуги</h2>
            <div className="space-y-3">
              {upsellTriggers.map((trigger: any, i: number) => (
                <div key={i} className="bg-white rounded-lg p-4 border border-yellow-200">
                  <div className="flex justify-between items-start mb-2">
                    <div className="font-bold text-gray-900">{trigger.service}</div>
                    <div className="text-sm font-semibold text-blue-600">{trigger.price_hint}</div>
                  </div>
                  <p className="text-sm text-gray-700 mb-2">
                    <strong className="text-red-600">Риск:</strong> {trigger.risk}
                  </p>
                  <p className="text-xs text-gray-500">
                    Ось «{trigger.dimension_name}» оценена на {trigger.score.toFixed(1)}/5
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Recommendations */}
        {auditData?.recommendations && auditData.recommendations.length > 0 && (
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">💡 Рекомендации</h2>
            <ul className="space-y-2">
              {auditData.recommendations.map((r: string, i: number) => (
                <li key={i} className="flex gap-2 text-gray-700">
                  <span className="text-blue-600">•</span>
                  <span>{r}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* CTA based on report type */}
        <div className="bg-blue-50 border border-blue-200 rounded-xl shadow-sm p-6 mb-6 text-center">
          <h3 className="text-lg font-bold text-blue-900 mb-2">
            Следующий шаг: {selectedReport.cta}
          </h3>
          <p className="text-sm text-blue-700 mb-4">
            {reportType === 'express' && 'Запишитесь на 30-минутный разбор результатов с экспертом'}
            {reportType === 'executive' && 'Получите шаблон AI Governance Canvas для обоснования бюджета'}
            {reportType === 'comprehensive' && 'Обсудите запуск Центра ИИ-компетенций в вашей компании'}
          </p>
          <Button size="lg" onClick={handleSendEmail}>
            📧 Получить полный отчёт на email
          </Button>
        </div>

        {/* Action buttons */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Button onClick={handleRestart} variant="secondary">
            🔄 Начать заново
          </Button>
        </div>

        <p className="text-center text-sm text-gray-500 mt-6">
          ✨ Спасибо за участие! Ваши данные анонимизированы и используются только для бенчмаркинга.
        </p>
      </div>
    </div>
  );
}