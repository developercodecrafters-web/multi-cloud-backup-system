import json
import os
from typing import Dict

METRICS_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs", "metrics.json")


def _ensure_metrics_file() -> None:
    os.makedirs(os.path.dirname(METRICS_FILE), exist_ok=True)
    if not os.path.exists(METRICS_FILE):
        initial = {
            "total_backups": 0,
            "success_count": 0,
            "failover_count": 0,
            "total_files": 0,
            "total_time": 0.0,
            "last_backup_time": "",
        }
        with open(METRICS_FILE, "w", encoding="utf-8") as f:
            json.dump(initial, f, indent=2)


def load_metrics() -> Dict[str, object]:
    _ensure_metrics_file()
    with open(METRICS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def update_metrics(
    files_processed: int,
    backup_time: float,
    success: bool,
    failover_used: bool,
    last_backup_time: str,
) -> Dict[str, object]:
    _ensure_metrics_file()
    metrics = load_metrics()

    metrics["total_backups"] += 1
    metrics["total_files"] += int(files_processed)
    metrics["total_time"] += float(backup_time)
    metrics["last_backup_time"] = last_backup_time
    if success:
        metrics["success_count"] += 1
    if failover_used:
        metrics["failover_count"] += 1

    with open(METRICS_FILE, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    return metrics


def compute_derived_metrics(metrics: Dict[str, object]) -> Dict[str, object]:
    total_backups = max(int(metrics.get("total_backups", 0)), 1)
    avg_time = float(metrics.get("total_time", 0.0)) / total_backups
    success_rate = (int(metrics.get("success_count", 0)) / total_backups) * 100

    return {
        "average_backup_time": round(avg_time, 3),
        "success_rate": round(success_rate, 2),
    }
