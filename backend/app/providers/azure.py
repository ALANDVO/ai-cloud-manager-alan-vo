import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta, timezone

from app.providers.base import CloudProvider

logger = logging.getLogger(__name__)


class AzureProvider(CloudProvider):

    def __init__(self, credentials: Dict[str, str]):
        super().__init__("azure", credentials)
        self.client_id = credentials.get("azure_client_id", "")
        self.client_secret = credentials.get("azure_client_secret", "")
        self.tenant_id = credentials.get("azure_tenant_id", "")
        self.subscription_id = credentials.get("azure_subscription_id", "")

    def _compute(self):
        from azure.identity import ClientSecretCredential
        from azure.mgmt.compute import ComputeManagementClient
        cred = ClientSecretCredential(self.tenant_id, self.client_id, self.client_secret)
        return ComputeManagementClient(cred, self.subscription_id)

    def _storage(self):
        from azure.identity import ClientSecretCredential
        from azure.mgmt.storage import StorageManagementClient
        cred = ClientSecretCredential(self.tenant_id, self.client_id, self.client_secret)
        return StorageManagementClient(cred, self.subscription_id)

    def _monitor(self):
        from azure.identity import ClientSecretCredential
        from azure.mgmt.monitor import MonitorManagementClient
        cred = ClientSecretCredential(self.tenant_id, self.client_id, self.client_secret)
        return MonitorManagementClient(cred, self.subscription_id)

    def list_resources(self, resource_type: Optional[str] = None) -> List[Dict[str, Any]]:
        if not self.is_configured():
            return self._mock_resources(resource_type)
        resources = []
        try:
            compute = self._compute()
            for vm in compute.virtual_machines.list_all():
                resources.append({
                    "id": vm.name,
                    "provider": "azure",
                    "resource_type": "vm",
                    "name": vm.name,
                    "region": vm.location,
                    "status": vm.provisioning_state or "unknown",
                    "created_at": vm.tags.get("created_at", datetime.now(timezone.utc)) if vm.tags else datetime.now(timezone.utc),
                    "monthly_cost": 0.0,
                    "utilization": {},
                })
            storage = self._storage()
            for account in storage.storage_accounts.list():
                resources.append({
                    "id": account.name,
                    "provider": "azure",
                    "resource_type": "storage_account",
                    "name": account.name,
                    "region": account.location,
                    "status": account.provisioning_state or "active",
                    "created_at": datetime.now(timezone.utc),
                    "monthly_cost": 0.0,
                    "utilization": {},
                })
        except Exception as e:
            logger.error("Azure resource listing failed: %s", e)
        if resource_type:
            resources = [r for r in resources if r["resource_type"] == resource_type]
        return resources

    def get_cost_data(self, days: int = 30) -> List[Dict[str, Any]]:
        costs = []
        try:
            from azure.identity import ClientSecretCredential
            from azure.mgmt.consumption import ConsumptionManagementClient
            cred = ClientSecretCredential(self.tenant_id, self.client_id, self.client_secret)
            client = ConsumptionManagementClient(cred, self.subscription_id)
            end = datetime.now(timezone.utc)
            start = end - timedelta(days=days)
            for charge in client.usage_details.list(start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")):
                costs.append({
                    "date": charge.date,
                    "provider": "azure",
                    "service": charge.service_name or "unknown",
                    "cost": charge.pre_tax_cost or 0.0,
                })
        except Exception as e:
            logger.error("Azure cost data failed: %s", e)
        return costs

    def get_security_config(self) -> Dict[str, Any]:
        config = {"provider": "azure", "checks": []}
        try:
            from azure.identity import ClientSecretCredential
            from azure.mgmt.authorization import AuthorizationManagementClient
            cred = ClientSecretCredential(self.tenant_id, self.client_id, self.client_secret)
            auth_client = AuthorizationManagementClient(cred, self.subscription_id)
            for role_def in auth_client.role_definitions.list(scope=f"/subscriptions/{self.subscription_id}"):
                config["checks"].append({"type": "role_definition", "name": role_def.role_name, "status": "review"})
        except Exception as e:
            logger.error("Azure security config failed: %s", e)
        return config

    def get_utilization(self) -> Dict[str, Any]:
        util = {"provider": "azure", "cpu": 0.0, "memory": 0.0, "storage": 0.0, "resources": 0}
        try:
            monitor = self._monitor()
            now = datetime.now(timezone.utc)
            start = now - timedelta(hours=1)
            metrics = monitor.metrics.list(
                resource_uri=f"/subscriptions/{self.subscription_id}/providers/Microsoft.Compute/virtualMachines",
                timespan=start.strftime("%Y-%m-%dT%H:%M:%SZ") + "/" + now.strftime("%Y-%m-%dT%H:%M:%SZ"),
                metric_names=["Percentage CPU"],
            )
            total, count = 0.0, 0
            for vm_metrics in metrics.value:
                for series in vm_metrics.timeseries:
                    for point in series.data:
                        if point.time_granularity and point.average is not None:
                            total += point.average
                            count += 1
            if count:
                util["cpu"] = total / count
            util["resources"] = count
        except Exception as e:
            logger.error("Azure utilization failed: %s", e)
        return util

    def _mock_resources(self, resource_type: Optional[str] = None) -> List[Dict[str, Any]]:
        mock = [
            {
                "id": "vm-data-warehouse-01",
                "provider": "azure",
                "resource_type": "vm",
                "name": "data-warehouse-01",
                "region": "eastus",
                "status": "Succeeded",
                "created_at": datetime.now(timezone.utc),
                "monthly_cost": 320.00,
                "utilization": {"cpu": 65.4, "memory": 78.9},
            },
            {
                "id": "vm-web-02",
                "provider": "azure",
                "resource_type": "vm",
                "name": "web-02",
                "region": "eastus",
                "status": "Succeeded",
                "created_at": datetime.now(timezone.utc),
                "monthly_cost": 120.00,
                "utilization": {"cpu": 23.1, "memory": 34.5},
            },
            {
                "id": "stg-prod-001",
                "provider": "azure",
                "resource_type": "storage_account",
                "name": "stgprod001",
                "region": "eastus",
                "status": "Succeeded",
                "created_at": datetime.now(timezone.utc),
                "monthly_cost": 87.50,
                "utilization": {"storage": 54.0},
            },
            {
                "id": "sql-crm-01",
                "provider": "azure",
                "resource_type": "sql_database",
                "name": "crm-db",
                "region": "eastus",
                "status": "Online",
                "created_at": datetime.now(timezone.utc),
                "monthly_cost": 245.00,
                "utilization": {"cpu": 41.2, "memory": 67.8, "storage": 38.0},
            },
        ]
        if resource_type:
            mock = [r for r in mock if r["resource_type"] == resource_type]
        return mock
