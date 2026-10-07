import logging
from typing import List, Dict, Any
from config import settings

logger = logging.getLogger(__name__)

class RightsizingEngine:

    INSTANCE_TYPES = {
        "aws": ["t3.micro", "t3.small", "t3.medium", "t3.large", "m5.large", "m5.xlarge", "c5.large", "c5.xlarge"],
        "gcp": ["e2-micro", "e2-small", "e2-medium", "e2-standard", "n2-standard-2", "n2-standard-4", "n2-highcpu-2", "n2-highcpu-4"],
        "azure": ["Basic_A1", "Basic_A2", "Basic_A4", "Standard_B1s", "Standard_B2s", "Standard_B4ms", "Standard_D2s_v3", "Standard_D4s_v3"],
    }

    def __init__(self):
        self.suggestions: List[Dict[str, Any]] = []

    def analyze(self, resources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        self.suggestions = []
        for r in resources:
            util = r.get("utilization", {})
            cpu = util.get("cpu", 0)
            mem = util.get("memory", 0)
            if cpu == 0 and mem == 0:
                continue
            avg = (cpu + mem) / 2
            if avg < 25:
                self.suggestions.append(self._downsize(r, avg, "underutilized"))
            elif avg > 85:
                self.suggestions.append(self._upsize(r, avg, "overutilized"))
        return self.suggestions

    def _downsize(self, resource: Dict, utilization: float, reason: str) -> Dict[str, Any]:
        provider = resource.get("provider", "aws")
        current = resource.get("name", "current")
        types = self.INSTANCE_TYPES.get(provider, [])
        recommended = types[max(0, len(types) - 3)] if types else "smaller"
        savings = resource.get("monthly_cost", 50.0) * 0.4
        return {
            "resource_id": resource.get("id", "unknown"),
            "provider": provider,
            "resource_type": resource.get("resource_type", "instance"),
            "current_spec": current,
            "recommended_spec": recommended,
            "utilization": round(utilization, 1),
            "estimated_savings_monthly": round(savings, 2),
            "confidence": 0.85,
        }

    def _upsize(self, resource: Dict, utilization: float, reason: str) -> Dict[str, Any]:
        provider = resource.get("provider", "aws")
        current = resource.get("name", "current")
        types = self.INSTANCE_TYPES.get(provider, [])
        recommended = types[min(len(types) - 1, len(types) - 1)] if types else "larger"
        return {
            "resource_id": resource.get("id", "unknown"),
            "provider": provider,
            "resource_type": resource.get("resource_type", "instance"),
            "current_spec": current,
            "recommended_spec": recommended,
            "utilization": round(utilization, 1),
            "estimated_savings_monthly": 0.0,
            "confidence": 0.75,
        }

    def get_suggestions(self) -> List[Dict[str, Any]]:
        if not self.suggestions:
            self._seed_demo()
        return self.suggestions

    def _seed_demo(self):
        self.suggestions = [
            {
                "resource_id": "i-0a1b2c3d4e5f67890",
                "provider": "aws",
                "resource_type": "ec2_instance",
                "current_spec": "m5.xlarge",
                "recommended_spec": "t3.large",
                "utilization": 18.5,
                "estimated_savings_monthly": 245.60,
                "confidence": 0.92,
            },
            {
                "resource_id": "gce-prod-api-03",
                "provider": "gcp",
                "resource_type": "gce_instance",
                "current_spec": "n2-standard-8",
                "recommended_spec": "n2-standard-4",
                "utilization": 22.1,
                "estimated_savings_monthly": 189.30,
                "confidence": 0.88,
            },
            {
                "resource_id": "vm-data-warehouse-01",
                "provider": "azure",
                "resource_type": "vm",
                "current_spec": "Standard_D8s_v3",
                "recommended_spec": "Standard_D4s_v3",
                "utilization": 15.3,
                "estimated_savings_monthly": 312.45,
                "confidence": 0.90,
            },
        ]

rightsizing_engine = RightsizingEngine()
