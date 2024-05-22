from .models import (
    UpdateUser, LoginParams, BearerToken, ErrorReport, UserAttrs, UserData,
    Organization, Bucket, Folder, RoleUpdate, Role
)
from .account import (
    authenticate_sync, update_info, get_user_data,
    post_organization, get_user_organizations,
    post_new_group, delete_group,
    update_role, get_role
)

from .storage import (
    create_bucket, get_folder_by_id
)

import getpass
from jwt import decode
from .utils import preety_print_error
from typing import Union, List


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

    def __get_instance_variables__(self):
        return {k: v for k, v in self.__dict__.items() if not k.startswith('__') and not callable(v)}

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
        except Exception as e:
            print("Unexpected Error: " + str(e))
            raise

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

    def update_my_password(self, new_password: str):
        """
        Update the user's password
        :param new_password: str
        """
        try:
            update_user = UpdateUser(password=new_password)
        except Exception as e:
            print("Unexpected Error: ", str(e))
        else:
            resp = update_info(self.account_url, update_user, self.api_key)
            if isinstance(resp, ErrorReport):
                preety_print_error(resp)
        

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

        return resp

    def get_my_organizations(self) -> Union[List[Organization], None]:
        return (get_user_organizations(self.account_url, self.api_key))

    def update_user_groups(self, group_id: str, new_org_data: dict) -> Union[Organization, None]:
        """
        Join the user in a new group.

        Parameters
        ----------
        group_id : str
            ID of the referring group.
        new_org_data : dict
            New data for updating the organization.

        Returns
        -------
        Organization : The updated organization if successful.
        None : If an error occurs.
        """
        try:
            org = Organization.model_validate(new_org_data)
            resp = post_new_group(self.account_url, group_id, org, self.api_key)
            if isinstance(resp, ErrorReport):
                preety_print_error(resp)
                return None
            return resp
        except Exception as e:
            print("Unexpected Error: " + str(e))
            raise

    def groups_cleaning(self, group_id: str) -> bool:
        """
        Delete an organization by its group ID.

        Parameters
        ----------
        group_id : str
            ID of the organization to delete.

        Returns
        -------
        bool : True if successful, False if an error occurs.
        """
        try:
            resp = delete_group(self.account_url, group_id, self.api_key)
            if isinstance(resp, ErrorReport):
                preety_print_error(resp)
                return False
            return True
        except Exception as e:
            print("Unexpected Error: " + str(e))
            raise

    def update_group_role(self, group_id: str, new_role_data: dict) -> bool:
        """
        Update a role for a specific group by its ID.

        Parameters
        ----------
        group_id : str
            ID of the group to update the role for.
        new_role_data : dict
            Dictionary containing the updated role data.

        Returns
        -------
        bool : True if successful, False if an error occurs.
        """
        try:
            role_update = RoleUpdate.model_validate(new_role_data)
            resp = update_role(self.account_url, group_id, role_update, self.api_key)
            if isinstance(resp, ErrorReport):
                preety_print_error(resp)
                return False
            return True
        except Exception as e:
            print("Unexpected Error: " + str(e))
            raise

    def get_group_role(self, group_id: str) -> Union[Role, None]:
        """
        Retrieve a role for a specific group by its ID.

        Parameters
        ----------
        group_id : str
            ID of the group to retrieve the role for.

        Returns
        -------
        Role : The role information if successful.
        None : If an error occurs.
        """
        try:
            resp = get_role(self.account_url, group_id, self.api_key)
            if isinstance(resp, ErrorReport):
                preety_print_error(resp)
                return None
            return resp
        except Exception as e:
            print("Unexpected Error: " + str(e))
            raise


    def get_folder(self, folder_id:str) -> Union[Folder, None]:
        folder = get_folder_by_id(self.api_url, folder_id, self.api_key)
        if isinstance(folder, ErrorReport):
            preety_print_error(folder)
            return None

        folder.client_params = self.__get_instance_variables__()
        print(folder)
        return folder

    def download_copernicus_dataset(self):
        return

    def get_download_status(self):
        return

    def list_copernicus_resources(self):
        return