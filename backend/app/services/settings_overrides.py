"""Переопределяемые настройки и правки бенчмарков (persist в data_storage)."""
import json
import os
from pathlib import Path
from typing import Any, Dict

DATA_PATH = Path(os.getenv("DATA_STORAGE_PATH", "/data_storage"))


def _overrides_path() -> Path:
    return DATA_PATH / "settings_overrides.json"


def _benchmarks_path() -> Path:
    return DATA_PATH / "benchmark_overrides.json"


def _read(path: Path) -> Dict[str, Any]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def load_overrides() -> Dict[str, Any]:
    return _read(_overrides_path())


def save_overrides(patch: Dict[str, Any], allowed: list) -> Dict[str, Any]:
    current = load_overrides()
    for k, v in (patch or {}).items():
        if k in allowed:
            current[k] = v
    _overrides_path().parent.mkdir(parents=True, exist_ok=True)
    with open(_overrides_path(), "w", encoding="utf-8") as f:
        json.dump(current, f, ensure_ascii=False, indent=2)
    return current


def get_public_base_url(default: str) -> str:
    return load_overrides().get("public_base_url", default)


def load_benchmark_overrides() -> Dict[str, Any]:
    return _read(_benchmarks_path())


def save_benchmark_override(industry: str, values: Dict[str, Any]) -> Dict[str, Any]:
    current = load_benchmark_overrides()
    current[industry] = values
    _benchmarks_path().parent.mkdir(parents=True, exist_ok=True)
    with open(_benchmarks_path(), "w", encoding="utf-8") as f:
        json.dump(current, f, ensure_ascii=False, indent=2)
    return current

def get_dimension_weights_override():
    """Override базовых весов осей ('1'..'7') или None."""
    w = load_overrides().get("dimension_weights")
    if not isinstance(w, dict) or set(w.keys()) != {str(i) for i in range(1, 8)}:
        return None
    try:
        return {k: float(v) for k, v in w.items()}
    except (TypeError, ValueError):
        return None
