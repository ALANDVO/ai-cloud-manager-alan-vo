import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta, timezone

from app.providers.base import CloudProvider

logger = logging.getLogger(__name__)


class GCPProvider(CloudProvider):

    def __init__(self, credentials: Dict[str, str]):
        super().__init__("gcp", credentials)
        self.project_id = credentials.get("gcp_project_id", "")
        self.sa_email = credentials.get("gcp_service_account_email", "")

    def _compute(self):
        from google.cloud import compute_v1
        return compute_v1.InstancesClient()

    def _storage(self):
        from google.cloud import storage
        return storage.Client(project=self.project_id)

    def list_resources(self, resource_type: Optional[str] = None) -> List[Dict[str, Any]]:
        if not self.is_configured():
            return self._mock_resources(resource_type)
        resources = []
        try:
            instances = []
            for zone in ["us-central1-a", "us-east1-b", "us-west1-a"]:
                try:
                    insts = self._compute().list(project=self.project_id, zone=zone)
                    instances.extend(insts)
                except Exception:
                    continue
            for inst in instances:
                resources.append({
                    "id": inst.name,
                    "provider": "gcp",
                    "resource_type": "gce_instance",
                    "name": inst.name,
                    "region": inst.zone.split("/")[-1] if inst.zone else "unknown",
                    "status": inst.status or "unknown",
                    "created_at": datetime.now(timezone.utc),
                    "monthly_cost": 0.0,
                    "utilization": {},
                })
            for bucket in self._storage().list_buckets():
                resources.append({
                    "id": bucket.name,
                    "provider": "gcp",
                    "resource_type": "gcs_bucket",
                    "name": bucket.name,
                    "region": bucket.location or "unknown",
                    "status": "active",
                    "created_at": bucket.time_created,
                    "monthly_cost": 0.0,
                    "utilization": {},
                })
        except Exception as e:
            logger.error("GCP resource listing failed: %s", e)
        if resource_type:
            resources = [r for r in resources if r["resource_type"] == resource_type]
        return resources

    def get_cost_data(self, days: int = 30) -> List[Dict[str, Any]]:
        costs = []
        try:
            from google.cloud import billing_budgets_v1
            client = billing_budgets_v1.BillingBudgetServiceClient()
            end = datetime.now(timezone.utc)
            start = end - timedelta(days=days)
            for budget in client.list_billing_budgets(parent=f"billingAccounts/{self.project_id}"):
                for info in budget.billing_plan.budgets:
                    costs.append({
                        "date": start.strftime("%Y-%m-%d"),
                        "provider": "gcp",
                        "service": info.id,
                        "cost": 0.0,
                    })
        except Exception as e:
            logger.error("GCP cost data failed: %s", e)
        return costs

    def get_security_config(self) -> Dict[str, Any]:
        config = {"provider": "gcp", "checks": []}
        try:
            from google.cloud import resourcemanager_v3
            client = resourcemanager_v3.ProjectsClient()
            for project in client.list_projects():
                config["checks"].append({"type": "project", "name": project.name, "status": "review"})
        except Exception as e:
            logger.error("GCP security config failed: %s", e)
        return config

    def get_utilization(self) -> Dict[str, Any]:
        util = {"provider": "gcp", "cpu": 0.0, "memory": 0.0, "storage": 0.0, "resources": 0}
        try:
            from google.cloud import monitoring_v3
            client = monitoring_v3.MetricServiceClient()
            now = datetime.now(timezone.utc)
            start = now - timedelta(hours=1)
            resp = client.list_time_series(
                name=f"projects/{self.project_id}/timeSeries",
                filter='resource.type = "gce_instance" AND metric.type = "compute.googleapis.com/instance/cpu/utilization"',
                interval={"start_time": start, "end_time": now},
            )
            total, count = 0.0, 0
            for ts in resp:
                for point in ts.points:
                    total += point.value.double_value
                    count += 1
            if count:
                util["cpu"] = total / count
            util["resources"] = count
        except Exception as e:
            logger.error("GCP utilization failed: %s", e)
        return util

    def _mock_resources(self, resource_type: Optional[str] = None) -> List[Dict[str, Any]]:
        mock = [
            {
                "id": "gce-prod-api-01",
                "provider": "gcp",
                "resource_type": "gce_instance",
                "name": "prod-api-01",
                "region": "us-central1-a",
                "status": "RUNNING",
                "created_at": datetime.now(timezone.utc),
                "monthly_cost": 54.00,
                "utilization": {"cpu": 38.5, "memory": 55.2},
            },
            {
                "id": "gce-prod-api-02",
                "provider": "gcp",
                "resource_type": "gce_instance",
                "name": "prod-api-02",
                "region": "us-central1-a",
                "status": "RUNNING",
                "created_at": datetime.now(timezone.utc),
                "monthly_cost": 54.00,
                "utilization": {"cpu": 42.1, "memory": 48.7},
            },
            {
                "id": "gcs-data-lake",
                "provider": "gcp",
                "resource_type": "gcs_bucket",
                "name": "data-lake",
                "region": "US",
                "status": "active",
                "created_at": datetime.now(timezone.utc),
                "monthly_cost": 89.30,
                "utilization": {"storage": 72.0},
            },
            {
                "id": "bq-analytics",
                "provider": "gcp",
                "resource_type": "bigquery",
                "name": "analytics",
                "region": "US",
                "status": "active",
                "created_at": datetime.now(timezone.utc),
                "monthly_cost": 234.00,
                "utilization": {},
            },
        ]
        if resource_type:
            mock = [r for r in mock if r["resource_type"] == resource_type]
        return mock
