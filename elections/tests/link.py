import os
from django.conf import settings
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import IntegrityError

from elections.models import Link, Candidate, Election
#from elections.forms import CandidateLinkFormset

dirname = os.path.dirname(os.path.abspath(__file__))

class LinkModelTest(TestCase):
    def setUp(self):
        self.user, created = User.objects.get_or_create(username='joe')
        self.election, created = Election.objects.get_or_create(name='BarBaz',
                                                           owner=self.user,
                                                           slug='barbaz',
                                                           description='esta es una descripcion')

        self.candidate, created = Candidate.objects.get_or_create(name='Juan Candidato',
                                                                  election=self.election)

    def test_create_link(self):
        link, created = Link.objects.get_or_create(
                                                    name='Google',
                                                    url='http://www.google.com',
                                                    candidate=self.candidate)
        self.assertTrue(created)
        self.assertEqual(link.name, 'Google')
        self.assertEqual(link.url, 'http://www.google.com')
        self.assertEqual(link.candidate, self.candidate)

    def test_http_prefixes(self):
        link, created = Link.objects.get_or_create(
                                                    name = 'Twitter',
                                                    url = 'www.twitter.com',
                                                    candidate = self.candidate)

        link2, created = Link.objects.get_or_create(
                                                    name = 'Twitter',
                                                    url = 'http://www.twitter.com',
                                                    candidate = self.candidate)
        self.assertTrue(created)
        self.assertEqual(link.http_prefix, 'http://www.twitter.com')
        self.assertEqual(link2.http_prefix, 'http://www.twitter.com')

    def test_css_classess(self):
        link, created = Link.objects.get_or_create(
                                                    name='Facebook',
                                                    url='http://www.facebook.com',
                                                    candidate=self.candidate)
        self.assertTrue(created)
        self.assertEqual(link.css_class, 'facebook')

        link, created = Link.objects.get_or_create(
                                                    name='Twitter',
                                                    url='http://www.twitter.com',
                                                    candidate=self.candidate)
        self.assertTrue(created)
        self.assertEqual(link.css_class, 'twitter')