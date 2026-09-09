import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Search } from 'lucide-react';
import { format } from 'date-fns';
import { Table } from '@/components/ui/Table';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { adminApi, User } from '@/services/adminApi';

export default function UsersPage() {
  const [search, setSearch] = useState('');

  const { data, isLoading } = useQuery({
    queryKey: ['users'],
    queryFn: adminApi.listUsers,
  });

  const users: User[] = (data?.items || []).filter((u) =>
    search
      ? u.email.toLowerCase().includes(search.toLowerCase()) ||
        (u.name || '').toLowerCase().includes(search.toLowerCase())
      : true
  );

  const columns = [
    {
      key: 'email',
      header: 'Email',
      render: (u: User) => <span className="font-medium">{u.email}</span>,
    },
    {
      key: 'name',
      header: 'Имя',
      render: (u: User) => u.name || '—',
    },
    {
      key: 'audits_count',
      header: 'Аудитов',
      render: (u: User) => (
        <span className="font-bold text-primary-600">{u.audits_count}</span>
      ),
    },
    {
      key: 'test_audits',
      header: 'Тестовых',
      render: (u: User) =>
        u.test_audits > 0 ? (
          <Badge variant="warning">{u.test_audits}</Badge>
        ) : (
          <span className="text-gray-400">—</span>
        ),
    },
    {
      key: 'last_seen',
      header: 'Последний аудит',
      render: (u: User) =>
        u.last_seen ? format(new Date(u.last_seen), 'dd.MM.yyyy HH:mm') : '—',
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
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Пользователи</h1>
          <p className="text-gray-600 mt-1">
            Респонденты аудитов: {data?.total || 0} адресов
          </p>
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
          columns={columns}
          data={users}
          keyExtractor={(u) => u.email}
          isLoading={isLoading}
          emptyMessage="Пользователи не найдены"
        />
      </div>

      <p className="text-xs text-gray-500 mt-3">
        Учётные записи администраторов управляются в Keycloak (realm ai-maturity).
        Инвайт новых администраторов — через консоль Keycloak.
      </p>
    </div>
  );
}
