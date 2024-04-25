from pydantic import BaseModel
from typing import Union

class ErrorReport(BaseModel):
    internal_status: Union[str, None] = 'No Internal Status Available'
    status: int = 400
    message: Union[str, None] = 'If you do not resolve the error, please contanct the CorePlatPy support team.'
    reason: str = 'Something unknown went wrong on the client side.'