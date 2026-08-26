import abc
from typing import Any

from environment.incidents.models import Incident


class BaseAgent(abc.ABC):
    @property
    @abc.abstractmethod
    def name(self) -> str:
        """Name of the agent."""

    @abc.abstractmethod
    def handle_incident(self, incident: Incident) -> dict[str, Any]:
        """
        Handle the given incident and return a dictionary containing actions taken,
        tokens used, and other relevant metadata for evaluation.
        """
