import requests
from ..models import ErrorReport, RoleUpdate, Role
from typing import Union, Dict
from ..utils import safe_json_request

# endpoint = "role"
endpoint = "role/group-admin/"

def update_role(baseurl: str, group_id: str, role_update: RoleUpdate, token: str) -> Union[None, ErrorReport]:
    uri = baseurl + endpoint + f"{group_id}"
    data = role_update.model_dump(exclude_unset=True, exclude_none=True)
    head = {'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'}
    
    response = safe_json_request('PUT', uri, data, head)
    if isinstance(response, ErrorReport):
        return response
    return None

def get_role(baseurl: str, group_id: str, token: str) -> Union[Dict, ErrorReport]:
    uri = baseurl + endpoint + f"{group_id}"
    head = {'Authorization': f'Bearer {token}'}
    
    response = safe_json_request('GET', uri, None, head)
    # if isinstance(response, ErrorReport):
    #     return response
    # return Role.model_validate(response)
    return response

