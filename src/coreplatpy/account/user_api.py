import requests
from ..models import LoginParams, AccessGranted, UpdateUser, ErrorReport, UserData
from typing import Union
from ..utils import safe_request

endpoint = "user/"


def authenticate_sync(baseurl: str, login_params: LoginParams) -> Union[AccessGranted, ErrorReport]:
    uri = baseurl + endpoint
    data = login_params.model_dump(exclude_unset=False)
    head = {'Content-Type': 'application/json'}

    response = safe_request('POST', uri, data, head)
    if isinstance(response,ErrorReport):
        return response
    return AccessGranted.model_validate(response)

def update_info(baseurl: str, user_id: str, update: UpdateUser, token: str) -> Union[ErrorReport, None]:
    uri = baseurl + endpoint + user_id
    data = update.model_dump(exclude_unset=True, exclude_none=True)
    head = {'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'}

    response = safe_request('PUT', uri, data, head)
    if isinstance(response, ErrorReport):
        return response
    return None

def get_user_data(baseurl: str, user_id: str, token: str) -> Union[ErrorReport, UserData]:
    uri = baseurl + endpoint + user_id
    head = {'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'}
    data = None

    response = safe_request('GET', uri, data, head)
    if isinstance(response, ErrorReport):
        return response
    return UserData.model_validate(response)