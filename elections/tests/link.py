import os
from django.conf import settings
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import IntegrityError

from elections.models import Link, Candidate, Election
from elections.forms import CandidateLinkFormset

dirname = os.path.dirname(os.path.abspath(__file__))

class LinkModelTest(TestCase):
    def setUp(self):
        self.user, created = User.objects.get_or_create(username='joe')
        self.election, created = Election.objects.get_or_create(name='BarBaz',
                                                           owner=self.user,
                                                           slug='barbaz',
                                                           description='esta es una descripcion')

        self.candidate, created = Candidate.objects.get_or_create(first_name='Juan',
                                                                  last_name='Candidato',
                                                                  slug='juan-candidato',
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



class CreateCandidateLinkViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='joe', password='doe', email='asd@asd.cl')
        self.election, created = Election.objects.get_or_create(name='BarBaz',
                                                           owner=self.user,
                                                           slug='barbaz',
                                                           description='esta es una descripcion')

        self.candidate, created = Candidate.objects.get_or_create(first_name='Juan',
                                                                  last_name='Candidato',
                                                                  slug='juan-candidato',
                                                                  election=self.election)

    def test_create_candidate_with_link_by_user_success(self):
        self.client.login(username='joe', password='doe')
        request = self.client.get(reverse('candidate_create', kwargs={'election_slug': self.election.slug}))

        self.assertTrue('link_formset' in request.context)
        self.assertTrue(isinstance(request.context['link_formset'], CandidateLinkFormset))


    def test_post_candidate_create_with_link_logged(self):
        self.client.login(username='joe', password='doe')

        f = open(os.path.join(dirname, 'media/dummy.jpg'), 'rb')
        params = {'first_name': 'Juan', 'last_name': 'Candidato',
                  'slug': 'nuevo_candidato_slug', 'photo': f,
                  'form-TOTAL_FORMS': u'0',
                  'form-INITIAL_FORMS': u'0',
                  'form-MAX_NUM_FORMS': u'',

                  'link-TOTAL_FORMS': u'2',
                  'link-INITIAL_FORMS': u'0',
                  'link-MAX_NUM_FORMS': u'',

                  'link-0-name': 'Foo',
                  'link-0-url': 'http://www.google.cl',
                  'link-1-name': 'Foo2',
                  'link-1-url': 'http://www.google.com'}
        response = self.client.post(reverse('candidate_create', kwargs={'election_slug': self.election.slug}), params, follow=True)
        f.seek(0)

        candidate = Candidate.objects.get(slug=params['slug'])
        self.assertEqual(candidate.link_set.count(), 2)

        link = candidate.link_set.all()[0]
        self.assertEqual(link.name, params['link-0-name'])
        self.assertEqual(link.url, params['link-0-url'])

        link = candidate.link_set.all()[1]
        self.assertEqual(link.name, params['link-1-name'])
        self.assertEqual(link.url, params['link-1-url'])

