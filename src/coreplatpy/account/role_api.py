import requests
from ..models import RoleUpdate, ErrorReport, Role
from ..utils import safe_request
from typing import Union

# endpoint = "role"
endpoint = "role/group-admin/"

def update_role(baseurl: str, group_id: str, role_update: RoleUpdate, token: str) -> Union[None, ErrorReport]:
    uri = baseurl + endpoint + f"{group_id}"
    data = role_update.model_dump(exclude_unset=True, exclude_none=True)
    head = {'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'}
    
    response = safe_request('PUT', uri, data, head)
    if isinstance(response, ErrorReport):
        return response
    return None

def get_role(baseurl: str, group_id: str, token: str) -> Union[Role, ErrorReport]:
    uri = baseurl + endpoint + f"{group_id}"
    head = {'Authorization': f'Bearer {token}'}
    
    response = safe_request('GET', uri, None, head)
    if isinstance(response, ErrorReport):
        return response
    return Role.model_validate(response)
