from pydantic import BaseModel, Field
from typing import List, Dict, Optional

class CopernicusInput(BaseModel):
    dataset_name: str
    body: str

class Form(BaseModel):
    access_token: str
    expires_in: int
    refresh_expires_in: int
    refresh_token: str
    token_type: str
    not_before_policy: int = Field(alias='not-before-policy')
    session_state: str
    scope: str

class Details(BaseModel):
    columns: int
    id: int
    labels: str
    values: List[str]
    accordion: bool
    accordion_groups: bool
    display_as_list: bool
    full_height: bool
    withmap: bool
    wrapping: bool
    precision: int
    maximum_selections: int
    text_file: str
    information: str
    accordion_options: str
    default: str
    extent_labels: List[str]
    Groups: str
    Range: str

