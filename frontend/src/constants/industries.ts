/**
 * Единый справочник отраслей: выпадающий список анкеты (Page1)
 * и подписи графиков дашборда используют один и тот же список.
 */
export interface IndustryOption {
  value: string;
  label: string;
}

export const INDUSTRIES: IndustryOption[] = [
  { value: 'retail', label: 'Ритейл' },
  { value: 'ecommerce', label: 'E-commerce' },
  { value: 'finance', label: 'Финансы / Банки' },
  { value: 'fintech', label: 'Финтех' },
  { value: 'manufacturing', label: 'Производство' },
  { value: 'telecom', label: 'Телеком' },
  { value: 'it', label: 'IT / Технологии' },
  { value: 'logistics', label: 'Логистика' },
  { value: 'energy', label: 'Энергетика' },
  { value: 'construction', label: 'Строительство / Девелопмент' },
  { value: 'healthcare', label: 'Здравоохранение' },
  { value: 'education', label: 'Образование' },
  { value: 'government', label: 'Госсектор' },
  { value: 'other', label: 'Другое' },
];

/** Легаси-коды из старых данных (для подписей графиков). */
export const INDUSTRY_EXTRA_LABELS: Record<string, string> = {
  services: 'Услуги',
  crossindustry: 'Кросс-отраслевой',
};

/** value -> русское название (для графиков). */
export const INDUSTRY_LABELS: Record<string, string> = Object.fromEntries([
  ...INDUSTRIES.map((i) => [i.value, i.label] as [string, string]),
  ...Object.entries(INDUSTRY_EXTRA_LABELS),
]);
