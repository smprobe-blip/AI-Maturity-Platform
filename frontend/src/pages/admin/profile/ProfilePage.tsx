import { keycloak, getUserRoles } from '@/auth/keycloak';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';

const ROLE_LABELS: Record<string, string> = {
  super_admin: 'Супер-администратор',
  facilitator: 'Фасилитатор',
  analyst: 'Аналитик',
  sales: 'Продажи',
  client: 'Клиент',
  auditor: 'Аудитор',
};

export default function ProfilePage() {
  const tp = (keycloak.tokenParsed || {}) as Record<string, any>;
  const roles = getUserRoles();

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Мой профиль</h1>
      <div className="bg-white rounded-lg border border-gray-200 p-6 max-w-xl">
        <div className="flex items-center gap-4 mb-6">
          <div className="w-14 h-14 rounded-full bg-primary-600 text-white flex items-center justify-center text-xl font-bold">
            {(tp.preferred_username || tp.email || 'A').slice(0, 1).toUpperCase()}
          </div>
          <div>
            <div className="text-lg font-semibold text-gray-900">
              {tp.name || tp.preferred_username || 'Администратор'}
            </div>
            <div className="text-sm text-gray-500">{tp.email || '—'}</div>
          </div>
        </div>

        <div className="space-y-2 text-sm">
          <div className="flex justify-between border-b border-gray-100 py-2">
            <span className="text-gray-600">Логин</span>
            <span className="font-mono">{tp.preferred_username || '—'}</span>
          </div>
          <div className="flex justify-between border-b border-gray-100 py-2">
            <span className="text-gray-600">ID (Keycloak)</span>
            <span className="font-mono">{tp.sub ? tp.sub.slice(0, 8) + '…' : '—'}</span>
          </div>
          <div className="flex justify-between border-b border-gray-100 py-2">
            <span className="text-gray-600">Роли</span>
            <span className="flex gap-1 flex-wrap justify-end">
              {roles.length ? (
                roles.map((r) => (
                  <Badge key={r} variant="info">
                    {ROLE_LABELS[r] || r}
                  </Badge>
                ))
              ) : (
                <span className="text-gray-400">—</span>
              )}
            </span>
          </div>
        </div>

        <div className="mt-6 flex justify-end">
          <Button
            variant="secondary"
            onClick={() => keycloak.logout({ redirectUri: window.location.origin })}
          >
            Выйти из системы
          </Button>
        </div>
      </div>
    </div>
  );
}
