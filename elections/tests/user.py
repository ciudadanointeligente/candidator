from django.test import TestCase
from django.contrib.auth.models import User
from tastypie.models import ApiKey


class UserApiKeyCreationTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='joe', password='doe', email='joe@doe.cl')


    def test_exit_api_key_to_a_new_user(self):
        api_key = ApiKey.objects.filter(user = self.user)
        self.assertEqual(len(api_key), 1)
