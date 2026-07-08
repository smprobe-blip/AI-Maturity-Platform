import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { RefreshCw, Download } from 'lucide-react';
import { toast } from 'sonner';
import { Table } from '@/components/ui/Table';
import { Button } from '@/components/ui/Button';
import { adminApi, Benchmark } from '@/services/adminApi';

export default function BenchmarksPage() {
  const queryClient = useQueryClient();

  const { data: benchmarks, isLoading } = useQuery({
    queryKey: ['benchmarks'],
    queryFn: adminApi.listBenchmarks,
  });

  const recalcMutation = useMutation({
    mutationFn: adminApi.recalculateBenchmarks,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['benchmarks'] });
      toast.success('Бенчмарки пересчитаны');
    },
    onError: () => toast.error('Ошибка пересчёта'),
  });

  const columns = [
    { key: 'industry', header: 'Отрасль' },
    {
      key: 'sample_size',
      header: 'Выборка',
      render: (b: Benchmark) => (
        <span className="font-mono text-sm">{b.sample_size}</span>
      ),
    },
    {
      key: 'mean_score',
      header: 'Среднее',
      render: (b: Benchmark) => (
        <span className="font-bold text-primary-600">
          {b.mean_score?.toFixed(2)}
        </span>
      ),
    },
    {
      key: 'median_score',
      header: 'Медиана',
      render: (b: Benchmark) => b.median_score?.toFixed(2),
    },
    {
      key: 'std_dev',
      header: 'Std Dev',
      render: (b: Benchmark) => b.std_dev?.toFixed(2),
    },
    {
      key: 'range',
      header: 'Диапазон (25-75)',
      render: (b: Benchmark) => (
        <span className="text-sm text-gray-600">
          {b.percentile_25?.toFixed(2)} — {b.percentile_75?.toFixed(2)}
        </span>
      ),
    },
  ];

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Бенчмарки</h1>
          <p className="text-gray-600 mt-1">Отраслевые эталоны зрелости</p>
        </div>
        <Button
          onClick={() => recalcMutation.mutate()}
          disabled={recalcMutation.isPending}
        >
          <RefreshCw
            className={`w-4 h-4 mr-2 ${recalcMutation.isPending ? 'animate-spin' : ''}`}
          />
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
    </div>
  );
}