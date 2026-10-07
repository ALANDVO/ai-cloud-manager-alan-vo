from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime

@dataclass
class ResourceRecord:
    id: str
    provider: str
    resource_type: str
    name: str
    region: str
    status: str
    monthly_cost: float = 0.0
    utilization: Dict[str, float] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class CostRecord:
    date: str
    provider: str
    service: str
    cost: float
    resource_type: str = "general"

@dataclass
class AuditRecord:
    id: str
    provider: str
    check: str
    severity: str
    status: str
    detected_at: datetime = field(default_factory=datetime.utcnow)
