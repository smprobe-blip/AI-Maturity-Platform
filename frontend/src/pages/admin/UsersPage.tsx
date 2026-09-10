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
  const [invited, setInvited] = useState<{ email: string; temp_password: string } | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<{ user_id: string; email: string } | null>(null);

  const { data: operators } = useQuery({
    queryKey: ['keycloak-users'],
    queryFn: adminApi.listKeycloakUsers,
  });

  const { data, isLoading } = useQuery({
    queryKey: ['users'],
    queryFn: adminApi.listUsers,
  });

  const inviteMutation = useMutation({
    mutationFn: adminApi.inviteOperator,
    onSuccess: (res) => {
      queryClient.invalidateQueries({ queryKey: ['keycloak-users'] });
      setInvited({ email: res.email, temp_password: res.temp_password });
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
        </div>
        <div className="flex justify-end gap-3">
          <Button variant="secondary" onClick={() => setInviteOpen(false)}>
            Отмена
          </Button>
          <Button
            variant="danger"
            disabled={!form.email.includes('@') || inviteMutation.isPending}
            onClick={() => inviteMutation.mutate(form)}
          >
            Создать
          </Button>
        </div>
      </Modal>

      {/* Temp password modal */}
      <Modal isOpen={!!invited} onClose={() => setInvited(null)} title="Оператор создан">
        <p className="text-gray-600 mb-4">
          Временный пароль для <strong>{invited?.email}</strong> — покажите его один раз,
          оператор сменит его при первом входе:
        </p>
        <div className="bg-gray-100 rounded p-3 font-mono text-center text-lg mb-6 select-all">
          {invited?.temp_password}
        </div>
        <div className="flex justify-end">
          <Button onClick={() => setInvited(null)}>Готово</Button>
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
