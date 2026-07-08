import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { UserPlus } from 'lucide-react';
import { toast } from 'sonner';
import { Table } from '@/components/ui/Table';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Select } from '@/components/ui/Select';
import { Badge } from '@/components/ui/Badge';
import { Modal } from '@/components/ui/Modal';
import { adminApi, User } from '@/services/adminApi';

const ROLES = [
  { value: 'super_admin', label: 'Super Admin' },
  { value: 'facilitator', label: 'Facilitator' },
  { value: 'analyst', label: 'Analyst' },
  { value: 'sales', label: 'Sales' },
  { value: 'auditor', label: 'Auditor' },
  { value: 'client', label: 'Client' },
];

export default function UsersPage() {
  const queryClient = useQueryClient();
  const [isInviteOpen, setIsInviteOpen] = useState(false);
  const [form, setForm] = useState({
    email: '',
    first_name: '',
    last_name: '',
    role: 'analyst',
  });

  const { data: users, isLoading } = useQuery({
    queryKey: ['users'],
    queryFn: adminApi.listUsers,
  });

  const inviteMutation = useMutation({
    mutationFn: () => adminApi.inviteUser(form),
    onSuccess: () => {
      toast.success(`Пользователь ${form.email} приглашён`);
      queryClient.invalidateQueries({ queryKey: ['users'] });
      setIsInviteOpen(false);
      setForm({ email: '', first_name: '', last_name: '', role: 'analyst' });
    },
    onError: () => toast.error('Ошибка приглашения'),
  });

  const columns = [
    {
      key: 'email',
      header: 'Email',
      render: (u: User) => (
        <div>
          <div className="font-medium">{u.email}</div>
          <div className="text-xs text-gray-500">{u.user_id.slice(0, 8)}...</div>
        </div>
      ),
    },
    {
      key: 'role',
      header: 'Роль',
      render: (u: User) => (
        <Badge
          variant={
            u.role === 'super_admin'
              ? 'danger'
              : u.role === 'facilitator'
              ? 'warning'
              : 'info'
          }
        >
          {u.role}
        </Badge>
      ),
    },
    {
      key: 'invited_at',
      header: 'Приглашён',
      render: (u: User) =>
        u.invited_at
          ? new Date(u.invited_at).toLocaleDateString('ru-RU')
          : '—',
    },
  ];

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Пользователи</h1>
          <p className="text-gray-600 mt-1">Управление доступом к платформе</p>
        </div>
        <Button onClick={() => setIsInviteOpen(true)}>
          <UserPlus className="w-4 h-4 mr-2" />
          Пригласить
        </Button>
      </div>

      <Table
        columns={columns}
        data={users || []}
        keyExtractor={(u) => u.user_id}
        isLoading={isLoading}
        emptyMessage="Пользователей пока нет"
      />

      <Modal
        isOpen={isInviteOpen}
        onClose={() => setIsInviteOpen(false)}
        title="Пригласить пользователя"
      >
        <div className="space-y-4">
          <Input
            label="Email"
            type="email"
            value={form.email}
            onChange={(e) => setForm({ ...form, email: e.target.value })}
            placeholder="user@company.com"
          />
          <div className="grid grid-cols-2 gap-4">
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
          </div>
          <Select
            label="Роль"
            value={form.role}
            onChange={(e) => setForm({ ...form, role: e.target.value })}
            options={ROLES}
          />

          <div className="flex justify-end gap-3 pt-4 border-t">
            <Button variant="secondary" onClick={() => setIsInviteOpen(false)}>
              Отмена
            </Button>
            <Button
              onClick={() => inviteMutation.mutate()}
              disabled={inviteMutation.isPending || !form.email}
            >
              {inviteMutation.isPending ? 'Отправка...' : 'Пригласить'}
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
}