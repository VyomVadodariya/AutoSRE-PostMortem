from abc import ABC, abstractmethod
from .models import Action, Observation, StepResult

class Environment(ABC):
    @abstractmethod
    def reset(self, **kwargs) -> Observation:
        pass

    @abstractmethod
    def step(self, action: Action) -> StepResult:
        pass
