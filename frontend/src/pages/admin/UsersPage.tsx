import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Search, UserPlus, Trash2 } from 'lucide-react';
import { format } from 'date-fns';
import { toast } from 'sonner';
import { Table } from '@/components/ui/Table';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Select } from '@/components/ui/Select';
import { Modal } from '@/components/ui/Modal';
import { adminApi, User } from '@/services/adminApi';

const ROLES = [
  { value: 'super_admin', label: 'Супер-администратор' },
  { value: 'facilitator', label: 'Фасилитатор' },
  { value: 'analyst', label: 'Аналитик' },
  { value: 'sales', label: 'Продажи' },
  { value: 'auditor', label: 'Аудитор' },
  { value: 'client', label: 'Клиент' },
];

export default function UsersPage() {
  const queryClient = useQueryClient();
  const [search, setSearch] = useState('');
  const [inviteOpen, setInviteOpen] = useState(false);
  const [form, setForm] = useState({ email: '', first_name: '', last_name: '', role: 'analyst' });
  const [sendEmail, setSendEmail] = useState(false);
  const [invited, setInvited] = useState<{ email: string; temp_password?: string; email_sent?: boolean } | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<{ user_id: string; email: string } | null>(null);

  const { data: operators } = useQuery({
    queryKey: ['keycloak-users'],
    queryFn: adminApi.listKeycloakUsers,
  });

  const { data, isLoading } = useQuery({
    queryKey: ['users'],
    queryFn: adminApi.listUsers,
  });

  const { data: kcSmtp } = useQuery({
    queryKey: ['kc-smtp'],
    queryFn: adminApi.getKeycloakSmtp,
  });

  const smtpMutation = useMutation({
    mutationFn: (payload: Record<string, string | boolean>) => adminApi.setKeycloakSmtp(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['kc-smtp'] });
      toast.success('SMTP Keycloak сохранён — письма с подтверждением будут уходить');
      setSmtpOpen(false);
    },
    onError: () => toast.error('Ошибка сохранения SMTP'),
  });

  const [smtpOpen, setSmtpOpen] = useState(false);
  const [smtpForm, setSmtpForm] = useState({ host: '', port: '465', from: '', from_display_name: 'AI Maturity Platform', user: '', password: '', ssl: true });

  const inviteMutation = useMutation({
    mutationFn: (vars: { form: typeof form; send_email: boolean }) =>
      adminApi.inviteOperator({ ...vars.form, send_email: vars.send_email }),
    onSuccess: (res) => {
      queryClient.invalidateQueries({ queryKey: ['keycloak-users'] });
      setInvited({ email: res.email, temp_password: res.temp_password, email_sent: res.email_sent });
      setInviteOpen(false);
      setForm({ email: '', first_name: '', last_name: '', role: 'analyst' });
    },
    onError: (err: any) => {
      const detail = err?.response?.data?.detail;
      toast.error(typeof detail === 'string' ? detail : 'Ошибка создания оператора');
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (userId: string) => adminApi.deleteOperator(userId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['keycloak-users'] });
      toast.success('Оператор удалён');
      setDeleteTarget(null);
    },
    onError: () => toast.error('Ошибка удаления'),
  });

  const users: User[] = (data?.items || []).filter((u) =>
    search
      ? u.email.toLowerCase().includes(search.toLowerCase()) ||
        (u.name || '').toLowerCase().includes(search.toLowerCase())
      : true
  );

  const respondentColumns = [
    { key: 'email', header: 'Email', render: (u: User) => <span className="font-medium">{u.email}</span> },
    { key: 'name', header: 'Имя', render: (u: User) => u.name || '—' },
    {
      key: 'audits_count',
      header: 'Аудитов',
      render: (u: User) => <span className="font-bold text-primary-600">{u.audits_count}</span>,
    },
    {
      key: 'test_audits',
      header: 'Тестовых',
      render: (u: User) =>
        u.test_audits > 0 ? <Badge variant="warning">{u.test_audits}</Badge> : <span className="text-gray-400">—</span>,
    },
    {
      key: 'last_seen',
      header: 'Последний аудит',
      render: (u: User) => (u.last_seen ? format(new Date(u.last_seen), 'dd.MM.yyyy HH:mm') : '—'),
    },
    {
      key: 'sources',
      header: 'Источники',
      render: (u: User) => (
        <div className="flex flex-wrap gap-1">
          {u.sources.length ? (
            u.sources.map((s) => (
              <Badge key={s} variant="neutral">
                {s}
              </Badge>
            ))
          ) : (
            <span className="text-gray-400">—</span>
          )}
        </div>
      ),
    },
  ];

  return (
    <div>
      {/* Операторы (Keycloak) */}
      <div className="flex items-center justify-between mb-4">
        <div>
          <h2 className="text-xl font-bold text-gray-900">Операторы (Keycloak)</h2>
          <p className="text-sm text-gray-600">Учётные записи доступа к админке</p>
        </div>
        <Button onClick={() => setInviteOpen(true)}>
          <UserPlus className="w-4 h-4 mr-2" />
          Пригласить оператора
        </Button>
      </div>

      <div className="bg-white rounded-lg border border-gray-200 p-4 mb-8">
        {(operators || []).length ? (
          <div className="space-y-2">
            {(operators || []).map((op) => (
              <div
                key={op.user_id}
                className="flex items-center justify-between p-2 bg-gray-50 rounded"
              >
                <div>
                  <div className="font-medium text-gray-900">
                    {op.email || op.username}{' '}
                    {op.service_account && (
                      <Badge variant="neutral">сервисный</Badge>
                    )}
                  </div>
                  <div className="text-xs text-gray-500">
                    {op.first_name || ''} {op.last_name || ''}
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <Badge variant={op.enabled ? 'success' : 'danger'}>
                    {op.enabled ? 'активен' : 'отключён'}
                  </Badge>
                  {!op.service_account && (
                    <Button
                      variant="secondary"
                      className="!px-2 !py-1"
                      title="Удалить оператора"
                      onClick={() => setDeleteTarget({ user_id: op.user_id, email: op.email || op.username })}
                    >
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  )}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-sm text-gray-400">Не удалось загрузить операторов</p>
        )}
      </div>

      {/* Респонденты */}
      <div className="flex items-center justify-between mb-4">
        <div>
          <h2 className="text-xl font-bold text-gray-900">Респонденты</h2>
          <p className="text-sm text-gray-600">Адреса из аудитов: {data?.total || 0}</p>
        </div>
        <div className="relative w-72">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            className="w-full pl-9 pr-3 py-2 border border-gray-300 rounded-lg text-sm"
            placeholder="Поиск по email или имени"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
      </div>

      <div className="bg-white rounded-lg border border-gray-200">
        <Table
          columns={respondentColumns}
          data={users}
          keyExtractor={(u) => u.email}
          isLoading={isLoading}
          emptyMessage="Пользователи не найдены"
        />
      </div>

      {/* Invite modal */}
      <Modal isOpen={inviteOpen} onClose={() => setInviteOpen(false)} title="Пригласить оператора">
        <div className="space-y-4 mb-6">
          <Input
            label="Email"
            value={form.email}
            onChange={(e) => setForm({ ...form, email: e.target.value })}
          />
          <Input
            label="Имя"
            value={form.first_name}
            onChange={(e) => setForm({ ...form, first_name: e.target.value })}
          />
          <Input
            label="Фамилия"
            value={form.last_name}
            onChange={(e) => setForm({ ...form, last_name: e.target.value })}
          />
          <Select
            label="Роль"
            value={form.role}
            onChange={(e) => setForm({ ...form, role: e.target.value })}
            options={ROLES}
          />
          <label className="flex items-center gap-2 text-sm text-gray-700">
            <input
              type="checkbox"
              checked={sendEmail}
              onChange={(e) => setSendEmail(e.target.checked)}
            />
            Отправить письмо с подтверждением (нужна почта Keycloak)
          </label>
        </div>
        <div className="flex justify-end gap-3">
          <Button variant="secondary" onClick={() => setInviteOpen(false)}>
            Отмена
          </Button>
          <Button
            variant="danger"
            disabled={!form.email.includes('@') || inviteMutation.isPending}
            onClick={() => inviteMutation.mutate({ form, send_email: sendEmail })}
          >
            Создать
          </Button>
        </div>
      </Modal>

      {/* Temp password modal */}
      <Modal isOpen={!!invited} onClose={() => setInvited(null)} title="Оператор создан">
        {invited?.email_sent ? (
          <p className="text-gray-600 mb-6">
            Письмо с подтверждением отправлено на <strong>{invited?.email}</strong>.
            Оператор подтвердит email и задаст пароль по ссылке.
          </p>
        ) : (
          <>
            <p className="text-gray-600 mb-4">
              Временный пароль для <strong>{invited?.email}</strong> — покажите его один раз,
              оператор сменит его при первом входе:
            </p>
            <div className="bg-gray-100 rounded p-3 font-mono text-center text-lg mb-6 select-all">
              {invited?.temp_password}
            </div>
          </>
        )}
        <div className="flex justify-end">
          <Button onClick={() => setInvited(null)}>Готово</Button>
        </div>
      </Modal>

      {/* SMTP Keycloak */}
      <div className="flex items-center justify-between mb-4 mt-10">
        <div>
          <h2 className="text-xl font-bold text-gray-900">Почта Keycloak</h2>
          <p className="text-sm text-gray-600">
            Нужна для писем с подтверждением при приглашении операторов
          </p>
        </div>
        <Button variant="secondary" onClick={() => setSmtpOpen(true)}>
          Настроить
        </Button>
      </div>
      <div className="bg-white rounded-lg border border-gray-200 p-4 mb-8">
        {kcSmtp?.configured ? (
          <div className="text-sm text-gray-700">
            <div className="flex items-center gap-2">
              <Badge variant="success">настроена</Badge>
              <span className="font-mono">
                {String(kcSmtp.smtp.host ?? '')}:{String(kcSmtp.smtp.port ?? '')}
              </span>
            </div>
          </div>
        ) : (
          <p className="text-sm text-gray-500">
            Не настроена — при приглашении используйте временный пароль.
          </p>
        )}
      </div>

      <Modal isOpen={smtpOpen} onClose={() => setSmtpOpen(false)} title="SMTP для писем Keycloak">
        <div className="space-y-4 mb-6">
          <Input label="SMTP-сервер" placeholder="smtp.yandex.ru" value={smtpForm.host} onChange={(e) => setSmtpForm({ ...smtpForm, host: e.target.value })} />
          <Input label="Порт" placeholder="465" value={smtpForm.port} onChange={(e) => setSmtpForm({ ...smtpForm, port: e.target.value })} />
          <Input label="От кого (email)" placeholder="reports@netbrainpower.ru" value={smtpForm.from} onChange={(e) => setSmtpForm({ ...smtpForm, from: e.target.value })} />
          <Input label="Имя отправителя" value={smtpForm.from_display_name} onChange={(e) => setSmtpForm({ ...smtpForm, from_display_name: e.target.value })} />
          <Input label="Логин (если с авторизацией)" value={smtpForm.user} onChange={(e) => setSmtpForm({ ...smtpForm, user: e.target.value })} />
          <Input label="Пароль (секрет API-ключа Postbox)" type="password" value={smtpForm.password} onChange={(e) => setSmtpForm({ ...smtpForm, password: e.target.value })} />
          <p className="text-xs text-gray-500">
            Postbox: сервер postbox.cloud.yandex.net:587 (STARTTLS), логин API_KEY,
            пароль — секрет API-ключа с правом yc.postbox.send.
          </p>
        </div>
        <div className="flex justify-end gap-3">
          <Button variant="secondary" onClick={() => setSmtpOpen(false)}>Отмена</Button>
          <Button
            disabled={!smtpForm.host || !smtpForm.from || smtpMutation.isPending}
            onClick={() => smtpMutation.mutate(smtpForm)}
          >
            Сохранить
          </Button>
        </div>
      </Modal>

      {/* Delete confirm */}
      <Modal isOpen={!!deleteTarget} onClose={() => setDeleteTarget(null)} title="Удалить оператора?">
        <p className="text-gray-600 mb-6">
          Учётная запись <strong>{deleteTarget?.email}</strong> будет удалена из Keycloak
          безвозвратно.
        </p>
        <div className="flex justify-end gap-3">
          <Button variant="secondary" onClick={() => setDeleteTarget(null)}>
            Отмена
          </Button>
          <Button
            variant="danger"
            onClick={() => deleteTarget && deleteMutation.mutate(deleteTarget.user_id)}
          >
            <Trash2 className="w-4 h-4 mr-2" />
            Удалить
          </Button>
        </div>
      </Modal>
    </div>
  );
}
