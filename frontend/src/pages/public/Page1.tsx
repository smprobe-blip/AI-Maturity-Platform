/**
 * Page 1 — User profile + report type selection + PDN consent.
 * v1.1 — Priority 1: 3 report variants, PDN consent (152-FZ).
 */
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Select } from '@/components/ui/Select';
import { useAuditStore } from '@/store/auditStore';
import { REPORT_TYPES } from '@/types';

const INDUSTRIES = [
  { value: 'retail', label: 'Ритейл' },
  { value: 'ecommerce', label: 'E-commerce' },
  { value: 'finance', label: 'Финансы / Банки' },
  { value: 'fintech', label: 'Финтех' },
  { value: 'manufacturing', label: 'Производство' },
  { value: 'telecom', label: 'Телеком' },
  { value: 'it', label: 'IT / Технологии' },
  { value: 'logistics', label: 'Логистика' },
  { value: 'energy', label: 'Энергетика' },
  { value: 'healthcare', label: 'Здравоохранение' },
  { value: 'education', label: 'Образование' },
  { value: 'government', label: 'Госсектор' },
  { value: 'other', label: 'Другое' },
];

const SIZES = [
  { value: 'small', label: 'Малый бизнес (до 100 чел.)' },
  { value: 'medium', label: 'Средний бизнес (100-500 чел.)' },
  { value: 'large', label: 'Крупный бизнес (500-5000 чел.)' },
  { value: 'enterprise', label: 'Корпорация (5000+ чел.)' },
];

export default function Page1() {
  const navigate = useNavigate();
  const { setProfile, profile } = useAuditStore();

  const [industry, setIndustry] = useState(profile?.industry || '');
  const [size, setSize] = useState(profile?.size || '');
  const [email, setEmail] = useState(profile?.email || '');
  const [name, setName] = useState(profile?.name || '');
  const [reportType, setReportType] = useState<'express' | 'executive' | 'comprehensive'>(
    profile?.reportType || 'express'
  );
  const [pdnConsent, setPdnConsent] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  const validate = (): boolean => {
    const e: Record<string, string> = {};
    if (!industry) e.industry = 'Выберите отрасль';
    if (!size) e.size = 'Выберите размер компании';
    if (!email) e.email = 'Введите email';
    else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) e.email = 'Некорректный email';
    if (!pdnConsent) {
      e.pdnConsent = 'Необходимо согласие на обработку персональных данных (152-ФЗ)';
    }
    setErrors(e);
    return Object.keys(e).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) return;
    setProfile({ industry, size, email, name, reportType });
    navigate('/assessment');
  };

  const selectedReport = REPORT_TYPES.find((r) => r.value === reportType)!;

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-secondary-50 py-12 px-4">
      <div className="max-w-3xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-3">
            🤖 Оценка ИИ-зрелости
          </h1>
          <p className="text-lg text-gray-600">
            Диагностика по <strong>35 критериям</strong> (7 осей × 5 вопросов).
            Займёт <strong>10-15 минут</strong>.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="card space-y-6">
          {/* Profile section */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Select
              label="Отрасль"
              value={industry}
              onChange={(e) => setIndustry(e.target.value)}
              options={INDUSTRIES}
              error={errors.industry}
            />
            <Select
              label="Размер компании"
              value={size}
              onChange={(e) => setSize(e.target.value)}
              options={SIZES}
              error={errors.size}
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Input
              label="Email для отчёта"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@company.com"
              error={errors.email}
            />
            <Input
              label="Имя (необязательно)"
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Иван Петров"
            />
          </div>

          {/* Report type selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Выберите вариант отчёта
            </label>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              {REPORT_TYPES.map((rt) => {
                const isSelected = reportType === rt.value;
                return (
                  <label
                    key={rt.value}
                    className={`relative cursor-pointer rounded-lg border-2 p-4 transition-all ${
                      isSelected
                        ? 'border-primary-600 bg-primary-50 shadow-md scale-[1.02]'
                        : 'border-gray-200 bg-white hover:border-gray-300'
                    }`}
                  >
                    <input
                      type="radio"
                      name="reportType"
                      value={rt.value}
                      checked={isSelected}
                      onChange={(e) =>
                        setReportType(e.target.value as 'express' | 'executive' | 'comprehensive')
                      }
                      className="sr-only"
                    />
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-bold text-gray-900">{rt.label}</span>
                      {isSelected && (
                        <span className="text-primary-600 text-lg">✓</span>
                      )}
                    </div>
                    <p className="text-xs text-gray-600 mb-2 min-h-[2.5rem]">
                      {rt.description}
                    </p>
                    <div className="text-sm font-semibold text-primary-600">
                      {rt.price}
                    </div>
                  </label>
                );
              })}
            </div>
          </div>

          {/* PDN consent (152-FZ) */}
          <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
            <label className="flex items-start gap-3 cursor-pointer">
              <input
                type="checkbox"
                checked={pdnConsent}
                onChange={(e) => setPdnConsent(e.target.checked)}
                className="mt-1 h-4 w-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
              />
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-900">
                  Согласие на обработку персональных данных
                </p>
                <p className="text-xs text-gray-600 mt-1">
                  Я даю согласие на обработку моих персональных данных в соответствии
                  с Федеральным законом №152-ФЗ «О персональных данных». Данные будут
                  анонимизированы и использованы только для отраслевых бенчмарков.
                </p>
                {errors.pdnConsent && (
                  <p className="text-xs text-danger-600 mt-1 font-medium">
                    ⚠️ {errors.pdnConsent}
                  </p>
                )}
              </div>
            </label>
          </div>

          {/* Privacy info */}
          <div className="bg-primary-50 border border-primary-200 rounded-lg p-4 text-sm text-gray-700">
            <p className="font-medium mb-1">🔒 Конфиденциальность</p>
            <p>
              Все данные анонимизируются. Результаты хранятся на территории РФ
              (Yandex Cloud, 152-ФЗ). Мы используем их только для отраслевых бенчмарков.
            </p>
          </div>

          {/* Submit button */}
          <Button type="submit" size="lg" className="w-full">
            Начать оценку →
          </Button>

          {/* Selected report hint */}
          <p className="text-center text-xs text-gray-500">
            Выбран отчёт: <strong>{selectedReport.label}</strong> — {selectedReport.cta}
          </p>
        </form>
      </div>
    </div>
  );
}