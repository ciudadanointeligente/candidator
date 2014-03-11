from django.conf import settings
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import IntegrityError

from elections.models import Election, PersonalData, Candidate, PersonalDataCandidate
from elections.forms import PersonalDataForm, PersonalDataCandidateForm


class PersonalDataModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='joe', password='doe', email='joe@doe.cl')
        self.election, created = Election.objects.get_or_create(name='BarBaz',
                                                            owner=self.user,
                                                            slug='barbaz')

    def test_create_personal_data(self):
        personal_data, created = PersonalData.objects.get_or_create(election=self.election,
                                                                    label='foo')
        self.assertTrue(created)
        self.assertEqual(personal_data.label, 'foo')
        self.assertEqual(personal_data.election, self.election)


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

    def test_post_personal_data_create_without_login(self):
        params = {'label': 'Bar'}
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

        params = {'label': 'Bar'}
        response = self.client.post(reverse('personal_data_create',
                                        kwargs={'election_slug': 'strager_election_slug'}),
                                    params)
        self.assertEquals(response.status_code, 404)

    def test_post_personal_data_create_logged(self):
        self.client.login(username='joe', password='doe')

        params = {'label': 'Bar'}
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

        self.assertRedirects(response, reverse('personal_data_create',
                                               kwargs={'election_slug': self.election.slug}))
                                               
                                               
    def test_step_three_template_rendered(self):
        self.client.login(username='joe', password='doe')
        response = self.client.get(reverse('personal_data_create',
                                    kwargs={'election_slug': self.election.slug}))
        
        self.assertTemplateUsed(response,'elections/wizard/step_three.html')



class PersonalDataCandidateModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='joe', password='doe', email='joe@doe.cl')
        self.election, created = Election.objects.get_or_create(name='BarBaz',
                                                            owner=self.user,
                                                            slug='barbaz')
        self.personal_data, created = PersonalData.objects.get_or_create(election=self.election,
                                                                    label='foo')
        self.candidate = Candidate.objects.create(name='Juan Candidato',
                                                            election=self.election)

    def test_personal_data_candidate_create(self):
        personal_data_candidate, created = PersonalDataCandidate.objects.get_or_create(candidate=self.candidate,
                                                                                       personal_data=self.personal_data,
                                                                                       value='new_value')

        self.assertEqual(personal_data_candidate.candidate, self.candidate)
        self.assertEqual(personal_data_candidate.personal_data, self.personal_data)
        self.assertEqual(personal_data_candidate.value, 'new_value')





class PersonalDataCandidateCreateViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='joe', password='doe', email='joe@doe.cl')
        self.election, created = Election.objects.get_or_create(name='BarBaz',
                                                            owner=self.user,
                                                            slug='barbaz')
        self.personal_data, created = PersonalData.objects.get_or_create(election=self.election,
                                                                    label='foo')
        self.candidate = Candidate.objects.create(name='Juan Candidato', election=self.election)

    def test_create_personal_data_candidate_by_user_without_login(self):
        request = self.client.get(reverse('personal_data_candidate_create',
                                    kwargs={'candidate_pk': self.candidate.pk,
                                            'personal_data_pk': self.personal_data.pk}))
        self.assertEquals(request.status_code, 302)

    def test_create_personal_data_candidate_by_user_success(self):
        self.client.login(username='joe', password='doe')
        request = self.client.get(reverse('personal_data_candidate_create',
                                    kwargs={'candidate_pk': self.candidate.pk,
                                            'personal_data_pk': self.personal_data.pk}))

        self.assertEqual(request.status_code, 200)
        self.assertTrue('form' in request.context)
        self.assertTrue(isinstance(request.context['form'], PersonalDataCandidateForm))
        self.assertTrue('candidate' in request.context)
        self.assertTrue(isinstance(request.context['candidate'], Candidate))
        self.assertTrue('personal_data' in request.context)
        self.assertTrue(isinstance(request.context['personal_data'], PersonalData))

    def test_post_personal_data_candidate_create_without_login(self):
        params = {'value': 'Bar'}
        response = self.client.post(reverse('personal_data_candidate_create',
                                    kwargs={'candidate_pk': self.candidate.pk,
                                            'personal_data_pk': self.personal_data.pk}),
                                    params)

        self.assertEquals(response.status_code, 302)

    def test_get_personal_data_candidate_create_with_login_stranger_candidate(self):
        self.user2 = User.objects.create_user(username='doe', password='doe', email='joe@doe.cl')
        self.election2, created = Election.objects.get_or_create(name='BarBaz',
                                                            owner=self.user2,
                                                            slug='barbaz')
        self.personal_data2, created = PersonalData.objects.get_or_create(election=self.election2,
                                                                    label='foo')
        self.candidate2 = Candidate.objects.create(name='Juan Candidato', election=self.election2)

        self.client.login(username='joe', password='doe')
        response = self.client.get(reverse('personal_data_candidate_create',
                                    kwargs={'candidate_pk': self.candidate2.pk,
                                            'personal_data_pk': self.personal_data2.pk}))
        self.assertEquals(response.status_code, 404)

    def test_post_personal_data_candidate_create_with_login_stranger_candidate(self):
        self.user2 = User.objects.create_user(username='doe', password='doe', email='joe@doe.cl')
        self.election2, created = Election.objects.get_or_create(name='BarBaz',
                                                            owner=self.user2,
                                                            slug='barbaz')
        self.personal_data2, created = PersonalData.objects.get_or_create(election=self.election2,
                                                                    label='foo')
        self.candidate2 = Candidate.objects.create(name='Juan Candidato', election=self.election2)

        self.client.login(username='joe', password='doe')

        params = {'value': 'Bar'}
        response = self.client.post(reverse('personal_data_candidate_create',
                                        kwargs={'candidate_pk': self.candidate2.pk,
                                                'personal_data_pk': self.personal_data2.pk}),
                                    params)
        self.assertEquals(response.status_code, 404)

    def test_post_personal_data_candidate_create_logged(self):
        self.client.login(username='joe', password='doe')

        params = {'value': 'Bar'}
        response = self.client.post(reverse('personal_data_candidate_create',
                                    kwargs={'candidate_pk': self.candidate.pk,
                                            'personal_data_pk': self.personal_data.pk}),
                                    params,
                                    follow=True)

        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.content, '{"value": "%s"}' % params['value'])

        expected = {self.personal_data.label: params['value']}

        self.assertEquals(params['value'], expected[self.personal_data.label])


class AsyncDeletePersonalDataTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='joe', password='doe', email='joe@doe.cl')
        self.election, created = Election.objects.get_or_create(name='BarBaz',
                                                           owner=self.user,
                                                           slug='barbaz',
                                                           description='esta es una descripcion')
        self.personal_data, created = PersonalData.objects.get_or_create(election=self.election,
                                                                    label='foo')

    def test_post_with_login(self):
        self.client.login(username='joe', password='doe')

        request = self.client.post(reverse('async_delete_personal_data',
                                kwargs={'personal_data_pk': self.personal_data.pk}),
                                        {})
        self.assertEquals(request.status_code, 200)

    def test_post_without_login(self):
        request = self.client.post(reverse('async_delete_personal_data',
                                kwargs={'personal_data_pk': self.personal_data.pk}),
                                        {})
        self.assertEquals(request.status_code, 302)


    def test_get_405(self):
        self.client.login(username='joe', password='doe')
        request = self.client.get(reverse('async_delete_personal_data',
                                kwargs={'personal_data_pk': self.personal_data.pk}))

        self.assertEquals(request.status_code, 405)

    def test_post_with_stranger_candidate(self):
        user2 = User.objects.create_user(username='doe', password='doe', email='joe@doe.cl')
        election2, created = Election.objects.get_or_create(name='BarBaz',
                                                           owner=user2,
                                                           slug='barbaz2',
                                                           description='esta es una descripcion')

        personal_data2, created = PersonalData.objects.get_or_create(election=election2,
                                                                        label='foo')

        self.client.login(username='joe', password='doe')
        request = self.client.post(reverse('async_delete_personal_data',
                                kwargs={'personal_data_pk': personal_data2.pk}))

        self.assertEquals(request.status_code, 404)

    def test_post_success(self):
        self.client.login(username='joe', password='doe')
        temp_pk = self.personal_data.pk
        request = self.client.post(reverse('async_delete_personal_data',
                                kwargs={'personal_data_pk': self.personal_data.pk}),
                                        {})

        self.assertEquals(request.status_code, 200)
        self.assertEquals(request.content, '{"result": "OK"}')

        self.assertRaises(PersonalData.DoesNotExist, PersonalData.objects.get, pk=temp_pk)


class AsyncCreatePersonalDataView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='joe', password='doe', email='joe@doe.cl')
        self.election, created = Election.objects.get_or_create(name='BarBaz',
                                                            owner=self.user,
                                                            slug='barbaz')
        self.personal_data, created = PersonalData.objects.get_or_create(election=self.election,
                                                                    label='foo')

        self.user2 = User.objects.create_user(username='johnny', password='doe', email='johnny@doe.cl')

        self.election2, created = Election.objects.get_or_create(name='BarBaz',
                                                            owner=self.user2,
                                                            slug='barbaz')
        self.personal_data2, created = PersonalData.objects.get_or_create(election=self.election2,
                                                                    label='foobar')


    def test_get_async_create_personal_data_with_login(self):
        self.client.login(username='joe', password='doe')
        response = self.client.get(reverse('async_create_personal_data',
                                    kwargs={'election_pk': self.election.pk}))
        self.assertEqual(response.status_code, 405)

    def test_get_async_create_personal_data_without_login(self):
        response = self.client.get(reverse('async_create_personal_data',
                                    kwargs={'election_pk': self.election.pk}))
        self.assertEqual(response.status_code, 302)


    def test_post_async_create_personal_data_without_login(self):
        params = {'value': 'Bar'}
        response = self.client.post(reverse('async_create_personal_data',
                                    kwargs={'election_pk': self.election.pk}),
                                    params)

        self.assertEquals(response.status_code, 302)

    def test_post_async_create_personal_data_with_login_stranger_election(self):
        self.client.login(username='joe', password='doe')

        params = {'value': 'Bar'}
        response = self.client.post(reverse('async_create_personal_data',
                                    kwargs={'election_pk': self.election2.pk}),
                                    params)
        self.assertEquals(response.status_code, 404)

    def test_post_async_create_personal_data_logged(self):
        self.client.login(username='joe', password='doe')

        params = {'value': 'Bar'}
        response = self.client.post(reverse('async_create_personal_data',
                                    kwargs={'election_pk': self.election.pk}),
                                    params,
                                    follow=True)

        self.assertEquals(response.status_code, 200)

        personal_datas = self.election.personaldata_set.all()
        personal_data_labels = [ personal_data.label for personal_data in personal_datas]

        self.assertTrue(params['value'] in personal_data_labels)

        personal_data = self.election.personaldata_set.get(label=params['value'])
        self.assertEquals(response.content, '{"pk": %d, "label": "%s"}' % (personal_data.pk, params['value']))
