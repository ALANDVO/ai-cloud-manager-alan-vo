import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.providers.aws import AWSProvider
from app.providers.gcp import GCPProvider
from app.providers.azure import AzureProvider
from app.config import settings

logger = logging.getLogger(__name__)

class ProviderRegistry:

    def __init__(self):
        self.providers = {}
        self._init_providers()

    def _init_providers(self):
        aws_configured = bool(settings.aws_access_key_id and settings.aws_secret_access_key)
        gcp_configured = bool(settings.gcp_project_id and settings.gcp_service_account_email)
        azure_configured = bool(settings.azure_client_id and settings.azure_client_secret and settings.azure_tenant_id)

        aws_creds = {
            "aws_access_key_id": settings.aws_access_key_id,
            "aws_secret_access_key": settings.aws_secret_access_key,
            "aws_default_region": settings.aws_default_region,
            "configured": aws_configured,
        }
        gcp_creds = {
            "gcp_project_id": settings.gcp_project_id,
            "gcp_service_account_email": settings.gcp_service_account_email,
            "configured": gcp_configured,
        }
        azure_creds = {
            "azure_client_id": settings.azure_client_id,
            "azure_client_secret": settings.azure_client_secret,
            "azure_tenant_id": settings.azure_tenant_id,
            "azure_subscription_id": settings.azure_subscription_id,
            "configured": azure_configured,
        }

        self.providers["aws"] = AWSProvider(aws_creds)
        self.providers["gcp"] = GCPProvider(gcp_creds)
        self.providers["azure"] = AzureProvider(azure_creds)
        logger.info("Registered %d cloud providers (aws=%s, gcp=%s, azure=%s)",
                    len(self.providers), aws_configured, gcp_configured, azure_configured)

    def get_provider(self, name: str):
        return self.providers.get(name)

    def get_all_resources(self, provider: Optional[str] = None,
                          resource_type: Optional[str] = None,
                          limit: int = 200) -> List[Dict[str, Any]]:
        resources = []
        names = [provider] if provider else list(self.providers.keys())
        for name in names:
            p = self.providers.get(name)
            if p:
                resources.extend(p.list_resources(resource_type))
        resources.sort(key=lambda r: r.get("monthly_cost", 0), reverse=True)
        return resources[:limit]

    def get_all_costs(self, days: int = 30) -> List[Dict[str, Any]]:
        costs = []
        for p in self.providers.values():
            costs.extend(p.get_cost_data(days))
        return costs

    def get_all_security(self) -> List[Dict[str, Any]]:
        configs = []
        for p in self.providers.values():
            configs.append(p.get_security_config())
        return configs

    def get_utilization(self) -> Dict[str, Any]:
        total_resources = 0
        by_provider = {}
        by_type = {}
        total_cpu, total_mem, total_storage = 0.0, 0.0, 0.0
        underutilized, overutilized = 0, 0
        for name, p in self.providers.items():
            util = p.get_utilization()
            count = util.get("resources", 0)
            total_resources += count
            by_provider[name] = count
            total_cpu += util.get("cpu", 0)
            total_mem += util.get("memory", 0)
            total_storage += util.get("storage", 0)
        return {
            "total_resources": total_resources,
            "by_provider": by_provider,
            "by_type": by_type,
            "avg_cpu": total_cpu / max(len(self.providers), 1),
            "avg_memory": total_mem / max(len(self.providers), 1),
            "avg_storage": total_storage / max(len(self.providers), 1),
            "underutilized": underutilized,
            "overutilized": overutilized,
        }

    def get_tenants(self) -> List[Dict[str, Any]]:
        return self._tenants

    def create_tenant(self, tenant) -> Dict[str, Any]:
        import uuid
        tid = f"tenant-{uuid.uuid4().hex[:8]}"
        record = {
            "id": tid,
            "name": tenant.name,
            "email": tenant.email,
            "providers": tenant.providers,
            "cost_budget_monthly": tenant.cost_budget_monthly,
            "status": "active",
            "created_at": datetime.utcnow(),
        }
        self._tenants.append(record)
        return record

    def get_tenant(self, tenant_id: str) -> Optional[Dict]:
        for t in self._tenants:
            if t["id"] == tenant_id:
                return t
        return None

    def update_tenant(self, tenant_id: str, update) -> Optional[Dict]:
        t = self.get_tenant(tenant_id)
        if not t:
            return None
        if update.name is not None:
            t["name"] = update.name
        if update.providers is not None:
            t["providers"] = update.providers
        if update.cost_budget_monthly is not None:
            t["cost_budget_monthly"] = update.cost_budget_monthly
        if update.status is not None:
            t["status"] = update.status
        return t

    _tenants = [
        {
            "id": "tenant-default",
            "name": "Default",
            "email": "admin@example.com",
            "providers": ["aws", "gcp", "azure"],
            "cost_budget_monthly": 10000.0,
            "status": "active",
            "created_at": datetime(2026, 1, 15, 10, 0, 0),
        }
    ]

provider_registry = ProviderRegistry()
