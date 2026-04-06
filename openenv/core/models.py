from pydantic import BaseModel

class Action(BaseModel):
    pass

class Observation(BaseModel):
    pass

class StepResult(BaseModel):
    observation: Observation
    reward: float
    done: bool
