import logging
from typing import List, Dict, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class ScalingEngine:

    def __init__(self):
        self.policies: List[Dict[str, Any]] = []
        self.predictions: List[Dict[str, Any]] = []
        self._seed()

    def _seed(self):
        self.policies = [
            {
                "id": "policy-001",
                "resource_id": "i-0a1b2c3d4e5f67890",
                "provider": "aws",
                "type": "horizontal",
                "min_size": 2,
                "max_size": 10,
                "metric": "CPUUtilization",
                "threshold": 70.0,
                "cooldown_minutes": 5,
                "active": True,
            },
            {
                "id": "policy-002",
                "resource_id": "gce-prod-api-03",
                "provider": "gcp",
                "type": "horizontal",
                "min_size": 3,
                "max_size": 15,
                "metric": "cpu_utilization",
                "threshold": 65.0,
                "cooldown_minutes": 10,
                "active": True,
            },
            {
                "id": "policy-003",
                "resource_id": "vm-data-warehouse-01",
                "provider": "azure",
                "type": "vertical",
                "min_size": 4,
                "max_size": 16,
                "metric": "memory_percent",
                "threshold": 80.0,
                "cooldown_minutes": 15,
                "active": False,
            },
        ]
        self.predictions = [
            {
                "resource_id": "i-0a1b2c3d4e5f67890",
                "provider": "aws",
                "forecast_hours": 24,
                "predicted_cpu": 82.5,
                "recommended_action": "scale_up",
                "confidence": 0.88,
            },
            {
                "resource_id": "gce-prod-api-03",
                "provider": "gcp",
                "forecast_hours": 48,
                "predicted_cpu": 35.2,
                "recommended_action": "scale_down",
                "confidence": 0.91,
            },
            {
                "resource_id": "vm-data-warehouse-01",
                "provider": "azure",
                "forecast_hours": 72,
                "predicted_cpu": 55.8,
                "recommended_action": "hold",
                "confidence": 0.79,
            },
        ]

    def get_policies(self) -> List[Dict[str, Any]]:
        return self.policies

    def get_predictions(self) -> List[Dict[str, Any]]:
        return self.predictions

scaling_engine = ScalingEngine()
