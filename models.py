from pydantic import BaseModel, Field
from typing import Literal, Optional
from openenv.core.models import Action, Observation

class SREAction(Action):
    # The 3 allowed action types
    action_type: Literal["bash_command", "patch_file", "submit_report"] = Field(
        ..., description="The type of action to perform."
    )
    
    # Used ONLY if action_type == "bash_command"
    command: Optional[str] = Field(
        None, 
        description="A valid Linux terminal command (whitelisted only)."
    )
    
    # Used ONLY if action_type == "patch_file"
    file_path: Optional[str] = Field(
        None, 
        description="The absolute path of the file to modify. Must be inside /tmp/sre_workspace/"
    )
    new_content: Optional[str] = Field(
        None, 
        description="The completely new code/text to overwrite the target file with."
    )
    
    # Used ONLY if action_type == "submit_report"
    root_cause: Optional[str] = Field(
        None, 
        description="Final explanation of the root cause and the applied fix."
    )

class SREObservation(Observation):
    terminal_output: str = Field(
        ..., 
        description="The stdout/stderr from the last action. Truncated to 5000 chars."
    )
    current_directory: str = Field(
        ..., 
        description="The current working directory."
    )
    system_health_score: float = Field(
        ..., 
        description="System health score. Starts at 1.0. Drops if you prioritize incorrectly."
    )