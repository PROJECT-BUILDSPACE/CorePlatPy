import unittest
from src.coreplatpy import *
from src.coreplatpy.models import *
from jwt import decode

class TestAuthentication(unittest.TestCase):

    def test_login(self):
        client = Client(api_url="http://localhost:30000/", account_url="http://localhost:5001/")
        client.login("s.aspragkathos@gmail.com", "new_pass")
        print(client.api_key)

    def test_decode_token(self):
        # client = Client()
        client = Client(api_url="http://localhost:30000/", account_url="http://localhost:5001/")
        client.login("s.aspragkathos@gmail.com", "new_pass")
        token_decoded = decode(client.api_key,  options={"verify_signature": False})

    def test_update_password(self):
        client = Client(api_url="http://localhost:30000/", account_url="http://localhost:5001/")
        client.login("s.aspragkathos@gmail.com", "new_pass")
        client.update_my_password('123456789')

    def test_attributes(self):
        client = Client(api_url="http://localhost:30000/", account_url="http://localhost:5001/")
        client.login("s.aspragkathos@gmail.com", "123456789")

        user_data = client.get_my_user()
        attrs = user_data.attributes
        old_country = attrs.country
        attrs.country = ["Cuba"]

        client.update_my_attributes(attrs)

        # Fetch the user data again to verify the update
        updated_user_data = client.get_my_user()
        #
        # Assert that the country attribute is updated
        self.assertEqual(updated_user_data.attributes.country, ['Greece'])
        #
        # # Clean up: revert the changes
        # revert_attributes = UpdateUser(attributes=old_attributes)
        # client.update_my_attributes(revert_attributes)

    def test_create_org(self):
        client = Client(api_url="http://localhost:30000/", account_url="http://localhost:5001/")
        client.login("s.aspragkathos@gmail.com", "123456789")

        org = client.create_organization('Another_ORG')
        print(org)

    def test_get_user_orgs(self):
        client = Client(api_url="http://localhost:30000/", account_url="http://localhost:5001/")
        client.login("s.aspragkathos@gmail.com", "123456789")

        print(client.get_my_organizations())

    def test_get_folder(self):
        client = Client(api_url="http://localhost:30000/", account_url="http://localhost:5001/")
        client.login("s.aspragkathos@gmail.com", "123456789")

        folder = client.get_folder('73e9532d-f1d7-45e8-b2ad-09469552be39')

    def test_upload_file(self):
        client = Client(api_url="http://localhost:30000/", account_url="http://localhost:5001/")
        client.login("s.aspragkathos@gmail.com", "123456789")

        folder = client.get_folder('73e9532d-f1d7-45e8-b2ad-09469552be39')

        resp = folder.upload_file('C:\\Users\\saspragkathos\\Documents\GitHub\\CorePlatPy\\src\\tests\\test_file.jpg',
                                  {'title': 'test_file.ipynb'})
        print(resp)

    def test_list_folder(self):
        client = Client(api_url="http://localhost:30000/", account_url="http://localhost:5001/")
        client.login("s.aspragkathos@gmail.com", "123456789")
        folder = client.get_folder('73e9532d-f1d7-45e8-b2ad-09469552be39')
        ls = folder.list_items()
        print(ls)

    def test_save_file(self):
        client = Client(api_url="http://localhost:30000/", account_url="http://localhost:5001/")
        client.login("s.aspragkathos@gmail.com", "123456789")
        folder = client.get_folder('73e9532d-f1d7-45e8-b2ad-09469552be39')
        folder.save_file('ff4208f5-8d9a-42b4-89cb-210a1f7c07eb', 'C:\\Users\\saspragkathos\\Downloads')

    def test_create_folder(self):
        client = Client(api_url="http://localhost:30000/", account_url="http://localhost:5001/")
        client.login("s.aspragkathos@gmail.com", "123456789")
        folder = client.get_folder('0b965b4e-3b83-4b03-9c7e-3ee03a483cd5')
        new = folder.create_folder(name="Level-2", description="Python Client Folder Level 1")
        print(new)

    def test_copy_folder(self):
        client = Client(api_url="http://localhost:30000/", account_url="http://localhost:5001/")
        client.login("s.aspragkathos@gmail.com", "123456789")
        folder = client.get_folder('aac35eda-a1ca-4a0d-8ad9-f2a83ec1a737')
        new = folder.copy_to(destination='73e9532d-f1d7-45e8-b2ad-09469552be39', new_name="NEW!")
        print(new)

    def test_share_folder(self):
        client = Client(api_url="http://localhost:30000/", account_url="http://localhost:5001/")
        client.login("s.aspragkathos@gmail.com", "123456789")
        folder = client.get_folder('ed90b4ee-9362-4dfa-81c3-61b47c9a2fed')

        resp = folder.share_with_organizations(['Another_ORG'])
        print(resp)


    def test_copernicus_list(self):
        client = Client(api_url="http://localhost:30000/", account_url="http://localhost:5001/")
        client.login("isotiropoulos@singularlogic.eu", "new_pass")
        client.list_copernicus_resources_per_service("cds")
        client.list_copernicus_resources_per_service("ads")
        return

    def test_copernicus_form(self):
        client = Client(api_url="http://localhost:30000/", account_url="http://localhost:5001/")
        client.login("isotiropoulos@singularlogic.eu", "new_pass")
        client.get_copernicus_form_for_resource("cds", "reanalysis-era5-pressure-levels")
        return

    def copernicus_dataset_request(self):
        client = Client(api_url="http://localhost:30000/", account_url="http://localhost:5001/")
        client.login("isotiropoulos@singularlogic.eu", "new_pass")
        my_task = client.copernicus_dataset_request("cds",{
                    "datasetname" : "reanalysis-era5-pressure-levels",
                    "body" :{
                              "date": "2017-12-01/2017-12-31",
                              "format": "grib",
                              "pressure_level": "1000",
                              "product_type": "reanalysis",
                              "time": "12:00",
                              "variable": "temperature"
                            }
                } )
        print(my_task.status)