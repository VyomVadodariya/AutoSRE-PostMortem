from typing import Dict, List, Set
from pydantic import BaseModel, Field

class ServiceNode(BaseModel):
    name: str
    dependencies: List[str] = Field(default_factory=list)
    is_database: bool = False
    
class DependencyGraph:
    def __init__(self):
        self.nodes: Dict[str, ServiceNode] = {}
        
    def add_service(self, name: str, dependencies: List[str] = None, is_database: bool = False):
        self.nodes[name] = ServiceNode(
            name=name, 
            dependencies=dependencies or [],
            is_database=is_database
        )
        
    def get_downstream_impact(self, failed_service: str) -> List[str]:
        """
        If a service fails, which services depend on it?
        (Services that call the failed service will be impacted)
        """
        impacted = set()
        for name, node in self.nodes.items():
            if failed_service in node.dependencies:
                if name not in impacted:
                    impacted.add(name)
                    # Recursively find others
                    impacted.update(self.get_downstream_impact(name))
        return list(impacted)

    def get_upstream_dependencies(self, service: str) -> List[str]:
        """
        What does this service depend on? 
        If this service is failing, what upstream services should we check?
        """
        if service not in self.nodes:
            return []
        
        deps = self.nodes[service].dependencies
        all_deps = set(deps)
        for dep in deps:
            all_deps.update(self.get_upstream_dependencies(dep))
            
        return list(all_deps)
