import { useState } from 'react';

interface UpsellTrigger {
  dimension_name: string;
  score: number;
  risk: string;
  service: string;
  price_hint: string;
  duration: string;
  deliverables: string[];
  case_study: string;
}

interface UpsellFunnelProps {
  triggers: UpsellTrigger[];
  auditId: string;
}

export function UpsellFunnel({ triggers, auditId }: UpsellFunnelProps) {
  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState({ name: '', email: '', phone: '' });
  const [submitted, setSubmitted] = useState(false);

  if (!triggers || triggers.length === 0) return null;

  // Фокусируемся на самом критичном триггере (первый в списке, так как они отсортированы по score)
  const trigger = triggers[0];

  const steps = [
    { id: 1, label: 'Диагноз' },
    { id: 2, label: 'Решение' },
    { id: 3, label: 'Результаты' },
    { id: 4, label: 'Заявка' },
  ];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await fetch(`/api/v1/public/audits/${auditId}/service-request`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: formData.name,
          email: formData.email,
          phone: formData.phone,
          service: trigger.service,
        }),
      });
      
      if (response.ok) {
        setSubmitted(true);
        console.log('Lead created successfully');
      } else {
        console.error('Failed to create lead:', await response.text());
        alert('Ошибка при отправке заявки. Попробуйте позже.');
      }
    } catch (error) {
      console.error('Network error:', error);
      alert('Ошибка сети. Проверьте подключение.');
    }
  };

  return (
    <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl shadow-lg border border-blue-100 p-6 mb-6">
      <div className="flex items-center gap-2 mb-4 flex-wrap">
        <span className="text-2xl"></span>
        <h2 className="text-xl font-bold text-gray-900">Персональный план развития</h2>
        <span className="inline-flex items-center gap-1 rounded-full border border-amber-200 bg-amber-100 px-2.5 py-1 text-xs font-semibold text-amber-700">
          🔧 В разработке
        </span>
      </div>
      <p className="text-xs text-amber-700 bg-amber-50 border border-amber-200 rounded-lg px-3 py-2 mb-6">
        🚧 Блок находится в разработке — запрос персонального плана станет доступен в следующем релизе.
      </p>

      {/* Progress Bar */}
      <div className="flex items-center justify-between mb-8 relative">
        <div className="absolute top-1/2 left-0 w-full h-1 bg-gray-200 -z-10 transform -translate-y-1/2"></div>
        {steps.map((s) => (
          <div key={s.id} className="flex flex-col items-center bg-blue-50 px-2">
            <div
              className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm transition-all ${
                step >= s.id ? 'bg-blue-600 text-white' : 'bg-gray-300 text-gray-600'
              }`}
            >
              {s.id}
            </div>
            <span className={`text-xs mt-1 font-medium ${step >= s.id ? 'text-blue-700' : 'text-gray-500'}`}>
              {s.label}
            </span>
          </div>
        ))}
      </div>

      {/* Content */}
      <div className="min-h-[250px]">
        {step === 1 && (
          <div className="animate-fadeIn">
            <h3 className="text-lg font-bold text-gray-900 mb-3">
              Зона роста: <span className="text-red-600">{trigger.dimension_name}</span>
            </h3>
            <div className="bg-white rounded-lg p-4 border-l-4 border-red-500 mb-4">
              <p className="text-gray-700">
                Текущая оценка: <strong>{trigger.score.toFixed(1)} / 5.0</strong>
              </p>
              <p className="text-gray-600 mt-2 text-sm">{trigger.risk}</p>
            </div>
            <p className="text-gray-600 text-sm">
              Без укрепления этого фундамента масштабирование ИИ-инициатив будет неэффективным и рискованным.
            </p>
          </div>
        )}

        {step === 2 && (
          <div className="animate-fadeIn">
            <h3 className="text-lg font-bold text-gray-900 mb-3">Наше решение: {trigger.service}</h3>
            <div className="grid grid-cols-2 gap-4 mb-4">
              <div className="bg-white rounded-lg p-3 shadow-sm">
                <div className="text-xs text-gray-500">Срок</div>
                <div className="font-bold text-gray-900">{trigger.duration}</div>
              </div>
              <div className="bg-white rounded-lg p-3 shadow-sm">
                <div className="text-xs text-gray-500">Инвестиции</div>
                <div className="font-bold text-green-600">{trigger.price_hint}</div>
              </div>
            </div>
            <div className="bg-white rounded-lg p-4">
              <div className="text-sm font-semibold text-gray-900 mb-2">Что вы получите:</div>
              <ul className="space-y-1">
                {trigger.deliverables.map((item, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm text-gray-700">
                    <span className="text-green-500 mt-0.5">✓</span> {item}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        )}

        {step === 3 && (
          <div className="animate-fadeIn">
            <h3 className="text-lg font-bold text-gray-900 mb-3">Кейс из вашей отрасли</h3>
            <div className="bg-white rounded-lg p-5 border border-green-200 relative overflow-hidden">
              <div className="absolute top-0 right-0 text-6xl text-green-100 opacity-50">"</div>
              <p className="text-gray-700 italic relative z-10">{trigger.case_study}</p>
              <div className="mt-4 pt-3 border-t border-gray-100 flex items-center gap-2">
                <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center text-green-600 font-bold">★</div>
                <div className="text-xs text-gray-500">Подтвержденный результат клиента</div>
              </div>
            </div>
          </div>
        )}

        {step === 4 && (
          <div className="animate-fadeIn">
            {submitted ? (
              <div className="text-center py-8">
                <div className="text-5xl mb-3">🎉</div>
                <h3 className="text-xl font-bold text-gray-900 mb-2">Заявка принята!</h3>
                <p className="text-gray-600">Наш эксперт свяжется с вами в течение 2 часов.</p>
              </div>
            ) : (
              <div>
                <h3 className="text-lg font-bold text-gray-900 mb-3">Получить коммерческое предложение</h3>
                <form onSubmit={handleSubmit} className="space-y-3">
                  <input
                    type="text"
                    placeholder="Ваше имя"
                    required
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                  <input
                    type="email"
                    placeholder="Email"
                    required
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                  <input
                    type="tel"
                    placeholder="Телефон"
                    value={formData.phone}
                    onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                  <button
                    type="submit"
                    className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 rounded-lg transition-colors shadow-md"
                  >
                    Получить КП и пример отчета
                  </button>
                </form>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Navigation Buttons */}
      {!submitted && (
        <div className="flex justify-between mt-8 pt-4 border-t border-blue-200">
          <button
            onClick={() => setStep(Math.max(1, step - 1))}
            disabled={step === 1}
            className="px-4 py-2 text-gray-600 hover:text-gray-900 disabled:opacity-30 disabled:cursor-not-allowed font-medium"
          >
            ← Назад
          </button>
          {step < 4 ? (
            <button
              disabled
              title="Функция в разработке"
              className="px-6 py-2 bg-gray-300 text-gray-500 rounded-lg font-medium shadow-sm cursor-not-allowed"
            >
              Далее →
            </button>
          ) : (
            <div className="text-sm text-amber-600 self-center font-medium">🚧 Функция в разработке</div>
          )}
        </div>
      )}
    </div>
  );
}
