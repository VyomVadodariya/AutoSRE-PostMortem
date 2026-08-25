from environment.adapters.interfaces import MetricsProvider, LogsProvider, ActionProvider
from typing import List

class KubernetesMetricsProvider(MetricsProvider):
    """
    Adapter that connects the AI Agent to a real Prometheus/Kubernetes cluster.
    This replaces the simulation MetricsStore when deployed to production.
    """
    def __init__(self, prometheus_url: str):
        self.prometheus_url = prometheus_url
        
    def get_cpu_usage(self, service: str) -> float:
        # TODO: Implement actual PromQL query
        return 0.0

    def get_memory_usage(self, service: str) -> float:
        # TODO: Implement actual PromQL query
        return 0.0

class KubernetesLogsProvider(LogsProvider):
    def __init__(self, k8s_client):
        self.client = k8s_client
        
    def get_recent_logs(self, service: str, lines: int = 100) -> List[str]:
        # TODO: Implement actual k8s client log retrieval
        return []

class KubernetesActionProvider(ActionProvider):
    def __init__(self, k8s_client):
        self.client = k8s_client
        
    def restart_service(self, service: str) -> bool:
        # TODO: Implement pod deletion / rollout restart
        return True
        
    def kill_process(self, pid: int) -> bool:
        # Not typically done directly in K8s, usually restart pod
        return False
