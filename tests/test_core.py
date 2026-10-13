import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.cost.analysis import cost_engine
from app.cost.optimization import optimization_engine
from app.cost.rightsizing import rightsizing_engine
from app.security.audit import audit_engine
from app.security.compliance import compliance_engine
from app.security.posture import posture_engine
from app.compute.scaling import scaling_engine
from app.compute.orchestration import orchestration_engine
from app.providers.registry import provider_registry

def test_cost_summary():
    summary = cost_engine.get_summary()
    assert "total_monthly" in summary
    assert "by_provider" in summary
    assert "by_service" in summary
    assert "savings_available" in summary

def test_cost_trends():
    trends = cost_engine.get_trends(days=30)
    assert isinstance(trends, list)

def test_cost_breakdown():
    breakdown = cost_engine.get_breakdown()
    assert isinstance(breakdown, list)
    for item in breakdown[:3]:
        assert "provider" in item
        assert "service" in item
        assert "monthly_cost" in item

def test_optimization_recommendations():
    recs = optimization_engine.get_recommendations()
    assert isinstance(recs, list)
    assert len(recs) > 0
    for rec in recs[:3]:
        assert "id" in rec
        assert "title" in rec
        assert "estimated_savings_monthly" in rec

def test_rightsizing():
    suggestions = rightsizing_engine.get_suggestions()
    assert isinstance(suggestions, list)
    for s in suggestions:
        assert "resource_id" in s
        assert "current_spec" in s
        assert "recommended_spec" in s

def test_security_audit():
    audit = audit_engine.get_audit()
    assert "total_checks" in audit
    assert "passed" in audit
    assert "warnings" in audit
    assert "critical" in audit
    assert audit["total_checks"] > 0

def test_compliance_scores():
    scores = compliance_engine.get_scores()
    assert len(scores) == 3
    frameworks = [s["framework"] for s in scores]
    assert "SOC2" in frameworks
    assert "ISO27001" in frameworks
    assert "HIPAA" in frameworks
    for s in scores:
        assert 0 <= s["score"] <= 100
        assert "categories" in s

def test_posture_report():
    report = posture_engine.get_report()
    assert "overall_score" in report
    assert "risk_level" in report
    assert "top_risks" in report
    assert "recommendations" in report
    assert 0 <= report["overall_score"] <= 100

def test_scaling_policies():
    policies = scaling_engine.get_policies()
    assert isinstance(policies, list)
    assert len(policies) > 0
    for p in policies:
        assert "min_size" in p
        assert "max_size" in p
        assert p["min_size"] <= p["max_size"]

def test_scaling_predictions():
    predictions = scaling_engine.get_predictions()
    assert isinstance(predictions, list)
    for p in predictions:
        assert "predicted_cpu" in p
        assert "recommended_action" in p

def test_orchestration_workloads():
    workloads = orchestration_engine.get_workloads()
    assert isinstance(workloads, list)
    assert len(workloads) > 0
    for w in workloads:
        assert "name" in w
        assert "provider" in w
        assert "replicas" in w

def test_provider_registry():
    resources = provider_registry.get_all_resources(limit=50)
    assert isinstance(resources, list)
    providers = set(r.get("provider", "") for r in resources)
    assert "aws" in providers or "gcp" in providers or "azure" in providers

def test_utilization_report():
    report = provider_registry.get_utilization()
    assert "total_resources" in report
    assert "by_provider" in report
    assert "avg_cpu" in report

def test_tenant_management():
    tenants = provider_registry.get_tenants()
    assert isinstance(tenants, list)
    assert len(tenants) > 0
    t = provider_registry.get_tenant("tenant-default")
    assert t is not None
    assert t["name"] == "Default"
