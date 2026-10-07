from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class CostSummary(BaseModel):
    total_monthly: float
    by_provider: Dict[str, float]
    by_service: Dict[str, float]
    month_over_month_change: float
    forecast_next_month: float
    savings_available: float

class CostTrend(BaseModel):
    date: str
    provider: str
    cost: float

class CostBreakdown(BaseModel):
    provider: str
    service: str
    resource_type: str
    monthly_cost: float
    daily_cost: float
    percent_of_total: float

class AnomalyAlert(BaseModel):
    id: str
    provider: str
    service: str
    description: str
    expected_cost: float
    actual_cost: float
    deviation_percent: float
    severity: str
    detected_at: datetime

class OptimizationRec(BaseModel):
    id: str
    provider: str
    service: str
    category: str
    title: str
    description: str
    estimated_savings_monthly: float
    confidence: float
    effort: str
    action: str

class RightsizingRec(BaseModel):
    resource_id: str
    provider: str
    resource_type: str
    current_spec: str
    recommended_spec: str
    utilization: float
    estimated_savings_monthly: float
    confidence: float

class AuditResult(BaseModel):
    total_checks: int
    passed: int
    warnings: int
    critical: int
    findings: List[Dict[str, Any]]
    last_audit: datetime

class ComplianceScore(BaseModel):
    framework: str
    score: float
    max_score: float
    status: str
    categories: List[Dict[str, Any]]
    last_assessed: datetime

class PostureReport(BaseModel):
    overall_score: float
    risk_level: str
    summary: str
    top_risks: List[Dict[str, Any]]
    recommendations: List[str]
    assessed_at: datetime

class CloudResource(BaseModel):
    id: str
    provider: str
    resource_type: str
    name: str
    region: str
    status: str
    created_at: datetime
    monthly_cost: float
    utilization: Dict[str, float]

class UtilizationReport(BaseModel):
    total_resources: int
    by_provider: Dict[str, int]
    by_type: Dict[str, int]
    avg_cpu: float
    avg_memory: float
    avg_storage: float
    underutilized: int
    overutilized: int

class ScalingPolicy(BaseModel):
    id: str
    resource_id: str
    provider: str
    type: str
    min_size: int
    max_size: int
    metric: str
    threshold: float
    cooldown_minutes: int
    active: bool

class ScalingPrediction(BaseModel):
    resource_id: str
    provider: str
    forecast_hours: int
    predicted_cpu: float
    recommended_action: str
    confidence: float

class Workload(BaseModel):
    id: str
    name: str
    provider: str
    region: str
    resource_type: str
    replicas: int
    status: str
    deployed_at: Optional[datetime] = None

class Tenant(BaseModel):
    id: str
    name: str
    email: str
    providers: List[str]
    cost_budget_monthly: float
    status: str
    created_at: datetime

class TenantCreate(BaseModel):
    name: str
    email: str = ""
    providers: List[str] = Field(default_factory=list)
    cost_budget_monthly: float = 0.0

class TenantUpdate(BaseModel):
    name: Optional[str] = None
    providers: Optional[List[str]] = None
    cost_budget_monthly: Optional[float] = None
    status: Optional[str] = None
