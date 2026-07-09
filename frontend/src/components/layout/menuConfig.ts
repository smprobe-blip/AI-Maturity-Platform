import {
  LayoutDashboard,
  ClipboardList,
  BarChart3,
  Download,
  Users,
  Settings,
  FileText,
  Radar,
  Mail,
  UserCircle,
  FileBarChart,
} from 'lucide-react';

export interface NavItem {
  to: string;
  icon: React.ComponentType<{ className?: string }>;
  label: string;
  end?: boolean;
  requiredRole?: string;
}

export interface NavGroup {
  title: string;
  items: NavItem[];
}

export const menuGroups: NavGroup[] = [
  {
    title: 'ОСНОВНОЕ',
    items: [
      { to: '/admin', icon: LayoutDashboard, label: 'Dashboard', end: true },
      { to: '/admin/audits', icon: ClipboardList, label: 'Аудиты' },
      { to: '/admin/radar', icon: Radar, label: 'Radar' },
    ],
  },
  {
    title: 'БИЗНЕС',
    items: [
      { to: '/admin/leads', icon: Users, label: 'Лиды' },
      { to: '/admin/analytics', icon: BarChart3, label: 'Аналитика' },
      { to: '/admin/exports', icon: Download, label: 'Выгрузки' },
      { to: '/admin/reports', icon: FileBarChart, label: 'Отчеты' },
    ],
  },
  {
    title: 'АДМИНИСТРИРОВАНИЕ',
    items: [
      { to: '/admin/benchmarks', icon: FileText, label: 'Бенчмарки' },
      { to: '/admin/users', icon: Users, label: 'Пользователи', requiredRole: 'super_admin' },
      { to: '/admin/audit-log', icon: FileText, label: 'Журнал действий', requiredRole: 'super_admin' },
      { to: '/admin/settings', icon: Settings, label: 'Настройки', requiredRole: 'super_admin' },
      { to: '/admin/profile', icon: UserCircle, label: 'Мой профиль' },
      { to: '/admin/mailings', icon: Mail, label: 'Рассылки' },
    ],
  },
];
