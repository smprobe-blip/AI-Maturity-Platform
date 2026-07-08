import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { format } from 'date-fns';
import { Search, Filter, Archive } from 'lucide-react';
import { toast } from 'sonner';
import { Table } from '@/components/ui/Table';
import { Badge, getMaturityBadgeVariant } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { Select } from '@/components/ui/Select';
import { Modal } from '@/components/ui/Modal';
import { adminApi, Audit } from '@/services/adminApi';
import { INDUSTRIES } from '@/utils/constants';

export default function AuditsListPage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [search, setSearch] = useState('');
  const [industry, setIndustry] = useState('');
  const [status, setStatus] = useState('');
  const [archiveTarget, setArchiveTarget] = useState<Audit | null>(null);

  const { data, isLoading } = useQuery({
    queryKey: ['audits', { industry, status }],
    queryFn: () =>
      adminApi.listAudits({
        industry: industry || undefined,
        status: status || undefined,
        limit: 100,
      }),
  });

  const archiveMutation = useMutation({
    mutationFn: adminApi.archiveAudit,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['audits'] });
      toast.success('Аудит архивирован');
      setArchiveTarget(null);
    },
    onError: () => toast.error('Ошибка архивации'),
  });

  const audits: Audit[] = (data?.items || []).filter((a: Audit) =>
    !search ||
    a.contact?.email?.toLowerCase().includes(search.toLowerCase()) ||
    a.company_profile?.industry?.toLowerCase().includes(search.toLowerCase()) ||
    a.audit_id.includes(search)
  );

  const columns = [
    {
      key: 'created_at',
      header: 'Дата',
      render: (a: Audit) =>
        format(new Date(a.created_at), 'dd.MM.yyyy HH:mm'),
      className: 'w-40',
    },
    {
      key: 'industry',
      header: 'Отрасль',
      render: (a: Audit) => a.company_profile?.industry || '—',
    },
    {
      key: 'size',
      header: 'Размер',
      render: (a: Audit) => a.company_profile?.company_size || '—',
    },
    {
      key: 'email',
      header: 'Email',
      render: (a: Audit) => (
        <span className="text-sm text-gray-600">{a.contact?.email}</span>
      ),
    },
    {
      key: 'score',
      header: 'Оценка',
      render: (a: Audit) => (
        <span className="font-bold text-primary-600">
          {a.calculated_indices?.composite_score?.toFixed(2)}
        </span>
      ),
    },
    {
      key: 'level',
      header: 'Уровень',
      render: (a: Audit) => (
        <Badge variant={getMaturityBadgeVariant(a.calculated_indices?.maturity_level || '')}>
          {a.calculated_indices?.maturity_level}
        </Badge>
      ),
    },
    {
      key: 'status',
      header: 'Статус',
      render: (a: Audit) => (
        <Badge
          variant={
            a.status === 'completed'
              ? 'success'
              : a.status === 'archived'
              ? 'neutral'
              : 'warning'
          }
        >
          {a.status}
        </Badge>
      ),
    },
  ];

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Аудиты</h1>
          <p className="text-gray-600 mt-1">
            Всего: {audits.length} записей
          </p>
        </div>
      </div>

      {/* Filters */}
      <div className="card mb-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              placeholder="Поиск..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-primary-500"
            />
          </div>

          <Select
            label="Отрасль"
            value={industry}
            onChange={(e) => setIndustry(e.target.value)}
            options={[
              { value: '', label: 'Все отрасли' },
              ...INDUSTRIES.map((i) => ({ value: i, label: i })),
            ]}
          />

          <Select
            label="Статус"
            value={status}
            onChange={(e) => setStatus(e.target.value)}
            options={[
              { value: '', label: 'Все статусы' },
              { value: 'completed', label: 'Завершённые' },
              { value: 'archived', label: 'Архивные' },
            ]}
          />

          <div className="flex items-end">
            <Button
              variant="secondary"
              onClick={() => {
                setSearch('');
                setIndustry('');
                setStatus('');
              }}
              className="w-full"
            >
              <Filter className="w-4 h-4 mr-2" />
              Сбросить
            </Button>
          </div>
        </div>
      </div>

      <Table
        columns={columns}
        data={audits}
        keyExtractor={(a) => a.audit_id}
        onRowClick={(a) => navigate(`/admin/audits/${a.audit_id}`)}
        isLoading={isLoading}
        emptyMessage="Аудиты не найдены"
      />

      {/* Archive modal */}
      <Modal
        isOpen={!!archiveTarget}
        onClose={() => setArchiveTarget(null)}
        title="Архивировать аудит?"
      >
        <p className="text-gray-600 mb-6">
          Аудит <strong>{archiveTarget?.audit_id.slice(0, 8)}...</strong> будет
          перемещён в архив. Это действие можно отменить.
        </p>
        <div className="flex justify-end gap-3">
          <Button variant="secondary" onClick={() => setArchiveTarget(null)}>
            Отмена
          </Button>
          <Button
            variant="danger"
            onClick={() =>
              archiveTarget && archiveMutation.mutate(archiveTarget.audit_id)
            }
          >
            <Archive className="w-4 h-4 mr-2" />
            Архивировать
          </Button>
        </div>
      </Modal>
    </div>
  );
}