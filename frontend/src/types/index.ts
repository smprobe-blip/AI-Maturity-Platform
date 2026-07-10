// ============================================================
// AI Maturity Platform — Type definitions
// v1.1 — Priority 1: 35 questions, patterns, upsell
// ============================================================

// ============================================================
// Pattern diagnosis (from pattern_service.py)
// ============================================================

export interface PatternInfo {
  pattern_type:
    | 'compressed_circle'
    | 'right_skew'
    | 'left_skew'
    | 'star_with_gaps'
    | 'benchmark_parity'
    | 'balanced';
  diagnosis: string;
  recommendation: string;
  severity: 'critical' | 'warning' | 'info' | 'success';
}

// ============================================================
// Top-3 analysis
// ============================================================

export interface BottleneckItem {
  dimension_id: string;
  dimension_name: string;
  score: number;
  severity: 'critical' | 'warning' | 'info';
  weight: number;
}

export interface AnchorItem {
  dimension_id: string;
  dimension_name: string;
  score: number;
  strength: 'strong' | 'moderate' | 'weak';
  weight: number;
}

// ============================================================
// Upsell triggers (monetization)
// ============================================================

export interface UpsellTrigger {
  type: 'fear_of_loss' | 'bottleneck' | 'new_roles' | 'methodology';
  dimension_id: string;
  dimension_name: string;
  score: number;
  risk: string;
  service: string;
  price_hint: string;
}

// ============================================================
// Gap analysis
// ============================================================

export interface DimensionGap {
  current: number;
  target: number;
  gap: number;
  priority: 'high' | 'medium' | 'low';
}

export interface GapAnalysis {
  dimension_gaps: Record<string, DimensionGap>;
  weighted_total_gap: number;
  priority_axes: string[];
}

// ============================================================
// Calculated indices (from backend)
// ============================================================

export interface CalculatedIndices {
  composite_score: number;
  maturity_level: string;
  dimension_scores: Record<string, number>;
  roi_estimate_percent?: number;
  tco_estimate_millions?: number;
  top3_bottlenecks: BottleneckItem[];
  top3_anchors: AnchorItem[];
  pattern?: PatternInfo;
  gap_analysis?: GapAnalysis;
}

// ============================================================
// Audit request / response
// ============================================================

export interface AuditRequest {
  company_industry: string;
  company_size: 'small' | 'medium' | 'large' | 'enterprise';
  contact_email: string;
  contact_name?: string;
  report_type: 'express' | 'executive' | 'comprehensive';
  responses: Record<string, Record<string, number>>;
  target_scores?: Record<string, number>;
  pdn_consent: boolean;
}

export interface AuditResponse {
  audit_id: string;
  created_at: string;
  report_type: string;
  company_profile: {
    industry: string;
    size: string;
    anonymized: boolean;
  };
  calculated_indices: CalculatedIndices;
  recommendations: string[];
  upsell_triggers: UpsellTrigger[];
}

// ============================================================
// Question & Dimension (35 questions matrix)
// ============================================================

export interface Question {
  id: string;
  text: string;
  descriptors: {
    1: string;
    2: string;
    3: string;
    4: string;
    5: string;
  };
}

export interface Dimension {
  id: string;
  name: string;
  shortName: string;
  description: string;
  weight: number;
  questions: Question[];
}

// ============================================================
// Concept v5.0 Chapter 2.2: Full matrix of 35 questions
// 7 dimensions × 5 questions each
// ============================================================

export const DIMENSIONS: Dimension[] = [
  {
    id: '1',
    name: 'Стратегия и управление',
    shortName: 'Стратегия',
    description: 'AI-стратегия, роль C-Level, измеримость ROI',
    weight: 0.15,
    questions: [
      {
        id: '1',
        text: 'Статус ИИ-стратегии',
        descriptors: {
          1: 'Нет',
          2: 'Декларируется',
          3: 'В разработке',
          4: 'Утверждена',
          5: 'Фундамент бизнеса',
        },
      },
      {
        id: '2',
        text: 'Роль C-Level',
        descriptors: {
          1: 'Нет',
          2: 'Эпизодически',
          3: 'Осознанно',
          4: 'Формальное управление',
          5: 'Личный пример',
        },
      },
      {
        id: '3',
        text: 'Измеримость ROI',
        descriptors: {
          1: 'Не измеряется',
          2: 'Локально',
          3: 'Базовые KPI',
          4: 'В KPI руководителей',
          5: 'Драйвер выручки',
        },
      },
      {
        id: '4',
        text: 'Структура управления',
        descriptors: {
          1: 'Нет',
          2: 'Энтузиасты',
          3: 'Формируется ЦК',
          4: 'Централизованно',
          5: 'Операционная система',
        },
      },
      {
        id: '5',
        text: 'Глубина в процессах',
        descriptors: {
          1: 'Не встроен',
          2: 'Инструмент',
          3: 'Встроен (чел. контроль)',
          4: 'Управляется ИИ',
          5: 'ИИ-операционная система',
        },
      },
    ],
  },
  {
    id: '2',
    name: 'Люди и культура',
    shortName: 'Люди',
    description: 'Найм талантов, команды, культура «Чел+ИИ»',
    weight: 0.15,
    questions: [
      {
        id: '1',
        text: 'Найм талантов',
        descriptors: {
          1: 'Хаотичный',
          2: 'Локальный',
          3: 'Системный',
          4: 'Центральный пул',
          5: 'Экосистема (академии)',
        },
      },
      {
        id: '2',
        text: 'Команды',
        descriptors: {
          1: 'Изолированные',
          2: 'Проектные',
          3: 'Кросс-функциональные',
          4: 'Сетевые',
          5: 'Автономные мини-ЦК',
        },
      },
      {
        id: '3',
        text: 'Культура «Чел+ИИ»',
        descriptors: {
          1: 'Страх',
          2: 'Информирование',
          3: 'Инструмент',
          4: 'Повседневная работа',
          5: '«Второй мозг»',
        },
      },
      {
        id: '4',
        text: 'Обучение',
        descriptors: {
          1: 'Нет',
          2: 'Вебинары',
          3: 'Системное',
          4: 'ИИ-Академия',
          5: 'Непрерывная норма',
        },
      },
      {
        id: '5',
        text: 'ИИ в HR',
        descriptors: {
          1: 'Нет',
          2: 'Фрагментарно',
          3: 'Частично',
          4: 'Системно',
          5: 'Интеллектуальное управление',
        },
      },
    ],
  },
  {
    id: '3',
    name: 'Инфраструктура',
    shortName: 'Инфра',
    description: 'Мощности, SLA, Open Source, AI Governance',
    weight: 0.15,
    questions: [
      {
        id: '1',
        text: 'Мощности',
        descriptors: {
          1: 'Локальные ПК',
          2: 'Разрозненные',
          3: 'Базовые кластеры',
          4: 'Гибридная платформа',
          5: 'Глобальная среда',
        },
      },
      {
        id: '2',
        text: 'Доступ к ресурсам',
        descriptors: {
          1: 'Нет',
          2: 'Ручное выделение',
          3: 'По ролям',
          4: 'Портал самообслуживания',
          5: 'Мгновенный запуск',
        },
      },
      {
        id: '3',
        text: 'SLA и инциденты',
        descriptors: {
          1: 'Реактивно',
          2: 'Частичная автоматизация',
          3: 'Тикеты',
          4: 'AIOps (сутки)',
          5: 'Предиктивная система',
        },
      },
      {
        id: '4',
        text: 'Open Source',
        descriptors: {
          1: 'Заблокирован',
          2: 'Эпизодически',
          3: 'Контролируемый',
          4: 'Корпоративный репозиторий',
          5: 'Активное участие',
        },
      },
      {
        id: '5',
        text: 'AI Governance',
        descriptors: {
          1: 'Нет политик',
          2: 'Базовые',
          3: 'Формализованы',
          4: 'Регулярные аудиты',
          5: 'ИИ-мониторинг аномалий',
        },
      },
    ],
  },
  {
    id: '4',
    name: 'Данные',
    shortName: 'Данные',
    description: 'Data Governance, Фабрика данных, качество',
    weight: 0.15,
    questions: [
      {
        id: '1',
        text: 'Data Governance',
        descriptors: {
          1: 'Хаос',
          2: 'Базовый каталог',
          3: 'Роли и стандарты',
          4: 'Системный (80%+)',
          5: 'Полная автоматизация',
        },
      },
      {
        id: '2',
        text: 'Фабрика данных',
        descriptors: {
          1: 'Excel/локально',
          2: 'Частичная централизация',
          3: 'DWH/Lakehouse',
          4: 'Центральная фабрика',
          5: 'Полная экосистема',
        },
      },
      {
        id: '3',
        text: 'Качество данных',
        descriptors: {
          1: 'Не контролируется',
          2: 'Ручные проверки',
          3: 'Скрипты',
          4: 'Авто-проверки',
          5: 'Непрерывный автоконтроль',
        },
      },
      {
        id: '4',
        text: 'Решения на данных',
        descriptors: {
          1: 'Интуитивно',
          2: 'По запросу',
          3: 'BI-дашборды',
          4: 'Data-Driven',
          5: 'Интеллектуальные (реалтайм)',
        },
      },
      {
        id: '5',
        text: 'Данные для ML',
        descriptors: {
          1: 'Нет датасетов',
          2: 'Ручной сбор',
          3: 'Воспроизводимые',
          4: 'Автоочистка',
          5: 'Сквозной контур',
        },
      },
    ],
  },
  {
    id: '5',
    name: 'Модели',
    shortName: 'Модели',
    description: 'Портфель моделей, MLOps, Time-to-Market',
    weight: 0.15,
    questions: [
      {
        id: '1',
        text: 'Портфель моделей',
        descriptors: {
          1: 'Нет',
          2: 'Эксперименты',
          3: 'Каталог',
          4: 'Управляемый реестр',
          5: 'Инвестиционный актив',
        },
      },
      {
        id: '2',
        text: 'Доля в продакшене',
        descriptors: {
          1: 'Нет',
          2: '<10%',
          3: '10-30%',
          4: '>50% (автодеплой)',
          5: '100% (MLOps)',
        },
      },
      {
        id: '3',
        text: 'Time-to-Market',
        descriptors: {
          1: 'Месяцы',
          2: '1-2 месяца',
          3: 'Около месяца',
          4: 'Несколько дней',
          5: 'Несколько часов',
        },
      },
      {
        id: '4',
        text: 'Мониторинг',
        descriptors: {
          1: 'Не отслеживается',
          2: 'Ручной',
          3: 'Частичный',
          4: 'Авто MLOps',
          5: 'Интеллектуальный (прогноз)',
        },
      },
      {
        id: '5',
        text: 'MLOps культура',
        descriptors: {
          1: 'Хаос',
          2: 'Лабораторные',
          3: 'CI/CD',
          4: 'Промышленная',
          5: 'MLOps как норма',
        },
      },
    ],
  },
  {
    id: '6',
    name: 'Внедрение ИИ',
    shortName: 'Внедрение',
    description: 'Доля процессов, аугментация, фреймворк AgentOps',
    weight: 0.20,
    questions: [
      {
        id: '1',
        text: 'Доля процессов',
        descriptors: {
          1: 'Эксперименты',
          2: 'Точечные',
          3: 'Ключевые функции',
          4: '>70% процессов',
          5: 'Автономное исполнение',
        },
      },
      {
        id: '2',
        text: 'Аугментация',
        descriptors: {
          1: 'Справочник',
          2: 'Локальная помощь',
          3: 'Регулярное использование',
          4: 'Помощь в решениях',
          5: 'Симбиоз',
        },
      },
      {
        id: '3',
        text: 'Клиентский путь',
        descriptors: {
          1: 'Нигде',
          2: 'Чат-боты',
          3: 'Отдельные этапы',
          4: 'Омниканальность',
          5: 'Полный интел. путь',
        },
      },
      {
        id: '4',
        text: 'Фреймворк',
        descriptors: {
          1: 'Хаос',
          2: 'Шаблоны',
          3: 'Стандартизирован',
          4: 'Управляемый',
          5: 'Автономный AgentOps',
        },
      },
      {
        id: '5',
        text: 'Принятие сотрудниками',
        descriptors: {
          1: 'Страх',
          2: 'Ограниченное',
          3: 'Регулярное',
          4: 'Высокое доверие',
          5: 'Цифровой коллега',
        },
      },
    ],
  },
  {
    id: '7',
    name: 'Исследования (R&D)',
    shortName: 'R&D',
    description: 'Партнёрства, качество R&D, применимость',
    weight: 0.05,
    questions: [
      {
        id: '1',
        text: 'Партнёрства',
        descriptors: {
          1: 'Нет',
          2: 'Эпизодические',
          3: 'Под задачи',
          4: 'Системные альянсы',
          5: 'Инновационная экосистема',
        },
      },
      {
        id: '2',
        text: 'Качество R&D',
        descriptors: {
          1: 'Хаотично',
          2: 'Эксперименты',
          3: 'Структурировано',
          4: 'Индустриализировано',
          5: 'Непрерывно',
        },
      },
      {
        id: '3',
        text: 'Доля R&D',
        descriptors: {
          1: '0%',
          2: 'Единичные',
          3: 'До 5%',
          4: 'До 10%',
          5: 'Стратегический блок',
        },
      },
      {
        id: '4',
        text: 'Применимость',
        descriptors: {
          1: 'В отчётах',
          2: 'Частично',
          3: 'На бизнес-задачи',
          4: 'Системный переход',
          5: 'Полный иннов. контур',
        },
      },
      {
        id: '5',
        text: 'Активность',
        descriptors: {
          1: 'Нет',
          2: 'Редкие выступления',
          3: 'Регулярные публикации',
          4: 'Лидер мнений',
          5: 'Формирование стандартов',
        },
      },
    ],
  },
];

// ============================================================
// Concept v5.0 Table 3.2: Maturity zones (for Radar Chart)
// ============================================================

export const MATURITY_ZONES = [
  { min: 1.0, max: 1.8, name: 'Начальный', color: '#FEE2E2', darkColor: '#7F1D1D' },
  { min: 1.9, max: 2.6, name: 'AI-Enabled', color: '#FEF3C7', darkColor: '#78350F' },
  { min: 2.7, max: 3.4, name: 'AI-Driven', color: '#DCFCE7', darkColor: '#14532D' },
  { min: 3.5, max: 4.2, name: 'AI-First', color: '#DBEAFE', darkColor: '#1E3A8A' },
  { min: 4.3, max: 5.0, name: 'AI-Native', color: '#EDE9FE', darkColor: '#4C1D95' },
];

// ============================================================
// Report types (3 variants for monetization)
// ============================================================

export const REPORT_TYPES = [
  {
    value: 'express',
    label: 'Экспресс',
    description: 'One-pager с радаром и топ-3 инсайтами',
    price: 'Бесплатно',
    cta: '30-мин разбор с экспертом',
  },
  {
    value: 'executive',
    label: 'Для ЛПР',
    description: 'PDF 10-15 стр. с бенчмарками и gap-анализом',
    price: 'от 50 000 ₽',
    cta: 'Шаблон AI Governance Canvas',
  },
  {
    value: 'comprehensive',
    label: 'Комплексный',
    description: 'Отчёт 20+ стр. + сессия с экспертом',
    price: 'от 150 000 ₽',
    cta: 'Запуск Центра ИИ-компетенций',
  },
];