import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { RefreshCw, TrendingUp, DollarSign } from 'lucide-react';
import { adminApi } from '@/services/adminApi';
import { RadarChartWithBenchmark } from '@/components/charts/RadarChartWithBenchmark';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { Select } from '@/components/ui/Select';
import benchmarksData from '@/data/benchmarks.json';

interface Audit {
  audit_id: string;
  company_profile: {
    industry: string;
    company_size: string;
  };
  contact: {
    name: string;
    email: string;
  };
  calculated_indices: {
    composite_score: number;
    maturity_level: string;
    dimension_scores: Record<string, number>;
  };
}

export default function RadarPage() {
  const navigate = useNavigate();
  const [audits, setAudits] = useState<Audit[]>([]);
  const [filteredAudits, setFilteredAudits] = useState<Audit[]>([]);
  const [selectedAuditId, setSelectedAuditId] = useState<string>('');
  const [selectedIndustry, setSelectedIndustry] = useState<string>('');
  const [selectedAudit, setSelectedAudit] = useState<Audit | null>(null);
  const [loading, setLoading] = useState(false);

  // Загрузка аудитов
  useEffect(() => {
    const loadAudits = async () => {
      try {
        const data = await adminApi.listAudits({ limit: 100 });
        const items = data.items || [];
        setAudits(items);
        setFilteredAudits(items);
      } catch (error) {
        console.error('Failed to load audits:', error);
      }
    };
    loadAudits();
  }, []);

  // Фильтрация по отрасли
  useEffect(() => {
    if (selectedIndustry) {
      const filtered = audits.filter(
        (audit) => audit.company_profile.industry === selectedIndustry
      );
      setFilteredAudits(filtered);
      setSelectedAuditId(''); // Сброс выбранного аудита
      setSelectedAudit(null);
    } else {
      setFilteredAudits(audits);
    }
  }, [selectedIndustry, audits]);

  // Загрузка данных выбранного аудита
  useEffect(() => {
    if (!selectedAuditId) return;

    const loadAudit = async () => {
      setLoading(true);
      try {
        const audit = await adminApi.getAudit(selectedAuditId);
        setSelectedAudit(audit);
      } catch (error) {
        console.error('Failed to load audit:', error);
      } finally {
        setLoading(false);
      }
    };
    loadAudit();
  }, [selectedAuditId]);

  // Получение бенчмарка для отрасли
  const getBenchmark = () => {
    if (!selectedAudit) return null;
    const industry = selectedAudit.company_profile.industry;
    return benchmarksData.benchmarks[industry] || benchmarksData.benchmarks.CrossIndustry;
  };

  // Расчет NPV
  const calculateNPV = () => {
    if (!selectedAudit) return 0;
    const score = selectedAudit.calculated_indices.composite_score;
    // Примерная формула: NPV = (score / 5) * 10 млн руб
    return ((score / 5) * 10).toFixed(2);
  };

  // Подготовка данных для радара
  const getRadarData = () => {
    if (!selectedAudit) return [];

    const currentScores = selectedAudit.calculated_indices.dimension_scores;
    const benchmark = getBenchmark();

    // Оси из benchmarks.json
    return benchmarksData.axes.map((axis: any) => {
      const current = currentScores[axis.key] || 0;
      const target = Math.min(current + 1.0, 5.0); // Целевое = текущее + 1 (макс 5)
      const bench = benchmark ? (benchmark[axis.key] || 0) : 2.5;

      return {
        axis: axis.label,
        key: axis.key,
        current: current,
        target: target,
        benchmark: bench,
        weight: axis.weight,
      };
    });
  };

  const radarData = getRadarData();

  // Получение уникальных отраслей из загруженных аудитов
  const uniqueIndustries = Array.from(
    new Set(audits.map((a) => a.company_profile.industry))
  ).sort();

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">🎯 AI Maturity Radar</h1>
          <p className="text-gray-600 mt-1">Визуализация профиля зрелости ИИ</p>
        </div>
        <div className="flex gap-2">
          <Button variant="secondary" onClick={() => navigate('/admin')}>
             Главная
          </Button>
          <Button variant="secondary" onClick={() => navigate('/admin/audits')}>
            📋 Аудиты
          </Button>
        </div>
      </div>

      {/* Controls */}
      <div className="bg-white rounded-lg border border-gray-200 p-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Select
            label="Отрасль"
            value={selectedIndustry}
            onChange={(e) => setSelectedIndustry(e.target.value)}
            options={[
              { value: '', label: 'Все отрасли' },
              ...uniqueIndustries.map((ind) => ({
                value: ind,
                label: ind,
              })),
            ]}
          />
          <Select
            label="Аудит"
            value={selectedAuditId}
            onChange={(e) => setSelectedAuditId(e.target.value)}
            options={[
              { value: '', label: 'Выберите аудит...' },
              ...filteredAudits.map((audit) => ({
                value: audit.audit_id,
                label: `${audit.contact.name || audit.company_profile.industry} - ${audit.company_profile.company_size}`,
              })),
            ]}
          />
        </div>
      </div>

      {loading && (
        <div className="flex justify-center items-center h-64">
          <RefreshCw className="w-8 h-8 animate-spin text-primary-600" />
        </div>
      )}

      {!loading && selectedAudit && (
        <>
          {/* Radar Chart */}
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-lg font-semibold text-gray-900">
                Профиль зрелости компании
              </h2>
              <div className="flex gap-2">
                <Badge variant="primary">Текущее состояние</Badge>
                <Badge variant="warning">Целевое состояние</Badge>
                <Badge variant="success">Отраслевой бенчмарк</Badge>
              </div>
            </div>

            <RadarChartWithBenchmark
              audit={selectedAudit}
            />

            {/* Financial Impact */}
            <div className="mt-6 p-4 bg-gradient-to-r from-primary-50 to-blue-50 rounded-lg border border-primary-200">
              <div className="flex items-center gap-3">
                <DollarSign className="w-6 h-6 text-primary-600" />
                <div>
                  <p className="text-sm text-gray-600">
                    💰 Финансовый эффект от прироста индекса на 1.0
                  </p>
                  <p className="text-2xl font-bold text-primary-700">
                    {calculateNPV()} млн ₽
                  </p>
                  <p className="text-xs text-gray-500">
                    NPV (чистая приведённая стоимость)
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Details by Axis */}
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">
               Детализация по осям
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {radarData.map((item) => (
                <div
                  key={item.key}
                  className="p-4 border border-gray-200 rounded-lg hover:shadow-md transition-shadow"
                >
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="font-semibold text-gray-900">{item.axis}</h3>
                    <Badge variant="neutral">{(item.weight * 100).toFixed(0)}%</Badge>
                  </div>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Текущее:</span>
                      <span className="font-semibold text-primary-600">
                        {item.current.toFixed(2)}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Целевое:</span>
                      <span className="font-semibold text-warning-600">
                        {item.target.toFixed(2)}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Бенчмарк:</span>
                      <span className="font-semibold text-success-600">
                        {item.benchmark.toFixed(2)}
                      </span>
                    </div>
                  </div>
                  <div className="mt-3 pt-3 border-t border-gray-200">
                    <div className="flex items-center gap-2 text-xs text-gray-500">
                      <TrendingUp className="w-3 h-3" />
                      <span>Gap: {(item.target - item.current).toFixed(2)}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </>
      )}

      {!loading && !selectedAudit && (
        <div className="bg-white rounded-lg border border-gray-200 p-12 text-center">
          <p className="text-gray-500">Выберите аудит для просмотра радарной диаграммы</p>
        </div>
      )}
    </div>
  );
}