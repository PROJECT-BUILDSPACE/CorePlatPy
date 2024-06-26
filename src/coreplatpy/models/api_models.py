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
        from ..utils.helpers import split_file_chunks, preety_print_error
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
            preety_print_error(resp)
            return resp

        chunks = split_file_chunks(path, num_chunks)
        threads = []
        for i in range(1, resp.total + 1):
            thread = Thread(target=send_part, args=(self.client_params['api_url'], next(chunks), i, resp.id, self.client_params['api_key']))
            thread.start()
            threads.append(thread)

        for thread in tqdm(threads, desc=f'Uploading {resp.meta.title}'):
            thread.join()

    def grab_file_info(self, file_id:str = None, file_name:str = None):
        from ..storage.files import get_info
        from .generic_models import ErrorReport
        from ..utils import preety_print_error

        if (file_id is None and file_name is None) or (file_id is not None and file_name is not None):
            error = ErrorReport(
                reason="Parameters file_id and file_name are mutually exclusive, meaning you can (and must) pass value only to one of them")
            preety_print_error(error)
            return None
        elif file_name:
            for file in self.list_items().files:
                if file.meta.title == file_name:
                    file_info = file
                    break
        else:
            file_info = get_info(self.client_params['api_url'], file_id, self.client_params['api_key'])

        return file_info



    def list_items(self):
        from ..storage.folders import list_folder_items
        return list_folder_items(self.client_params['api_url'], self.id, self.client_params['api_key'])

    def expand_items_tree(self):
        def __iterative__call__(folder_id, level=0):
            from ..storage.folders import list_folder_items
            items = list_folder_items(self.client_params['api_url'], folder_id, self.client_params['api_key'])
            resp = ""
            if len(items.folders) > 0:
                for folder in items.folders:
                    resp += level * '\t' + f"└── 📁{folder.meta.title}\n"
                    resp += __iterative__call__(folder.id, level + 1)
            for item in items.files:
                resp += level * '\t' + f"    📄{item.meta.title}\n"
            return resp

        return f"📁{self.meta.title}\n" + __iterative__call__(self.id)

    def save_file(self, path: str, file_id:str = None, file_name:str = None):
        from ..storage.files import get_info, get_part
        from ..storage.folders import folder_acquisition_by_name
        from .generic_models import ErrorReport
        from ..utils import preety_print_error

        file_info = self.grab_file_info(file_name=file_name, file_id=file_id)

        if isinstance(file_info, ErrorReport):
            raise ValueError('Could not find file')

        results = [b''] * file_info.total
        threads = []

        for i in range(1, file_info.total + 1):
            thread = Thread(target=get_part, args=(self.client_params['api_url'], file_info.id, results, i, self.client_params['api_key']))
            thread.start()
            threads.append(thread)

        for thread in tqdm(threads, desc=f'Multi-Thread Download of {file_info.meta.title}'):
            thread.join()

        with open(os.path.join(path, f"{file_info.meta.title}{file_info.file_type}"), 'wb') as f:
            f.write(b''.join(results))

    def download_file(self, file_id:str = None, file_name:str = None) -> bytes:
        from ..storage.files import get_info, get_part
        from ..storage.folders import folder_acquisition_by_name
        from .generic_models import ErrorReport
        from ..utils import preety_print_error

        file_info = self.grab_file_info(file_name=file_name, file_id=file_id)

        if isinstance(file_info, ErrorReport):
            raise ValueError('Could not find file')

        results = [b''] * file_info.total
        threads = []

        for i in range(1, file_info.total + 1):
            thread = Thread(target=get_part, args=(self.client_params['api_url'], file_info.id, results, i, self.client_params['api_key']))
            thread.start()
            threads.append(thread)

        for thread in tqdm(threads, desc=f'Multi-Thread Download of {file_info.meta.title}'):
            thread.join()

        return b''.join(results)


    def create_folder(self, name: str, description: str = ""):
        from ..storage.folders import post_folder
        meta = Meta(title=name, description=description)
        folder = PostFolder(meta=meta, parent=self.id)
        new_folder = post_folder(self.client_params['api_url'], folder, self.client_params['api_key'])
        return new_folder

    def copy_to(self, destination_name:str = None, destination_id:str = None, new_name: str = None):
        from ..storage.folders import copy_folder, folder_acquisition_by_name
        from .generic_models import ErrorReport

        if not new_name:
            new_name = self.meta.title

        if (destination_id is None and destination_name is None) or (destination_id is not None and destination_name is not None):
            error = ErrorReport(
                reason="Parameters destination_id and destination_name are mutually exclusive, meaning you can (and must) pass value only to one of them")
            preety_print_error(error)
            return None
        elif destination_name:
            destination = folder_acquisition_by_name(self.client_params['api_url'], destination_name, self.client_params['api_key'])
            if isinstance(destination, ErrorReport):
                preety_print_error(destination)
                return None
            destination_id = destination.id
        else:
            pass
        body = CopyModel(_id=self.id, destination=destination_id, new_name=new_name)
        new_folder = copy_folder(self.client_params['api_url'], body, self.client_params['api_key'])
        return new_folder

    def share_with_organizations(self, organizations: List[str]):
        from .generic_models import ErrorReport
        from .account_models import Organization, JoinGroupBody
        from ..account.group_api import post_organization, get_organization_by_id, get_organization_members, get_organization_by_name, post_new_group
        from ..utils.helpers import preety_print_error
        from ..storage.buckets import create_bucket

        user_org = get_organization_by_id(self.client_params['account_url'], self.ancestors[0], self.client_params['api_key'])
        if isinstance(user_org, ErrorReport):
            preety_print_error(user_org)
            return None

        organizations.append(user_org.name)

        users = {org:get_organization_members(self.client_params['account_url'], org, self.client_params['api_key']) for org in organizations}
        # users = {user: ('admin' if key == user_org.name else 'member') for key, val in users.items() for user in val}

        new_name = '-'.join(sorted(organizations))

        new_org = Organization(name=new_name, path='/')

        resp = post_organization(self.client_params['account_url'], new_org, self.client_params['api_key'])
        if isinstance(resp, ErrorReport):
            if resp.status == 409:
                resp = get_organization_by_name(self.client_params['account_url'], new_name, self.client_params['api_key'])
            # preety_print_error(resp)
            # return None

        orgId = resp.id
        bucket = Bucket(_id=orgId, name=new_name)
        resp = create_bucket(self.client_params['api_url'], bucket, self.client_params['api_key'])
        if isinstance(resp, ErrorReport):
            preety_print_error(resp)
            return None

        # Add users to shared organization. Admins are the users of the Organization that Shares data.
        body = {"users": [ {user: {'admin': (True if key == user_org.name else False)}} for key, val in users.items() for user in val ]}
        data = JoinGroupBody.model_validate(body)
        resp = post_new_group(self.client_params['account_url'], new_name, data, self.client_params['api_key'])
        if isinstance(resp, ErrorReport):
            preety_print_error(resp)
            return None

        return self.copy_to(destination_id=orgId, new_name=self.meta.title)

class FolderList(BaseModel):
	files: List[File]
	folders: List[Folder]
