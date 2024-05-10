import requests
from urllib.parse import urlencode
from ..models import ErrorReport, Folder, FolderList, PostFolder, CopyModel
from typing import Union
from ..utils import safe_data_request

endpoint = "folder"

def get_folder_by_id(baseurl: str, folder_id: str, token: str) -> Union[Folder, ErrorReport]:
    uri = baseurl + endpoint + f'?id={folder_id}'
    data = None
    head = {'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'}

    response = safe_data_request('GET', uri, data, head)
    if isinstance(response, ErrorReport):
        return response
    return Folder.model_validate(response)


def list_folder_items(baseurl: str, folder_id: str, token: str) -> Union[FolderList, ErrorReport]:
    uri = baseurl + endpoint + f'/list?id={folder_id}'
    data = None
    head = {'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'}

    response = safe_data_request('GET', uri, data, head)
    if isinstance(response, ErrorReport):
        return response
    return FolderList.model_validate(response)

def post_folder(baseurl: str, body: PostFolder, token: str) -> Union[Folder, ErrorReport]:
    uri = baseurl + endpoint
    data = body.model_dump_json()
    head = {'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'}

    response = safe_data_request('POST', uri, data, head)
    if isinstance(response, ErrorReport):
        return response
    return Folder.model_validate(response)

def copy_folder(baseurl: str, body: CopyModel, token: str) -> Union[Folder, ErrorReport]:
    uri = baseurl + endpoint + '/copy'
    data = body.model_dump_json(by_alias=True)
    head = {'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'}

    response = safe_data_request('POST', uri, data, head)
    if isinstance(response, ErrorReport):
        return response
    return Folder.model_validate(response)
