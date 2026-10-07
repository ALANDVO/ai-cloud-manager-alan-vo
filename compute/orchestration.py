import logging, uuid
from typing import List, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class OrchestrationEngine:

    def __init__(self):
        self.workloads: List[Dict[str, Any]] = []
        self._seed()

    def _seed(self):
        self.workloads = [
            {
                "id": "wl-001",
                "name": "api-gateway-cluster",
                "provider": "aws",
                "region": "us-east-1",
                "resource_type": "ec2_instance",
                "replicas": 6,
                "status": "running",
                "deployed_at": datetime(2026, 9, 15, 10, 30, 0),
            },
            {
                "id": "wl-002",
                "name": "ml-inference-pool",
                "provider": "gcp",
                "region": "us-central1",
                "resource_type": "gce_instance",
                "replicas": 4,
                "status": "running",
                "deployed_at": datetime(2026, 9, 20, 14, 0, 0),
            },
            {
                "id": "wl-003",
                "name": "data-lake-workers",
                "provider": "azure",
                "region": "eastus",
                "resource_type": "vm",
                "replicas": 8,
                "status": "running",
                "deployed_at": datetime(2026, 10, 1, 8, 0, 0),
            },
        ]

    def get_workloads(self) -> List[Dict[str, Any]]:
        return self.workloads

    def deploy(self, workload: Dict[str, Any]) -> Dict[str, Any]:
        workload["id"] = workload.get("id") or f"wl-{uuid.uuid4().hex[:6]}"
        workload["status"] = workload.get("status", "deploying")
        workload["deployed_at"] = workload.get("deployed_at") or datetime.utcnow()
        self.workloads.append(workload)
        logger.info("Deployed workload %s: %s on %s", workload["id"], workload["name"], workload["provider"])
        return workload

orchestration_engine = OrchestrationEngine()
