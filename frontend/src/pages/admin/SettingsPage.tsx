import { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Save } from 'lucide-react';
import { toast } from 'sonner';
import { Tabs } from '@/components/ui/Tabs';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { adminApi, Methodology } from '@/services/adminApi';

export default function SettingsPage() {
  const queryClient = useQueryClient();
  const [activeTab, setActiveTab] = useState('methodology');
  const [weights, setWeights] = useState<Record<string, number>>({});

  const { data: methodology } = useQuery({
    queryKey: ['methodology'],
    queryFn: adminApi.getMethodology,
  });

  const { data: integrations } = useQuery({
    queryKey: ['integrations'],
    queryFn: adminApi.getIntegrations,
  });

  const [intForm, setIntForm] = useState<Record<string, any>>({});

  useEffect(() => {
    if (methodology?.weights) setWeights(methodology.weights);
  }, [methodology]);

  useEffect(() => {
    if (integrations) setIntForm(integrations);
  }, [integrations]);

  const updateMethodology = useMutation({
    mutationFn: () => adminApi.updateMethodology({ weights }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['methodology'] });
      toast.success('Методология обновлена');
    },
    onError: (err: any) => toast.error(err.response?.data?.error?.message || 'Ошибка'),
  });

  const updateIntegrations = useMutation({
    mutationFn: () => adminApi.updateIntegrations(intForm),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['integrations'] });
      toast.success('Интеграции обновлены');
    },
  });

  const totalWeight = Object.values(weights).reduce((s, v) => s + (v || 0), 0);

  const tabs = [
    { id: 'methodology', label: 'Методология' },
    { id: 'integrations', label: 'Интеграции' },
  ];

  const dimensionNames: Record<string, string> = {
    '1': 'Strategy & Vision',
    '2': 'Data & Analytics',
    '3': 'Technology',
    '4': 'Processes',
    '5': 'People & Skills',
    '6': 'Culture & Change',
    '7': 'Ethics & Governance',
  };

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Настройки</h1>
        <p className="text-gray-600 mt-1">Конфигурация платформы</p>
      </div>

      <div className="card">
        <Tabs tabs={tabs} activeTab={activeTab} onChange={setActiveTab} />

        <div className="mt-6">
          {activeTab === 'methodology' && (
            <div>
              <div className="mb-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold">Веса осей</h3>
                  <div
                    className={`text-sm font-semibold ${
                      Math.abs(totalWeight - 1) < 0.01
                        ? 'text-green-600'
                        : 'text-red-600'
                    }`}
                  >
                    Сумма: {totalWeight.toFixed(2)}{' '}
                    {Math.abs(totalWeight - 1) < 0.01 ? '✓' : '(должно быть 1.00)'}
                  </div>
                </div>

                <div className="space-y-3">
                  {Object.entries(weights).map(([dimId, weight]) => (
                    <div
                      key={dimId}
                      className="flex items-center gap-4 p-3 bg-gray-50 rounded-lg"
                    >
                      <div className="flex-1">
                        <div className="font-medium text-sm">
                          Ось {dimId}: {dimensionNames[dimId]}
                        </div>
                      </div>
                      <input
                        type="number"
                        step="0.01"
                        min="0"
                        max="1"
                        value={weight}
                        onChange={(e) =>
                          setWeights({
                            ...weights,
                            [dimId]: parseFloat(e.target.value) || 0,
                          })
                        }
                        className="w-24 px-3 py-2 border border-gray-300 rounded-lg text-right"
                      />
                    </div>
                  ))}
                </div>
              </div>

              <Button
                onClick={() => updateMethodology.mutate()}
                disabled={Math.abs(totalWeight - 1) > 0.01 || updateMethodology.isPending}
              >
                <Save className="w-4 h-4 mr-2" />
                Сохранить методологию
              </Button>
            </div>
          )}

          {activeTab === 'integrations' && (
            <div className="space-y-6">
              <div className="p-4 border border-gray-200 rounded-lg">
                <h3 className="font-semibold mb-3">Baserow CRM</h3>
                <div className="space-y-3">
                  <Input
                    label="URL"
                    value={intForm.baserow?.url || ''}
                    onChange={(e) =>
                      setIntForm({
                        ...intForm,
                        baserow: { ...intForm.baserow, url: e.target.value },
                      })
                    }
                  />
                  <Input
                    label="API Token"
                    type="password"
                    value={intForm.baserow?.api_token || ''}
                    onChange={(e) =>
                      setIntForm({
                        ...intForm,
                        baserow: { ...intForm.baserow, api_token: e.target.value },
                      })
                    }
                  />
                </div>
              </div>

              <div className="p-4 border border-gray-200 rounded-lg">
                <h3 className="font-semibold mb-3">SMTP</h3>
                <div className="space-y-3">
                  <Input
                    label="Хост"
                    value={intForm.smtp?.host || ''}
                    onChange={(e) =>
                      setIntForm({
                        ...intForm,
                        smtp: { ...intForm.smtp, host: e.target.value },
                      })
                    }
                  />
                  <Input
                    label="Порт"
                    type="number"
                    value={intForm.smtp?.port || ''}
                    onChange={(e) =>
                      setIntForm({
                        ...intForm,
                        smtp: { ...intForm.smtp, port: parseInt(e.target.value) || 0 },
                      })
                    }
                  />
                </div>
              </div>

              <Button
                onClick={() => updateIntegrations.mutate()}
                disabled={updateIntegrations.isPending}
              >
                <Save className="w-4 h-4 mr-2" />
                Сохранить интеграции
              </Button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}