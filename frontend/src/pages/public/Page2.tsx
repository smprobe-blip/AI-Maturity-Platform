import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/Button';
import { useAuditStore } from '@/store/auditStore';
import { publicApi } from '@/services/api';
import { DIMENSIONS } from '@/types';

export default function Page2() {
  const navigate = useNavigate();
  const { profile, responses, setQuestionScore, setTargetScores, setResults, targetScores } = useAuditStore();
  const [activeDimension, setActiveDimension] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showTarget, setShowTarget] = useState(false);
  const [localTargets, setLocalTargets] = useState<Record<string, number>>(
    targetScores || {}
  );

  if (!profile) {
    navigate('/');
    return null;
  }

  const getDimensionScore = (dimId: string): number => {
    const dimResponses = responses[dimId] || {};
    const scores = Object.values(dimResponses);
    if (scores.length === 0) return 0;
    return scores.reduce((a, b) => a + b, 0) / scores.length;
  };

  const isDimensionComplete = (dimId: string): boolean => {
    const dim = DIMENSIONS.find((d) => d.id === dimId);
    if (!dim) return false;
    const dimResponses = responses[dimId] || {};
    return dim.questions.every((q) => dimResponses[q.id] !== undefined && dimResponses[q.id] > 0);
  };

  const allComplete = DIMENSIONS.every((d) => isDimensionComplete(d.id));
  const completedCount = DIMENSIONS.filter((d) => isDimensionComplete(d.id)).length;

  const handleQuestionChange = (dimId: string, qId: string, value: number) => {
    setQuestionScore(dimId, qId, value);
  };

  const handleTargetChange = (dimId: string, value: number) => {
    setLocalTargets({ ...localTargets, [dimId]: value });
  };

  const handleSubmit = async () => {
    if (!allComplete || !profile) return;
    setLoading(true);
    setError('');
    try {
      if (showTarget) {
        setTargetScores(localTargets);
      }
      const result = await publicApi.createAudit({
        company_industry: profile.industry,
        company_size: profile.size,
        contact_email: profile.email,
        contact_name: profile.name,
        report_type: profile.reportType,
        responses,
        target_scores: showTarget ? localTargets : undefined,
        pdn_consent: true,
      });
      setResults(result.audit_id, result.calculated_indices);
      navigate('/results/' + result.audit_id);
    } catch (err) {
      console.error(err);
      setError('Не удалось сохранить результаты. Попробуйте ещё раз.');
    } finally {
      setLoading(false);
    }
  };

  const getZoneColor = (score: number): string => {
    if (score === 0) return 'bg-gray-100 border-gray-200';
    if (score < 1.9) return 'bg-red-50 border-red-300';
    if (score < 2.7) return 'bg-yellow-50 border-yellow-300';
    if (score < 3.5) return 'bg-green-50 border-green-300';
    if (score < 4.3) return 'bg-blue-50 border-blue-300';
    return 'bg-purple-50 border-purple-300';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-secondary-50 py-8 px-4">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-6">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Оцените вашу компанию
          </h1>
          <p className="text-gray-600">
            Кликните на ось для детальной оценки по 5 подкритериям
          </p>
          <div className="mt-3 flex items-center justify-center gap-6 text-sm flex-wrap">
            <span className="text-gray-600 font-medium">
              Прогресс: <strong>{completedCount} / {DIMENSIONS.length}</strong> осей
            </span>
            <label className="flex items-center gap-2 cursor-pointer bg-white px-3 py-1.5 rounded-lg border border-gray-200 hover:border-primary-300 transition-colors">
              <input
                type="checkbox"
                checked={showTarget}
                onChange={(e) => setShowTarget(e.target.checked)}
                className="h-4 w-4 text-primary-600 rounded"
              />
              <span className="text-gray-700">Указать целевое состояние</span>
            </label>
          </div>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-3 mb-6">
          {DIMENSIONS.map((dim) => {
            const score = getDimensionScore(dim.id);
            const complete = isDimensionComplete(dim.id);
            const isActive = activeDimension === dim.id;
            const zoneColor = getZoneColor(score);

            return (
              <button
                key={dim.id}
                onClick={() => setActiveDimension(isActive ? null : dim.id)}
                className={'relative p-3 rounded-lg border-2 transition-all ' + (
                  isActive
                    ? 'border-primary-600 shadow-lg scale-105 bg-white'
                    : complete
                    ? zoneColor + ' hover:shadow-md'
                    : 'bg-white border-gray-200 hover:border-gray-300 hover:shadow-sm'
                )}
              >
                <div className="text-xs font-bold text-gray-500 mb-1">
                  {dim.id}. {dim.shortName}
                </div>
                <div className="text-2xl font-bold text-gray-900">
                  {score > 0 ? score.toFixed(1) : '—'}
                </div>
                <div className="text-xs text-gray-500 mt-1">
                  вес {Math.round(dim.weight * 100)}%
                </div>
                {complete && (
                  <div className="absolute top-1 right-1 text-green-600 text-sm font-bold">✓</div>
                )}
                {isActive && (
                  <div className="absolute -bottom-1 left-1/2 -translate-x-1/2 w-2 h-2 bg-primary-600 rounded-full"></div>
                )}
              </button>
            );
          })}
        </div>

        {activeDimension && (
          <div className="card mb-6 border-2 border-primary-300 shadow-lg">
            {(() => {
              const dim = DIMENSIONS.find((d) => d.id === activeDimension);
              if (!dim) return null;

              return (
                <div>
                  <div className="flex justify-between items-start mb-4 pb-4 border-b border-gray-100">
                    <div>
                      <h2 className="text-xl font-bold text-gray-900">
                        {dim.id}. {dim.name}
                      </h2>
                      <p className="text-sm text-gray-600 mt-1">{dim.description}</p>
                    </div>
                    <Button
                      variant="secondary"
                      size="sm"
                      onClick={() => setActiveDimension(null)}
                    >
                      Закрыть
                    </Button>
                  </div>

                  <div className="space-y-5">
                    {dim.questions.map((q) => {
                      const currentValue = responses[dim.id]?.[q.id] ?? 0;
                      const roundedValue = Math.round(currentValue);
                      const descriptor = roundedValue >= 1 && roundedValue <= 5
                        ? q.descriptors[roundedValue as 1 | 2 | 3 | 4 | 5]
                        : 'Выберите уровень';

                      return (
                        <div key={q.id} className="border-b border-gray-100 pb-5 last:border-0 last:pb-0">
                          <div className="flex justify-between items-start mb-3">
                            <div className="flex-1">
                              <div className="font-semibold text-gray-900">
                                Q{q.id}. {q.text}
                              </div>
                            </div>
                            <div className="text-2xl font-bold text-primary-600 min-w-[3rem] text-right">
                              {currentValue > 0 ? currentValue.toFixed(1) : '—'}
                            </div>
                          </div>

                          <div className="flex flex-wrap gap-1.5 mb-2">
                            {[1, 2, 3, 4, 5].map((level) => {
                              const isActive = roundedValue === level && currentValue > 0;
                              return (
                                <button
                                  key={level}
                                  type="button"
                                  onClick={() => handleQuestionChange(dim.id, q.id, level)}
                                  className={'px-2.5 py-1 text-xs rounded-full transition-all ' + (
                                    isActive
                                      ? 'bg-primary-600 text-white font-bold shadow-sm'
                                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                                  )}
                                  title={q.descriptors[level as 1 | 2 | 3 | 4 | 5]}
                                >
                                  {level}
                                </button>
                              );
                            })}
                          </div>

                          <div className={'text-sm italic mb-3 px-3 py-2 rounded-lg ' + (
                            currentValue > 0
                              ? 'bg-primary-50 text-primary-900 border-l-4 border-primary-500'
                              : 'bg-gray-50 text-gray-500 border-l-4 border-gray-300'
                          )}>
                            {currentValue > 0 && (
                              <span className="font-semibold not-italic">
                                Уровень {roundedValue}:
                              </span>
                            )}{' '}
                            {descriptor}
                          </div>

                          <input
                            type="range"
                            min={1}
                            max={5}
                            step={0.5}
                            value={currentValue > 0 ? currentValue : 3}
                            onChange={(e) => handleQuestionChange(dim.id, q.id, parseFloat(e.target.value))}
                            className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-primary-600"
                          />
                          <div className="flex justify-between text-xs text-gray-400 mt-1">
                            <span>1 — {q.descriptors[1]}</span>
                            <span>5 — {q.descriptors[5]}</span>
                          </div>

                          {showTarget && (
                            <div className="mt-3 pt-3 border-t border-dashed border-gray-200">
                              <label className="text-xs font-semibold text-green-700 flex items-center gap-1">
                                Целевое состояние через 12 мес.:
                              </label>
                              <div className="flex items-center gap-3 mt-2">
                                <input
                                  type="range"
                                  min={1}
                                  max={5}
                                  step={0.5}
                                  value={localTargets[dim.id] ?? currentValue ?? 3}
                                  onChange={(e) => handleTargetChange(dim.id, parseFloat(e.target.value))}
                                  className="flex-1 h-1.5 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-green-600"
                                />
                                <span className="text-sm font-bold text-green-600 min-w-[2.5rem] text-right">
                                  {(localTargets[dim.id] ?? currentValue ?? 3).toFixed(1)}
                                </span>
                              </div>
                            </div>
                          )}
                        </div>
                      );
                    })}
                  </div>

                  <div className="mt-5 pt-4 border-t border-gray-200 flex justify-between items-center">
                    <div className="text-sm text-gray-600">
                      Средний балл по оси:{' '}
                      <span className="font-bold text-gray-900">
                        {getDimensionScore(dim.id) > 0 ? getDimensionScore(dim.id).toFixed(2) : '—'}
                      </span>
                    </div>
                    <Button onClick={() => setActiveDimension(null)}>
                      Зафиксировать блок
                    </Button>
                  </div>
                </div>
              );
            })()}
          </div>
        )}

        {error && (
          <div className="mb-4 bg-danger-50 border border-danger-200 text-danger-700 px-4 py-3 rounded-lg">
            {error}
          </div>
        )}

        <div className="flex gap-4">
          <Button variant="secondary" onClick={() => navigate('/')}>
            Назад
          </Button>
          <Button
            onClick={handleSubmit}
            disabled={!allComplete || loading}
            className="flex-1"
            size="lg"
          >
            {loading ? 'Отправка...' : 'Получить результаты (' + completedCount + '/' + DIMENSIONS.length + ')'}
          </Button>
        </div>

        {!activeDimension && completedCount < DIMENSIONS.length && (
          <div className="mt-6 text-center text-sm text-gray-500 bg-white rounded-lg p-4 border border-gray-200">
            <strong>Подсказка:</strong> Кликните на любую ось выше, чтобы открыть панель с 5 вопросами.
          </div>
        )}
      </div>
    </div>
  );
}