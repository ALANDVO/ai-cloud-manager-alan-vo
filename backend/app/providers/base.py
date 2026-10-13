import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class CloudProvider(ABC):

    def __init__(self, name: str, credentials: Dict[str, str]):
        self.name = name
        self.credentials = credentials

    @abstractmethod
    def list_resources(self, resource_type: Optional[str] = None) -> List[Dict[str, Any]]:
        ...

    @abstractmethod
    def get_cost_data(self, days: int = 30) -> List[Dict[str, Any]]:
        ...

    @abstractmethod
    def get_security_config(self) -> Dict[str, Any]:
        ...

    @abstractmethod
    def get_utilization(self) -> Dict[str, Any]:
        ...

    def get_provider_name(self) -> str:
        return self.name

    def is_configured(self) -> bool:
        return bool(self.credentials.get("configured"))
