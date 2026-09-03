/**
 * Радар с бенчмарком для админ-контура.
 * Связывает данные аудита (коды измерений '1'..'7') с RadarChart
 * и отраслевым бенчмарком из benchmarks.json.
 */
import { useMemo } from 'react';
import { RadarChart } from './RadarChart';
import { getBenchmarkForIndustry, BENCHMARK_AXES } from '@/utils/axes';

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
  // Бенчмарк отрасли: переводим ключи осей ('strategy') в коды измерений ('1'..'7')
  const benchmarkScores = useMemo(() => {
    const bench = getBenchmarkForIndustry(audit.company_profile?.industry);
    const out: Record<string, number> = {};
    BENCHMARK_AXES.forEach((a, i) => {
      const v = bench?.[a.key];
      if (typeof v === 'number') out[String(i + 1)] = v;
    });
    return out;
  }, [audit]);

  return (
    <RadarChart
      dimensionScores={audit.calculated_indices?.dimension_scores ?? {}}
      targetScores={audit.request?.target_scores}
      benchmarkScores={benchmarkScores}
      theme="brand"
    />
  );
};
