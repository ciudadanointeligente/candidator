import os
from django.conf import settings
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import IntegrityError

from elections.models import Link, Candidate, Election
from django.core.exceptions import ValidationError
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

    def test_does_not_create_an_empty_link(self):
        link = Link(name="", url="", candidate=self.candidate)
        try:
            link.full_clean()
            self.fail('The link name can not be empty')
        except ValidationError as e:
            expected_error = {'name':[u'This field cannot be blank.'], 'url':[u'This field cannot be blank.']}
            self.assertEqual(e.message_dict,expected_error)

        
        link = Link(name="", url="http://www.google.com", candidate=self.candidate)
        try:
            link.full_clean()
            self.fail('The link name can not be empty')
        except ValidationError as e:
            expected_error = {'name':[u'This field cannot be blank.']}
            self.assertEqual(e.message_dict,expected_error)


        link = Link(name="Twitter", url="", candidate=self.candidate)
        try:
            link.full_clean()
            self.fail('The url not can be empty')
        except ValidationError as e:
            expected_error = {'url':[u'This field cannot be blank.']}
            self.assertEqual(e.message_dict,expected_error)

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


class AsyncDeleteLinkTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='joe', password='doe', email='joe@doe.cl')
        self.election, created = Election.objects.get_or_create(name='BarBaz',
                                                           owner=self.user,
                                                           slug='barbaz',
                                                           description='esta es una descripcion')

        self.candidate, created = Candidate.objects.get_or_create(name='Juan Candidato',
                                                                  election=self.election)
        self.link, created = Link.objects.get_or_create(name='Google',
                                                        url='http://www.google.com',
                                                        candidate=self.candidate)


    def test_post_with_login(self):
        self.client.login(username='joe', password='doe')

        request = self.client.post(reverse('async_delete_link',
                                kwargs={'link_pk': self.link.pk}),
                                        {})
        self.assertEquals(request.status_code, 200)

    def test_post_without_login(self):
        request = self.client.post(reverse('async_delete_link',
                                kwargs={'link_pk': self.link.pk}),
                                        {})
        self.assertEquals(request.status_code, 302)


    def test_get_405(self):
        self.client.login(username='joe', password='doe')
        request = self.client.get(reverse('async_delete_link',
                                kwargs={'link_pk': self.link.pk}))
        self.assertEquals(request.status_code, 405)

    def test_post_with_stranger_candidate(self):
        user2 = User.objects.create_user(username='doe', password='doe', email='joe@doe.cl')
        election2, created = Election.objects.get_or_create(name='BarBaz',
                                                           owner=user2,
                                                           slug='barbaz2',
                                                           description='esta es una descripcion')

        candidate2, created = Candidate.objects.get_or_create(name='Juan Candidato',
                                                                  election=election2)
        link2, created = Link.objects.get_or_create(name='Google',
                                                    url='http://www.google.com',
                                                    candidate=candidate2)


        self.client.login(username='joe', password='doe')
        request = self.client.post(reverse('async_delete_link',
                                kwargs={'link_pk': link2.pk}))

        self.assertEquals(request.status_code, 404)

    def test_post_success(self):
        self.client.login(username='joe', password='doe')
        temp_pk = self.link.pk
        request = self.client.post(reverse('async_delete_link',
                                kwargs={'link_pk': self.link.pk}),
                                        {})

        self.assertEquals(request.status_code, 200)
        self.assertEquals(request.content, '{"result": "OK"}')

        self.assertRaises(Link.DoesNotExist, Link.objects.get, pk=temp_pk)