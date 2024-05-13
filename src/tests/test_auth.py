import unittest
from coreplatpy import *
from coreplatpy.models import *
from jwt import decode

class TestAuthentication(unittest.TestCase):

    def test_login(self):
        client = Client(api_url="http://localhost:30000/", account_url="http://localhost:5001/")
        client.login("isotiropoulos@singularlogic.eu", "new_pass")
        print(client.api_key)

    def test_decode_token(self):
        client = Client()
        client.login("isotiropoulos@singularlogic.eu", "1234")
        token_decoded = decode(client.api_key,  options={"verify_signature": False})

    def test_update_password(self):
        client = Client(api_url="http://localhost:30000/", account_url="http://localhost:5001/")
        client.login("isotiropoulos@singularlogic.eu", "1234")
        client.update_my_password('new_pass')

    def test_attributes(self):
        user_data = self.client.get_my_user()
        attrs = user_data.attributes
        old_country = attrs.country
        attrs.country = ['Greece']

        self.client.update_my_attributes(attrs)
        updated_user_data = self.client.get_my_user()
        self.assertEqual(updated_user_data.attributes.country, ['Greece'])
        self.client.update_my_attributes(attrs)

    def test_create_org(self):
        client = Client(api_url="http://localhost:30000/", account_url="http://localhost:5001/")
        client.login("jasonsoti1@gmail.com", "1234")

        org = client.create_organization('Another_ORG')
        print(org)

    def test_get_user_orgs(self):
        client = Client(api_url="http://localhost:30000/", account_url="http://localhost:5001/")
        client.login("isotiropoulos@singularlogic.eu", "new_pass")

        print(client.get_my_organization())

    def test_get_folder(self):
        client = Client(api_url="http://localhost:30000/", account_url="http://localhost:5001/")
        client.login("isotiropoulos@singularlogic.eu", "new_pass")

        folder = client.get_folder('27e3f766-6f1d-4b61-b99f-a0f3180a6251')

    def test_upload_file(self):
        # client = Client(api_url="http://localhost:30000/", account_url="http://localhost:5001/")
        client = Client()
        client.login("isotiropoulos@singularlogic.eu", "1234")

        folder = client.get_folder('6f340dad-76f9-43c9-8071-50e6cc7a9c4d')

        # resp = folder.upload_file('C:\\Users\\isotiropoulos\\centralenv\\Flights.ipynb', {'title':'Flights.ipynb'})
        resp = folder.upload_file('C:\\Users\\isotiropoulos\\Downloads\\Free_Test_Data_1MB_JPG.jpg', {'title':'Flights.ipynb'})
        print(resp)

    def test_list_folder(self):
        client = Client(api_url="http://localhost:30000/", account_url="http://localhost:5001/")
        client.login("isotiropoulos@singularlogic.eu", "new_pass")
        folder = client.get_folder('27e3f766-6f1d-4b61-b99f-a0f3180a6251')
        ls = folder.list_items()
        print(ls)

    def test_save_file(self):
        client = Client(api_url="http://localhost:30000/", account_url="http://localhost:5001/")
        client.login("isotiropoulos@singularlogic.eu", "new_pass")
        folder = client.get_folder('27e3f766-6f1d-4b61-b99f-a0f3180a6251')
        folder.save_file('e6c3b371-0793-4356-80ef-f925d38e5c07', 'C:\\Users\\isotiropoulos\\Desktop')

    def test_create_folder(self):
        client = Client(api_url="http://localhost:30000/", account_url="http://localhost:5001/")
        client.login("isotiropoulos@singularlogic.eu", "new_pass")
        folder = client.get_folder('0423242f-3c64-43fd-aa9f-847ebfb1d5b7')
        new = folder.create_folder(name="Level-2", description="Python Client Folder Level 1")
        print(new)

    def test_copy_folder(self):
        client = Client(api_url="http://localhost:30000/", account_url="http://localhost:5001/")
        client.login("isotiropoulos@singularlogic.eu", "new_pass")
        folder = client.get_folder('277d7f77-2e66-4ecf-af59-1354743a3e1d')
        new = folder.copy_to(destination="d57dd714-e287-4871-ab7c-a50c09e48f83", new_name="NEW!")
        print(new)

    def test_share_folder(self):
        client = Client(api_url="http://localhost:30000/", account_url="http://localhost:5001/")
        client.login("isotiropoulos@singularlogic.eu", "new_pass")
        folder = client.get_folder("a1a7e383-c15d-4f95-803a-693e8e86aa29")

        resp = folder.share_with_organizations(['Another_ORG'])
        print(resp)