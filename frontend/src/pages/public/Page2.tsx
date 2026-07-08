import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useMutation } from '@tanstack/react-query';
import { Button } from '@/components/ui/Button';
import { Slider } from '@/components/ui/Slider';
import { useAuditStore } from '@/store/auditStore';
import { publicApi } from '@/services/api';
import { DIMENSIONS } from '@/utils/constants';

export default function Page2() {
  const navigate = useNavigate();
  const { companyProfile, contactInfo, rawResponses, setRawResponse, setResults } = useAuditStore();
  const [currentDimension, setCurrentDimension] = useState(0);
  const [startTime] = useState(Date.now());

  // Инициализация store при первом рендере
  useEffect(() => {
    if (companyProfile && contactInfo && rawResponses.length === 0) {
      // Заполняем все 35 вопросов дефолтными значениями
      for (let dimId = 1; dimId <= 7; dimId++) {
        for (let qId = 1; qId <= 5; qId++) {
          setRawResponse(dimId, qId, 3);
        }
      }
    }
  }, [companyProfile, contactInfo, rawResponses.length, setRawResponse]);

  const mutation = useMutation({
    mutationFn: publicApi.createExpressAudit,
    onSuccess: (data) => {
      setResults(data.audit_id, data.calculated_indices);
      navigate(`/results/${data.audit_id}`);
    },
    onError: (error: any) => {
      console.error('Audit creation failed:', error);
      const msg = error?.response?.data?.error?.message || error?.message || 'Неизвестная ошибка';
      alert(`Ошибка при создании аудита: ${msg}`);
    },
  });

  if (!companyProfile || !contactInfo) {
    navigate('/');
    return null;
  }

  const dimension = DIMENSIONS[currentDimension];
  const progress = ((currentDimension + 1) / DIMENSIONS.length) * 100;

  const handleNext = () => {
    if (currentDimension < DIMENSIONS.length - 1) {
      setCurrentDimension(currentDimension + 1);
    } else {
      // Проверяем что все 35 ответов есть
      if (rawResponses.length !== 35) {
        alert(`Заполнены ${rawResponses.length} из 35 вопросов. Пожалуйста, ответьте на все вопросы.`);
        return;
      }

      mutation.mutate({
        company_profile: companyProfile,
        contact: contactInfo,
        raw_responses: rawResponses.map(r => ({
          ...r,
          time_to_answer_sec: (Date.now() - startTime) / 1000,
          confidence_level: r.confidence_level || 3,
        })),
      });
    }
  };

  const handlePrev = () => {
    if (currentDimension > 0) {
      setCurrentDimension(currentDimension - 1);
    } else {
      navigate('/');
    }
  };

  const getScore = (questionId: number): number => {
    const response = rawResponses.find(
      (r) => r.dimension_id === dimension.id && r.question_id === questionId
    );
    return response?.score || 3;
  };

  // Считаем сколько ответов на текущей оси
  const currentDimensionResponses = rawResponses.filter(
    (r) => r.dimension_id === dimension.id
  ).length;

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-secondary-50 py-12 px-4">
      <div className="max-w-3xl mx-auto">
        {/* Progress bar */}
        <div className="mb-8">
          <div className="flex justify-between text-sm text-gray-600 mb-2">
            <span>Ось {currentDimension + 1} из {DIMENSIONS.length} ({currentDimensionResponses}/5)</span>
            <span>{Math.round(progress)}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-primary-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>

        {/* Dimension card */}
        <div className="card">
          <div className="mb-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-2">
              {dimension.name}
            </h2>
            <p className="text-gray-600">{dimension.description}</p>
          </div>

          <div className="space-y-8">
            {dimension.questions.map((question) => (
              <div key={question.id} className="border-b border-gray-200 pb-6 last:border-0">
                <Slider
                  label={question.text}
                  description={question.description}
                  value={getScore(question.id)}
                  onChange={(score) => {
                    setRawResponse(dimension.id, question.id, score);
                    console.log(`D${dimension.id} Q${question.id} = ${score} (Total: ${rawResponses.length}/35)`);
                  }}
                />
              </div>
            ))}
          </div>

          <div className="flex justify-between mt-8">
            <Button variant="secondary" onClick={handlePrev}>
              ← Назад
            </Button>

            <Button onClick={handleNext} disabled={mutation.isPending}>
              {mutation.isPending
                ? 'Обработка...'
                : currentDimension === DIMENSIONS.length - 1
                ? 'Завершить ✓'
                : 'Далее →'}
            </Button>
          </div>
        </div>

        {/* Отладочная информация */}
        <div className="mt-4 text-xs text-gray-500 text-center">
          Всего ответов: {rawResponses.length} / 35
        </div>
      </div>
    </div>
  );
}