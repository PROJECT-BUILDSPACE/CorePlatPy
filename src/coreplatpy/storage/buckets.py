import requests
from urllib.parse import urlencode
from ..models import ErrorReport, Bucket
from typing import Union
from ..utils import safe_json_request

endpoint = "bucket"

def create_bucket(baseurl: str, bucket: Bucket, token: str) -> Union[Bucket, ErrorReport]:
    uri = baseurl + endpoint
    # data = bucket.model_dump(exclude_none=True, exclude_unset=False)
    data = bucket.model_dump(by_alias=True, exclude_none=True, exclude_unset=False)
    head = {'Content-Type': 'application/application-json', 'Authorization': f'Bearer {token}'}

    response = safe_json_request("POST", uri ,data, head)

    if isinstance(response,ErrorReport):
        return response
    return Bucket.model_validate(response)


def delete_bucket(baseurl: str, bucket_id: str, token: str) -> Union[Bucket, ErrorReport]:
    uri = baseurl + endpoint + f'/{bucket_id}'
    data = None
    head = {'Content-Type': 'application/application-json', 'Authorization': f'Bearer {token}'}

    response = safe_json_request("DELETE", uri ,data, head)

    if isinstance(response,ErrorReport):
        return response
    return Bucket.model_validate(response)

