import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { FileText, Download, Sparkles } from 'lucide-react';
import { adminApi } from '@/services/adminApi';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { Table } from '@/components/ui/Table';
import { toast } from 'sonner';

interface ReportFile {
  filename: string;
  kind: 'dissertation' | 'audit';
  size_bytes: number;
  created_at: string;
}

const formatSize = (b: number) =>
  b > 1024 * 1024 ? `${(b / 1024 / 1024).toFixed(1)} МБ` : `${Math.max(1, Math.round(b / 1024))} КБ`;

export default function ReportsPage() {
  const queryClient = useQueryClient();

  const { data, isLoading } = useQuery({
    queryKey: ['reports'],
    queryFn: adminApi.getReports,
  });

  const generateMutation = useMutation({
    mutationFn: adminApi.generateDissertationReport,
    onSuccess: () => {
      toast.success('Диссертационный отчет сгенерирован');
      queryClient.invalidateQueries({ queryKey: ['reports'] });
    },
    onError: () => toast.error('Ошибка генерации'),
  });

  const download = async (filename: string) => {
    try {
      const blob = await adminApi.downloadReport(filename);
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      a.click();
      URL.revokeObjectURL(url);
    } catch {
      toast.error('Ошибка скачивания');
    }
  };

  const items: ReportFile[] = data?.items || [];

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Отчеты</h1>
        <Button
          onClick={() => generateMutation.mutate()}
          disabled={generateMutation.isPending}
          className="flex items-center gap-2"
        >
          <Sparkles className="w-4 h-4" />
          Сгенерировать диссертационный отчет
        </Button>
      </div>

      {items.length === 0 && !isLoading ? (
        <div className="bg-white rounded-lg border border-gray-200 p-8 text-center">
          <FileText className="w-10 h-10 text-gray-300 mx-auto mb-3" />
          <p className="text-gray-600">
            Отчетов пока нет. Сгенерируйте диссертационный отчет или пройдите диагностику —
            PDF появится в библиотеке автоматически.
          </p>
        </div>
      ) : (
        <div className="bg-white rounded-lg border border-gray-200">
          <Table
            columns={[
              {
                key: 'filename',
                header: 'Файл',
                render: (r: ReportFile) => (
                  <span className="flex items-center gap-2">
                    <FileText className="w-4 h-4 text-primary-600" />
                    <span className="font-medium">{r.filename}</span>
                  </span>
                ),
              },
              {
                key: 'kind',
                header: 'Тип',
                render: (r: ReportFile) => (
                  <Badge variant={r.kind === 'dissertation' ? 'success' : 'info'}>
                    {r.kind === 'dissertation' ? 'Диссертационный' : 'Аудит'}
                  </Badge>
                ),
              },
              {
                key: 'created_at',
                header: 'Создан',
                render: (r: ReportFile) => new Date(r.created_at).toLocaleString('ru-RU'),
              },
              {
                key: 'size_bytes',
                header: 'Размер',
                render: (r: ReportFile) => <span className="font-mono text-sm">{formatSize(r.size_bytes)}</span>,
              },
              {
                key: 'actions',
                header: '',
                render: (r: ReportFile) => (
                  <Button variant="secondary" size="sm" onClick={() => download(r.filename)}>
                    <Download className="w-4 h-4 mr-2" />
                    Скачать
                  </Button>
                ),
              },
            ]}
            data={items}
            keyExtractor={(r) => r.filename}
            isLoading={isLoading}
            emptyMessage="Отчеты не найдены"
          />
        </div>
      )}
    </div>
  );
}
