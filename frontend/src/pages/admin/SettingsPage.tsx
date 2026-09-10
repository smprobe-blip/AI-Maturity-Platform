import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { KeyRound, Database, Mail, ShieldCheck, Pencil } from 'lucide-react';
import { toast } from 'sonner';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Modal } from '@/components/ui/Modal';
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
  const queryClient = useQueryClient();
  const [editOpen, setEditOpen] = useState(false);
  const [editForm, setEditForm] = useState({ public_base_url: '', postbox_from_email: '', postbox_from_name: '' });

  const { data: settings, isLoading } = useQuery({
    queryKey: ['settings'],
    queryFn: adminApi.getSettings,
  });

  const updateMutation = useMutation({
    mutationFn: adminApi.updateSettings,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['settings'] });
      queryClient.invalidateQueries({ queryKey: ['email-status'] });
      toast.success('Настройки сохранены');
      setEditOpen(false);
    },
    onError: () => toast.error('Ошибка сохранения'),
  });

  const openEdit = () => {
    setEditForm({
      public_base_url: '',
      postbox_from_email: settings?.integrations.email.postbox?.from_email || settings?.integrations.email.from_email || '',
      postbox_from_name: settings?.integrations.email.from_name || '',
    });
    setEditOpen(true);
  };

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
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Настройки</h1>
          <p className="text-gray-600">
            Состояние платформы; секреты не отображаются
          </p>
        </div>
        <Button variant="secondary" onClick={openEdit}>
          <Pencil className="w-4 h-4 mr-2" />
          Изменить
        </Button>
      </div>

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
          {settings.platform && 'public_base_url' in settings.platform && (
            <Row label="Публичный URL" value={String(settings.platform.public_base_url)} />
          )}
        </div>
      </div>

      <EditModal
        isOpen={editOpen}
        onClose={() => setEditOpen(false)}
        initial={{
          public_base_url: 'https://audit.netbrainpower.ru',
          postbox_from_email: settings.integrations.email.postbox?.from_email || settings.integrations.email.from_email,
          postbox_from_name: settings.integrations.email.from_name,
        }}
        pending={updateMutation.isPending}
        onSave={(v) => updateMutation.mutate(v)}
      />
    </div>
  );
}

function EditModal({
  isOpen,
  onClose,
  initial,
  pending,
  onSave,
}: {
  isOpen: boolean;
  onClose: () => void;
  initial: { public_base_url: string; postbox_from_email: string; postbox_from_name: string };
  pending: boolean;
  onSave: (v: { public_base_url?: string; postbox_from_email?: string; postbox_from_name?: string }) => void;
}) {
  const [f, setF] = useState(initial);
  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Редактировать настройки">
      <p className="text-sm text-gray-500 mb-4">
        Пустое поле — оставить текущее значение. URL и адрес отправителя используются
        в письмах респондентам.
      </p>
      <div className="space-y-4 mb-6">
        <Input
          label="Публичный URL (ссылка на результаты в письмах)"
          placeholder={initial.public_base_url}
          value={f.public_base_url}
          onChange={(e) => setF({ ...f, public_base_url: e.target.value })}
        />
        <Input
          label="Адрес отправителя (Postbox)"
          placeholder={initial.postbox_from_email}
          value={f.postbox_from_email}
          onChange={(e) => setF({ ...f, postbox_from_email: e.target.value })}
        />
        <Input
          label="Имя отправителя"
          placeholder={initial.postbox_from_name}
          value={f.postbox_from_name}
          onChange={(e) => setF({ ...f, postbox_from_name: e.target.value })}
        />
      </div>
      <div className="flex justify-end gap-3">
        <Button variant="secondary" onClick={onClose}>Отмена</Button>
        <Button
          disabled={pending}
          onClick={() =>
            onSave({
              public_base_url: f.public_base_url || undefined,
              postbox_from_email: f.postbox_from_email || undefined,
              postbox_from_name: f.postbox_from_name || undefined,
            })
          }
        >
          {pending ? 'Сохранение…' : 'Сохранить'}
        </Button>
      </div>
    </Modal>
  );
}
