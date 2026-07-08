import type { Dimension } from '@/types';

export const DIMENSIONS: Dimension[] = [
  {
    id: 1,
    name: 'Strategy & Vision',
    description: 'Стратегия и видение ИИ-трансформации',
    questions: [
      { id: 1, text: 'Наличие утверждённой стратегии ИИ', description: 'Формализованный документ с целями и KPI' },
      { id: 2, text: 'Поддержка топ-менеджмента', description: 'Активное участие C-level в ИИ-инициативах' },
      { id: 3, text: 'Дорожная карта внедрения', description: 'План на 3-5 лет с этапами и бюджетом' },
      { id: 4, text: 'Интеграция с бизнес-стратегией', description: 'Связь ИИ-целей с бизнес-целями' },
      { id: 5, text: 'Мониторинг и оценка', description: 'Регулярный пересмотр стратегии' },
    ],
  },
  {
    id: 2,
    name: 'Data & Analytics',
    description: 'Данные и аналитика',
    questions: [
      { id: 1, text: 'Качество данных', description: 'Чистота, полнота, актуальность' },
      { id: 2, text: 'Data governance', description: 'Политики управления данными' },
      { id: 3, text: 'Data lake/warehouse', description: 'Централизованное хранилище' },
      { id: 4, text: 'Real-time аналитика', description: 'Потоковая обработка данных' },
      { id: 5, text: 'Data literacy', description: 'Культура работы с данными' },
    ],
  },
  {
    id: 3,
    name: 'Technology & Infrastructure',
    description: 'Технологии и инфраструктура',
    questions: [
      { id: 1, text: 'Cloud infrastructure', description: 'Использование облачных сервисов' },
      { id: 2, text: 'MLOps platform', description: 'Платформа для ML-моделей' },
      { id: 3, text: 'API-first подход', description: 'Микросервисная архитектура' },
      { id: 4, text: 'GPU/TPU ресурсы', description: 'Вычислительные мощности для AI' },
      { id: 5, text: 'Безопасность и compliance', description: 'Защита данных и моделей' },
    ],
  },
  {
    id: 4,
    name: 'Processes & Operations',
    description: 'Процессы и операции',
    questions: [
      { id: 1, text: 'Agile/DevOps практики', description: 'Гибкие методологии разработки' },
      { id: 2, text: 'CI/CD для ML', description: 'Автоматизация деплоя моделей' },
      { id: 3, text: 'Мониторинг моделей', description: 'Отслеживание drift и performance' },
      { id: 4, text: 'A/B тестирование', description: 'Эксперименты с моделями' },
      { id: 5, text: 'Автоматизация рутины', description: 'RPA и интеллектуальная автоматизация' },
    ],
  },
  {
    id: 5,
    name: 'People & Skills',
    description: 'Люди и навыки',
    questions: [
      { id: 1, text: 'Data science команда', description: 'Наличие ML-инженеров и data scientists' },
      { id: 2, text: 'Обучение и развитие', description: 'Программы повышения квалификации' },
      { id: 3, text: 'Кросс-функциональность', description: 'Сотрудничество бизнес + IT' },
      { id: 4, text: 'Привлечение талантов', description: 'HR-стратегия для AI-специалистов' },
      { id: 5, text: 'Knowledge sharing', description: 'Обмен знаниями внутри компании' },
    ],
  },
  {
    id: 6,
    name: 'Culture & Change',
    description: 'Культура и изменения',
    questions: [
      { id: 1, text: 'Innovation culture', description: 'Культура экспериментов' },
      { id: 2, text: 'Fail-fast mindset', description: 'Готовность к неудачам' },
      { id: 3, text: 'Change management', description: 'Управление изменениями' },
      { id: 4, text: 'AI adoption rate', description: 'Скорость внедрения AI' },
      { id: 5, text: 'Employee engagement', description: 'Вовлечённость сотрудников' },
    ],
  },
  {
    id: 7,
    name: 'Ethics & Governance',
    description: 'Этика и управление',
    questions: [
      { id: 1, text: 'AI ethics policy', description: 'Политика этики ИИ' },
      { id: 2, text: 'Bias detection', description: 'Выявление смещений в моделях' },
      { id: 3, text: 'Explainability', description: 'Интерпретируемость моделей' },
      { id: 4, text: 'Privacy by design', description: 'Защита приватности' },
      { id: 5, text: 'Regulatory compliance', description: 'Соответствие регуляторным требованиям' },
    ],
  },
];

export const INDUSTRIES = [
  'Retail',
  'Finance',
  'Manufacturing',
  'Healthcare',
  'Telecommunications',
  'Energy',
  'Transportation',
  'Technology',
  'Other',
];

export const COMPANY_SIZES = [
  'Small (1-50)',
  'Medium (51-250)',
  'Large (251-1000)',
  'Enterprise (1000+)',
];

export const REGIONS = [
  'Moscow',
  'Saint Petersburg',
  'Central Russia',
  'Northwest Russia',
  'South Russia',
  'Volga Region',
  'Urals',
  'Siberia',
  'Far East',
];