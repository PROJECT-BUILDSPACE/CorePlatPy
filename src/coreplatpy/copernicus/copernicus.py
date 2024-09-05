import requests, json
from urllib.parse import urlencode
from ..models import ErrorReport, Folder, FolderList, PostFolder, CopyModel
from ..models.cop_models import CopernicusTaskError, CopernicusTask, CopernicusDetails, Details, Form
from typing import Union
from ..utils import safe_data_request

endpoint = "/copernicus"


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


def get_status(baseurl: str, task_id: str, token: str) -> Union[CopernicusTask, ErrorReport]:

    uri = baseurl + endpoint + '/getstatus/' + task_id
    data = None
    head = {'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'}

    response = safe_data_request('GET', uri, data, head)
    if isinstance(response, ErrorReport):
        return response
    return response


def post_dataset(baseurl: str, body: Details, service: str, token: str) -> Union[CopernicusDetails, ErrorReport]:

    uri = baseurl + endpoint + '/' + service + "/dataset"
    data = body
    print(json.dumps(data, indent=4))
    head = {'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'}

    response = safe_data_request('POST', uri, json.dumps(data), head)
    print(response)
    if isinstance(response, ErrorReport):
        return response
    return CopernicusDetails.model_validate(response) #do we want copernicusdetails or copericustask?
