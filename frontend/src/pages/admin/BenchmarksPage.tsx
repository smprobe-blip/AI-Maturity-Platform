import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { RefreshCw, Pencil } from 'lucide-react';
import { toast } from 'sonner';
import { Table } from '@/components/ui/Table';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Badge } from '@/components/ui/Badge';
import { Modal } from '@/components/ui/Modal';
import { adminApi, Benchmark } from '@/services/adminApi';

type EditForm = {
  mean_score: string;
  median_score: string;
  std_dev: string;
  percentile_25: string;
  percentile_75: string;
};

export default function BenchmarksPage() {
  const queryClient = useQueryClient();
  const [editTarget, setEditTarget] = useState<Benchmark | null>(null);
  const [editForm, setEditForm] = useState<EditForm>({
    mean_score: '', median_score: '', std_dev: '', percentile_25: '', percentile_75: '',
  });

  const { data: benchmarks, isLoading } = useQuery({
    queryKey: ['benchmarks'],
    queryFn: adminApi.listBenchmarks,
  });

  const recalcMutation = useMutation({
    mutationFn: adminApi.recalculateBenchmarks,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['benchmarks'] });
      toast.success('Бенчмарки пересчитаны по накопленным аудитам');
    },
    onError: () => toast.error('Ошибка пересчёта'),
  });

  const editMutation = useMutation({
    mutationFn: (vars: { industry: string; payload: Record<string, number | null> }) =>
      adminApi.updateBenchmark(vars.industry, vars.payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['benchmarks'] });
      toast.success('Бенчмарк сохранён (ручная правка)');
      setEditTarget(null);
    },
    onError: () => toast.error('Ошибка сохранения'),
  });

  const openEdit = (b: Benchmark) => {
    setEditTarget(b);
    setEditForm({
      mean_score: b.mean_score?.toString() ?? '',
      median_score: b.median_score?.toString() ?? '',
      std_dev: b.std_dev?.toString() ?? '',
      percentile_25: b.percentile_25?.toString() ?? '',
      percentile_75: b.percentile_75?.toString() ?? '',
    });
  };

  const numOrNull = (v: string) => (v.trim() === '' ? null : Number(v));

  const columns = [
    {
      key: 'industry',
      header: 'Отрасль',
      render: (b: Benchmark) => (
        <span className="font-medium">
          {b.industry}{' '}
          {b.manual && <Badge variant="warning">ручная правка</Badge>}
        </span>
      ),
    },
    {
      key: 'sample_size',
      header: 'Выборка',
      render: (b: Benchmark) => <span className="font-mono text-sm">{b.sample_size ?? '—'}</span>,
    },
    {
      key: 'mean_score',
      header: 'Среднее',
      render: (b: Benchmark) => (
        <span className="font-bold text-primary-600">{b.mean_score?.toFixed(2) ?? '—'}</span>
      ),
    },
    {
      key: 'median_score',
      header: 'Медиана',
      render: (b: Benchmark) => b.median_score?.toFixed(2) ?? '—',
    },
    {
      key: 'std_dev',
      header: 'Std Dev',
      render: (b: Benchmark) => b.std_dev?.toFixed(2) ?? '—',
    },
    {
      key: 'range',
      header: 'Диапазон (25–75)',
      render: (b: Benchmark) => (
        <span className="text-sm text-gray-600">
          {b.percentile_25 != null && b.percentile_75 != null
            ? `${b.percentile_25.toFixed(2)} — ${b.percentile_75.toFixed(2)}`
            : '—'}
        </span>
      ),
    },
    {
      key: 'actions',
      header: '',
      render: (b: Benchmark) => (
        <Button variant="secondary" className="!px-2 !py-1" title="Редактировать" onClick={() => openEdit(b)}>
          <Pencil className="w-4 h-4" />
        </Button>
      ),
    },
  ];

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Бенчмарки</h1>
          <p className="text-gray-600 mt-1">
            Композитный балл по отраслям; расчёт по накопленным аудитам, ручная правка сохраняется
          </p>
        </div>
        <Button onClick={() => recalcMutation.mutate()} disabled={recalcMutation.isPending}>
          <RefreshCw className={`w-4 h-4 mr-2 ${recalcMutation.isPending ? 'animate-spin' : ''}`} />
          Пересчитать
        </Button>
      </div>

      <Table
        columns={columns}
        data={benchmarks || []}
        keyExtractor={(b) => b.industry}
        isLoading={isLoading}
        emptyMessage="Бенчмарки не рассчитаны"
      />

      <Modal isOpen={!!editTarget} onClose={() => setEditTarget(null)} title={`Бенчмарк: ${editTarget?.industry ?? ''}`}>
        <p className="text-sm text-gray-500 mb-4">
          Пустое значение — вернуться к автоматическому расчёту (нужно ≥ 4 наблюдения).
        </p>
        <div className="grid grid-cols-2 gap-4 mb-6">
          <Input label="Среднее" value={editForm.mean_score} onChange={(e) => setEditForm({ ...editForm, mean_score: e.target.value })} />
          <Input label="Медиана" value={editForm.median_score} onChange={(e) => setEditForm({ ...editForm, median_score: e.target.value })} />
          <Input label="Std Dev" value={editForm.std_dev} onChange={(e) => setEditForm({ ...editForm, std_dev: e.target.value })} />
          <Input label="Перцентиль 25" value={editForm.percentile_25} onChange={(e) => setEditForm({ ...editForm, percentile_25: e.target.value })} />
          <Input label="Перцентиль 75" value={editForm.percentile_75} onChange={(e) => setEditForm({ ...editForm, percentile_75: e.target.value })} />
        </div>
        <div className="flex justify-end gap-3">
          <Button variant="secondary" onClick={() => setEditTarget(null)}>Отмена</Button>
          <Button
            onClick={() =>
              editTarget &&
              editMutation.mutate({
                industry: editTarget.industry,
                payload: {
                  mean_score: numOrNull(editForm.mean_score),
                  median_score: numOrNull(editForm.median_score),
                  std_dev: numOrNull(editForm.std_dev),
                  percentile_25: numOrNull(editForm.percentile_25),
                  percentile_75: numOrNull(editForm.percentile_75),
                },
              })
            }
            disabled={editMutation.isPending}
          >
            Сохранить
          </Button>
        </div>
      </Modal>
    </div>
  );
}
