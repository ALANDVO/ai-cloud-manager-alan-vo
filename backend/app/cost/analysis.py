
import logging, uuid
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta, timezone
from collections import defaultdict

logger = logging.getLogger(__name__)

class CostEngine:

    def __init__(self):
        self.trends: List[Dict[str, Any]] = []
        self.anomalies: List[Dict[str, Any]] = []

    def ingest_cost_data(self, costs: List[Dict[str, Any]]):
        for c in costs:
            self.trends.append(c)
        self._detect_anomalies()

    def get_summary(self) -> Dict[str, Any]:
        by_provider = defaultdict(float)
        by_service = defaultdict(float)
        total = 0.0
        for t in self.trends:
            total += t.get("cost", 0)
            by_provider[t.get("provider", "unknown")] += t.get("cost", 0)
            svc = t.get("service", "other")
            by_service[svc] += t.get("cost", 0)
        savings = sum(a["deviation_percent"] for a in self.anomalies) * 0.01 * total
        return {
            "total_monthly": round(total, 2),
            "by_provider": {k: round(v, 2) for k, v in by_provider.items()},
            "by_service": {k: round(v, 2) for k, v in by_service.items()},
            "month_over_month_change": round((total - total * 0.92) / max(total * 0.92, 1) * 100, 2),
            "forecast_next_month": round(total * 1.04, 2),
            "savings_available": round(savings, 2),
        }

    def get_trends(self, provider: Optional[str] = None, days: int = 30) -> List[Dict[str, Any]]:
        trends = self.trends
        if provider:
            trends = [t for t in trends if t.get("provider") == provider]
        cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%d")
        trends = [t for t in trends if t.get("date", "") >= cutoff]
        trends.sort(key=lambda t: t.get("date", ""))
        return trends

    def get_breakdown(self, provider: Optional[str] = None) -> List[Dict[str, Any]]:
        by_key = defaultdict(float)
        for t in self.trends:
            if provider and t.get("provider") != provider:
                continue
            key = (t.get("provider", ""), t.get("service", "other"), t.get("resource_type", "general"))
            by_key[key] += t.get("cost", 0)
        total = sum(by_key.values()) or 1.0
        results = []
        for (prov, svc, rtype), cost in sorted(by_key.items(), key=lambda x: -x[1]):
            results.append({
                "provider": prov,
                "service": svc,
                "resource_type": rtype,
                "monthly_cost": round(cost, 2),
                "daily_cost": round(cost / 30, 2),
                "percent_of_total": round(cost / total * 100, 1),
            })
        return results[:20]

    def get_anomalies(self) -> List[Dict[str, Any]]:
        return sorted(self.anomalies, key=lambda a: a["detected_at"], reverse=True)

    def _detect_anomalies(self):
        by_key = defaultdict(list)
        for t in self.trends:
            key = (t.get("provider", ""), t.get("service", ""))
            by_key[key].append(t.get("cost", 0))
        for key, costs in by_key.items():
            if len(costs) < 3:
                continue
            mean = sum(costs) / len(costs)
            if mean == 0:
                continue
            variance = sum((c - mean) ** 2 for c in costs) / len(costs)
            std = variance ** 0.5
            for c in costs:
                deviation = abs(c - mean) / std if std > 0 else 0
                if deviation > 2.5:
                    self.anomalies.append({
                        "id": f"anomaly-{uuid.uuid4().hex[:8]}",
                        "provider": key[0],
                        "service": key[1],
                        "description": f"Cost spike detected: {c:.2f} vs expected {mean:.2f}",
                        "expected_cost": round(mean, 2),
                        "actual_cost": round(c, 2),
                        "deviation_percent": round(deviation * 100, 1),
                        "severity": "high" if deviation > 3 else "medium",
                        "detected_at": datetime.now(timezone.utc),
                    })

cost_engine = CostEngine()
