from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any


class LoginParams(BaseModel):
    username: str
    password: str

class AccessGranted(BaseModel):
    access_token: str
    expires_in: int
    refresh_expires_in: int
    refresh_token: str
    token_type: str
    not_before_policy: int = Field(alias='not-before-policy')
    session_state: str
    scope: str

class UserAttrs(BaseModel):
    occupation: Optional[List[str]] = ['Not defined']
    affiliation: Optional[List[str]] = ['Not defined']
    country: Optional[List[str]]= ['Not defined']
    city: Optional[List[str]]= ['Not defined']

class UpdateUser(BaseModel):
    attributes: Optional[UserAttrs] = None
    password: Optional[str] = None

class RealmAccess(BaseModel):
    roles: List[str]

class Account(BaseModel):
    roles: List[str]

class ResourceAccess(BaseModel):
    account: Account

class BearerToken(BaseModel):
    exp: int
    iat: int
    jti: str
    iss: str
    aud: str
    sub: str
    typ: str
    azp: str
    session_state: str
    acr: str
    realm_access: RealmAccess
    resource_access: ResourceAccess
    scope: str
    sid: str
    email_verified: bool
    group_names: List[str]
    name: str
    preferred_username: str
    given_name: str
    family_name: str
    email: str

class Access(BaseModel):
    manageGroupMembership: bool
    view: bool
    mapRoles: bool
    impersonate: bool
    manage: bool

class UserData(BaseModel):
    id: str
    createdTimestamp: int
    username: str
    enabled: bool
    totp: bool
    emailVerified: bool
    firstName: str
    lastName: str
    email: str
    disableableCredentialTypes: List
    requiredActions: List
    notBefore: int
    access: Access
    attributes: UserAttrs = UserAttrs()

class Organization(BaseModel):
    id: Optional[str] = None
    name: str
    path: str
    subGroups: Optional[List[str]] = []
    attributes: Optional[Dict[str, List]] = {}

class Role(BaseModel):
    attributes: Dict[str, Any] = Field(default_factory=dict)

class RoleUpdate(BaseModel):
    attributes: Dict[str, Any] = Field(default_factory=dict)

class Administrator(BaseModel):
    admin: bool
class JoinGroupBody(BaseModel):
    users: List[Dict[str, Administrator]]

class UserRegistration(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str
    # picture: str

