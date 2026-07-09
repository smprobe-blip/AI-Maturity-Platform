import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, Filter, RefreshCw, TrendingUp, Users, ChevronLeft, ChevronRight } from 'lucide-react';
import { adminApi } from '@/services/adminApi';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { Select } from '@/components/ui/Select';
import { Table } from '@/components/ui/Table';
import { toast } from 'sonner';

interface Lead {
  id?: number;
  audit_id: string;
  name: string;
  email: string;
  position: string;
  industry: string;
  company_size: string;
  region: string;
  composite_score: number;
  maturity_level: string;
  roi_estimate: number;
  status: string;
  created_at: string;
}

const statusOptions = [
  { value: '', label: 'Все статусы' },
  { value: 'New', label: 'New' },
  { value: 'Contacted', label: 'Contacted' },
  { value: 'Qualified', label: 'Qualified' },
  { value: 'Converted', label: 'Converted' },
  { value: 'Lost', label: 'Lost' },
];

const safeFloat = (val: any, fallback = 0): number => {
  const num = parseFloat(val);
  return isNaN(num) ? fallback : num;
};

export default function LeadsPage() {
  const navigate = useNavigate();
  const [leads, setLeads] = useState<Lead[]>([]);
  const [filteredLeads, setFilteredLeads] = useState<Lead[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [industryFilter, setIndustryFilter] = useState('');
  
  // Пагинация
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize] = useState(10);

  const uniqueIndustries = Array.from(
    new Set(leads.map(l => l.industry).filter(Boolean))
  ).sort();

  useEffect(() => {
    loadLeads();
  }, []);

  useEffect(() => {
    let filtered = leads;
    if (search) {
      const s = search.toLowerCase();
      filtered = filtered.filter(
        lead =>
          (lead.name || '').toLowerCase().includes(s) ||
          (lead.email || '').toLowerCase().includes(s) ||
          (lead.company_size || '').toLowerCase().includes(s) ||
          (lead.audit_id || '').toLowerCase().includes(s)
      );
    }
    if (statusFilter) {
      filtered = filtered.filter(lead => lead.status === statusFilter);
    }
    if (industryFilter) {
      filtered = filtered.filter(lead => lead.industry === industryFilter);
    }
    setFilteredLeads(filtered);
    setCurrentPage(1);
  }, [search, statusFilter, industryFilter, leads]);

  const loadLeads = async () => {
    setLoading(true);
    try {
      const data = await adminApi.listLeads({ limit: 100 });
      setLeads(data.items || []);
    } catch (error) {
      console.error('Failed to load leads:', error);
      toast.error('Не удалось загрузить лиды');
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setSearch('');
    setStatusFilter('');
    setIndustryFilter('');
  };

  const handleStatusChange = async (leadId: number | undefined, newStatus: string) => {
    if (!leadId) return;
    try {
      toast.success(`Статус обновлён на ${newStatus}`);
      setLeads(prev => prev.map(l => l.id === leadId ? { ...l, status: newStatus } : l));
    } catch {
      toast.error('Не удалось обновить статус');
    }
  };

  // Пагинация
  const totalPages = Math.ceil(filteredLeads.length / pageSize);
  const paginatedLeads = filteredLeads.slice(
    (currentPage - 1) * pageSize,
    currentPage * pageSize
  );

  const startIndex = (currentPage - 1) * pageSize + 1;
  const endIndex = Math.min(currentPage * pageSize, filteredLeads.length);

  const columns = [
    {
      key: 'created_at',
      header: 'Дата',
      render: (lead: Lead) => {
        try {
          return new Date(lead.created_at).toLocaleDateString('ru-RU');
        } catch {
          return '—';
        }
      },
      className: 'w-32',
    },
    {
      key: 'name',
      header: 'Контакт',
      render: (lead: Lead) => (
        <div>
          <div className="font-medium">{lead.name || '—'}</div>
          <div className="text-sm text-gray-500">{lead.email || '—'}</div>
          <div className="text-xs text-gray-400">{lead.position || ''}</div>
        </div>
      ),
    },
    {
      key: 'company',
      header: 'Компания',
      render: (lead: Lead) => (
        <div>
          <div>{lead.industry || '—'}</div>
          <div className="text-sm text-gray-500">{lead.company_size || ''}</div>
        </div>
      ),
    },
    {
      key: 'score',
      header: 'Зрелость',
      render: (lead: Lead) => {
        const score = safeFloat(lead.composite_score);
        return (
          <div>
            <div className="font-bold text-primary-600">{score.toFixed(2)}</div>
            <Badge variant="neutral" className="text-xs">
              {lead.maturity_level || '—'}
            </Badge>
          </div>
        );
      },
    },
    {
      key: 'roi',
      header: 'ROI',
      render: (lead: Lead) => {
        const roi = safeFloat(lead.roi_estimate);
        return (
          <div className="font-semibold text-green-600">
            +{roi.toFixed(0)}%
          </div>
        );
      },
    },
    {
      key: 'status',
      header: 'Статус',
      render: (lead: Lead) => (
        <Select
          value={lead.status || 'New'}
          onChange={(e) => handleStatusChange(lead.id, e.target.value)}
          options={statusOptions.filter(opt => opt.value)}
          className="w-32"
        />
      ),
    },
    {
      key: 'actions',
      header: 'Действия',
      render: (lead: Lead) => (
        <div className="flex gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => navigate(`/admin/audits/${lead.audit_id}`)}
          >
            Аудит
          </Button>
          {lead.status === 'New' && (
            <Button
              variant="primary"
              size="sm"
              onClick={() => handleStatusChange(lead.id, 'Contacted')}
            >
              Связаться
            </Button>
          )}
        </div>
      ),
    },
  ];

  const stats = {
    total: leads.length,
    new: leads.filter(l => l.status === 'New').length,
    contacted: leads.filter(l => l.status === 'Contacted').length,
    qualified: leads.filter(l => l.status === 'Qualified').length,
    converted: leads.filter(l => l.status === 'Converted').length,
  };

  const conversionRate = stats.total > 0
    ? ((stats.converted / stats.total) * 100).toFixed(1)
    : '0.0';

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">👥 Лиды</h1>
          <p className="text-gray-600 mt-1">Управление лидами из аудитов</p>
        </div>
        <Button variant="secondary" onClick={loadLeads} disabled={loading}>
          <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
          Обновить
        </Button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-6">
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="flex items-center gap-3">
            <Users className="w-8 h-8 text-primary-600" />
            <div>
              <div className="text-2xl font-bold">{stats.total}</div>
              <div className="text-sm text-gray-600">Всего</div>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="flex items-center gap-3">
            <div className="w-3 h-3 rounded-full bg-blue-500" />
            <div>
              <div className="text-2xl font-bold">{stats.new}</div>
              <div className="text-sm text-gray-600">Новые</div>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="flex items-center gap-3">
            <div className="w-3 h-3 rounded-full bg-yellow-500" />
            <div>
              <div className="text-2xl font-bold">{stats.contacted}</div>
              <div className="text-sm text-gray-600">В работе</div>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="flex items-center gap-3">
            <div className="w-3 h-3 rounded-full bg-green-500" />
            <div>
              <div className="text-2xl font-bold">{stats.qualified}</div>
              <div className="text-sm text-gray-600">Квалифицированы</div>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="flex items-center gap-3">
            <TrendingUp className="w-8 h-8 text-green-600" />
            <div>
              <div className="text-2xl font-bold">{conversionRate}%</div>
              <div className="text-sm text-gray-600">Конверсия</div>
            </div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="card mb-6">
        <div className="grid grid-cols-1 md:grid-cols-12 gap-4">
          {/* Search */}
          <div className="md:col-span-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                placeholder="Поиск..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="w-full pl-10 pr-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
            </div>
          </div>
          
          {/* Status Filter */}
          <div className="md:col-span-3">
            <Select
              label="Статус"
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              options={statusOptions}
            />
          </div>
          
          {/* Industry Filter */}
          <div className="md:col-span-3">
            <Select
              label="Отрасль"
              value={industryFilter}
              onChange={(e) => setIndustryFilter(e.target.value)}
              options={[
                { value: '', label: 'Все отрасли' },
                ...uniqueIndustries.map(ind => ({ value: ind, label: ind })),
              ]}
            />
          </div>
          
          {/* Reset Button */}
          <div className="md:col-span-2 flex items-end">
            <Button
              variant="outline"
              onClick={handleReset}
              className="w-full"
            >
              <Filter className="w-4 h-4 mr-2" />
              Сбросить
            </Button>
          </div>
        </div>
      </div>

      {/* Table */}
      <div className="bg-white rounded-lg border border-gray-200">
        <Table
          columns={columns}
          data={paginatedLeads}
          keyExtractor={(lead) => lead.id?.toString() || lead.audit_id}
          isLoading={loading}
          emptyMessage="Лиды не найдены"
        />
        
        {/* Pagination */}
        {totalPages > 1 && (
          <div className="flex items-center justify-between px-4 py-3 border-t border-gray-200 bg-white">
            <div className="text-sm text-gray-700">
              Показано <span className="font-medium">{startIndex}</span>
              {' '}-{' '}
              <span className="font-medium">{endIndex}</span>
              {' '}из{' '}
              <span className="font-medium">{filteredLeads.length}</span> записей
            </div>
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setCurrentPage(1)}
                disabled={currentPage === 1}
                className="px-2"
              >
                <ChevronLeft className="w-4 h-4" />
                <ChevronLeft className="w-4 h-4 -ml-2" />
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setCurrentPage(currentPage - 1)}
                disabled={currentPage === 1}
              >
                <ChevronLeft className="w-4 h-4" />
              </Button>
              
              {Array.from({ length: totalPages }, (_, i) => i + 1).map(page => (
                <Button
                  key={page}
                  variant={currentPage === page ? 'primary' : 'outline'}
                  size="sm"
                  onClick={() => setCurrentPage(page)}
                  className="min-w-[36px] px-3"
                >
                  {page}
                </Button>
              ))}
              
              <Button
                variant="outline"
                size="sm"
                onClick={() => setCurrentPage(currentPage + 1)}
                disabled={currentPage === totalPages}
              >
                <ChevronRight className="w-4 h-4" />
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setCurrentPage(totalPages)}
                disabled={currentPage === totalPages}
                className="px-2"
              >
                <ChevronRight className="w-4 h-4" />
                <ChevronRight className="w-4 h-4 -ml-2" />
              </Button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}