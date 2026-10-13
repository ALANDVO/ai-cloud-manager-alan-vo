from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel

from app.api.auth import get_current_user, User
from app.api.schemas import (
    CostSummary, CostTrend, CostBreakdown, AnomalyAlert,
    OptimizationRec, RightsizingRec,
    AuditResult, ComplianceScore, PostureReport,
    CloudResource, UtilizationReport, ScalingPolicy,
    ScalingPrediction, Workload, Tenant, TenantCreate, TenantUpdate
)

from app.providers.registry import provider_registry
from app.cost.analysis import cost_engine
from app.cost.optimization import optimization_engine
from app.cost.rightsizing import rightsizing_engine
from app.security.audit import audit_engine
from app.security.compliance import compliance_engine
from app.security.posture import posture_engine
from app.compute.scaling import scaling_engine
from app.compute.orchestration import orchestration_engine

router = APIRouter(prefix="/api", tags=["cloud-manager"])

@router.get("/health")
async def health():
    return {"status": "ok", "service": "ai-cloud-manager", "version": "1.0.0"}

@router.get("/costs/summary", response_model=CostSummary)
async def cost_summary(user: User = Depends(get_current_user)):
    return cost_engine.get_summary()

@router.get("/costs/trends", response_model=List[CostTrend])
async def cost_trends(
    provider: Optional[str] = Query(None),
    days: int = Query(30, le=365),
    user: User = Depends(get_current_user),
):
    return cost_engine.get_trends(provider=provider, days=days)

@router.get("/costs/breakdown", response_model=List[CostBreakdown])
async def cost_breakdown(
    provider: Optional[str] = Query(None),
    user: User = Depends(get_current_user),
):
    return cost_engine.get_breakdown(provider=provider)

@router.get("/costs/anomalies", response_model=List[AnomalyAlert])
async def cost_anomalies(user: User = Depends(get_current_user)):
    return cost_engine.get_anomalies()

@router.get("/recommendations", response_model=List[OptimizationRec])
async def get_recommendations(user: User = Depends(get_current_user)):
    return optimization_engine.get_recommendations()

@router.post("/recommendations/generate", response_model=List[OptimizationRec])
async def generate_recommendations(user: User = Depends(get_current_user)):
    recs = await optimization_engine.generate()
    return recs

@router.get("/rightsizing", response_model=List[RightsizingRec])
async def get_rightsizing(user: User = Depends(get_current_user)):
    return rightsizing_engine.get_suggestions()

@router.get("/security/audit", response_model=AuditResult)
async def get_audit(user: User = Depends(get_current_user)):
    return audit_engine.get_audit()

@router.get("/security/compliance", response_model=List[ComplianceScore])
async def get_compliance(user: User = Depends(get_current_user)):
    return compliance_engine.get_scores()

@router.get("/security/posture", response_model=PostureReport)
async def get_posture(user: User = Depends(get_current_user)):
    return posture_engine.get_report()

@router.get("/resources", response_model=List[CloudResource])
async def get_resources(
    provider: Optional[str] = Query(None),
    resource_type: Optional[str] = Query(None),
    limit: int = Query(200, le=1000),
    user: User = Depends(get_current_user),
):
    return provider_registry.get_all_resources(provider=provider, resource_type=resource_type, limit=limit)

@router.get("/resources/utilization", response_model=UtilizationReport)
async def get_utilization(user: User = Depends(get_current_user)):
    return provider_registry.get_utilization()

@router.get("/scaling/policies", response_model=List[ScalingPolicy])
async def get_scaling_policies(user: User = Depends(get_current_user)):
    return scaling_engine.get_policies()

@router.get("/scaling/predictions", response_model=List[ScalingPrediction])
async def get_scaling_predictions(user: User = Depends(get_current_user)):
    return scaling_engine.get_predictions()

@router.get("/orchestration/workloads", response_model=List[Workload])
async def get_workloads(user: User = Depends(get_current_user)):
    return orchestration_engine.get_workloads()

@router.post("/orchestration/deploy", response_model=Workload)
async def deploy_workload(workload: Workload, user: User = Depends(get_current_user)):
    return orchestration_engine.deploy(workload)

@router.get("/tenants", response_model=List[Tenant])
async def list_tenants(user: User = Depends(get_current_user)):
    return provider_registry.get_tenants()

@router.post("/tenants", response_model=Tenant)
async def create_tenant(tenant: TenantCreate, user: User = Depends(get_current_user)):
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin role required")
    return provider_registry.create_tenant(tenant)

@router.get("/tenants/{tenant_id}", response_model=Tenant)
async def get_tenant(tenant_id: str, user: User = Depends(get_current_user)):
    tenant = provider_registry.get_tenant(tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return tenant

@router.put("/tenants/{tenant_id}", response_model=Tenant)
async def update_tenant(tenant_id: str, update: TenantUpdate, user: User = Depends(get_current_user)):
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin role required")
    tenant = provider_registry.update_tenant(tenant_id, update)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return tenant
@router.get("/tenants/{tenant_id}/connections")
async def get_tenant_connections(tenant_id: str, user: User = Depends(get_current_user)):
    return [
        {"provider": "aws", "status": "connected", "account": "123456789012", "last_sync": "2026-10-13T10:00:00Z"},
        {"provider": "gcp", "status": "connected", "account": "my-gcp-project", "last_sync": "2026-10-13T10:05:00Z"},
        {"provider": "azure", "status": "pending", "account": "sub-abc123", "last_sync": "2026-10-13T09:00:00Z"},
    ]
