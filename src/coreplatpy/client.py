from .models import (
    UpdateUser, LoginParams, BearerToken, ErrorReport, UserAttrs, UserData,
    Organization
)
from .account import (
    authenticate_sync, update_info, get_user_data,
    post_organization, get_user_organizations
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

    def __init__(self, api_url=None, account_url=None, create_logs=False) -> None:
        if api_url:
            self.api_url = api_url
        else:
            self.api_url = 'https://api-buildspace.euinno.eu/'

        if account_url:
            self.account_url = account_url
        else:
            self.account_url = 'https://account-buildspace.euinno.eu/'

        self.api_key = None
        self.user_id = None

    def authenticate(self):
        """
        Secure authentication for Core Platform.
        """
        try:
            username = input("Username: ")
            password = getpass.getpass("Password: ")
            params = LoginParams.model_validate({
                'username': username,
                'password': password
            })

            access = authenticate_sync(self.account_url, params)
            if access.__repr_name__() == 'ErrorReport':
                preety_print_error(access)
            else:
                self.api_key = access.access_token
            # print("API key is set")
            # self.user_id = jwtok.decode_jwt(self.api_key).get('sub')
        except Exception as e:
            print("Error: " + str(e))



    def login(self, username: str, password: str) -> None:
        """
        Login to Core Platform.

        Parameters
        ----------
        username : username
        password : password
        """
        try:
            params = LoginParams.model_validate({
                'username': username,
                'password': password
            })

            access = authenticate_sync(self.account_url, params)
            if isinstance(access, ErrorReport):
                preety_print_error(access)
            else:
                self.api_key = access.access_token
            # self.user_id = jwtok.decode_jwt(self.api_key).get('sub')
        except Exception as e:
            print("Unexpected Error: " + str(e))

    def get_my_user(self) -> Union[UserData, None]:
        """
        Get the user data, once logged in

        :return: UserData
        """
        token_data = BearerToken.model_validate(decode(self.api_key, options={"verify_signature": False}))
        resp = get_user_data(self.account_url, token_data.sub, self.api_key)
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
            token_data = BearerToken.model_validate(decode(self.api_key, options={"verify_signature": False}))
            resp = update_info(self.account_url, token_data.sub, update_user, self.api_key)
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
            token_data = BearerToken.model_validate(decode(self.api_key, options={"verify_signature": False}))
            resp = update_info(self.account_url, token_data.sub, update_user, self.api_key)
            if isinstance(resp, ErrorReport):
                preety_print_error(resp)

    def create_organization(self, organization: str, path: str = '/',
                            sub_orgs: List[str] = [], attributes: dict = {},
                            org_id: str = None) -> Union[Organization, None]:
        """
        Create Organization

        :param organization: Name of the new organization
        :param path: Optional (specify path when creating a sub organization)
        :param sub_orgs: Optional list of sub groups in organization
        :param attributes: Optional dictionary of attributes
        :param org_id: Optional group id (only in case that ID of organization should be defined)
        :return: Organization object
        """
        new_org = Organization(name=organization, id=org_id, sub_orgs=sub_orgs,
                                    attributes=attributes, path=path)

        resp = post_organization(self.account_url, new_org, self.api_key)
        if isinstance(resp, ErrorReport):
            preety_print_error(resp)
            return None
        return resp

    def get_my_organization(self) -> Union[List[Organization], None]:
        return (get_user_organizations(self.account_url, self.api_key))