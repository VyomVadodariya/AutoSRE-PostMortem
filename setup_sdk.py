import os

print("--- 🛠️ BUILDING OPENENV SDK STUBS ---")

# 1. Create the folder structure
os.makedirs("openenv/core", exist_ok=True)

# 2. Make them valid Python modules
with open("openenv/__init__.py", "w") as f: f.write("")
with open("openenv/core/__init__.py", "w") as f: f.write("")

# 3. Create the Base Models
models_code = """from pydantic import BaseModel

class Action(BaseModel):
    pass

class Observation(BaseModel):
    pass

class StepResult(BaseModel):
    observation: Observation
    reward: float
    done: bool
"""
with open("openenv/core/models.py", "w") as f:
    f.write(models_code)

# 4. Create the Base Environment
env_code = """from abc import ABC, abstractmethod
from .models import Action, Observation, StepResult

class Environment(ABC):
    @abstractmethod
    def reset(self, **kwargs) -> Observation:
        pass

    @abstractmethod
    def step(self, action: Action) -> StepResult:
        pass
"""
with open("openenv/core/environment.py", "w") as f:
    f.write(env_code)

print("✅ OpenEnv SDK successfully mocked! You can now run the engine.")