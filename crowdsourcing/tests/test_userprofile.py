import os, django, json, pprint, types
from rest_framework.test import APIClient
from rest_framework.test import APITestCase
from crowdsourcing import models
from rest_framework import status
from django.contrib.auth.models import User
from crowdsourcing.viewsets.user import UserProfileViewSet

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FIXTURE_DIR = os.path.join(BASE_DIR, 'fixtures')
userprofile_data = os.path.join(FIXTURE_DIR, 'lucaUserProfileTestData.json')

"""
    Unit test for UserProfile API

    You can run just this test like,
    > python manage.py test crowdsourcing.tests.test_userprofile.UserProfileTestCase

    This test uses data files:
        crowdsource-platform/fixtures/lucaUserProfileTestData.json
"""
class UserProfileTestCase(APITestCase):
    fixtures = [userprofile_data]

    # Preparing test data
    def setUp(self):
        self.creste_req = {
          'user': 1,
          'user_username': 'luca1.matsumoto',
          'gender': 'M',
          'birthday': '2001-01-01',
          'address': {
            'city': {
              'country': {
                'code': '456',
                'name': 'U.S.A.',
                'region': {
                  'code': '123456',
                  'name': 'California'
                }
              },
              'name': 'Palo Alto'
            },
            'country': {
              'code': '456',
              'name': 'U.S.A.',
              'region': {
                'code': '123456',
                'name': 'California'
              }
            },
            'street': '123 University Ave.'
          }
        }

        self.expected_addr = {
            "id": 3,
            "country": {
                "id": 2,
                "region": {
                    "id": 2,
                    "name": "California",
                    "code": "123456"
                },
                "name": "U.S.A.",
                "code": "456"
            },
            "city": {
                "id": 2,
                "country": {
                    "id": 3,
                    "region": {
                        "id": 3,
                        "name": "California",
                        "code": "123456"
                    },
                    "name": "U.S.A.",
                    "code": "456"
                },
                "name": "Palo Alto"
            },
            "street": "123 University Ave."
        }

        self.bad_req = {
          'user': 1,
          'user_username': 'luca1.matsumoto',
          'gender': 'M',
          'birthday': '2001-01-01',
          'address': {
            'city': {
              'name': 'Palo Alto'
            },
            'country': {
              'code': '456',
              'name': 'U.S.A.',
              'region': {
                'code': '123456',
                'name': 'California'
              }
            },
            'street': '123 University Ave.'
          }
        }

        self.creste_req2 = {
          'user': 2,
          'user_username': 'luca2.matsumoto',
          'gender': 'F',
          'birthday': '2002-02-02',
          'address': {
            'city': {
              'country': {
                'code': '456789',
                'name': 'U.S.A.',
                'region': {
                  'code': '123456789',
                  'name': 'California'
                }
              },
              'name': 'Palo Alto'
            },
            'country': {
              'code': '456789',
              'name': 'U.S.A.',
              'region': {
                'code': '123456789',
                'name': 'California'
              }
            },
            'street': '123456 University Ave.'
          }
        }



    def testCreateUserProfile(self):
        # Create a new user profile
        response = self.client.post('/api/profile/', self.creste_req, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Get the user profile just created
        response = self.client.get('/api/profile/luca1.matsumoto/', format='json')
        # print(json.dumps(response.data.get('address'), indent=4))

        # Remove timestamps from address in response
        addr = delete_keys_from_dict(
            dict(response.data.get('address')), 
            ['created_timestamp', 'last_updated'])

        # Compare with extected address
        self.assertEqual(addr, self.expected_addr )
        self.assertEqual(models.Address.objects.count(), 3)
        self.assertEqual(models.UserProfile.objects.count(), 1)

        # Create the another user profile
        response = self.client.post('/api/profile/', self.creste_req2, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(models.Address.objects.count(), 4)
        self.assertEqual(models.UserProfile.objects.count(), 2)


    # def testIntegrity(self):
    #     # Create a new user profile
    #     response = self.client.post('/api/profile/', self.creste_req, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)

    #     # Create the same user profile
    #     response = self.client.post('/api/profile/', self.creste_req, format='json')
    #     # How do we check?


    def testBadCreateRequest(self):
        # Create a new user profile
        response = self.client.post('/api/profile/', self.bad_req, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


def delete_keys_from_dict(dict_del, lst_keys):
    for k in lst_keys:
        try:
            del dict_del[k]
        except KeyError:
            pass
    for v in dict_del.values():
        if isinstance(v, dict):
            delete_keys_from_dict(v, lst_keys)

    return dict_del