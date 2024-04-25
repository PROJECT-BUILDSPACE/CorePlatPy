import unittest
from ..coreplatpy import *
from ..coreplatpy.models import *
from jwt import decode

class TestAuthentication(unittest.TestCase):

    # def test_authenticate(self):
    #     client = Client(api_url="http://localhost:30000/", account_url="http://localhost:5001/")
    #     client.authenticate()

    def test_login(self):
        client = Client(api_url="http://localhost:30000/", account_url="http://localhost:5001/")
        client.login("isotiropoulos@singularlogic.eu", "1234")

    def test_decode_token(self):
        client = Client(api_url="http://localhost:30000/", account_url="http://localhost:5001/")
        client.login("isotiropoulos@singularlogic.eu", "1234")
        token_decoded = decode(client.api_key,  options={"verify_signature": False})

    def test_update_password(self):
        client = Client(api_url="http://localhost:30000/", account_url="http://localhost:5001/")
        client.login("isotiropoulos@singularlogic.eu", "1234")
        client.update_password('new_pass')

    def test_attributes(self):
        client = Client(api_url="http://localhost:30000/", account_url="http://localhost:5001/")
        client.login("isotiropoulos@singularlogic.eu", "new_pass")
        user_data = client.get_my_user()

        attrs = user_data.attributes

        old_country = attrs.country
        attrs.country = ['Greece']

        client.update_my_attributes(attrs)
        new_attrs = client.get_my_user()

    def test_create_org(self):
        client = Client(api_url="http://localhost:30000/", account_url="http://localhost:5001/")
        client.login("isotiropoulos@singularlogic.eu", "new_pass")

        org = client.create_organization('python_organization')
        print(org)

    def test_get_user_orgs(self):
        client = Client(api_url="http://localhost:30000/", account_url="http://localhost:5001/")
        client.login("isotiropoulos@singularlogic.eu", "new_pass")

        print(client.get_my_organization())
