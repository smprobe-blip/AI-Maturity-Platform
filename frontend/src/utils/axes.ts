/**
 * Соответствие осей бенчмарков (строковые ключи benchmarks.json)
 * и кодов измерений методики ('1'..'7').
 */
import benchmarksData from '@/data/benchmarks.json';

export interface BenchmarkAxis {
  key: string;
  label: string;
  weight: number;
  position?: string;
}

export const BENCHMARK_AXES = benchmarksData.axes as BenchmarkAxis[];

/** axis.key ('strategy') -> код измерения ('1'). */
export const AXIS_DIM: Record<string, string> = {};
BENCHMARK_AXES.forEach((a, i) => {
  AXIS_DIM[a.key] = String(i + 1);
});

/** Код отрасли из анкеты -> ключ отраслевого бенчмарка. */
const BENCHMARK_KEY_BY_CODE: Record<string, string> = {
  retail: 'Retail',
  it: 'IT',
  finance: 'Finance',
  manufacturing: 'Manufacturing',
  services: 'Services',
  healthcare: 'Healthcare',
};

export function getBenchmarkForIndustry(industry?: string) {
  const key = BENCHMARK_KEY_BY_CODE[(industry || '').toLowerCase()];
  return (key && benchmarksData.benchmarks[key]) || benchmarksData.benchmarks.CrossIndustry;
}
