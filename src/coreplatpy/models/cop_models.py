from pydantic import BaseModel, Field
from typing import List, Dict, Optional


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
    openGroups: Optional[dict]
    searchable: Optional[bool]


class RangeLocal:
    e: Optional[float]
    n: Optional[float]
    w: Optional[float]
    s: Optional[float]


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
    maxlength: Optional[int]
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
    displayaslist: Optional[bool]
    fullheight: Optional[bool]
    withmap: Optional[bool]
    wrapping: Optional[bool]
    precision: Optional[int]
    maximum_selections: Optional[int]
    text_file: Optional[str]
    information: Optional[str]
    accordionOptions: Optional[AccordionOpts]
    default: Optional[dict]
    extentlabels: Optional[List[str]]
    groups: Optional[dict]
    range: Optional[RangeLocal]
    changevisible: Optional[bool]
    concat: Optional[str]
    latitude: Optional[Coords]
    longitude: Optional[Coords]
    projection: Optional[Projection]
    text: Optional[str]
    fields: Optional[List[Fields]]


class CopernicusInput(BaseModel):
    dataset_name: str
    body: Details


class Form(BaseModel):
    css: Optional[str]
    details: Optional[Details]
    help: Optional[str]
    label: Optional[str]
    name: Optional[str]
    required: Optional[bool]
    type: Optional[str]