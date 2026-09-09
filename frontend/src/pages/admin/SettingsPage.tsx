import { useQuery } from '@tanstack/react-query';
import { KeyRound, Database, Mail, ShieldCheck } from 'lucide-react';
import { Badge } from '@/components/ui/Badge';
import { adminApi } from '@/services/adminApi';

function Row({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="flex items-center justify-between py-1.5 border-b border-gray-100 last:border-0">
      <span className="text-sm text-gray-600">{label}</span>
      <span className="text-sm font-medium text-gray-900 font-mono">{value}</span>
    </div>
  );
}

function Dot({ ok }: { ok: boolean }) {
  return (
    <span
      className={`inline-block w-2 h-2 rounded-full mr-2 ${ok ? 'bg-green-500' : 'bg-red-400'}`}
    />
  );
}

export default function SettingsPage() {
  const { data: settings, isLoading } = useQuery({
    queryKey: ['settings'],
    queryFn: adminApi.getSettings,
  });

  if (isLoading || !settings) {
    return (
      <div>
        <h1 className="text-3xl font-bold text-gray-900 mb-6">Настройки</h1>
        <p className="text-gray-500">Загрузка…</p>
      </div>
    );
  }

  const k = settings.integrations.keycloak;
  const b = settings.integrations.baserow;
  const e = settings.integrations.email;
  const d = settings.data;

  return (
    <div>
      <h1 className="text-3xl font-bold text-gray-900 mb-1">Настройки</h1>
      <p className="text-gray-600 mb-6">
        Состояние платформы (только чтение; секреты не отображаются)
      </p>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <KeyRound className="w-5 h-5 text-primary-600" />
            Аутентификация (Keycloak)
          </h2>
          <Row label="Realm" value={k.realm} />
          <Row label="Client ID" value={k.client_id} />
          <div className="flex items-center justify-between py-1.5">
            <span className="text-sm text-gray-600 flex items-center">
              <Dot ok={k.configured} />
              Состояние
            </span>
            <Badge variant={k.configured ? 'success' : 'danger'}>
              {k.configured ? 'подключено' : 'не настроено'}
            </Badge>
          </div>
        </div>

        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Database className="w-5 h-5 text-primary-600" />
            CRM (Baserow)
          </h2>
          <Row label="URL" value={b.url} />
          <Row label="Таблица лидов" value={`#${b.leads_table_id}`} />
          <div className="flex items-center justify-between py-1.5">
            <span className="text-sm text-gray-600 flex items-center">
              <Dot ok={b.configured} />
              Состояние
            </span>
            <Badge variant={b.configured ? 'success' : 'danger'}>
              {b.configured ? 'подключено' : 'не настроено'}
            </Badge>
          </div>
        </div>

        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Mail className="w-5 h-5 text-primary-600" />
            Почта (SMTP)
          </h2>
          <Row label="Сервер" value={`${e.host}:${e.port}`} />
          <Row label="Отправитель" value={`${e.from_name} <${e.from_email}>`} />
          <Row label="TLS" value={e.use_tls ? 'да' : 'нет'} />
          <div className="flex items-center justify-between py-1.5">
            <span className="text-sm text-gray-600 flex items-center">
              <Dot ok={e.configured} />
              Состояние
            </span>
            <Badge variant={e.configured ? 'success' : 'warning'}>
              {e.configured ? 'настроена' : 'не настроена'}
            </Badge>
          </div>
        </div>

        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <ShieldCheck className="w-5 h-5 text-primary-600" />
            Данные
          </h2>
          <Row label="Аудитов всего" value={d.audits_total} />
          <Row label="Активных" value={d.audits_active} />
          <Row label="В архиве" value={d.audits_archived} />
          <Row label="Тестовых (test_manual)" value={d.audits_test_manual} />
          <Row label="PDF в библиотеке отчётов" value={d.reports_pdf} />
        </div>
      </div>
    </div>
  );
}
