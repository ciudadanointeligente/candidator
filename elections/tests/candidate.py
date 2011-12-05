import os
from django.conf import settings
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import IntegrityError

from elections.models import Candidate, Election
from elections.forms import CandidateUpdateForm, CandidateForm

dirname = os.path.dirname(os.path.abspath(__file__))


class CandidateModelTest(TestCase):
    def setUp(self):
        self.user, created = User.objects.get_or_create(username='joe')
        self.election, created = Election.objects.get_or_create(name='BarBaz',
                                                           owner=self.user,
                                                           slug='barbaz',
                                                           description='esta es una descripcion')

    def test_create_candidate(self):
        candidate, created = Candidate.objects.get_or_create(first_name='Juan',
                                                            last_name='Candidato',
                                                            slug='juan-candidato',
                                                            election=self.election)

        self.assertTrue(created)
        self.assertEqual(candidate.first_name, 'Juan')
        self.assertEqual(candidate.last_name, 'Candidato')
        self.assertEqual(candidate.slug, 'juan-candidato')
        self.assertEqual(candidate.election, self.election)

    def test_update_candidate(self):
        candidate, created = Candidate.objects.get_or_create(first_name='Juan',
                                                            last_name='Candidato',
                                                            slug='juan-candidato',
                                                            election=self.election)

        candidate.first_name = 'nuevo_nombre'
        candidate.save()

        candidate2 = Candidate.objects.get(slug='juan-candidato', election=self.election)
        self.assertEqual(candidate2.first_name, 'nuevo_nombre')


    def test_create_two_candidate_with_same_election_with_same_slug(self):
        candidate = Candidate.objects.create(first_name='Juan',
                                                            last_name='Candidato',
                                                            slug='juan-candidato',
                                                            election=self.election)

        self.assertRaises(IntegrityError, Candidate.objects.create,
                          first_name='Juanito', last_name='Candidatito', slug='juan-candidato', election=self.election)

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


class CandidateCreateViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='joe', password='doe', email='joe@doe.cl')
        self.election, created = Election.objects.get_or_create(name='BarBaz',
                                                           owner=self.user,
                                                           slug='barbaz',
                                                           description='esta es una descripcion')

    def test_create_candidate_by_user_without_login(self):
        request = self.client.get(reverse('candidate_create', kwargs={'election_slug': self.election.slug}))

        self.assertEquals(request.status_code, 302)

    def test_create_candidate_by_user_success(self):
        self.client.login(username='joe', password='doe')
        request = self.client.get(reverse('candidate_create', kwargs={'election_slug': self.election.slug}))

        self.assertTrue('form' in request.context)
        self.assertTrue(isinstance(request.context['form'], CandidateForm))
        self.assertTrue('election' in request.context)
        self.assertTrue(isinstance(request.context['election'], Election))

    def test_post_candidate_create_with_same_slug(self):
        candidate = Candidate.objects.create(first_name='Juan',
                                            last_name='Candidato',
                                            slug='juan-candidato',
                                            election=self.election)
        self.client.login(username='joe', password='doe')

        f = open(os.path.join(dirname, 'media/dummy.jpg'), 'rb')
        params = {'first_name': 'first', 'last_name': 'last',
                  'slug': candidate.slug, 'photo': f,
                  'form-TOTAL_FORMS': u'0',
                  'form-INITIAL_FORMS': u'0',
                  'form-MAX_NUM_FORMS': u'',
                  'link-TOTAL_FORMS': u'0',
                  'link-INITIAL_FORMS': u'0',
                  'link-MAX_NUM_FORMS': u'',
                  }
        response = self.client.post(reverse('candidate_create', kwargs={'election_slug': self.election.slug}), params)
        f.close()

        self.assertEquals(response.status_code, 200)
        self.assertFormError(response, 'form', 'slug','Ya tienes un candidato con ese slug.' )

        # falta revisar que no funcione el formulario

    def test_post_candidate_create_without_login(self):
        f = open(os.path.join(dirname, 'media/dummy.jpg'), 'rb')
        params = {'first_name': 'Juan', 'last_name': 'Candidato',
                  'slug': 'juan-candidato', 'photo': f,
                  'form-TOTAL_FORMS': u'0',
                  'form-INITIAL_FORMS': u'0',
                  'form-MAX_NUM_FORMS': u'',
                  'link-TOTAL_FORMS': u'0',
                  'link-INITIAL_FORMS': u'0',
                  'link-MAX_NUM_FORMS': u'',}
        response = self.client.post(reverse('candidate_create', kwargs={'election_slug': self.election.slug}), params)
        f.close()

        self.assertEquals(response.status_code, 302)

    def test_get_candidate_create_with_login_stranger_election(self):
        self.client.login(username='joe', password='doe')
        response = self.client.get(reverse('candidate_create',
                                    kwargs={'election_slug': 'strager_election_slug'}))
        self.assertEquals(response.status_code, 404)

    def test_post_candidate_create_with_login_stranger_election(self):
        f = open(os.path.join(dirname, 'media/dummy.jpg'), 'rb')
        self.client.login(username='joe', password='doe')

        params = {'first_name': 'Juan', 'last_name': 'Candidato',
                  'slug': 'juan-candidato', 'photo': f,
                  'form-TOTAL_FORMS': u'0',
                  'form-INITIAL_FORMS': u'0',
                  'form-MAX_NUM_FORMS': u'',
                  'link-TOTAL_FORMS': u'0',
                  'link-INITIAL_FORMS': u'0',
                  'link-MAX_NUM_FORMS': u'',}
        response = self.client.post(reverse('candidate_create',
                                        kwargs={'election_slug': 'strager_election_slug'}),
                                    params)
        f.close()

        self.assertEquals(response.status_code, 404)

    def test_post_candidate_create_logged(self):
        self.client.login(username='joe', password='doe')

        f = open(os.path.join(dirname, 'media/dummy.jpg'), 'rb')
        params = {'first_name': 'Juan', 'last_name': 'Candidato',
                  'slug': 'juan-candidato', 'photo': f,
                  'form-TOTAL_FORMS': u'0',
                  'form-INITIAL_FORMS': u'0',
                  'form-MAX_NUM_FORMS': u'',
                  'link-TOTAL_FORMS': u'0',
                  'link-INITIAL_FORMS': u'0',
                  'link-MAX_NUM_FORMS': u'',}
        response = self.client.post(reverse('candidate_create', kwargs={'election_slug': self.election.slug}), params, follow=True)
        f.seek(0)

        self.assertEquals(response.status_code, 200)
        qs = Candidate.objects.filter(election= self.election, slug='juan-candidato')
        self.assertEquals(qs.count(), 1)
        candidate = qs.get()
        self.assertEquals(candidate.first_name, params['first_name'])
        self.assertEquals(candidate.last_name, params['last_name'])
        self.assertEquals(f.read(), candidate.photo.file.read())
        f.close()
        os.unlink(candidate.photo.path)
        self.assertEquals(candidate.election, self.election)
        self.assertRedirects(response, reverse('candidate_create',
                                               kwargs={'election_slug': candidate.election.slug}))


class CandidateUpdateViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='joe', password='doe', email='joe@doe.cl')
        self.election, created = Election.objects.get_or_create(name='BarBaz',
                                                           owner=self.user,
                                                           slug='barbaz',
                                                           description='esta es una descripcion')

        self.candidate, created = Candidate.objects.get_or_create(first_name='Juan',
                                            last_name='Candidato',
                                            slug='juan-candidato',
                                            election=self.election)


    def test_update_candidate_by_user_without_login(self):
        request = self.client.get(reverse('candidate_update', kwargs={'slug': self.candidate.slug, 'election_slug': self.election.slug}))

        self.assertEquals(request.status_code, 302)

    def test_update_candidate_by_user_success(self):
        self.client.login(username='joe', password='doe')
        request = self.client.get(reverse('candidate_update', kwargs={'slug': self.candidate.slug, 'election_slug': self.election.slug}))

        self.assertTrue('form' in request.context)
        self.assertTrue(isinstance(request.context['form'], CandidateUpdateForm))
        self.assertTrue('first_name' in request.context['form'].initial)
        self.assertEquals(request.context['form'].initial['first_name'], 'Juan')
        self.assertTrue('last_name' in request.context['form'].initial)
        self.assertEquals(request.context['form'].initial['last_name'], 'Candidato')

    def test_post_candidate_update_without_login(self):
        f = open(os.path.join(dirname, 'media/dummy.jpg'), 'rb')
        params = {'first_name': 'Juan', 'last_name': 'Candidato',
                  'photo': f,}
        response = self.client.post(reverse('candidate_update', kwargs={'slug': self.candidate.slug, 'election_slug': self.election.slug}), params)
        f.close()

        self.assertEquals(response.status_code, 302)

    def test_get_candidate_update_with_login_stranger_election(self):
        self.client.login(username='joe', password='doe')
        response = self.client.get(reverse('candidate_update',
                                    kwargs={'slug': self.candidate.slug, 'election_slug': 'strager_election_slug'}))
        self.assertEquals(response.status_code, 404)

    def test_post_candidate_update_with_login_stranger_election(self):
        f = open(os.path.join(dirname, 'media/dummy.jpg'), 'rb')
        self.client.login(username='joe', password='doe')

        params = {'first_name': 'Juan', 'last_name': 'Candidato',
                  'photo': f,}
        response = self.client.post(reverse('candidate_update',
                                        kwargs={'slug': self.candidate.slug, 'election_slug': 'strager_election_slug'}),
                                    params)
        f.close()

        self.assertEquals(response.status_code, 404)

    def test_post_candidate_update_logged(self):
        self.client.login(username='joe', password='doe')

        f = open(os.path.join(dirname, 'media/dummy.jpg'), 'rb')
        params = {'first_name': 'Juanito', 'last_name': 'Candidato',
                  'photo': f,}
        response = self.client.post(reverse('candidate_update', kwargs={'slug': self.candidate.slug, 'election_slug': self.election.slug}), params, follow=True)
        f.seek(0)

        self.assertEquals(response.status_code, 200)
        qs = Candidate.objects.filter(election= self.election, slug='juan-candidato')
        self.assertEquals(qs.count(), 1)
        candidate = qs.get()
        self.assertEquals(candidate.first_name, params['first_name'])
        self.assertEquals(candidate.last_name, params['last_name'])
        self.assertEquals(f.read(), candidate.photo.file.read())
        f.close()
        os.unlink(candidate.photo.path)
        self.assertEquals(candidate.election, self.election)
        self.assertRedirects(response, reverse('candidate_update',
                                               kwargs={'slug': self.candidate.slug, 'election_slug': candidate.election.slug}))


class CandidateUrlsTest(TestCase):
    def test_create_url(self):
        expected = '/bar-baz/candidate/create'
        result = reverse('candidate_create', kwargs={'election_slug': 'bar-baz'})
        self.assertEquals(result, expected)

    def test_detail_url(self):
        expected = '/juanito/bar-baz/juan-candidato'
        result = reverse('candidate_detail', kwargs={'username': 'juanito', 'election_slug': 'bar-baz', 'slug': 'juan-candidato'})
        self.assertEquals(result, expected)
