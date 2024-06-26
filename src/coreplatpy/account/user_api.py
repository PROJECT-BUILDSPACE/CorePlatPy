import requests
from urllib.parse import urlencode
from ..models import LoginParams, AccessGranted, UpdateUser, ErrorReport, UserData, UserRegistration
from typing import Union
from ..utils import safe_json_request, safe_login, safe_data_request

endpoint = "user/"


def authenticate_sync(baseurl: str, login_params: LoginParams) -> Union[AccessGranted, ErrorReport]:
    uri = baseurl + endpoint
    data = login_params.model_dump(exclude_unset=False)
    head = {'Content-Type': 'application/x-www-form-urlencoded'}

    response = safe_login(uri ,data, head)

    if isinstance(response,ErrorReport):
        return response
    return AccessGranted.model_validate(response)

def register(baseurl: str, register_params: UserRegistration) -> Union[None, ErrorReport]:
    uri = baseurl + endpoint + 'register/'
    data = register_params.model_dump()
    head = {'Content-Type': 'application/x-www-form-urlencoded'}

    response = safe_login(uri ,data, head)

    if isinstance(response,ErrorReport):
        return response
    return response

def update_info(baseurl: str, update: UpdateUser, token: str) -> Union[ErrorReport, None]:
    uri = baseurl + endpoint
    # data = update.model_dump(exclude_unset=True, exclude_none=True)
    data = update.model_dump(exclude_none=True)
    head = {'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'}

    response = safe_json_request('PUT', uri, data, head)
    if isinstance(response, ErrorReport):
        return response
    return None

def get_user_data(baseurl: str, token: str) -> Union[ErrorReport, UserData]:
    uri = baseurl + endpoint
    head = {'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'}
    data = None

    response = safe_json_request('GET', uri, data, head)
    if isinstance(response, ErrorReport):
        return response
    return UserData.model_validate(response)

def post_picture(baseurl: str, part_raw: bytes, file_id, token: str):
    uri = baseurl + f'{endpoint}picture/{file_id}'
    headers = {'Content-Type': 'application/octet-stream', 'Authorization': f'Bearer {token}', 'Content-Length': f'{len(part_raw)}'}

    response = safe_data_request('POST', uri, headers=headers, data=part_raw)
    if isinstance(response, ErrorReport):
        raise ValueError(f"HTTP Status: {response.status} \nHTTP Reason: {response.reason} \nAPI Message: {response.message} \nAPI Status Code: {response.internal_status}")
    return True