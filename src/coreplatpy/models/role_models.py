from pydantic import BaseModel, Field
from typing import Dict, Any

class Role(BaseModel):
    attributes: Dict[str, Any] = Field(default_factory=dict)

class RoleUpdate(BaseModel):
    attributes: Dict[str, Any] = Field(default_factory=dict)
