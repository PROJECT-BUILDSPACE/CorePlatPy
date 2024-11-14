from coreplatpy.models import File, CopernicusInput, CopernicusTask
from coreplatpy.storage import get_list, get_form, post_dataset, get_available
from coreplatpy.storage import folder_acquisition_by_name
from typing import Union
from ..utils import ensure_token



class Copernicus:
    """
    Copernicus Client for the Core Platform.
    """
    def __init__(self, api_url=None, account_url=None, api_key=None, user_id=None, refresh_token=None, expires_at=None) -> None:
        self.api_url = api_url
        self.account_url = account_url
        self.api_key = api_key
        self.user_id = user_id
        self.refresh_token = refresh_token
        self.expires_at = expires_at

        self.__folder__ = folder_acquisition_by_name(api_url, 'Copernicus', api_key)
        self.__folder__.client_params = self.__get_instance_variables__()

    def __get_instance_variables__(self):
        return {k: v for k, v in self.__dict__.items() if not k.startswith('__') and not callable(v)}

    @ensure_token
    def list_service_datasets(self, service:str):
        resource_list = get_list(self.api_url, service, self.api_key)
        return resource_list

    @ensure_token
    def get_dataset_form(self,  service:str, dataset:str):
        dataset_form = get_form(self.api_url, service, dataset, self.api_key)
        return dataset_form

    @ensure_token
    def request_dataset(self, service:str, dataset_name:str, dataset_params) -> Union[File, None]:
        body = CopernicusInput(dataset_name=dataset_name, body=dataset_params)
        file_task = post_dataset(self.api_url, body, service, self.api_key)
        return file_task

    @ensure_token
    def get_dataset(self, dataset_id):
        return self.__folder__.get_file(file_id=dataset_id)

    @ensure_token
    def get_folder(self):
        return self.__folder__

    @ensure_token
    def download_dataset(self, service:str, dataset_name:str, dataset_params: dict):
        dataset = self.get_dataset(service, dataset_name, dataset_params)
        return dataset.download()

    @ensure_token
    def store_dataset(self, service:str, dataset_name:str, dataset_params: dict, path: str):
        dataset = self.get_dataset(service, dataset_name, dataset_params)
        return dataset.store(path)

    @ensure_token
    def list_available_datasets(self, service:str = 'all'):
        return get_available(self.api_url, service, self.api_key)


