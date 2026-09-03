import { useMemo } from 'react';
import { RadarChart } from './RadarChart';
import benchmarksData from '@/data/benchmarks.json';
import { AXIS_DIM, getBenchmarkForIndustry } from '@/utils/axes';

interface Audit {
  company_profile: {
    industry: string;
  };
  request?: {
    target_scores?: Record<string, number>;
  };
  calculated_indices: {
    dimension_scores: Record<string, number>;
  };
}

interface RadarChartWithBenchmarkProps {
  audit: Audit;
}

export const RadarChartWithBenchmark: React.FC<RadarChartWithBenchmarkProps> = ({ audit }) => {
  const radarData = useMemo(() => {
    if (!audit || !audit.calculated_indices?.dimension_scores) return [];

    const currentScores = audit.calculated_indices.dimension_scores;
    const industry = audit.company_profile?.industry || 'CrossIndustry';
    const targets = audit.request?.target_scores;

    // Бенчмарк отрасли: код анкеты -> ключ бенчмарка
    const benchmark = getBenchmarkForIndustry(industry);

    // Формируем данные для радара с тремя слоями
    return benchmarksData.axes.map((axis: any) => {
      const dim = AXIS_DIM[axis.key];
      const current = currentScores[dim] || 0;
      const target = targets?.[dim] ?? Math.min(current + 1.0, 5.0);
      const bench = benchmark?.[axis.key] || 2.5;

      return {
        axis: axis.label,
        key: axis.key,
        current: current,
        target: target,
        benchmark: bench,
        weight: axis.weight,
      };
    });
  }, [audit]);

  if (radarData.length === 0) {
    return (
      <div className="flex justify-center items-center h-[400px]">
        <p className="text-gray-400">Нет данных для отображения</p>
      </div>
    );
  }

  return <RadarChart data={radarData} width={500} height={500} />;
};