from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from datetime import datetime
import os
from tqdm import tqdm
from threading import Thread

chunk_size = 5 * 1024 * 1024


class Bucket(BaseModel):
    id: str = Field(alias='_id', validation_alias='_id')
    name: str
    creation_date: Optional[datetime] = None

class Updated(BaseModel):
    date: datetime = None
    user: str = ""

class Meta(BaseModel):
    creator: str = ""
    description: str = ""
    title: str = ""
    date_creation: datetime = None
    read: List[str] = []
    write: List[str] = []
    tags: Optional[List[str]] = []
    update: Updated = Updated()

class CopernicusTaskError(BaseModel):
    reason: str = ""
    message: str = ""
    url: Optional[str] = ""
    context: Optional[list] = []
    permanent: Optional[bool] = False
    who: Optional[str] = ""


class CopernicusDetails(BaseModel):
    task_id: str = ""
    service: str = ""
    fingerprint: str = ""
    status: str = ""
    error: Optional[CopernicusTaskError] = CopernicusTaskError()

class File(BaseModel):
    id: str = Field(alias='_id', default=None)
    meta: Meta = Meta()
    folder: str = ""
    ancestors: List[str] = []
    original_title: str = ""
    file_type: str = ""
    size: int = 0
    total: int = 0
    copernicus_details: Optional[CopernicusDetails] = CopernicusDetails()

class Part(BaseModel):
    id: str = Field(alias='_id')
    part_number: int
    file_id: str
    size: int
    upload_info: dict


class PostFolder(BaseModel):
    meta: Meta
    parent: str

class CopyModel(BaseModel):
    id: str = Field(alias='_id')
    destination: str
    new_name: str

class Folder(BaseModel):
    id: str = Field(alias='_id')
    meta: Meta
    parent: str
    ancestors: List[str]
    files: List[str]
    folders: List[str]
    level: int
    size: int

    client_params: Optional[dict] = {}
    def upload_file(self, path: str, meta: dict = None):
        from ..storage.files import initialize_upload, send_part
        from ..utils.helpers import split_file_chunks
        from .generic_models import ErrorReport

        file_size = os.path.getsize(path)
        num_chunks = file_size // chunk_size
        if file_size % chunk_size != 0:
            num_chunks += 1

        if meta:
            meta = Meta.model_validate(meta)
        else:
            meta = Meta()

        file = File(meta=meta, size=file_size, original_title=path, total=num_chunks, folder=self.id)
        resp = initialize_upload(self.client_params['api_url'], file, num_chunks, self.client_params['api_key'])

        if isinstance(resp, ErrorReport):
            return resp

        chunks = split_file_chunks(path, num_chunks)
        threads = []
        for i in range(1, resp.total + 1):
            thread = Thread(target=send_part, args=(self.client_params['api_url'], next(chunks), i, resp.id, self.client_params['api_key']))
            thread.start()
            threads.append(thread)

        for thread in tqdm(threads, desc=f'Uploading {resp.meta.title}'):
            thread.join()

    def list_items(self):
        from ..storage.folders import list_folder_items
        return list_folder_items(self.client_params['api_url'], self.id, self.client_params['api_key'])

    def save_file(self, file_id:str, path: str):
        from ..storage.files import get_info, get_part
        from .generic_models import ErrorReport
        from ..utils import preety_print_error

        file_info = get_info(self.client_params['api_url'], file_id, self.client_params['api_key'])
        if isinstance(file_info, ErrorReport):
            preety_print_error(file_info)
            raise ValueError('Could not find file')

        results = [b''] * file_info.total
        threads = []
        file = b''

        for i in range(1, file_info.total + 1):
            thread = Thread(target=get_part, args=(self.client_params['api_url'], file_id, results, i, self.client_params['api_key']))
            thread.start()
            threads.append(thread)

        for thread in tqdm(threads, desc=f'Multi-Thread Download of {file_info.meta.title}'):
            thread.join()

        with open(os.path.join(path, f"{file_info.meta.title}.{file_info.file_type}"), 'wb') as f:
            f.write(b''.join(results))

    def create_folder(self, name: str, description: str = ""):
        from ..storage.folders import post_folder
        meta = Meta(title=name, description=description)
        folder = PostFolder(meta=meta, parent=self.id)
        new_folder = post_folder(self.client_params['api_url'], folder, self.client_params['api_key'])
        return new_folder

    def copy_to(self, destination:str, new_name: str = None):
        from ..storage.folders import copy_folder
        if not new_name:
            new_name = self.meta.title
        body = CopyModel(_id=self.id, destination=destination, new_name=new_name)
        new_folder = copy_folder(self.client_params['api_url'], body, self.client_params['api_key'])
        return new_folder

    def share_with_organizations(self, organizations: List[str]):
        from .generic_models import ErrorReport
        from .account_models import Organization
        from ..account.group_api import post_organization, get_organization_info, get_organization_members
        from ..utils.helpers import preety_print_error
        from ..storage.buckets import create_bucket

        user_org = get_organization_info(self.client_params['account_url'], self.ancestors[0], self.client_params['api_key'])
        if isinstance(user_org, ErrorReport):
            preety_print_error(user_org)
            return None

        organizations.append(user_org.name)

        users = [get_organization_members(self.client_params['account_url'], org, self.client_params['api_key']) for org in organizations]
        users = [item for sublist in users for item in sublist]

        new_name = '-'.join(sorted(organizations))

        new_org = Organization(name=new_name, path='/')

        resp = post_organization(self.client_params['account_url'], new_org, self.client_params['api_key'])
        if isinstance(resp, ErrorReport):
            # if resp.status == 409:
            #     resp = ()
            preety_print_error(resp)
            return None

        orgId = resp.id
        bucket = Bucket(_id=orgId, name=new_name)
        resp = create_bucket(self.client_params['api_url'], bucket, self.client_params['api_key'])
        if isinstance(resp, ErrorReport):
            preety_print_error(resp)
            return None

        return self.copy_to(orgId, self.meta.title)

class FolderList(BaseModel):
	files: List[File]
	folders: List[Folder]
