"""
Dynamic Benchmark Service using DuckDB.
Calculates industry benchmarks from raw JSON audits.
Falls back to static benchmarks.json if sample size < MIN_SAMPLE_SIZE.
"""
import json
import statistics
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import duckdb

MIN_SAMPLE_SIZE = 30
DIMENSION_IDS = ['1', '2', '3', '4', '5', '6', '7']

# Маппинг для статического файла (fallback)
BENCHMARK_KEY_TO_DIM_ID = {
    'strategy': '1', 'people': '2', 'infrastructure': '3',
    'data': '4', 'models': '5', 'implementation': '6', 'rnd': '7',
}
INDUSTRY_KEY_MAP = {
    'retail': 'Retail', 'ecommerce': 'Retail', 'finance': 'Finance',
    'fintech': 'Finance', 'manufacturing': 'Manufacturing', 'it': 'IT',
    'telecom': 'Services', 'logistics': 'Services', 'energy': 'Services',
    'healthcare': 'Healthcare', 'education': 'Services',
    'government': 'Services', 'other': 'CrossIndustry',
}


class BenchmarkService:
    def __init__(self):
        self._cache: Dict[str, Dict[str, float]] = {}
        self._counts: Dict[str, int] = {}
        
        # Путь внутри Docker-контейнера
        self.raw_audits_path = Path("/data_storage/raw_audits")
        # Fallback для локального запуска вне Docker
        if not self.raw_audits_path.exists():
            self.raw_audits_path = Path(__file__).parent.parent.parent / "data_storage" / "raw_audits"
            
        self._benchmarks_file = self._find_benchmarks_file()

    def _find_benchmarks_file(self) -> Optional[Path]:
        current = Path(__file__).resolve().parent
        candidates = [
            current.parent.parent.parent / 'frontend' / 'data' / 'benchmarks.json',
            current.parent.parent / 'frontend' / 'data' / 'benchmarks.json',
            current.parent.parent / 'data' / 'benchmarks.json',
        ]
        for p in candidates:
            if p.exists():
                return p
        return None

    def clear_cache(self):
        self._cache.clear()
        self._counts.clear()

    def get_benchmark(self, industry: str) -> Tuple[Dict[str, float], str]:
        """
        Возвращает (бенчмарк, источник).
        Источник: 'duckdb_dynamic' или 'json_static_fallback'.
        """
        if not industry:
            return self._load_static_fallback('CrossIndustry'), 'json_static_fallback'

        industry_lower = industry.lower()
        
        if industry_lower in self._cache:
            return self._cache[industry_lower], 'cache'

        scores_by_dim: Dict[str, List[float]] = {dim: [] for dim in DIMENSION_IDS}
        count = 0

        # Сканируем JSON-аудиты
        if self.raw_audits_path.exists():
            for json_file in self.raw_audits_path.rglob("audit_*.json"):
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    req_industry = data.get('request', {}).get('company_industry', '').lower()
                    if req_industry == industry_lower:
                        dim_scores = data.get('calculated_indices', {}).get('dimension_scores', {})
                        for dim_id in DIMENSION_IDS:
                            if dim_id in dim_scores:
                                scores_by_dim[dim_id].append(float(dim_scores[dim_id]))
                        count += 1
                except Exception as e:
                    print(f"[benchmark_service] Error reading {json_file}: {e}")

        self._counts[industry_lower] = count

        if count >= MIN_SAMPLE_SIZE:
            # Рассчитываем медиану через DuckDB (или statistics)
            dynamic_bench = {}
            for dim_id, scores in scores_by_dim.items():
                # DuckDB отлично считает медиану, но для 7 чисел проще использовать statistics
                dynamic_bench[dim_id] = round(statistics.median(scores), 2)
            
            self._cache[industry_lower] = dynamic_bench
            return dynamic_bench, 'duckdb_dynamic'
        else:
            # Fallback на статический JSON
            fallback = self._load_static_fallback(industry)
            self._cache[industry_lower] = fallback
            return fallback, 'json_static_fallback'

    def _load_static_fallback(self, industry: str) -> Dict[str, float]:
        if not self._benchmarks_file:
            return {dim: 2.5 for dim in DIMENSION_IDS} # Hardcoded default

        try:
            with open(self._benchmarks_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            benchmarks = data.get('benchmarks', {})
            raw = benchmarks.get(industry, {})
            
            if not raw:
                mapped = INDUSTRY_KEY_MAP.get(industry.lower(), 'CrossIndustry')
                raw = benchmarks.get(mapped, benchmarks.get('CrossIndustry', {}))

            result = {}
            for eng_key, score in raw.items():
                dim_id = BENCHMARK_KEY_TO_DIM_ID.get(eng_key.strip().lower())
                if dim_id:
                    result[dim_id] = float(score)
            return result
        except Exception as e:
            print(f"[benchmark_service] Static fallback error: {e}")
            return {dim: 2.5 for dim in DIMENSION_IDS}

    def get_stats(self) -> Dict[str, int]:
        return self._counts.copy()


# Глобальный инстанс
benchmark_service = BenchmarkService()
