import requests
from ..models import Organization, ErrorReport
from typing import Union, List
from ..utils import safe_json_request

endpoint = "group/"

def post_organization(baseurl: str, organization: Organization, token:str) -> Union[Organization, ErrorReport]:
    uri = baseurl + endpoint
    data = organization.model_dump(exclude_unset=False)
    head = {'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'}

    response = safe_json_request('POST', uri, data, head)
    if isinstance(response, ErrorReport):
        return response
    return Organization.model_validate(response)

def get_user_organizations(baseurl: str, token:str) -> Union[List[Organization], ErrorReport]:
    uri = baseurl + endpoint
    data = None
    head = {'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'}

    response = safe_json_request('GET', uri, data, head)
    if isinstance(response, ErrorReport):
        return response
    return [Organization.model_validate(item) for item in response]

def post_new_group(baseurl: str, group_name: str, organization: Organization, token: str) -> Union[Organization, ErrorReport]:
    uri = baseurl + endpoint + f"{group_name}"
    data = organization.model_dump(exclude_unset=True)
    head = {'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'}

    response = safe_json_request('POST', uri, data, head)
    if isinstance(response, ErrorReport):
        return response
    return Organization.model_validate(response)

def delete_group(baseurl: str, group_name: str, token: str) -> Union[None, ErrorReport]:
    uri = baseurl + endpoint + f"{group_name}"
    head = {'Authorization': f'Bearer {token}'}

    response = safe_json_request('DELETE', uri, head)
    if isinstance(response, ErrorReport):
        return response
    return None  


def get_organization_by_id(baseurl: str, group_id: str, token:str) -> Union[Organization, ErrorReport]:
    uri = baseurl + endpoint + group_id
    data = None
    head = {'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'}

    response = safe_json_request('GET', uri, data, head)
    if isinstance(response, ErrorReport):
        return response
    return Organization.model_validate(response)


def get_organization_by_name(baseurl: str, group_name: str, token:str) -> Union[Organization, ErrorReport]:
    uri = baseurl + endpoint + group_name
    data = None
    head = {'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'}

    response = safe_json_request('GET', uri, data, head)
    if isinstance(response, ErrorReport):
        return response
    return Organization.model_validate(response)


def get_organization_members(baseurl: str, organization_name: str, token:str) -> Union[List[str], ErrorReport]:
    uri = baseurl + f'{endpoint + organization_name}/members'
    data = None
    head = {'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'}

    response = safe_json_request('GET', uri, data, head)
    if isinstance(response, ErrorReport):
        return response
    return response
