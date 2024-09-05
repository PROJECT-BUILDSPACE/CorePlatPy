from .models import (
    UpdateUser, LoginParams, BearerToken, ErrorReport, UserAttrs, UserData,
    Organization, Bucket, Folder, RoleUpdate, Role, File, JoinGroupBody, UserRegistration,
    PostFolder, Updated
)
from .account import (
    authenticate_sync, update_info, get_user_data,
    post_organization, get_user_organizations,
    post_new_group, delete_group,
    update_role, get_role, get_organization_by_id, get_organization_by_name, post_picture, register
)

from .storage import (
    create_bucket, folder_acquisition_by_id, folder_acquisition_by_name, delete_bucket,
    update_folder, delete_folder, get_info, delete_file, update_file
)

from .copernicus import(
    get_list, get_form, get_status, post_dataset, CopernicusDetails, CopernicusTask
)

from .utils import ensure_token

import getpass
from jwt import decode
from .utils import preety_print_error
from typing import Union, List
import uuid
from datetime import datetime


class Client:
    """
    A Client for the Core Platform.

    Parameters
    ----------
    api_url : The url of Core Platform API
    account_url: The url of Account API
    """

    def __init__(self, api_url=None, account_url=None) -> None:
        self.api_url = api_url or 'https://api-buildspace.euinno.eu/'
        self.account_url = account_url or 'https://account-buildspace.euinno.eu/'
        self.api_key = None
        self.user_id = None
        self.refresh_token = None
        self.expires_at = None
        self.pictures = "pictures"

    def __get_instance_variables__(self):
        return {k: v for k, v in self.__dict__.items() if not k.startswith('__') and not callable(v)}

    def register(self):
        """
         Register new User to Core Platform.
         """
        try:
            email = input("Email: ")
            firstName = input("First Name: ")
            lastName = input("Last Name: ")
            # password = input("Last Name: ")
            # password_confirm = input("Last Name: ")
            password = getpass.getpass("Password: ")
            password_confirm = getpass.getpass("Confirm Password: ")

            if password_confirm!=password:
                raise ValueError("Passwords do not match!")

            params = UserRegistration(email=email,
                                      first_name=firstName,
                                      last_name=lastName,
                                      password=password,
                                      picture=None
                                      )

            registration = register(self.account_url, params)
            if isinstance(registration, ErrorReport):
                preety_print_error(registration)
                raise
            else:
                self.login(email, password)
            picture_path = input("Profile picture path (can be omitted): ")
            picture = None
            if picture_path != "":
                with open(picture_path, 'rb') as f:
                    picture = f.read()
                    if len(picture) >  5 * 1024 * 1024:  # 5MB in bytes
                        raise Warning('Picture is larger than 5MB. Using default.')
                    unique_id = str(uuid.uuid4())
                    resp = post_picture(self.account_url, picture, unique_id, self.api_key)
                    if isinstance(resp, ErrorReport):
                        preety_print_error(resp)
                        raise
        except Exception as e:
            print("Error: " + str(e))
            raise

    def authenticate(self):
        """
        Secure authentication for Core Platform.
        """
        try:
            username = input("Username: ")
            password = getpass.getpass("Password: ")
            params = LoginParams.model_validate({'username': username, 'password': password})
            access = authenticate_sync(self.account_url, params)
            if isinstance(access, ErrorReport):
                preety_print_error(access)
            else:
                self.api_key = access.access_token
                self.refresh_token = access.refresh_token
                self.expires_at =  datetime.utcfromtimestamp(decode(access.access_token, options={"verify_signature": False,"verify_aud": False})['exp'])
        except Exception as e:
            print("Error: " + str(e))
            raise

    def login(self, username: str, password: str) -> None:
        """
        Login to Core Platform.

        Parameters
        ----------
        username : username
        password : password
        """
        try:
            params = LoginParams.model_validate({'username': username, 'password': password})
            access = authenticate_sync(self.account_url, params)
            if isinstance(access, ErrorReport):
                preety_print_error(access)
            else:
                self.api_key = access.access_token
                print(access.access_token)
                self.refresh_token = access.refresh_token
                self.expires_at =  datetime.utcfromtimestamp(decode(access.access_token, options={"verify_signature": False, "verify_aud": False})['exp'])
        except Exception as e:
            print("Unexpected Error: " + str(e))
            raise

    @ensure_token
    def get_my_user(self) -> Union[UserData, None]:
        """
        Get the user data, once logged in.

        Returns
        -------
        UserData : The user's data if successful.
        None : If an error occurs.
        """
        resp = get_user_data(self.account_url, self.api_key)
        if isinstance(resp, ErrorReport):
            preety_print_error(resp)
            return None
        return resp

    @ensure_token
    def update_my_attributes(self, new_attributes: dict):
        """
        Update your user's attributes
        :param new_attributes: dict (should follow the UserAttrs model)
        """
        try:

            attributes = UserAttrs.model_validate(new_attributes)
            update_user = UpdateUser(attributes=attributes)
        except Exception as e:
            print("Unexpected Error: ", str(e))
        else:
            resp = update_info(self.account_url, update_user, self.api_key)
            if isinstance(resp, ErrorReport):
                preety_print_error(resp)

    @ensure_token
    def update_my_password(self):
        """
        Update the user's password
        """
        password = getpass.getpass("Password: ")
        password_confirm = getpass.getpass("Confirm Password: ")

        if password_confirm != password:
            raise ValueError("Passwords do not match!")

        try:
            update_user = UpdateUser(password=password)
        except Exception as e:
            print("Unexpected Error: ", str(e))
        else:
            resp = update_info(self.account_url, update_user, self.api_key)
            if isinstance(resp, ErrorReport):
                preety_print_error(resp)
        

    @ensure_token
    def create_organization(self, organization: str, path: str = '/', sub_orgs: List[str] = [], attributes: dict = {}, org_id: str = None) -> Union[Organization, None]:
        """
        Create Organization.

        :param organization: Name of the new organization.
        :param path: Optional path for sub-organization creation.
        :param sub_orgs: Optional list of sub-groups in the organization.
        :param attributes: Optional dictionary of attributes.
        :param org_id: Optional group ID if predefined.
        :return: Organization object.
        """
        new_org = Organization(name=organization, id=org_id, sub_orgs=sub_orgs,
                                    attributes=attributes, path=path)

        resp = post_organization(self.account_url, new_org, self.api_key)
        if isinstance(resp, ErrorReport):
            preety_print_error(resp)
            return None

        bucket = Bucket(_id=resp.id, name=organization)
        resp = create_bucket(self.api_url, bucket, self.api_key)
        if isinstance(resp, ErrorReport):
            preety_print_error(resp)
            return None

        # Refresh token to have the organization ID in attributes
        try:
            response = requests.post(self.account_url + 'user/refresh',
                                     data={'refresh_token': self.refresh_token})
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Failed to refresh access token: {e}")
        else:
            self.api_key = response.json()['access_token']
            self.refresh_token = response.json()['refresh_token']
            self.expires_at = datetime.utcfromtimestamp(
                decode(self.api_key, options={"verify_signature": False})['exp'])
        return resp

    @ensure_token
    def get_my_organizations(self) -> Union[List[Organization], None]:
        return (get_user_organizations(self.account_url, self.api_key))

    @ensure_token
    def add_user_to_group(self, group_name: str, user_data: dict) -> bool:
        try:
            body = {
                "users": [{email: {"admin": True}} if role == 'admin' else {email: {"admin": False}} for email, role in
                          user_data.items()]}

            data = JoinGroupBody.model_validate(body)
            resp = post_new_group(self.account_url, group_name, data, self.api_key)
            if isinstance(resp, ErrorReport):
                preety_print_error(resp)
                return False
            return True
        except Exception as e:
            print("Unexpected Error: " + str(e))
            raise

    @ensure_token
    def remove_organization(self, organization_name: str) -> bool:
        try:
            organization = get_organization_by_name(self.account_url, organization_name, self.api_key)
            if isinstance(organization, ErrorReport):
                preety_print_error(organization)
                return False

            resp = delete_bucket(self.api_url, organization.id, self.api_key)
            if isinstance(resp, ErrorReport):
                preety_print_error(resp)
                return False

            resp = delete_group(self.account_url, organization.id, self.api_key)
            if isinstance(resp, ErrorReport):
                preety_print_error(resp)
                return False

        except Exception as e:
            print("Unexpected Error: " + str(e))
            raise
        else:
            return True

    # def update_group_role(self, group_name: str, new_role_data: dict) -> bool:
    #     try:
    #         group = get_organization_by_name(self.account_url, group_name, self.api_key)
    #         if isinstance(group, ErrorReport):
    #             preety_print_error(group)
    #             return False
    #         print("Group:", group)
    #     except Exception as e:
    #         print("Unexpected Error while getting group:", str(e))
    #         raise
    #
    #     try:
    #         role_update = RoleUpdate.model_validate(new_role_data)
    #         print("Role Update Data:", role_update)
    #
    #         resp = update_role(self.account_url, group.id, role_update, self.api_key)
    #         print("Update Role Response:", resp)
    #
    #         if isinstance(resp, ErrorReport):
    #             preety_print_error(resp)
    #             return False
    #         return True
    #     except Exception as e:
    #         print("Unexpected Error while updating role:", str(e))
    #         raise

    @ensure_token
    def get_group_role(self, group_name: str):
        """Get the role of a group."""
        try:
            group = get_organization_by_name(self.account_url, group_name, self.api_key)
            if isinstance(group, ErrorReport):
                preety_print_error(group)
                return group

            resp = get_role(self.account_url, group.id, self.api_key)
            if isinstance(resp, ErrorReport):
                preety_print_error(resp)
                return resp

            return resp

        except AttributeError as e:
            print(f"AttributeError: {e}")
            raise

        except Exception as e:
            print(f"Unexpected error: {e}")
            raise

    @ensure_token
    def get_folder(self, folder_name: str = None, folder_id: str = None) -> Union[Folder, None]:
        if (folder_id is None and folder_name is None) or (folder_id is not None and folder_name is not None):
            error = ErrorReport(reason="Parameters folder_id and folder_name are mutually exclusive, meaning you can (and must) pass value only to one of them")
            preety_print_error(error)
            return None
        elif folder_id:
            folder = folder_acquisition_by_id(self.api_url, folder_id, self.api_key)
            if isinstance(folder, ErrorReport):
                preety_print_error(folder)
                return None
            folder.client_params = self.__get_instance_variables__()
            return folder
        else:
            folder = folder_acquisition_by_name(self.api_url, folder_name, self.api_key)
            if isinstance(folder, ErrorReport):
                preety_print_error(folder)
                return None

            folder.client_params = self.__get_instance_variables__()
            return folder

    @ensure_token
    def list_copernicus_resources_per_service(self, service:str):
        resource_list = get_list(self.api_url, service, self.api_key)
        return

    @ensure_token
    def get_copernicus_form_for_resource(self,  service:str, dataset:str):
        dataset_form = get_form(self.api_url, service, dataset, self.api_key)
        return

    @ensure_token
    def copernicus_dataset_request(self, service:str, body:any) -> Union[CopernicusDetails, None]:
        new_task = post_dataset(self.api_url, body, service, self.api_key)
        return new_task

    @ensure_token
    def check_download_status(self, task_id:str) -> Union[CopernicusTask, None]:
        complete_task = get_status(self.api_url, task_id, self.api_key)
        #if returns complete then proceeds to download dataset to cop bucket
        return complete_task

    @ensure_token
    def download_copernicus_dataset(self, task_id:str) -> Union[File, None]:
        #copy download file from above xd
        #is download file not implemented?
        #GET COPERNICUS BUCKET...

        return

    @ensure_token
    def upload_picture(self, picture_path):
        with open(picture_path, 'rb') as f:
            picture = f.read()
            if len(picture) > 5 * 1024 * 1024:  # 5MB in bytes
                raise Warning('Picture is larger than 5MB. Using default.')
            else:
                user_data = decode(self.api_key, options={"verify_signature": False,"verify_aud": False})
                return post_picture(self.account_url, picture, user_data['sub'], self.api_key)
        return False


    @ensure_token
    def del_file(self, file_id: str) -> bool:

        try:
            resp = delete_file(self.api_url, file_id, self.api_key)
            if isinstance(resp, ErrorReport):
                preety_print_error(resp)
                return False
            return True
        except Exception as e:
            print(f"Unexpected error while deleting folder: {e}")
            return False