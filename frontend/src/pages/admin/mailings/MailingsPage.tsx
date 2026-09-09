import { useState } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { Mail } from 'lucide-react';
import { toast } from 'sonner';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Badge } from '@/components/ui/Badge';
import { adminApi } from '@/services/adminApi';

export default function MailingsPage() {
  const [testEmail, setTestEmail] = useState('');

  const { data: status } = useQuery({
    queryKey: ['email-status'],
    queryFn: adminApi.getEmailStatus,
  });

  const testMutation = useMutation({
    mutationFn: () => adminApi.sendTestEmail(testEmail),
    onSuccess: () => {
      toast.success(`Тестовое письмо отправлено на ${testEmail}`);
      setTestEmail('');
    },
    onError: () => toast.error('Ошибка отправки — проверьте SMTP-настройки'),
  });

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-1">Рассылки</h1>
      <p className="text-gray-600 mb-6">
        Отправка отчётов на email респондентов и проверка SMTP-конфигурации
      </p>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 max-w-4xl">
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Mail className="w-5 h-5 text-primary-600" />
            SMTP-конфигурация
          </h2>
          {status ? (
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600">Состояние</span>
                <Badge variant={status.configured ? 'success' : 'warning'}>
                  {status.configured ? 'настроена' : 'не настроена'}
                </Badge>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Сервер</span>
                <span className="font-mono">{status.host}:{status.port}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Отправитель</span>
                <span className="font-mono">{status.from_email}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">TLS</span>
                <span>{status.use_tls ? 'да' : 'нет'}</span>
              </div>
            </div>
          ) : (
            <p className="text-gray-400">Загрузка…</p>
          )}
        </div>

        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h2 className="text-lg font-semibold mb-4">Проверка отправки</h2>
          <p className="text-sm text-gray-600 mb-4">
            Отправляет тестовое письмо с платформы на указанный адрес.
          </p>
          <Input
            placeholder="email@example.com"
            value={testEmail}
            onChange={(e) => setTestEmail(e.target.value)}
          />
          <Button
            className="mt-4 w-full"
            disabled={!testEmail.includes('@') || testMutation.isPending}
            onClick={() => testMutation.mutate()}
          >
            {testMutation.isPending ? 'Отправка…' : 'Отправить тестовое письмо'}
          </Button>
        </div>
      </div>

      <p className="text-xs text-gray-500 mt-4 max-w-4xl">
        Массовые рассылки появятся после подключения продового SMTP-провайдера
        (Yandex Cloud Postbox — задача EMAIL-1 в бэклоге). Сейчас используется
        текущая SMTP-конфигурация платформы.
      </p>
    </div>
  );
}
