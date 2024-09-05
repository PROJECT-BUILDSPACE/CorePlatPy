import unittest
from src.coreplatpy import *
from src.coreplatpy.models import *
from jwt import decode
# import pytest
from unittest.mock import patch, mock_open

EMAIL1 = 'test@python.eu'
EMAIL2 = 'test-2@python.eu'
FIRST_NAME = 'John'
LAST_NAME = 'Doe'
PWD = '132456789'
PWD2 = 'password'

ORG = 'Organization_'
FOL = "Folder_"

class TestAuthentication(unittest.TestCase):

    @patch('builtins.input')
    @patch('getpass.getpass')
    @patch('builtins.open', new_callable=mock_open)
    def test_register(self, mock_open, mock_getpass, mock_input):
        # Arrange
        mock_input.side_effect = [EMAIL1, FIRST_NAME, LAST_NAME, '']  # Mock input for email1, firstName, lastName, and picture path
        mock_getpass.side_effect = [PWD, PWD]  # Mock getpass for password and password_confirm

        # Initialize the Client instance
        client = Client()

        # Act
        client.register()

    @patch('builtins.input')
    @patch('getpass.getpass')
    @patch('builtins.open', new_callable=mock_open)
    def test_authenticate(self, mock_open, mock_getpass, mock_input):
        # Arrange
        mock_input.side_effect = [EMAIL1]  # Mock input for email1, firstName, lastName, and picture path
        mock_getpass.side_effect = [PWD]  # Mock getpass for password and password_confirm

        # Initialize the Client instance
        client = Client()

        # Act
        client.authenticate()
        user_data = decode(client.api_key, options={"verify_signature": False})
        self.assertEqual(user_data['name'], f'{FIRST_NAME} {LAST_NAME}')
        self.assertEqual(user_data['preferred_username'], EMAIL1)
        self.assertIn('groupIDs', user_data.keys())


    def test_login(self):
        # client = Client(account_url='http://localhost:5001/')
        client = Client(account_url='https://account-buildspace.euinno.eu/')

        client.login(EMAIL1, PWD2)
        user_data = decode(client.api_key,  options={"verify_signature": False})

        self.assertEqual(user_data['name'], f'{FIRST_NAME} {LAST_NAME}')
        self.assertEqual(user_data['preferred_username'], EMAIL1)
        self.assertIn('groupIDs', user_data.keys())
        self.assertIn('groupIDs', user_data.keys())

    def test_update_password(self):
        client = Client()
        client.login(EMAIL1, PWD)
        client.update_my_password(PWD2)
        client.login(EMAIL1, PWD2)


    def test_attributes(self):
        import random
        import string

        client = Client()
        client.login(EMAIL1, PWD2)

        user_data = client.get_my_user()
        attrs = user_data.attributes

        new_country = [''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))]
        old_country = attrs.country

        attrs.country = new_country
        client.update_my_attributes(attrs)

        # Fetch the user data again to verify the update
        updated_user_data = client.get_my_user()

        # Assert that the country attribute is updated
        self.assertEqual(updated_user_data.attributes.country, new_country)


    def test_create_org(self):
        client = Client()
        client.login(EMAIL1, PWD2)

        org = client.create_organization(ORG + '4')
        self.assertEqual(org.name, ORG + '4')

    def test_get_user_orgs(self):
        client = Client()
        client.login(EMAIL1, PWD2)
        organizations = client.get_my_organizations()
        user_data = decode(client.api_key,  options={"verify_signature": False})

        self.assertEqual(len(organizations), len(user_data['groupIDs']))
        for org in organizations:
            self.assertIn(org.id, user_data['groupIDs'])

    def test_create_folder(self):
        client = Client()
        client.login(EMAIL1, PWD2)
        folder = client.get_folder(folder_name =  "Organization_1")
        new = folder.create_folder(name=FOL + '1', description="Python Client Folder Level 1")
        self.assertEqual(len(new.ancestors), len(folder.ancestors) + 1)
        self.assertEqual(new.ancestors[-1], folder.id)
        self.assertEqual(new.parent, folder.id)
        self.assertEqual(len(new.ancestors), new.level)

    def test_get_folder_by_id_and_name(self):
        client = Client()
        client.login(EMAIL1, PWD2)

        selection = client.get_folder(folder_name=f"{ORG + '1'}/{FOL + '1'}")
        folder = client.get_folder(folder_id=selection.parent)

        self.assertEqual(selection.parent, folder.id)

    def test_upload_file(self):
        client = Client()
        client.login(EMAIL1, PWD2)

        folder = client.get_folder(folder_name=f"{ORG + '1'}/{FOL + '1'}")

        resp = folder.upload_file('test_file.jpg',
                                  {'title': 'test-name'})

    def test_list_folder(self):
        client = Client()
        client.login(EMAIL1, PWD2)
        folder = client.get_folder(folder_name=ORG + '1' )
        items_list = folder.list_items()
        folder.expand_items_tree()


    def test_file_info(self):
        client = Client()
        client.login(EMAIL1, PWD2)
        folder = client.get_folder(folder_name=f"{ORG + '1'}/{FOL + '1'}")
        file = folder.grab_file_info(file_name='test-name')
        self.assertEqual(file.meta.title, 'test-name')
        self.assertEqual(file.total, 3)

    def test_download_file(self):
        client = Client()
        client.login(EMAIL1, PWD2)
        folder = client.get_folder(folder_name=f"{ORG + '1'}/{FOL + '1'}")
        file = folder.download_file(file_name='test-name')
        file_info = folder.grab_file_info(file_name='test-name')
        self.assertEqual(len(file), file_info.size)

    def test_save_file(self):
        client = Client()
        client.login(EMAIL1, PWD2)
        folder = client.get_folder(folder_name=f"{ORG + '1'}/{FOL + '1'}")
        folder.save_file(path='.\\', file_name='test-name')

    def test_copy_folder(self):
        client = Client()
        client.login(EMAIL1, PWD2)

        # Create destination
        root = client.get_folder(folder_name=ORG + '1')
        destination = root.create_folder(FOL + 'Destination')

        # Copy Folder to new Destination
        folder = client.get_folder(folder_name=f"{ORG + '1'}/{FOL + '1'}")

        copied = folder.copy_to(destination_name=f"{ORG + '1'}/{FOL + 'Destination'}", new_name="Recently Copied")

        self.assertEqual(len(folder.files), len(copied.files))
        self.assertEqual(len(folder.folders), len(copied.folders))
        self.assertEqual(copied.parent, destination.id)
        self.assertEqual(copied.meta.title, "Recently Copied")

        # Get again destination items to check updated folders
        destination = client.get_folder(folder_id=destination.id)
        self.assertIn(copied.id, destination.folders)

    @patch('builtins.input')
    @patch('getpass.getpass')
    @patch('builtins.open', new_callable=mock_open)
    def test_share_folder(self, mock_open, mock_getpass, mock_input):
        # Arrange
        mock_input.side_effect = [EMAIL2, FIRST_NAME + '_2', LAST_NAME + '_2',
                                  '']  # Mock input for email2, firstName, lastName, and picture path
        mock_getpass.side_effect = [PWD, PWD]  # Mock getpass for password and password_confirm

        # Initialize the Client instance
        client = Client()

        # Create new Organization to share the data with
        # But first create new user, the one that will create the destination org
        client.register()
        destination_org = client.create_organization(ORG + '2')
        self.assertEqual(destination_org.name, ORG + '2')

        # Login to first user and share the folder
        client.login(EMAIL1, PWD2)
        folder = client.get_folder(folder_name=f"{ORG + '1'}/{FOL + 'Destination'}")

        resp = folder.share_with_organizations([ORG + '2'])


        # Login to second user and check if part of the new org with the shared data
        client.login(EMAIL2, PWD)
        shared = client.get_folder(folder_name=f"{ ORG + '1' }-{ ORG + '2' }/{ FOL + 'Destination'}")

        # shared.folders
        self.assertEqual(len(folder.folders), len(shared.folders))
        self.assertEqual(len(folder.files), len(shared.files))
        self.assertEqual(resp.id, shared.id)
        self.assertEqual(resp.parent, shared.parent)



    def test_copernicus_list(self):
        client = Client()
        client.login("isotiropoulos@singularlogic.eu", "new_pass")
        client.list_copernicus_resources_per_service("cds")
        client.list_copernicus_resources_per_service("ads")
        return

    def test_copernicus_form(self):
        client = Client()
        client.login("isotiropoulos@singularlogic.eu", "new_pass")
        client.get_copernicus_form_for_resource("cds", "reanalysis-era5-pressure-levels")
        return

    def test_copernicus_dataset_request(self):
        client = Client()
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
        client = Client()

        # Add EMAIL2 user to Organization_1
        client.login(EMAIL1, PWD2)

        users = {
            EMAIL2: "admin"
        }
        success = client.add_user_to_group(ORG + '1', users)
        self.assertTrue(success)

    def test_get_group_role(self):
        client = Client()
        client.login(EMAIL1, PWD2)

        role = client.get_group_role(ORG + '1')


    # def test_update_group_role(self):
    #     client = Client()
    #     client.login(EMAIL1, PWD2)
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

    def test_remove_organization(self):
        client = Client()
        client.login(EMAIL1, PWD2)

        success = client.remove_organization(ORG + '1')
        self.assertTrue(success)


    def test_upload_picture(self):
        client = Client()
        client.login(EMAIL1, PWD2)

        success = client.upload_picture("profile_test.png")
        self.assertTrue(success)


    def test_step_into(self):
        client = Client()
        client.login(EMAIL1, PWD2)

        folder = client.get_folder(folder_name= ORG + "1")
        print(folder.meta.title)
        folder.step_into("Folder_Destination")
        print(folder)

    def test_step_out(self):
        client = Client()
        client.login(EMAIL1, PWD2)

        folder = client.get_folder(folder_name=f'{ORG + "1"}/{FOL + "Destination"}')
        print(folder.meta.title)
        folder.step_out()
        print(folder.meta.title)
        print(folder)

    def test_update_folder(self):
        client = Client()
        client.login(EMAIL1, PWD2)
        # client.login('isotiropoulos@singularlogic.eu', '123456789')

        folder = client.get_folder(folder_id="d598293b-1eaa-42b3-bb7b-fc55ceb52457")
        # folder = client.get_folder(folder_name="test1234567890")
        print("folder: ", folder)
        print("folder.id: ", folder.id)

        updated_name = "Folder_Destination"
        updated_folder = folder.rename_folder(updated_name)

        new_folder = client.get_folder(folder_id="d598293b-1eaa-42b3-bb7b-fc55ceb52457")
        print("new_folder: ", new_folder)

        self.assertEqual(updated_folder.meta.title, updated_name)

    def test_folder_removal(self):
        client = Client()
        client.login(EMAIL1, PWD2)

        folder = client.get_folder(folder_name="Folder_Destination")
        # folder = client.get_folder(folder_id="d598293b-1eaa-42b3-bb7b-fc55ceb52457")

        print("folder: ", folder)
        # print("folder_id: ", folder.id)
        # client.del_folder(folder.id)
        client.del_folder(folder.id)
        # folder.del_folder(folder.id)

    def test_update_file(self):
        client = Client()
        # client.login(EMAIL1, PWD2)
        client.login('isotiropoulos@singularlogic.eu', '123456789')

        folder = client.get_folder(folder_id="c2c7c2f7-321c-4cd3-9712-7c346e77fcbc")
        print("folder: ", folder)
        file = folder.grab_file_info(file_id = "1aff2306-283b-4138-999c-4d6140d6f714")
        print("file: ", file)
        print("file.title: ", file.meta.title)

        folder.rename_file("revised_DJI_photo.jpg")
        print("folder.title: ", folder.meta.title)


    def test_file_removal(self):

        client = Client()

        client.login('isotiropoulos@singularlogic.eu', '123456789')

        folder = client.get_folder(folder_id="c2c7c2f7-321c-4cd3-9712-7c346e77fcbc")
        # print("folder: ", folder)
        file = folder.grab_file_info(file_id="1aff2306-283b-4138-999c-4d6140d6f714")
        print("file: ", file)
        print("file.title: ", file.meta.title)

        client.del_file(file.id)










