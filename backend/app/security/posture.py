import logging, json
from typing import List, Dict, Any
from datetime import datetime, timezone
import httpx
from app.config import settings

logger = logging.getLogger(__name__)


class PostureEngine:

    def __init__(self):
        self.base_url = settings.llm_base_url.rstrip("/")
        self.api_key = settings.llm_api_key
        self.model = settings.llm_model
        self.report: Dict[str, Any] = {}

    async def _chat(self, system: str, user: str, temperature: float = 0.3) -> str:
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                f"{self.base_url}/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                json={"model": self.model, "temperature": temperature, "max_tokens": 2048,
                      "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}]},
            )
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]

    async def assess(self) -> Dict[str, Any]:
        from app.security.audit import audit_engine
        from app.security.compliance import compliance_engine
        audit = audit_engine.get_audit()
        compliance = compliance_engine.get_scores()
        context = json.dumps({
            "audit": {k: v for k, v in audit.items() if k != "findings"},
            "top_findings": audit["findings"][:10],
            "compliance": compliance,
        }, default=str)[:3000]
        system = ("You are a CISO. Assess the overall security posture based on the audit and compliance data. "
                  "Return JSON: overall_score (0-100), risk_level (low|medium|high|critical), "
                  "summary (2-3 paragraphs), top_risks (array of {risk, impact, likelihood, mitigation}), "
                  "recommendations (array of 5 prioritized actions).")
        try:
            raw = await self._chat(system, f"Security posture data:\n{context}")
            clean = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
            self.report = json.loads(clean)
            self.report["assessed_at"] = datetime.now(timezone.utc).isoformat()
            return self.report
        except Exception as e:
            logger.warning("LLM posture assessment failed: %s", e)
        return self._fallback_report(audit)

    def _fallback_report(self, audit: Dict) -> Dict[str, Any]:
        score = 100 - (audit.get("critical", 0) * 10) - (audit.get("warnings", 0) * 3)
        risk = "low" if score >= 80 else "medium" if score >= 60 else "high" if score >= 40 else "critical"
        return {
            "overall_score": max(0, score),
            "risk_level": risk,
            "summary": "Security posture assessment based on audit findings. Critical issues require immediate attention.",
            "top_risks": [
                {"risk": "Unencrypted storage at rest", "impact": "data_breach", "likelihood": "medium", "mitigation": "Enable encryption on all storage"},
                {"risk": "Excessive IAM permissions", "impact": "privilege_escalation", "likelihood": "high", "mitigation": "Implement least-privilege RBAC"},
                {"risk": "Public network exposure", "impact": "unauthorized_access", "likelihood": "medium", "mitigation": "Restrict security groups to VPC"},
            ],
            "recommendations": [
                "Enable encryption at rest for all storage and databases",
                "Implement MFA for all IAM roles with administrative privileges",
                "Restrict security group rules to specific CIDR ranges",
                "Deploy a CSPM tool for continuous compliance monitoring",
                "Conduct quarterly penetration testing across all clouds",
            ],
            "assessed_at": datetime.now(timezone.utc).isoformat(),
        }

    def get_report(self) -> Dict[str, Any]:
        if not self.report:
            from app.security.audit import audit_engine
            self.report = self._fallback_report(audit_engine.get_audit())
        return self.report

posture_engine = PostureEngine()
