import requests
from urllib.parse import urlencode
from ..models import ErrorReport, File
from typing import Union
from ..utils import safe_data_request

endpoint = "file"

def initialize_upload(baseurl: str, file: File, total: int, token: str) -> Union[File, ErrorReport]:
    uri = baseurl + endpoint
    data = file.model_dump_json(by_alias=True, exclude_none=True)
    head = {'Content-Type': 'application/json', 'Authorization': f'Bearer {token}', 'total': f'{file.total}'}

    response = safe_data_request('POST', uri, data, head)
    if isinstance(response, ErrorReport):
        return response
    return File.model_validate(response)

def send_part(baseurl: str, part_raw: bytes, index: int, file_id, token: str) -> Union[File, ErrorReport]:
    uri = baseurl + f'{endpoint}/{file_id}?part={index}'
    headers = {'Content-Type': 'application/octet-stream', 'Authorization': f'Bearer {token}', 'Content-Length': f'{len(part_raw)}'}
    print(len(part_raw))
    response = safe_data_request('POST', uri, headers=headers, data=part_raw)
    if isinstance(response, ErrorReport):
        raise ValueError(f"HTTP Status: {response.status} \nHTTP Reason: {response.reason} \nAPI Message: {response.message} \nAPI Status Code: {response.internal_status}")
    return File.model_validate(response)

def get_part(baseurl: str, file_id: str, results: list, index: int, token: str):
    uri = baseurl + f'{endpoint}/{file_id}?part={index}'
    headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'}

    response = safe_data_request('GET', uri, headers=headers, data=None)
    if isinstance(response, ErrorReport):
        return response

    results[index-1] = response

def get_info(baseurl: str, file_id: str, token: str) -> Union[File, ErrorReport]:
    uri = baseurl + f'{endpoint}/info/{file_id}'
    headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'}

    response = safe_data_request('GET', uri, headers=headers, data=None)
    if isinstance(response, ErrorReport):
        return response
    return File.model_validate(response)
def delete_file(baseurl: str, file_id: str, token: str) -> Union[File, ErrorReport]:
    return

def update_file(baseurl: str, file_id: str, token: str) -> Union[File, ErrorReport]:
    return