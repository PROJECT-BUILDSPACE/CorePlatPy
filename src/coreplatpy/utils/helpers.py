from jwt import decode
from requests import Response
from ..models.generic_models import ErrorReport
from typing import Union
import requests
from ..globals.globals import Globals
from functools import wraps
from datetime import datetime
import requests


def respond_with_error(response: Response) -> ErrorReport:
    try:
        error = ErrorReport.model_validate(response.json())
    except:
        error = ErrorReport.model_validate({
            'internal_status': None,
            'status': response.status_code,
            'message': None,
            'reason': response.reason
        })
    return error

def preety_print_error(error: ErrorReport):
    print('Something went wrong...')
    print('HTTP Status:', str(error.status))
    print('HTTP Reason:', str(error.reason))
    print('API Status :', str(error.internal_status))
    print('API Message:', str(error.message))

def safe_login(uri: str, data: dict, headers: dict) -> Union[dict, ErrorReport]:
    try:
        response = requests.post(uri, data=data, headers=headers)
    except Exception as e:
        print("Error at request: " + str(e))
        return ErrorReport()
    else:
        if response.status_code >= 300:
            return respond_with_error(response)
        return response.json()

def safe_json_request(request: str, uri: str, data: Union[dict, None], headers: dict) -> Union[dict, ErrorReport, None]:
    requests_max_size = 10 * 1024 * 1024  # 10 MB
    session = requests.Session()
    session.max_request_size = requests_max_size
    if request == 'POST':
        try:
            if data:
                response = session.post(uri, json=data, headers=headers)
            else:
                response = session.post(uri, headers=headers)
        except Exception as e:
            print("Error at request: " + str(e))
            return ErrorReport()
        else:
            if response.status_code >= 300:
                return respond_with_error(response)
            if response.content:
                try:
                    return response.json()
                except:
                    return response.content
            else:
                return None
    elif request == 'GET':
        try:
            if data:
                response = session.get(uri, json=data, headers=headers)
            else:
                response = session.get(uri, headers=headers)
        except Exception as e:
            print("Error at request: " + str(e))
            return ErrorReport()
        else:
            if response.status_code >= 300:
                return respond_with_error(response)
            if response.content:
                try:
                    return response.json()
                except:
                    return response.content
            else:
                return None
    elif request == 'PUT':
        try:
            if data:
                response = session.put(uri, json=data, headers=headers)
            else:
                response = session.put(uri, headers=headers)
        except Exception as e:
            print("Error at request: " + str(e))
            return ErrorReport()
        else:
            if response.status_code >= 300:
                return respond_with_error(response)
            if response.content:
                try:
                    return response.json()
                except:
                    return response.content
            else:
                return None
    elif request == 'DELETE':
        try:
            if data:
                response = session.delete(uri, json=data, headers=headers)
            else:
                response = session.delete(uri, headers=headers)
        except Exception as e:
            print("Error at request: " + str(e))
            return ErrorReport()
        else:
            if response.status_code >= 300:
                return respond_with_error(response)
            if response.content:
                try:
                    return response.json()
                except:
                    return response.content
            else:
                return None
    else:
        print("Not a valid method: " + str(e))
        return ErrorReport()

def safe_data_request(request: str, uri: str, data: Union[dict, None], headers: dict) -> Union[dict, ErrorReport, None]:
    requests_max_size = 10 * 1024 * 1024  # 10 MB
    session = requests.Session()
    session.max_request_size = requests_max_size
    if request == 'POST':
        try:
            if data:
                response = session.post(uri, data=data, headers=headers)
            else:
                response = session.post(uri, headers=headers)
        except Exception as e:
            print("Error at request: " + str(e))
            return ErrorReport()
        else:
            if response.status_code >= 300:
                return respond_with_error(response)
            if response.content:
                try:
                    return response.json()
                except:
                    return response.content
            else:
                return None
    elif request == 'GET':
        try:
            if data:
                response = session.get(uri, data=data, headers=headers)
            else:
                response = session.get(uri, headers=headers)
        except Exception as e:
            print("Error at request: " + str(e))
            return ErrorReport()
        else:
            if response.status_code >= 300:
                return respond_with_error(response)
            if response.content:
                try:
                    return response.json()
                except:
                    return response.content
            else:
                return None
    elif request == 'PUT':
        try:
            if data:
                response = session.put(uri, data=data, headers=headers)
            else:
                response = session.put(uri, headers=headers)
        except Exception as e:
            print("Error at request: " + str(e))
            return ErrorReport()
        else:
            if response.status_code >= 300:
                return respond_with_error(response)
            if response.content:
                try:
                    return response.json()
                except:
                    return response.content
            else:
                return None
    elif request == 'DELETE':
        try:
            if data:
                response = session.delete(uri, data=data, headers=headers)
            else:
                response = session.delete(uri, headers=headers)
        except Exception as e:
            print("Error at request: " + str(e))
            return ErrorReport()
        else:
            if response.status_code >= 300:
                return respond_with_error(response)
            if response.content:
                try:
                    return response.json()
                except:
                    return response.content
            else:
                return None
    else:
        print("Not a valid method: " + str(e))
        return ErrorReport()

def split_file_chunks(file_path, num_chunks, chunk_size_mb = 1 * 1024 * 1024 ):
    with open(file_path, 'rb') as f:
        # Read the file in chunks
        for i in range(num_chunks):
            # Seek to the appropriate position in the file
            f.seek(i * chunk_size_mb)
            # Read the chunk
            chunk = f.read(chunk_size_mb)
            # Yield the chunk
            yield chunk

def ensure_token(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            if datetime.utcnow() >= self.expires_at:
                try:
                    response = requests.post(self.account_url + 'user/refresh', data={'refresh_token': self.refresh_token})
                    response.raise_for_status()
                except requests.RequestException as e:
                    print(f"Failed to refresh access token: {e}")
                else:
                    self.api_key = response.json()['access_token']
                    self.refresh_token = response.json()['refresh_token']
                    self.expires_at = datetime.utcfromtimestamp(decode(self.api_key, options={"verify_signature": False})['exp'])
        except AttributeError:
            if datetime.utcnow() >= self.client_params['expires_at']:
                try:
                    response = requests.post(self.client_params['account_url'] + 'user/refresh', data={'refresh_token': self.client_params['refresh_token']})
                    response.raise_for_status()
                except requests.RequestException as e:
                    print(f"Failed to refresh access token: {e}")
                else:
                    self.client_params['api_key'] = response.json()['access_token']
                    self.client_params['refresh_token'] = response.json()['refresh_token']
                    self.client_params['expires_at'] = datetime.utcfromtimestamp(decode(self.client_params['api_key'], options={"verify_signature": False})['exp'])
        except Exception as e:
            raise Exception(e)
        return func(self, *args, **kwargs)
    return wrapper