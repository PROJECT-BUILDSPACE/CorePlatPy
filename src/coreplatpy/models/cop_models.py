from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from numpy import float32


class Form(BaseModel):
    access_token: str
    expires_in: int
    refresh_expires_in: int
    refresh_token: str
    token_type: str
    not_before_policy: int = Field(alias='not-before-policy')
    session_state: str
    scope: str


class CopernicusTaskError(BaseModel):
    reason: str = ""
    message: str = ""
    url: Optional[str] = ""
    context: Optional[list] = []
    permanent: Optional[bool] = False
    who: Optional[str] = ""


class CopernicusTask(BaseModel):
    state: str = ""
    location: str = ""
    request_id: str = ""
    message: Optional[str] = ""
    error: Optional[CopernicusTaskError] = CopernicusTaskError()


class CopernicusDetails(BaseModel):
    task_id: str = ""
    service: str = ""
    fingerprint: str = ""
    status: str = ""
    error: Optional[CopernicusTaskError] = CopernicusTaskError()


class AccordionOpts:
    open_groups: Optional[dict]
    searchable: Optional[bool]


class RangeLocal:
    e: Optional[float32]
    n: Optional[float32]
    w: Optional[float32]
    s: Optional[float32]


class CoordRange:
    min: Optional[int]
    max: Optional[int]


class Coords:
    default: Optional[int]
    precision: Optional[int]
    range: Optional[CoordRange]


class Projection:
    id: Optional[int]
    overlay: Optional[bool]
    use: Optional[bool]

class Fields:
    comments: Optional[str]
    max_length: Optional[int]
    placeholder: Optional[str]
    required: Optional[bool]
    type: Optional[str]


class Details(BaseModel):
    columns: Optional[int]
    id: Optional[int]
    labels: Optional[dict]
    values: Optional[List[str]]
    accordion: Optional[bool]
    accordion_groups: Optional[bool]
    display_as_list: Optional[bool]
    full_height: Optional[bool]
    with_map: Optional[bool]
    wrapping: Optional[bool]
    precision: Optional[int]
    maximum_selections: Optional[int]
    text_file: Optional[str]
    information: Optional[str]
    accordion_options: Optional[AccordionOpts]
    default: Optional[dict]
    extent_labels: Optional[List[str]]
    groups: Optional[dict]
    range: Optional[RangeLocal]
    change_visible: Optional[bool]
    concat: Optional[str]
    latitude: Optional[Coords]
    longitude: Optional[Coords]
    projection: Optional[Projection]
    text: Optional[str]
    fields: Optional[List[Fields]]


class CopernicusInput(BaseModel):
    dataset_name: str
    body: Details

