"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.contrib.auth.models import User

from models import Profile

class SimpleTest(TestCase):
    def test_basic_addition(self):
        user = User.objects.create(username='foo', password='foo', email='foo@example.net')
        self.assertEqual(Profile.objects.count(), 1)
        profile = Profile.objects.get()
        self.assertEqual(profile.user, user)
        self.assertEqual(profile.name, user.username)
