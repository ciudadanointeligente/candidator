from django.conf import settings
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import IntegrityError

from elections.models import Election, BackgroundCategory, Background, BackgroundCandidate, Candidate
from elections.forms import BackgroundForm, BackgroundCandidateForm


class BackgroundModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='joe', password='doe', email='joe@doe.cl')
        self.election, created = Election.objects.get_or_create(name='BarBaz',
                                                            owner=self.user,
                                                            slug='barbaz')
        self.background_category, created = BackgroundCategory.objects.get_or_create(election=self.election,
                                                                    name='FooBar')

    def test_create_background(self):
        background, created = Background.objects.get_or_create(category=self.background_category,
                                                                name='foo')
        self.assertTrue(created)
        self.assertEqual(background.name, 'foo')
        self.assertEqual(background.category, self.background_category)


class BackgroundCreateView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='joe', password='doe', email='joe@doe.cl')
        self.election, created = Election.objects.get_or_create(name='BarBaz',
                                                            owner=self.user,
                                                            slug='barbaz')
        self.background_category, created = BackgroundCategory.objects.get_or_create(election=self.election,
                                                                    name='FooBar')

    def test_create_background_by_user_without_login(self):
        request = self.client.get(reverse('background_create',
                                    kwargs={'background_category_pk': self.background_category.pk}))
        self.assertEquals(request.status_code, 302)

    def test_create_background_by_user_success(self):
        self.client.login(username='joe', password='doe')
        request = self.client.get(reverse('background_create',
                                    kwargs={'background_category_pk': self.background_category.pk}))

        self.assertEqual(request.status_code, 200)
        self.assertTrue('form' in request.context)
        self.assertTrue(isinstance(request.context['form'], BackgroundForm))
        self.assertTrue('background_category' in request.context)
        self.assertTrue(isinstance(request.context['background_category'], BackgroundCategory))

    def test_post_background_create_without_login(self):
        params = {'name': 'Bar'}
        response = self.client.post(reverse('background_create',
                                        kwargs={'background_category_pk': self.background_category.pk}),
                                    params)

        self.assertEquals(response.status_code, 302)

    def test_get_background_create_with_login_stranger_background_category(self):
        self.client.login(username='joe', password='doe')
        response = self.client.get(reverse('background_create',
                                    kwargs={'background_category_pk': 97965678765}))
        self.assertEquals(response.status_code, 404)

    def test_post_background_create_with_login_stranger_background_category(self):
        self.client.login(username='joe', password='doe')

        params = {'name': 'Bar'}
        response = self.client.post(reverse('background_create',
                                        kwargs={'background_category_pk': 23678543567}),
                                    params)
        self.assertEquals(response.status_code, 404)

    def test_post_background_create_logged(self):
        self.client.login(username='joe', password='doe')

        params = {'name': 'Bar'}
        response = self.client.post(reverse('background_create',
                                        kwargs={'background_category_pk': self.background_category.pk}),
                                    params,
                                    follow=True)

        self.assertEquals(response.status_code, 200)
        qs = Background.objects.filter(name='Bar')
        self.assertEquals(qs.count(), 1)
        background = qs.get()
        self.assertEqual(background.name, params['name'])
        self.assertEqual(background.category, self.background_category)

        self.assertRedirects(response, reverse('background_category_create',
                                               kwargs={'election_slug': self.election.slug}))


class BackgroundCandidateModelTest(TestCase):
    def test_background_candidate_create(self):
        self.user = User.objects.create_user(username='joe', password='doe', email='joe@doe.cl')
        self.election, created = Election.objects.get_or_create(name='BarBaz',
                                                            owner=self.user,
                                                            slug='barbaz')
        self.background_category, created = BackgroundCategory.objects.get_or_create(election=self.election,
                                                                    name='FooBar')

        self.background, created = Background.objects.get_or_create(category=self.background_category,
                                                                name='foo')

        self.candidate, created = Candidate.objects.get_or_create(name='Juan Candidato',
                                                            election=self.election)

        background_candidate, created = BackgroundCandidate.objects.get_or_create(candidate=self.candidate,
                                                                                       background=self.background,
                                                                                       value='new_value')

        self.assertEqual(background_candidate.candidate, self.candidate)
        self.assertEqual(background_candidate.background, self.background)
        self.assertEqual(background_candidate.value, 'new_value')

class BackgroundCandidateCreateViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='joe', password='doe', email='joe@doe.cl')
        self.election, created = Election.objects.get_or_create(name='BarBaz',
                                                            owner=self.user,
                                                            slug='barbaz')
        #deleting all background categories by default
        for backgroundcategory in self.election.backgroundcategory_set.all():
            backgroundcategory.delete()
            
        self.background_category, created = BackgroundCategory.objects.get_or_create(election=self.election,
                                                                    name='FooBar')

        self.background, created = Background.objects.get_or_create(category=self.background_category,
                                                                name='foo')

        self.candidate, created = Candidate.objects.get_or_create(name='Juan Candidato',
                                                            slug='juan-candidato',
                                                            election=self.election)

        self.user2 = User.objects.create_user(username='johnny', password='doe', email='johnny@doe.cl')

        self.election2, created = Election.objects.get_or_create(name='BarBaz',
                                                            owner=self.user2,
                                                            slug='barbaz')
        self.background_category2, created = BackgroundCategory.objects.get_or_create(election=self.election2,
                                                                    name='FooBar')

        self.background2, created = Background.objects.get_or_create(category=self.background_category2,
                                                                name='foo')

        self.candidate2, created = Candidate.objects.get_or_create(name='Juan Candidato',
                                                            slug='juan-candidato',
                                                            election=self.election2)

    def test_create_background_candidate_by_user_without_login(self):
        response = self.client.get(reverse('background_candidate_create',
                                    kwargs={'candidate_pk': self.candidate.pk,
                                            'background_pk': self.background.pk}))
        self.assertEquals(response.status_code, 302)

    def test_create_background_candidate_by_user_success(self):
        self.client.login(username='joe', password='doe')
        request = self.client.get(reverse('background_candidate_create',
                                    kwargs={'candidate_pk': self.candidate.pk,
                                            'background_pk': self.background.pk}))

        self.assertEqual(request.status_code, 200)
        self.assertTrue('form' in request.context)
        self.assertTrue(isinstance(request.context['form'], BackgroundCandidateForm))
        self.assertTrue('candidate' in request.context)
        self.assertTrue(isinstance(request.context['candidate'], Candidate))
        self.assertTrue('background' in request.context)
        self.assertTrue(isinstance(request.context['background'], Background))

    def test_post_background_candidate_create_without_login(self):
        params = {'value': 'Bar'}
        response = self.client.get(reverse('background_candidate_create',
                                    kwargs={'candidate_pk': self.candidate.pk,
                                            'background_pk': self.background.pk}),
                                    params)

        self.assertEquals(response.status_code, 302)

    def test_get_background_candidate_create_with_login_stranger_background_category(self):
        self.client.login(username='joe', password='doe')
        response = self.client.get(reverse('background_candidate_create',
                                    kwargs={'candidate_pk': self.candidate2.pk,
                                            'background_pk': self.background2.pk}))
        self.assertEquals(response.status_code, 404)

    def test_post_background_candidate_create_with_login_stranger_background_category(self):
        self.client.login(username='joe', password='doe')

        params = {'value': 'Bar'}
        response = self.client.get(reverse('background_candidate_create',
                                    kwargs={'candidate_pk': self.candidate2.pk,
                                            'background_pk': self.background2.pk}),
                                    params)
        self.assertEquals(response.status_code, 404)

    def test_post_background_create_logged(self):
        self.client.login(username='joe', password='doe')

        params = {'value': 'Bar'}
        response = self.client.post(reverse('background_candidate_create',
                                    kwargs={'candidate_pk': self.candidate.pk,
                                            'background_pk': self.background.pk}),
                                    params,
                                    follow=True)

        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.content, '{"value": "%s"}' % params['value'])
        
        expected_dict = {
        1: {'name': self.background_category.name,
            'backgrounds': {
                1: {'name': self.background.name, 'value': 'Bar'},
                }
            },
        }
        self.assertEquals(self.candidate.get_background, expected_dict)


class AsyncCreateBackgroundViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='joe', password='doe', email='joe@doe.cl')
        self.election, created = Election.objects.get_or_create(name='BarBaz',
                                                            owner=self.user,
                                                            slug='barbaz')
        self.background_category, created = BackgroundCategory.objects.get_or_create(election=self.election,
                                                                    name='FooBar')

        self.background, created = Background.objects.get_or_create(category=self.background_category,
                                                                name='foo')

        self.user2 = User.objects.create_user(username='johnny', password='doe', email='johnny@doe.cl')

        self.election2, created = Election.objects.get_or_create(name='BarBaz',
                                                            owner=self.user2,
                                                            slug='barbaz')
        self.background_category2, created = BackgroundCategory.objects.get_or_create(election=self.election2,
                                                                    name='FooBar')

        self.background2, created = Background.objects.get_or_create(category=self.background_category2,
                                                                name='foo')

    def test_get_async_create_background_with_login(self):
        self.client.login(username='joe', password='doe')
        response = self.client.get(reverse('async_create_background',
                                    kwargs={'background_category_pk': self.background_category.pk}))
        self.assertEqual(response.status_code, 405)

    def test_get_async_create_background_without_login(self):
        response = self.client.get(reverse('async_create_background',
                                    kwargs={'background_category_pk': self.background_category.pk}))
        self.assertEqual(response.status_code, 302)


    def test_post_async_create_background_without_login(self):
        params = {'value': 'Bar'}
        response = self.client.post(reverse('async_create_background',
                                    kwargs={'background_category_pk': self.background_category.pk}),
                                    params)

        self.assertEquals(response.status_code, 302)

    def test_post_async_create_background_with_login_stranger_background_category(self):
        self.client.login(username='joe', password='doe')

        params = {'value': 'Bar'}
        response = self.client.post(reverse('async_create_background',
                                    kwargs={'background_category_pk': self.background_category2.pk}),
                                    params)
        self.assertEquals(response.status_code, 404)

    def test_post_async_create_background_logged(self):
        self.client.login(username='joe', password='doe')

        params = {'value': 'Bar'}
        response = self.client.post(reverse('async_create_background',
                                    kwargs={'background_category_pk': self.background_category.pk}),
                                    params,
                                    follow=True)

        self.assertEquals(response.status_code, 200)

        backgrounds = self.background_category.background_set.all()
        background_names = [ background.name for background in backgrounds]

        self.assertTrue(params['value'] in background_names)
        background = self.background_category.background_set.get(name=params['value'])
        self.assertEquals(response.content, '{"pk": %d, "name": "%s"}' % (background.pk, params['value']))


class AsyncDeleteBackgroundTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='joe', password='doe', email='joe@doe.cl')
        self.election, created = Election.objects.get_or_create(name='BarBaz',
                                                            owner=self.user,
                                                            slug='barbaz')
        self.background_category, created = BackgroundCategory.objects.get_or_create(election=self.election,
                                                                    name='FooBar')

        self.background, created = Background.objects.get_or_create(category=self.background_category,
                                                                name='foo')


    def test_post_with_login(self):
        self.client.login(username='joe', password='doe')

        request = self.client.post(reverse('async_delete_background',
                                kwargs={'background_pk': self.background.pk}),
                                        {})
        self.assertEquals(request.status_code, 200)

    def test_post_without_login(self):
        request = self.client.post(reverse('async_delete_background',
                                kwargs={'background_pk': self.background.pk}),
                                        {})
        self.assertEquals(request.status_code, 302)


    def test_get_405(self):
        self.client.login(username='joe', password='doe')
        request = self.client.get(reverse('async_delete_background',
                                kwargs={'background_pk': self.background.pk}))

        self.assertEquals(request.status_code, 405)

    def test_post_with_stranger_background(self):
        user2 = User.objects.create_user(username='johnny', password='doe', email='johnny@doe.cl')

        election2, created = Election.objects.get_or_create(name='BarBaz',
                                                            owner=user2,
                                                            slug='barbaz')
        background_category2, created = BackgroundCategory.objects.get_or_create(election=election2,
                                                                    name='FooBar')

        background2, created = Background.objects.get_or_create(category=background_category2,
                                                                name='foo')

        self.client.login(username='joe', password='doe')
        request = self.client.post(reverse('async_delete_background',
                                kwargs={'background_pk': background2.pk}))

        self.assertEquals(request.status_code, 404)

    def test_post_success(self):
        self.client.login(username='joe', password='doe')
        temp_pk = self.background.pk
        request = self.client.post(reverse('async_delete_background',
                                kwargs={'background_pk': self.background.pk}),
                                        {})

        self.assertEquals(request.status_code, 200)
        self.assertEquals(request.content, '{"result": "OK"}')

        self.assertRaises(Background.DoesNotExist, Background.objects.get, pk=temp_pk)
