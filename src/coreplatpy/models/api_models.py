from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from datetime import datetime
import os
from tqdm import tqdm
from threading import Thread
from ..utils import ensure_token

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

    client_params: Optional[dict] = {}

    @ensure_token
    def save(self, path: str):
        from ..storage.files import get_part

        results = [b''] * self.total
        threads = []

        for i in range(1, self.total + 1):
            thread = Thread(target=get_part, args=(
            self.client_params['api_url'], self.id, results, i, self.client_params['api_key']))
            thread.start()
            threads.append(thread)

        for thread in tqdm(threads, desc=f'Multi-Thread Download of {self.meta.title}'):
            thread.join()

        with open(os.path.join(path, f"{self.meta.title}{self.file_type}"), 'wb') as f:
            f.write(b''.join(results))

    @ensure_token
    def download(self) -> bytes:
        from ..storage.files import get_part

        results = [b''] * self.total
        threads = []

        for i in range(1, self.total + 1):
            thread = Thread(target=get_part, args=(
            self.client_params['api_url'], self.id, results, i, self.client_params['api_key']))
            thread.start()
            threads.append(thread)

        for thread in tqdm(threads, desc=f'Multi-Thread Download of {self.meta.title}'):
            thread.join()

        return b''.join(results)


    @ensure_token
    def rename(self, new_name):
        """
            Rename current file
        """
        from ..storage.files import update_file
        self.meta.title = new_name
        return update_file(self.client_params['api_url'], self, self.client_params['api_key'])


    @ensure_token
    def copy_to(self, destination_name:str = None, destination_id:str = None, new_name: str = None):
        from ..storage.files import copy_file
        from ..storage.folders import folder_acquisition_by_name
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
        new_file = copy_file(self.client_params['api_url'], body, self.client_params['api_key'])
        new_file.client_params = self.client_params
        return new_file

    @ensure_token
    def move_to(self, destination_name:str = None, destination_id:str = None, new_name: str = None):
        from ..storage.files import move_file
        from ..storage.folders import folder_acquisition_by_name
        from .generic_models import ErrorReport

        keep_client_params = self.client_params

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
        moved_file = move_file(self.client_params['api_url'], body, self.client_params['api_key'])
        self.__class__ = moved_file.__class__
        self.__dict__ = moved_file.__dict__
        self.client_params = keep_client_params


    @ensure_token
    def delete(self) -> bool:
        from ..storage.files import delete_file
        from .generic_models import ErrorReport
        try:
            resp = delete_file(self.client_params['api_url'], self.id, self.client_params['api_key'])
            if isinstance(resp, ErrorReport):
                preety_print_error(resp)
                return False
            return True
        except Exception as e:
            print(f"Unexpected error while deleting folder: {e}")
            return False



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

    @ensure_token
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

        chunks = split_file_chunks(path, num_chunks, chunk_size)
        threads = []
        for i in range(1, resp.total + 1):
            thread = Thread(target=send_part, args=(self.client_params['api_url'], next(chunks), i, resp.id, self.client_params['api_key']))
            thread.start()
            threads.append(thread)

        for thread in tqdm(threads, desc=f'Uploading {resp.meta.title}'):
            thread.join()

    @ensure_token
    def beta_upload_file(self, path: str, meta: dict = None, verbose: bool = True):
        import concurrent.futures
        import multiprocessing

        from ..storage.files import initialize_upload, beta_send_part
        from ..utils.helpers import split_file_chunks, preety_print_error
        from .generic_models import ErrorReport

        file_size = os.path.getsize(path)
        num_chunks = int(file_size // chunk_size)
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

        chunks = split_file_chunks(path, num_chunks, chunk_size)

        with concurrent.futures.ThreadPoolExecutor(max_workers=multiprocessing.cpu_count()) as executor:
            futures = [
                executor.submit(beta_send_part, self.client_params['api_url'], next(chunks), i, resp.id, self.client_params['api_key'])
                for i in range(1, resp.total + 1)
            ]
            exc = None
            if verbose:
                for future in tqdm(concurrent.futures.as_completed(futures), total=resp.total):
                    try:
                        future.result()  # Will raise an exception if the thread has failed

                    except Exception as exc:
                        print(f'Chunk failed with exception: {exc}')
                        break
            else:
                for future in concurrent.futures.as_completed(futures):
                    try:
                        future.result()  # Will raise an exception if the thread has failed
                    except Exception as exc:
                        print(f'Chunk failed with exception: {exc}')
                        break

    @ensure_token
    def beta_upload_folder_contents(self, path: str, range: range = None):
        import concurrent.futures
        import multiprocessing
        with concurrent.futures.ThreadPoolExecutor(max_workers=multiprocessing.cpu_count()) as executor:
            files = os.listdir(path)
            if range:
                futures = [
                    executor.submit(self.beta_upload_file, path+files[j], {'title': files[j]}, False)
                    for j in range
                ]
                for future in tqdm(concurrent.futures.as_completed(futures), total=len(range)):
                    try:
                        future.result()  # Will raise an exception if the thread has failed
                    except Exception as exc:
                        print(f'Chunk failed with exception: {exc}')
                        break
            else:
                futures = [
                    executor.submit(self.beta_upload_file, path + file, {'title': file}, False)
                    for file in files
                ]
                for future in tqdm(concurrent.futures.as_completed(futures), total=len(files)):
                    try:
                        future.result()  # Will raise an exception if the thread has failed
                    except Exception as exc:
                        print(f'Chunk failed with exception: {exc}')
                        break


    @ensure_token
    def get_file(self, file_id:str = None, file_name:str = None):
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

        file_info.client_params = self.client_params
        return file_info



    @ensure_token
    def list_items(self):
        from ..storage.folders import list_folder_items
        return list_folder_items(self.client_params['api_url'], self.id, self.client_params['api_key'])

    @ensure_token
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

        print(f"📁{self.meta.title}\n" + __iterative__call__(self.id))

    @ensure_token
    def save_file(self, path: str, file_id:str = None, file_name:str = None):
        from ..storage.files import get_info, get_part
        from ..storage.folders import folder_acquisition_by_name
        from .generic_models import ErrorReport
        from ..utils import preety_print_error

        file_info = self.get_file(file_name=file_name, file_id=file_id)

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

    @ensure_token
    def download_file(self, file_id:str = None, file_name:str = None) -> bytes:
        from ..storage.files import get_info, get_part
        from ..storage.folders import folder_acquisition_by_name
        from .generic_models import ErrorReport
        from ..utils import preety_print_error

        file_info = self.get_file(file_name=file_name, file_id=file_id)

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


    @ensure_token
    def create_folder(self, name: str, description: str = ""):
        from ..storage.folders import post_folder
        meta = Meta(title=name, description=description)
        folder = PostFolder(meta=meta, parent=self.id)
        new_folder = post_folder(self.client_params['api_url'], folder, self.client_params['api_key'])
        return new_folder

    @ensure_token
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

    @ensure_token
    def share_with_organizations(self, organizations: List[str]):
        from .generic_models import ErrorReport
        from .account_models import Organization, JoinGroupBody
        from ..account.group_api import post_organization, get_organization_by_id, get_organization_members, get_organization_by_name, post_new_group
        from ..utils.helpers import preety_print_error
        from ..storage.buckets import create_bucket

        try:
            user_org = get_organization_by_id(self.client_params['account_url'], self.ancestors[0],
                                              self.client_params['api_key'])
        except IndexError:
            user_org = get_organization_by_id(self.client_params['account_url'], self.id,
                                              self.client_params['api_key'])
        except Exception as e:
            raise ValueError(f'Something unexpected just happend: {e}')
            return None

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

    @ensure_token
    def pop_nested_folder(self, folder_name: str = None, folder_id: str = None):
        from ..storage.folders import folder_acquisition_by_id
        from .generic_models import ErrorReport
        from ..utils.helpers import preety_print_error

        folder_id_names = {item.meta.title: item.id for item in self.list_items().folders}

        if (folder_id is None and folder_name is None) or (folder_id is not None and folder_name is not None):
            error = ErrorReport(
                reason="Parameters folder_id and folder_name are mutually exclusive, meaning you can (and must) pass value only to one of them")
            preety_print_error(error)
            return None
        elif folder_id:
            if folder_id not in folder_id_names.values():
                error = ErrorReport(
                    reason="Folder does not exist in current path. Consider using client.get_folder() with the provided id.")
                preety_print_error(error)
                return
            folder = folder_acquisition_by_id(self.client_params['api_url'], folder_id, self.client_params['api_key'])
            if isinstance(folder, ErrorReport):
                preety_print_error(folder)
                return None
        else:
            if folder_name not in folder_id_names.keys():
                error = ErrorReport(
                    reason="Folder does not exist in current path. Consider using folder.expand_items_tree() to double-check the folder name you provided.")
                preety_print_error(error)
                return None
            folder = folder_acquisition_by_id(self.client_params['api_url'], folder_id_names[folder_name],
                                             self.client_params['api_key'])
            if isinstance(folder, ErrorReport):
                preety_print_error(folder)
                return None
        return folder

    @ensure_token
    def step_into(self, folder_name: str = None, folder_id: str = None):
        keep_client_params = self.client_params
        go_to = self.pop_nested_folder(folder_name, folder_id)
        self.__class__ = go_to.__class__
        self.__dict__ = go_to.__dict__
        self.client_params = keep_client_params

    @ensure_token
    def step_out(self, steps=1):
        from ..storage.folders import folder_acquisition_by_name, folder_acquisition_by_id
        keep_client_params = self.client_params
        go_to = folder_acquisition_by_id(self.client_params['api_url'], self.ancestors[ self.level - steps ], self.client_params['api_key'])
        self.__class__ = go_to.__class__
        self.__dict__ = go_to.__dict__
        self.client_params = keep_client_params

    @ensure_token
    def rename(self, new_name):
        """
            Rename current folder
        """
        from ..storage.folders import update_folder
        self.meta.title = new_name
        return update_folder(self.client_params['api_url'], self, self.client_params['api_key'])

    @ensure_token
    def rename_folder(self, folder_name, new_name):
        """
            Rename nested folder
        """
        from ..storage.folders import update_folder

        folder = self.pop_nested_folder(folder_name=folder_name)
        folder.meta.title = new_name

        return update_folder(self.client_params['api_url'], folder, self.client_params['api_key'])

    @ensure_token
    def rename_file(self, file_name, new_name):
        """
            Rename nested file
        """
        from ..storage.files import update_file

        file = self.get_file(file_name = file_name)
        file.meta.title = new_name
        return update_file(self.client_params['api_url'], file, self.client_params['api_key'])


    @ensure_token
    def delete(self) -> bool:
        from ..storage.folders import delete_folder
        from .generic_models import ErrorReport

        try:
            resp = delete_folder(self.client_params['api_url'], self.id, self.client_params['api_key'])
            if isinstance(resp, ErrorReport):
                preety_print_error(resp)
                return False
            return True
        except Exception as e:
            print(f"Unexpected error while deleting folder: {e}")
            return False


class FolderList(BaseModel):
	files: List[File]
	folders: List[Folder]
