import { useQuery } from '@tanstack/react-query';
import { format } from 'date-fns';
import { Table } from '@/components/ui/Table';
import { Badge } from '@/components/ui/Badge';
import { adminApi } from '@/services/adminApi';

export default function AuditLogPage() {
  const { data: logs, isLoading } = useQuery({
    queryKey: ['audit-log'],
    queryFn: () => adminApi.getAuditLog({ limit: 200 }),
  });

  const columns = [
    {
      key: 'timestamp',
      header: 'Время',
      render: (l: any) =>
        format(new Date(l.timestamp), 'dd.MM.yyyy HH:mm:ss'),
      className: 'w-48',
    },
    {
      key: 'user_email',
      header: 'Пользователь',
      render: (l: any) => l.user_email,
    },
    {
      key: 'action',
      header: 'Действие',
      render: (l: any) => <Badge variant="info">{l.action}</Badge>,
    },
    {
      key: 'resource_type',
      header: 'Ресурс',
      render: (l: any) => (
        <span className="text-sm">
          {l.resource_type}
          {l.resource_id !== '*' && (
            <span className="text-gray-500 ml-1">
              ({l.resource_id.slice(0, 8)}...)
            </span>
          )}
        </span>
      ),
    },
    {
      key: 'success',
      header: 'Результат',
      render: (l: any) => (
        <Badge variant={l.success ? 'success' : 'danger'}>
          {l.success ? '✓' : '✗'}
        </Badge>
      ),
    },
  ];

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Журнал действий</h1>
        <p className="text-gray-600 mt-1">Аудит всех действий администраторов</p>
      </div>

      <Table
        columns={columns}
        data={logs || []}
        keyExtractor={(l, i) => `${l.timestamp}-${i}`}
        isLoading={isLoading}
        emptyMessage="Журнал пуст"
      />
    </div>
  );
}