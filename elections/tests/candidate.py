import os
from django.conf import settings
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import IntegrityError

from elections.models import Candidate, Election

dirname = os.path.dirname(os.path.abspath(__file__))

class CandidateModelTest(TestCase):
    def test_create_candidate(self):
        user, created = User.objects.get_or_create(username='joe')
        election, created = Election.objects.get_or_create(name='BarBaz',
                                                           owner=user,
                                                           slug='barbaz',
                                                           description='esta es una descripcion')

        candidate, created = Candidate.objects.get_or_create(first_name='Juan',
                                                            last_name='Candidato',
                                                            slug='juan-candidato',
                                                            election=election)

        self.assertTrue(created)
        self.assertEqual(candidate.first_name, 'Juan')
        self.assertEqual(candidate.last_name, 'Candidato')
        self.assertEqual(candidate.slug, 'juan-candidato')
        self.assertEqual(candidate.election, election)

    def test_create_two_candidate_with_same_election_with_same_slug(self):
        user = User.objects.create_user(username='joe', password='doe', email='joe@doe.cl')

        election, created = Election.objects.get_or_create(name='BarBaz',
                                                           owner=user,
                                                           slug='barbaz',
                                                           description='esta es una descripcion')

        candidate = Candidate.objects.create(first_name='Juan',
                                                            last_name='Candidato',
                                                            slug='juan-candidato',
                                                            election=election)

        self.assertRaises(IntegrityError, Candidate.objects.create,
                          first_name='Juanito', last_name='Candidatito', slug='juan-candidato', election=election)

    def test_name_property(self):
        candidate = Candidate()
        candidate.first_name = 'Juanito'
        candidate.last_name = 'Perez'

        expected_name = 'Juanito Perez'

        self.assertEqual(candidate.name, expected_name)


class CandidateDetailViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='foobar')
        self.election, created = Election.objects.get_or_create(name='BarBaz',
                                                           owner=self.user,
                                                           slug='barbaz',
                                                           description='esta es una descripcion')

        self.candidate = Candidate.objects.create(first_name='Juan',
                                                            last_name='Candidato',
                                                            slug='juan-candidato',
                                                            election=self.election)

    def test_detail_existing_candidate_view(self):
        response = self.client.get(reverse('candidate_detail',
                                           kwargs={
                                               'username': self.user.username,
                                               'election_slug': self.election.slug,
                                               'slug': self.candidate.slug}))

        self.assertEquals(response.status_code, 200)
        self.assertTrue('candidate' in response.context)
        self.assertEquals(response.context['candidate'], self.candidate)

    def test_detail_non_existing_candidate_view(self):
        response = self.client.get(reverse('candidate_detail',
                                           kwargs={
                                               'username': self.user.username,
                                               'election_slug': self.election.slug,
                                               'slug': 'asd-asd'}))
        self.assertEquals(response.status_code, 404)

    def test_detail_non_existing_candidate_for_user_view(self):
        election, created = Election.objects.get_or_create(name='AsdAsd',
                                                           owner=self.user,
                                                           slug='asdasd',
                                                           description='esta es una descripcion dos')
        response = self.client.get(reverse('candidate_detail',
                                           kwargs={
                                               'username': self.user.username,
                                               'election_slug': election.slug,
                                               'slug': self.candidate.slug}))
        self.assertEquals(response.status_code, 404)

        '''
        TODO: distintos usuarios, mismo slug de eleccion,
                mismo slug de candidato (inexistente en uno, pero existente en otra)
        '''

'''
class CandidateCreateViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='joe', password='doe', email='joe@doe.cl')

    def test_create_Candidate_by_user_without_login(self):
        user = self.user

        request = self.client.get(reverse('Candidate_create'))

        self.assertEquals(request.status_code, 302)

    def test_create_Candidate_by_user_success(self):
        user = self.user

        self.client.login(username='joe', password='doe')
        request = self.client.get(reverse('Candidate_create'))

        self.assertTrue('form' in request.context)
        self.assertTrue(isinstance(request.context['form'], CandidateForm))

    def test_post_Candidate_create_with_same_slug(self):
        Candidate = Candidate.objects.create(name='BarBaz1', slug='barbaz', description='whatever', owner=self.user)

        self.client.login(username='joe', password='doe')
        params = {'name': 'BarBaz', 'slug': 'barbaz', 'description': 'esta es una descripcion'}
        response = self.client.post(reverse('Candidate_create'), params)

        self.assertEquals(response.status_code, 200)

    def test_post_Candidate_create_without_login(self):
        params = {'name': 'BarBaz', 'slug': 'barbaz', 'description': 'esta es una descripcion'}
        response = self.client.post(reverse('Candidate_create'), params)

        self.assertEquals(response.status_code, 302)

    def test_post_Candidate_create_logged(self):
        self.client.login(username='joe', password='doe')

        f = open(os.path.join(dirname, 'media/dummy.jpg'), 'rb')
        params = {'name': 'BarBaz', 'slug': 'barbaz', 'description': 'esta es una descripcion', 'logo': f}
        response = self.client.post(reverse('Candidate_create'), params, follow=True)
        f.seek(0)

        self.assertEquals(response.status_code, 200)
        qs = Candidate.objects.filter(name='BarBaz')
        self.assertEquals(qs.count(), 1)
        Candidate = qs.get()
        self.assertEquals(Candidate.name, 'BarBaz')
        self.assertEquals(Candidate.slug, 'barbaz')
        self.assertEquals(Candidate.description, 'esta es una descripcion')
        self.assertEquals(f.read(), Candidate.logo.file.read())

        os.unlink(Candidate.logo.path)
        self.assertEquals(Candidate.owner, self.user)
        self.assertRedirects(response, reverse('candidate_create',
                                               kwargs={'slug': Candidate.slug}))
'''

class CandidateUrlsTest(TestCase):
    def test_create_url(self):
        expected = '/bar-baz/candidate/create'
        result = reverse('candidate_create', kwargs={'slug': 'bar-baz' })
        self.assertEquals(result, expected)

    def test_detail_url(self):
        expected = '/juanito/bar-baz/juan-candidato'
        result = reverse('candidate_detail', kwargs={'username': 'juanito', 'election_slug': 'bar-baz', 'slug': 'juan-candidato'})
        self.assertEquals(result, expected)
