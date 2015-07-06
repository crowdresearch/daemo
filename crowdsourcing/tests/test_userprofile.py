from django.test import TestCase
from rest_framework.test import APIRequestFactory
from crowdsourcing.viewsets.user import UserProfileViewSet
#from rest_framework import status
#from rest_framework.test import APITestCase

"""
    This test is not working yet. The test data file won't be loaded somehow.
    If I move it under crowdsource-platform/crowdsourcing/fixtures, auto fixture loader
    can find the file, but won't load it.
"""

class UserProfileTestCase(TestCase):
#    fixtures = ['lucaUserProfileTestData.json']

    def setUp(self):
        pass

    def testCreateUserProfile(self):
        data = {'user_name': 'rachel.ginzberg', 'gender': 'F', 'birthday': '1990-01-01', 'address': 2}
        factory = APIRequestFactory()
        request = factory.post('/api/profile/', data)

        get_request = factory.get('/api/profile/rachel.ginzberg/')
        view = UserProfileViewSet.as_view({'get': 'retrieve'})
        get_response = view(get_request)
        get_response.render()
        print get_response.content


#class UserProfileAPITestCase(APITestCase):
#    fixtures = ['lucaUserProfileTestData.json']
#
#    def setUp(self):
#        pass
#
#    def testCreateUserProfile(self):
#        data = {'user_name': 'adam.ginzberg', 'gender': 'M', 'birthday': '1990-01-01', 'address': 1}
#        response = self.client.post('/api/profile/', data, format='json')
#        print response.data
       
