import requests
from urllib.parse import urlencode
from ..models import ErrorReport, Folder, FolderList, PostFolder, CopyModel
from ..models.cop_models import CopernicusTaskError, CopernicusTask, CopernicusDetails, Details
from typing import Union
from ..utils import safe_data_request

endpoint = "copernicus"

def get_list(baseurl: str, service: str, token: str) -> Union[Folder, ErrorReport]:
    uri = baseurl + endpoint + service + '/getall'
    data = None
    head = {'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'}

    response = safe_data_request('GET', uri, data, head)
    if isinstance(response, ErrorReport):
        return response
    return Folder.model_validate(response)


def get_form(baseurl: str, service: str, dataset_id: str, token: str) -> Union[Folder, ErrorReport]:
    uri = baseurl + endpoint + '/'+ service + '/getform/' + dataset_id
    data = None
    head = {'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'}

    response = safe_data_request('GET', uri, data, head)
    if isinstance(response, ErrorReport):
        return response
    return FolderList.model_validate(response)


def get_status(baseurl: str, task_id: str, token: str) -> Union[CopernicusTask, ErrorReport]:

    uri = baseurl + endpoint + '/getstatus/' + task_id
    data = None
    head = {'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'}

    response = safe_data_request('GET', uri, data, head)
    if isinstance(response, ErrorReport):
        return response
    return CopernicusTask.model_validate(response)


def post_dataset(baseurl: str, body: Details, token: str) -> Union[CopernicusDetails, ErrorReport]:

    uri = baseurl + endpoint + "/dataset"
    data = body.model_dump_json(by_alias=True)
    head = {'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'}

    response = safe_data_request('POST', uri, data, head)
    if isinstance(response, ErrorReport):
        return response
    return CopernicusDetails.model_validate(response) #do we want copernicusdetails or copericustask?
