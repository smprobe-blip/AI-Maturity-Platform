"""
Dynamic Benchmark Service using DuckDB.
Calculates industry benchmarks from raw JSON audits.
Falls back to static benchmarks.json if sample size < MIN_SAMPLE_SIZE.
"""
import json
import statistics
from pathlib import Path

from app.services.settings_overrides import load_benchmark_overrides
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
    'telecom': 'Services', 'logistics': 'Services', 'energy': 'Services', 'construction': 'Manufacturing',
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


    # ------------------------------------------------------------------
    # Админская сводка: композитные статы по отраслям + ручные правки
    # ------------------------------------------------------------------
    def admin_summary(self) -> List[Dict]:
        """Сводка по отраслям: n, mean, median, std, p25, p75 по композитному баллу.

        Учёт: code -> INDUSTRY_KEY_MAP (Retail/Finance/...), без учёта архивных.
        Ручные правки из data_storage/benchmark_overrides.json перекрывают расчёт.
        """
        buckets: Dict[str, List[float]] = {}

        if self.raw_audits_path.exists():
            for json_file in self.raw_audits_path.rglob("audit_*.json"):
                try:
                    with open(json_file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                except Exception:
                    continue
                if data.get("status") == "archived":
                    continue
                code = (data.get("request", {}) or {}).get("company_industry", "").lower()
                composite = (data.get("calculated_indices", {}) or {}).get("composite_score")
                if composite is None:
                    continue
                bucket = INDUSTRY_KEY_MAP.get(code, "CrossIndustry")
                buckets.setdefault(bucket, []).append(float(composite))

        overrides = load_benchmark_overrides()
        items = []
        keys = ["CrossIndustry", "Retail", "Finance", "IT", "Manufacturing", "Services", "Healthcare"]
        for key in keys:
            scores = buckets.get(key, [])
            manual = overrides.get(key)
            if manual:
                items.append({"industry": key, "manual": True, **manual})
                continue
            n = len(scores)
            item = {
                "industry": key,
                "manual": False,
                "sample_size": n,
                "mean_score": round(statistics.mean(scores), 2) if n else None,
                "median_score": round(statistics.median(scores), 2) if n else None,
                "std_dev": round(statistics.stdev(scores), 2) if n > 1 else None,
            }
            if n >= 4:
                q = statistics.quantiles(scores, n=4)
                item["percentile_25"] = round(q[0], 2)
                item["percentile_75"] = round(q[2], 2)
            else:
                item["percentile_25"] = None
                item["percentile_75"] = None
            items.append(item)
        return items


# Глобальный инстанс
benchmark_service = BenchmarkService()
