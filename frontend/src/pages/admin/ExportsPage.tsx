import { useState } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { format } from 'date-fns';
import { Download, FileText, Check } from 'lucide-react';
import { toast } from 'sonner';
import { Table } from '@/components/ui/Table';
import { Button } from '@/components/ui/Button';
import { Select } from '@/components/ui/Select';
import { Badge } from '@/components/ui/Badge';
import { Modal } from '@/components/ui/Modal';
import { adminApi, ExportRecord } from '@/services/adminApi';

const EXPORT_TYPES = [
  { value: 'audits_raw', label: 'Сырые аудиты (L0, требует NDA)' },
  { value: 'audits_aggregated', label: 'Агрегированные аудиты (L2)' },
  { value: 'benchmarks', label: 'Бенчмарки (L3)' },
  { value: 'efa_dataset', label: 'Данные для EFA (диссертация)' },
];

const FORMATS = [
  { value: 'csv', label: 'CSV' },
  { value: 'parquet', label: 'Parquet' },
  { value: 'json', label: 'JSON' },
];

export default function ExportsPage() {
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [exportType, setExportType] = useState('audits_aggregated');
  const [format, setFormat] = useState('csv');
  const [ndaSigned, setNdaSigned] = useState(false);

  const { data: history, isLoading, refetch } = useQuery({
    queryKey: ['exports'],
    queryFn: adminApi.getExportHistory,
  });

  const createMutation = useMutation({
    mutationFn: () =>
      adminApi.createExport({
        export_type: exportType,
        format,
        nda_signed: ndaSigned,
      }),
    onSuccess: () => {
      toast.success('Выгрузка создана');
      refetch();
      setIsCreateOpen(false);
      setNdaSigned(false);
    },
    onError: (err: any) => {
      toast.error(err.response?.data?.detail || 'Ошибка создания выгрузки');
    },
  });

  const handleDownload = async (exportId: string, filename: string) => {
    try {
      const blob = await adminApi.downloadExport(exportId);
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

  const columns = [
    {
      key: 'created_at',
      header: 'Дата',
      render: (e: ExportRecord) =>
        format(new Date(e.created_at), 'dd.MM.yyyy HH:mm'),
    },
    {
      key: 'export_type',
      header: 'Тип',
      render: (e: ExportRecord) => (
        <Badge variant="info">{e.export_type}</Badge>
      ),
    },
    {
      key: 'format',
      header: 'Формат',
      render: (e: ExportRecord) => e.format.toUpperCase(),
    },
    {
      key: 'row_count',
      header: 'Строк',
      render: (e: ExportRecord) => (
        <span className="font-mono">{e.row_count}</span>
      ),
    },
    {
      key: 'status',
      header: 'Статус',
      render: (e: ExportRecord) => (
        <Badge variant={e.status === 'completed' ? 'success' : 'warning'}>
          {e.status}
        </Badge>
      ),
    },
    {
      key: 'actions',
      header: '',
      render: (e: ExportRecord) => (
        <Button
          variant="secondary"
          size="sm"
          onClick={() => handleDownload(e.export_id, e.filename)}
        >
          <Download className="w-4 h-4 mr-1" />
          Скачать
        </Button>
      ),
    },
  ];

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Выгрузки</h1>
          <p className="text-gray-600 mt-1">Экспорт данных для анализа и диссертации</p>
        </div>
        <Button onClick={() => setIsCreateOpen(true)}>
          <FileText className="w-4 h-4 mr-2" />
          Создать выгрузку
        </Button>
      </div>

      <Table
        columns={columns}
        data={history || []}
        keyExtractor={(e) => e.export_id}
        isLoading={isLoading}
        emptyMessage="Выгрузок пока нет"
      />

      <Modal
        isOpen={isCreateOpen}
        onClose={() => setIsCreateOpen(false)}
        title="Новая выгрузка"
      >
        <div className="space-y-4">
          <Select
            label="Тип данных"
            value={exportType}
            onChange={(e) => {
              setExportType(e.target.value);
              if (e.target.value === 'audits_raw') setNdaSigned(false);
            }}
            options={EXPORT_TYPES}
          />

          <Select
            label="Формат"
            value={format}
            onChange={(e) => setFormat(e.target.value)}
            options={FORMATS}
          />

          {exportType === 'audits_raw' && (
            <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
              <label className="flex items-start gap-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={ndaSigned}
                  onChange={(e) => setNdaSigned(e.target.checked)}
                  className="mt-1"
                />
                <div>
                  <div className="font-semibold text-gray-900">
                    Подтверждение NDA
                  </div>
                  <div className="text-sm text-gray-600 mt-1">
                    Я подтверждаю, что имею подписанное NDA для работы с
                    персональными данными (L0). Экспорт без NDA запрещён.
                  </div>
                </div>
              </label>
            </div>
          )}

          <div className="flex justify-end gap-3 pt-4 border-t">
            <Button variant="secondary" onClick={() => setIsCreateOpen(false)}>
              Отмена
            </Button>
            <Button
              onClick={() => createMutation.mutate()}
              disabled={
                createMutation.isPending ||
                (exportType === 'audits_raw' && !ndaSigned)
              }
            >
              {createMutation.isPending ? (
                'Создание...'
              ) : (
                <>
                  <Check className="w-4 h-4 mr-2" />
                  Создать
                </>
              )}
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
}