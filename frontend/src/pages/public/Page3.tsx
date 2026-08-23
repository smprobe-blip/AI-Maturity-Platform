import { useEffect, useState, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/Button';
import { RadarChart } from '@/components/charts/RadarChart';
import { Speedometer } from '@/components/charts/Speedometer';
import { UpsellFunnel } from '@/components/UpsellFunnel';
import { useAuditStore } from '@/store/auditStore';
import { publicApi } from '@/services/api';
import { REPORT_TYPES } from '@/types';

const DIM_ORDER = ['1', '2', '3', '4', '5', '6', '7'];

const DIM_NAMES: Record<string, string> = {
  '1': 'Стратегия и управление',
  '2': 'Люди и культура',
  '3': 'Инфраструктура',
  '4': 'Данные',
  '5': 'Модели',
  '6': 'Внедрение ИИ',
  '7': 'Исследования (R&D)',
};

const bandPhrase = (s: number): string =>
  s <= 1.8 ? 'начальный уровень: нет системного подхода' :
  s <= 2.6 ? 'enabled: отдельные инициативы, но нет системы' :
  s <= 3.4 ? 'driven: процессы стандартизированы' :
  s <= 4.2 ? 'first: ИИ встроен в бизнес-процессы' :
  'native: ИИ — ядро бизнес-модели';

const ACTION_STEPS: Record<string, [string, string, string][]> = {
  '1': [
    ['Провести ИИ-стратегическую сессию с топ-менеджментом', 'CEO', '2 дня'],
    ['Утвердить роадмап на 12 мес с 3 измеримыми целями', 'Стратег-блок', '30 дней'],
    ['Закрепить ИИ-бюджет отдельной статьёй', 'CFO', '60 дней'],
  ],
  '2': [
    ['Назначить AI-чемпионов в каждом подразделении', 'HRD', '30 дней'],
    ['Запустить курс ИИ-грамотности для 20% сотрудников', 'L&D', '60 дней'],
    ['Включить ИИ-инициативы в KPI руководителей', 'CEO', '90 дней'],
  ],
  '3': [
    ['Провести аудит вычислительных ресурсов и облачных затрат', 'CTO', '30 дней'],
    ['Развернуть dev-среду для ИИ-пилотов', 'CTO', '60 дней'],
    ['Утвердить политику безопасности ИИ-инструментов', 'CISO', '90 дней'],
  ],
  '4': [
    ['Определить топ-3 самых ценных дата-активов', 'CDO', '30 дней'],
    ['Назначить владельцев данных и метрики качества', 'CDO', '60 дней'],
    ['Построить пилотный пайплайн с мониторингом качества', 'Data Lead', '90 дней'],
  ],
  '5': [
    ['Выбрать 2–3 use case с быстрым измеримым эффектом', 'AI Lead', '30 дней'],
    ['Построить baseline-модель или выбрать vendor-решение', 'AI Lead', '60 дней'],
    ['Настроить мониторинг точности и дрейфа', 'MLOps', '90 дней'],
  ],
  '6': [
    ['Запустить 2–3 ИИ-пилота с бизнес-владельцами', 'Бизнес-владелец', '6–8 нед.'],
    ['Определить критерии успеха пилотов в деньгах/времени', 'CEO', '30 дней'],
    ['Внедрить ежемесячное ревью ИИ-инициатив', 'CEO', 'постоянно'],
  ],
  '7': [
    ['Установить партнёрство с 1–2 университетами', 'R&D Lead', '60 дней'],
    ['Подать заявку на 1 грант в квартал', 'R&D Lead', 'ежеквартально'],
    ['Публиковать 1 кейс/статью в полугодие', 'R&D + Marketing', '6 мес'],
  ],
};

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

  const planPriorities = DIM_ORDER
    .map((id) => ({ id, score: Number(indices.dimension_scores?.[id] ?? 0) }))
    .sort((a, b) => a.score - b.score)
    .slice(0, 3);

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
              {pattern && (
                <div className={'rounded-lg border-2 p-3 ' + (patternSeverityColors[pattern.severity] || '')}>
                  <div className="flex items-start gap-2">
                    <div className="text-xl">{patternIcons[pattern.severity] || '📊'}</div>
                    <div>
                      <div className="font-bold mb-1">Диагноз: {pattern.diagnosis}</div>
                      <p className="text-xs">{pattern.recommendation}</p>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Анализ по 7 осям зрелости */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-6">
          <h2 className="text-lg font-bold text-gray-900 mb-3">📊 Анализ по 7 осям зрелости</h2>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-xs text-gray-500 uppercase border-b border-gray-200">
                  <th className="py-2 pr-2">Ось</th>
                  <th className="py-2 pr-2">Балл</th>
                  <th className="py-2 pr-2">Бенчмарк</th>
                  <th className="py-2 pr-2">Разрыв</th>
                  <th className="py-2">Интерпретация</th>
                </tr>
              </thead>
              <tbody>
                {DIM_ORDER.map((id) => {
                  const s = Number(indices.dimension_scores?.[id] ?? 0);
                  const b = benchmarkScores ? Number(benchmarkScores[id] ?? 0) : null;
                  const gap = b !== null ? s - b : null;
                  let interp = bandPhrase(s);
                  if (gap !== null) {
                    interp += gap < -0.4 ? '; ниже среднего по отрасли' : gap > 0.4 ? '; выше среднего по отрасли' : '; вблизи среднего';
                  }
                  return (
                    <tr key={id} className="border-b border-gray-100">
                      <td className="py-2 pr-2 font-medium text-gray-900">{DIM_NAMES[id]}</td>
                      <td className="py-2 pr-2 font-bold text-gray-900">{s.toFixed(1)}</td>
                      <td className="py-2 pr-2 text-gray-600">{b !== null ? b.toFixed(1) : '—'}</td>
                      <td className={'py-2 pr-2 font-semibold ' + (gap !== null && gap < 0 ? 'text-red-600' : 'text-green-600')}>
                        {gap !== null ? (gap > 0 ? '+' : '') + gap.toFixed(1) : '—'}
                      </td>
                      <td className="py-2 text-xs text-gray-600">{interp}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
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

        {/* План действий на 90 дней (вместо рекомендуемых услуг) */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-6">
          <h2 className="text-lg font-bold text-gray-900 mb-1">🗓️ План действий на 90 дней</h2>
          <p className="text-sm text-gray-600 mb-4">
            Три приоритета — оси с наименьшими оценками. По каждому: конкретные шаги, владелец и срок.
          </p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {planPriorities.map((p, n) => (
              <div key={p.id} className="bg-gray-50 rounded-lg p-4 border border-gray-200">
                <div className="font-bold text-gray-900 mb-2 text-sm">
                  Приоритет {n + 1}: {DIM_NAMES[p.id]} ({p.score.toFixed(1)}/5)
                </div>
                <ol className="space-y-2 list-decimal list-inside">
                  {(ACTION_STEPS[p.id] || []).map(([what, owner, term], i) => (
                    <li key={i} className="text-xs text-gray-700">
                      <strong>{what}</strong>
                      <div className="text-gray-500">{owner} · {term}</div>
                    </li>
                  ))}
                </ol>
              </div>
            ))}
          </div>
          <div className="mt-4 text-xs text-green-800 bg-green-50 border border-green-200 rounded-lg px-3 py-2">
            <strong>Как измерять успех:</strong> по каждому шагу зафиксируйте метрику до старта
            (число пилотов в проде, доля обученных сотрудников, доля утверждённого бюджета)
            и сверяйтесь ежемесячно.
          </div>
        </div>

        {/* Recommendations (скрыто: дублирует план действий) */}
        {false && auditData?.recommendations && auditData.recommendations.length > 0 && (
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

        
        {/* Upsell Funnel */}
        {upsellTriggers.length > 0 && (
          <UpsellFunnel triggers={upsellTriggers} auditId={auditId} />
        )}

        {/* Action buttons */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <a 
            href={`/api/v1/public/audits/${auditId}/pdf`} 
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center justify-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-white bg-red-600 hover:bg-red-700 shadow-sm transition-colors"
          >
            📄 Скачать PDF-отчёт
          </a>
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