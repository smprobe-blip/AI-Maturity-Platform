import { useMemo } from 'react';
import { RadarChart } from './RadarChart';
import benchmarksData from '@/data/benchmarks.json';

interface Audit {
  company_profile: {
    industry: string;
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
    
    // Получаем бенчмарк для отрасли
    const benchmark = benchmarksData.benchmarks[industry] || benchmarksData.benchmarks.CrossIndustry;

    // Формируем данные для радара с тремя слоями
    return benchmarksData.axes.map((axis: any) => {
      const current = currentScores[axis.key] || 0;
      const target = Math.min(current + 1.0, 5.0); // Целевое = текущее + 1 (макс 5)
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