import logging
from typing import List, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class ComplianceEngine:

    def __init__(self):
        self.last_assessed = datetime(2026, 9, 28, 12, 0, 0)
        self.scores: List[Dict[str, Any]] = []
        self._calculate_scores()

    def _calculate_scores(self):
        soc2 = {
            "framework": "SOC2",
            "score": 78,
            "max_score": 100,
            "status": "partial",
            "categories": [
                {"name": "Security", "score": 85, "max": 100, "controls": 17, "passed": 14},
                {"name": "Availability", "score": 72, "max": 100, "controls": 12, "passed": 9},
                {"name": "Confidentiality", "score": 80, "max": 100, "controls": 15, "passed": 12},
                {"name": "Processing Integrity", "score": 65, "max": 100, "controls": 10, "passed": 6},
            ],
        }
        iso = {
            "framework": "ISO27001",
            "score": 72,
            "max_score": 100,
            "status": "partial",
            "categories": [
                {"name": "Information Security Policies", "score": 80, "max": 100, "controls": 8, "passed": 6},
                {"name": "Access Control", "score": 75, "max": 100, "controls": 12, "passed": 9},
                {"name": "Cryptography", "score": 68, "max": 100, "controls": 6, "passed": 4},
                {"name": "Incident Management", "score": 70, "max": 100, "controls": 10, "passed": 7},
            ],
        }
        hipaa = {
            "framework": "HIPAA",
            "score": 65,
            "max_score": 100,
            "status": "gap",
            "categories": [
                {"name": "Administrative Safeguards", "score": 70, "max": 100, "controls": 10, "passed": 7},
                {"name": "Physical Safeguards", "score": 60, "max": 100, "controls": 8, "passed": 5},
                {"name": "Technical Safeguards", "score": 65, "max": 100, "controls": 12, "passed": 8},
                {"name": "Transmission Security", "score": 55, "max": 100, "controls": 6, "passed": 3},
            ],
        }
        self.scores = [soc2, iso, hipaa]

    def get_scores(self) -> List[Dict[str, Any]]:
        for s in self.scores:
            s["last_assessed"] = self.last_assessed
        return self.scores

compliance_engine = ComplianceEngine()
