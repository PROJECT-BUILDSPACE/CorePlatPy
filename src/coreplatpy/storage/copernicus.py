import requests, json
from urllib.parse import urlencode
from coreplatpy.models import ErrorReport, Folder, FolderList, PostFolder, CopyModel, CopernicusTaskError, CopernicusTask, CopernicusRecord, Details, Form, CopernicusInput, File
from typing import Union, List
from coreplatpy.utils import safe_data_request, safe_json_request

endpoint = "copernicus"


def get_list(baseurl: str, service: str, token: str):
    uri = baseurl + endpoint + '/' + service + '/getall'
    data = None
    head = {'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'}

    response = safe_data_request('GET', uri, data, head)
    if isinstance(response, ErrorReport):
        return ErrorReport
    return response

def get_form(baseurl: str, service: str, dataset_name: str, token: str) -> Union[Form, ErrorReport]:
    uri = baseurl + endpoint + '/' + service + '/getform/' + dataset_name
    data = None
    head = {'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'}

    response = safe_data_request('GET', uri, data, head)
    if isinstance(response, ErrorReport):
        return ErrorReport
    return response


def get_status(baseurl: str, file_id: str, token: str) -> Union[File, ErrorReport]:

    uri = baseurl + endpoint + f'/copernicus/status/dataset/{file_id}'
    data = None
    head = {'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'}

    response = safe_data_request('GET', uri, data, head)
    if isinstance(response, ErrorReport):
        return response
    return File.model_validate(response) #do we want copernicusdetails or copericustask?


def post_dataset(baseurl: str, body: CopernicusInput, service: str, token: str) -> Union[File, ErrorReport]:

    uri = baseurl + endpoint + f"/{service}" + "/dataset"
    data = body.model_dump_json()
    head = {'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'}

    response = safe_data_request('POST', uri, data, head)
    if isinstance(response, ErrorReport):
        return response
    return File.model_validate(response) #do we want copernicusdetails or copericustask?


def get_available(baseurl: str, service: str, token: str) -> Union[List[CopernicusRecord], ErrorReport]:

    uri = baseurl + endpoint + f"/{service}/available"
    head = {'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'}
    data = None

    response = safe_data_request('GET', uri, data, head)
    if isinstance(response, ErrorReport):
        return response
    return [CopernicusRecord.model_validate(item) for item in response]