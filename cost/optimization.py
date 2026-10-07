import logging, json
from typing import List, Dict, Any
import httpx
from config import settings

logger = logging.getLogger(__name__)

class OptimizationEngine:

    def __init__(self):
        self.base_url = settings.llm_base_url.rstrip("/")
        self.api_key = settings.llm_api_key
        self.model = settings.llm_model
        self.recommendations: List[Dict[str, Any]] = []

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

    async def generate(self) -> List[Dict[str, Any]]:
        from cost.analysis import cost_engine
        summary = cost_engine.get_summary()
        breakdown = cost_engine.get_breakdown()
        anomalies = cost_engine.get_anomalies()[:5]
        context = json.dumps({
            "summary": summary,
            "top_services": breakdown[:10],
            "anomalies": anomalies,
        }, default=str)[:3000]
        system = ("You are a cloud cost optimization expert. Analyze the cloud cost data and generate "
                  "3-5 specific, actionable cost optimization recommendations. Return a JSON array where "
                  "each item has: id, provider, service, category (compute|storage|network|database|reserved), "
                  "title, description, estimated_savings_monthly (float), confidence (0-1), "
                  "effort (low|medium|high), action (concrete command or console step).")
        try:
            raw = await self._chat(system, f"Cloud cost data:
{context}")
            clean = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
            recs = json.loads(clean)
            if isinstance(recs, list):
                self.recommendations = recs
                return recs
        except Exception as e:
            logger.warning("LLM optimization failed: %s", e)
        return self._fallback_recommendations(summary, breakdown)

    def _fallback_recommendations(self, summary: Dict, breakdown: List[Dict]) -> List[Dict[str, Any]]:
        recs = []
        for item in breakdown[:5]:
            if item["monthly_cost"] > 100:
                recs.append({
                    "id": f"rec-{len(recs)+1}",
                    "provider": item["provider"],
                    "service": item["service"],
                    "category": "compute" if "compute" in item["service"] else "general",
                    "title": f"Review {item['service']} usage",
                    "description": f"{item['service']} costs {item['monthly_cost']:.0f}/mo ({item['percent_of_total']}% of total). Review for right-sizing or reserved instances.",
                    "estimated_savings_monthly": round(item["monthly_cost"] * 0.25, 2),
                    "confidence": 0.7,
                    "effort": "medium",
                    "action": f"Open {item['provider']} console > {item['service']} > review utilization and rightsizing",
                })
        recs.append({
            "id": f"rec-{len(recs)+1}",
            "provider": "aws",
            "service": "ec2",
            "category": "reserved",
            "title": "Purchase Reserved Instances",
            "description": "Convert on-demand EC2 instances to 1-year Reserved Instances for 30-40% savings.",
            "estimated_savings_monthly": round(summary.get("by_provider", {}).get("aws", 0) * 0.35, 2),
            "confidence": 0.85,
            "effort": "low",
            "action": "AWS Console > Cost Explorer > Purchase Options > Reserved Instances",
        })
        return recs

    def get_recommendations(self) -> List[Dict[str, Any]]:
        if not self.recommendations:
            summary = {}
            try:
                from cost.analysis import cost_engine
                summary = cost_engine.get_summary()
            except Exception:
                pass
            return self._fallback_recommendations(summary, [])
        return self.recommendations

optimization_engine = OptimizationEngine()
