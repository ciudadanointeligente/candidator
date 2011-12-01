from django.conf import settings
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import IntegrityError

from elections.models import Election, PersonalData
from elections.forms import PersonalDataForm


class PersonalDataModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='joe', password='doe', email='joe@doe.cl')
        self.election, created = Election.objects.get_or_create(name='BarBaz',
                                                            owner=self.user,
                                                            slug='barbaz')

    def test_create_personal_data(self):
        personal_data, created = PersonalData.objects.get_or_create(election=self.election,
                                                                    label='foo',
                                                                    slug='foo')
        self.assertTrue(created)
        self.assertEqual(personal_data.label, 'foo')
        self.assertEqual(personal_data.election, self.election)
        self.assertEqual(personal_data.slug, 'foo')

    def test_create_personal_data_with_same_slug(self):
        personal_data, created = PersonalData.objects.get_or_create(election=self.election,
                                                                    label='foo',
                                                                    slug='foo')
        self.assertRaises(IntegrityError, PersonalData.objects.create,
                      label='fooabr', slug='foo', election=self.election)

class PersonalDataCreateView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='joe', password='doe', email='joe@doe.cl')
        self.election, created = Election.objects.get_or_create(name='BarBaz',
                                                            owner=self.user,
                                                            slug='barbaz')

    def test_create_personal_data_by_user_without_login(self):
        request = self.client.get(reverse('personal_data_create',
                                    kwargs={'election_slug': self.election.slug}))
        self.assertEquals(request.status_code, 302)

    def test_create_personal_data_by_user_success(self):
        self.client.login(username='joe', password='doe')
        request = self.client.get(reverse('personal_data_create',
                                    kwargs={'election_slug': self.election.slug}))

        self.assertEqual(request.status_code, 200)
        self.assertTrue('form' in request.context)
        self.assertTrue(isinstance(request.context['form'], PersonalDataForm))
        self.assertTrue('election' in request.context)
        self.assertTrue(isinstance(request.context['election'], Election))

    def test_post_personal_data_create_with_same_slug(self):
        personal_data, created = PersonalData.objects.get_or_create(election=self.election,
                                                                    label='foo',
                                                                    slug='foo')
        self.client.login(username='joe', password='doe')
        params = {'label': 'Bar', 'slug': 'foo'}
        response = self.client.post(reverse('personal_data_create',
                                        kwargs={'election_slug': self.election.slug}),
                                    params)

        self.assertEquals(response.status_code, 200)
        self.assertFormError(response, 'form', 'slug','Ya tienes un dato personal con ese slug.' )


    def test_post_personal_data_create_without_login(self):
        params = {'label': 'Bar', 'slug': 'bar'}
        response = self.client.post(reverse('personal_data_create',
                                        kwargs={'election_slug': self.election.slug}),
                                    params)

        self.assertEquals(response.status_code, 302)

    def test_get_personal_data_create_with_login_stranger_election(self):
        self.client.login(username='joe', password='doe')
        response = self.client.get(reverse('personal_data_create',
                                    kwargs={'election_slug': 'strager_election_slug'}))
        self.assertEquals(response.status_code, 404)

    def test_post_personal_data_create_with_login_stranger_election(self):
        self.client.login(username='joe', password='doe')

        params = {'label': 'Bar', 'slug': 'bar'}
        response = self.client.post(reverse('personal_data_create',
                                        kwargs={'election_slug': 'strager_election_slug'}),
                                    params)
        self.assertEquals(response.status_code, 404)

    def test_post_personal_data_create_logged(self):
        self.client.login(username='joe', password='doe')

        params = {'label': 'Bar', 'slug': 'bar'}
        response = self.client.post(reverse('personal_data_create',
                                        kwargs={'election_slug': self.election.slug}),
                                    params,
                                    follow=True)

        self.assertEquals(response.status_code, 200)
        qs = PersonalData.objects.filter(label='Bar')
        self.assertEquals(qs.count(), 1)
        personal_data = qs.get()
        self.assertEqual(personal_data.label, params['label'])
        self.assertEqual(personal_data.election, self.election)
        self.assertEqual(personal_data.slug, params['slug'])

        self.assertRedirects(response, reverse('personal_data_create',
                                               kwargs={'election_slug': self.election.slug}))