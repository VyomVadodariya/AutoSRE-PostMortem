from abc import ABC, abstractmethod
from typing import Dict, Any, List

class MetricsProvider(ABC):
    @abstractmethod
    def get_cpu_usage(self, service: str) -> float:
        pass
        
    @abstractmethod
    def get_memory_usage(self, service: str) -> float:
        pass

class LogsProvider(ABC):
    @abstractmethod
    def get_recent_logs(self, service: str, lines: int = 100) -> List[str]:
        pass

class ActionProvider(ABC):
    @abstractmethod
    def restart_service(self, service: str) -> bool:
        pass
        
    @abstractmethod
    def kill_process(self, pid: int) -> bool:
        pass
