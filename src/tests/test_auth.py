import unittest
from src.coreplatpy import *
from src.coreplatpy.models import *
from jwt import decode

class TestAuthentication(unittest.TestCase):

    def test_login(self):
        client = Client(api_url="http://localhost:30000/", account_url="http://localhost:5001/")
        client.login("s.aspragkathos@gmail.com", "1234")
        # client.login("saspragkathos@singularlogic.eu", "1234567890")
        print(client.api_key)

    def test_decode_token(self):
        # client = Client()
        client = Client(api_url="http://localhost:30000/", account_url="http://localhost:5001/")
        client.login("s.aspragkathos@gmail.com", "123456789")
        token_decoded = decode(client.api_key,  options={"verify_signature": False})

    def test_update_password(self):
        client = Client(api_url="http://localhost:30000/", account_url="http://localhost:5001/")
        client.login("s.aspragkathos@gmail.com", "123456789")
        client.update_my_password('1234')

    def test_attributes(self):
        client = Client(api_url="http://localhost:30000/", account_url="http://localhost:5001/")
        client.login("s.aspragkathos@gmail.com", "1234")

        user_data = client.get_my_user()
        attrs = user_data.attributes
        print("attrs: ", attrs)
        old_country = attrs.country
        attrs.country = ["Cuba"]

        client.update_my_attributes(attrs)

        # Fetch the user data again to verify the update
        updated_user_data = client.get_my_user()

        # Assert that the country attribute is updated
        # print("Updated user attributes:", updated_user_data.attributes)
        self.assertEqual(updated_user_data.attributes.country, ['Cuba'])


    def test_create_org(self):
        client = Client(api_url="http://localhost:30000/", account_url="http://localhost:5001/")
        client.login("s.aspragkathos@gmail.com", "1234")

        org = client.create_organization('New_fold_to_test_2')
        print(org)

    def test_get_user_orgs(self):
        client = Client(api_url="http://localhost:30000/", account_url="http://localhost:5001/")
        client.login("s.aspragkathos@gmail.com", "123456789")

        print(client.get_my_organizations())

    def test_create_folder(self):
        client = Client(api_url="http://localhost:30000/", account_url="http://localhost:5001/")
        client.login("s.aspragkathos@gmail.com", "1234")
        folder = client.folder_acquisition('25ccd072-fef8-4341-a5d7-c993366e56a3')
        new = folder.create_folder(name="To_SEND_1", description="Python Client Folder Level 1")
        print(new)

    def test_get_folder_by_id(self):
        client = Client(api_url="http://localhost:30000/", account_url="http://localhost:5001/")
        client.login("s.aspragkathos@gmail.com", "1234")

        folder = client.folder_acquisition('91f44778-04fe-49ab-ba59-994d274ccb2d')

    def test_get_folder_by_name(self):
        client = Client(api_url="http://localhost:30000/", account_url="http://localhost:5001/")
        client.login("s.aspragkathos@gmail.com", "1234")

        folder = client.folder_acquisition_by_name("/ORG_FROM/To_SEND")

    def test_upload_file(self):
        client = Client(api_url="http://localhost:30000/", account_url="http://localhost:5001/")
        client.login("s.aspragkathos@gmail.com", "123456789")

        folder = client.folder_acquisition('73e9532d-f1d7-45e8-b2ad-09469552be39')

        resp = folder.upload_file('C:\\Users\\saspragkathos\\Documents\GitHub\\CorePlatPy\\src\\tests\\test_file.jpg',
                                  {'title': 'test_file.ipynb'})
        print(resp)

    def test_list_folder(self):
        client = Client(api_url="http://localhost:30000/", account_url="http://localhost:5001/")
        client.login("s.aspragkathos@gmail.com", "123456789")
        folder = client.folder_acquisition('73e9532d-f1d7-45e8-b2ad-09469552be39')
        ls = folder.list_items()
        print(ls)

    def test_save_file(self):
        client = Client(api_url="http://localhost:30000/", account_url="http://localhost:5001/")
        client.login("s.aspragkathos@gmail.com", "123456789")
        folder = client.folder_acquisition('73e9532d-f1d7-45e8-b2ad-09469552be39')
        folder.save_file('ff4208f5-8d9a-42b4-89cb-210a1f7c07eb', 'C:\\Users\\saspragkathos\\Downloads')

    def test_copy_folder(self):
        client = Client(api_url="http://localhost:30000/", account_url="http://localhost:5001/")
        client.login("s.aspragkathos@gmail.com", "123456789")
        folder = client.folder_acquisition('aac35eda-a1ca-4a0d-8ad9-f2a83ec1a737')
        new = folder.copy_to(destination='73e9532d-f1d7-45e8-b2ad-09469552be39', new_name="NEW!")
        print(new)

    def test_share_folder(self):
        client = Client(api_url="http://localhost:30000/", account_url="http://localhost:5001/")
        client.login("s.aspragkathos@gmail.com", "1234")
        folder = client.folder_acquisition("2ac38c18-1c6b-42bc-8add-484e50a054c7")

        resp = folder.share_with_organizations(['New_fold_to_test_2'])
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

    def test_update_user_groups(self):
        client = Client(api_url="http://localhost:30000/", account_url="http://localhost:5001/")
        # client.login("s.aspragkathos@gmail.com", "1234")
        client.login("saspragkathos@singularlogic.eu", "1234567890")

        users = {
            "s.aspragkathos@gmail.com": "admin"
        }

        success = client.add_user_to_group("New_ORG_other_USER", users)
        print(success)

    def test_get_group_role(self):
        client = Client(api_url="http://localhost:30000/", account_url="http://localhost:5001/")
        client.login("s.aspragkathos@gmail.com", "1234")

        role = client.get_group_role("ORG_TO_ver_1")
        # role = client.get_group_role("6d80c384-f2c1-49dd-bf10-8a1f98fb4430")
        print(role)

    # def test_update_group_role(self):
    #     client = Client(api_url="http://localhost:30000/", account_url="http://localhost:5001/")
    #     client.login("s.aspragkathos@gmail.com", "1234")
    #
    #     new_role_data = {
    #         "role_name": "admin",
    #         "permissions": ["read", "write"]
    #     }
    #
    #     "attributes": {
    #         "{{KC_UGID_1}}": ["{{KC_UID}},NEW_DUMMY_ID"]
    #     }
    #     attributes: Dict[str, Any] = Field(default_factory=dict)
    #
    #     try:
    #         result = client.update_group_role("ORG_TO", new_role_data)
    #         print("Result of update_group_role:", result)
    #         self.assertTrue(result)
    #     except Exception as e:
    #         print("Test update_group_role failed with error:", str(e))
    #         self.fail("Exception raised in test_update_group_role")

    def test_groups_cleaning(self):
        client = Client(api_url="http://localhost:30000/", account_url="http://localhost:5001/")
        client.login("s.aspragkathos@gmail.com", "1234")

        group_name = "ORG_TO_ver_2"
        # Assuming that group creation is already tested and works
        # client.create_organization(group_name)

        success = client.groups_cleaning(group_name)

        self.assertTrue(success)
