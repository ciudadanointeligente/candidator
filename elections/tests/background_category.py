from django.conf import settings
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import IntegrityError

from elections.models import Election, BackgroundCategory
from elections.forms import BackgroundCategoryForm


class BackgroundCategoryModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='joe', password='doe', email='joe@doe.cl')
        self.election, created = Election.objects.get_or_create(name='BarBaz',
                                                            owner=self.user,
                                                            slug='barbaz')

    def test_create_background_category(self):
        background_category, created = BackgroundCategory.objects.get_or_create(election=self.election,
                                                                    name='foo')
        self.assertTrue(created)
        self.assertEqual(background_category.name, 'foo')
        self.assertEqual(background_category.election, self.election)


class AsyncDeleteBackgroundCategoryTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='joe', password='doe', email='joe@doe.cl')
        self.election, created = Election.objects.get_or_create(name='BarBaz',
                                                           owner=self.user,
                                                           slug='barbaz',
                                                           description='esta es una descripcion')

        self.category = BackgroundCategory.objects.create(name="Bar1", election=self.election)

    def test_post_with_login(self):
        self.client.login(username='joe', password='doe')

        response = self.client.post(reverse('async_delete_background_category',
                                kwargs={'category_pk': self.category.pk}),
                                        {})
        self.assertEquals(response.status_code, 200)

    def test_post_without_login(self):
        response = self.client.post(reverse('async_delete_background_category',
                                kwargs={'category_pk': self.category.pk}),
                                        {})
        self.assertEquals(response.status_code, 302)


    def test_get_405(self):
        self.client.login(username='joe', password='doe')
        response = self.client.get(reverse('async_delete_background_category',
                                kwargs={'category_pk': self.category.pk}))
        self.assertEquals(response.status_code, 405)

    def test_post_with_stranger_election(self):
        user2 = User.objects.create_user(username='doe', password='doe', email='joe@doe.cl')
        election2, created = Election.objects.get_or_create(name='BarBaz',
                                                           owner=user2,
                                                           slug='barbaz2',
                                                           description='esta es una descripcion')

        category2 = BackgroundCategory.objects.create(name="Bar1", election=election2)

        self.client.login(username='joe', password='doe')
        response = self.client.post(reverse('async_delete_background_category',
                                kwargs={'category_pk': category2.pk}))

        self.assertEquals(response.status_code, 404)

    def test_post_success(self):
        self.client.login(username='joe', password='doe')
        temp_pk = self.category.pk
        request = self.client.post(reverse('async_delete_background_category',
                                kwargs={'category_pk': self.category.pk}),
                                        {})

        self.assertEquals(request.status_code, 200)
        self.assertEquals(request.content, '{"result": "OK"}')

        self.assertRaises(BackgroundCategory.DoesNotExist, BackgroundCategory.objects.get, pk=temp_pk)


class BackgroundCategoryCreateViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='joe', password='doe', email='joe@doe.cl')
        self.election, created = Election.objects.get_or_create(name='BarBaz',
                                                            owner=self.user,
                                                            slug='barbaz')

    def test_create_background_category_by_user_without_login(self):
        request = self.client.get(reverse('background_category_create',
                                    kwargs={'election_slug': self.election.slug}))
        self.assertEquals(request.status_code, 302)

    def test_create_background_category_by_user_success(self):
        self.client.login(username='joe', password='doe')
        request = self.client.get(reverse('background_category_create',
                                    kwargs={'election_slug': self.election.slug}))

        self.assertEqual(request.status_code, 200)
        self.assertTrue('form' in request.context)
        self.assertTrue(isinstance(request.context['form'], BackgroundCategoryForm))
        self.assertTrue('election' in request.context)
        self.assertTrue(isinstance(request.context['election'], Election))
    
    def test_renders_step_four_template(self):
        self.client.login(username='joe', password='doe')
        response = self.client.get(reverse('background_category_create',
                                    kwargs={'election_slug': self.election.slug}))
        
        self.assertTemplateUsed(response, 'elections/wizard/step_four.html')

    def test_post_background_category_create_without_login(self):
        params = {'name': 'Bar'}
        response = self.client.post(reverse('background_category_create',
                                        kwargs={'election_slug': self.election.slug}),
                                    params)

        self.assertEquals(response.status_code, 302)

    def test_get_background_category_create_with_login_stranger_election(self):
        self.client.login(username='joe', password='doe')
        response = self.client.get(reverse('background_category_create',
                                    kwargs={'election_slug': 'strager_election_slug'}))
        self.assertEquals(response.status_code, 404)

    def test_post_background_category_create_with_login_stranger_election(self):
        self.client.login(username='joe', password='doe')

        params = {'name': 'Bar'}
        response = self.client.post(reverse('background_category_create',
                                        kwargs={'election_slug': 'strager_election_slug'}),
                                    params)
        self.assertEquals(response.status_code, 404)

    def test_post_background_category_create_logged(self):
        self.client.login(username='joe', password='doe')

        params = {'name': 'Bar'}
        response = self.client.post(reverse('background_category_create',
                                        kwargs={'election_slug': self.election.slug}),
                                    params,
                                    follow=True)

        self.assertEquals(response.status_code, 200)
        qs = BackgroundCategory.objects.filter(name='Bar')
        self.assertEquals(qs.count(), 1)
        background_category = qs.get()
        self.assertEqual(background_category.name, params['name'])
        self.assertEqual(background_category.election, self.election)

        self.assertRedirects(response, reverse('background_category_create',
                                               kwargs={'election_slug': self.election.slug}))

class AsyncCreateBackgroundCategoryViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='joe', password='doe', email='joe@doe.cl')
        self.election, created = Election.objects.get_or_create(name='BarBaz',
                                                            owner=self.user,
                                                            slug='barbaz')
        self.background_category, created = BackgroundCategory.objects.get_or_create(election=self.election,
                                                                    name='FooBar')

        self.user2 = User.objects.create_user(username='johnny', password='doe', email='johnny@doe.cl')

        self.election2, created = Election.objects.get_or_create(name='BarBaz',
                                                            owner=self.user2,
                                                            slug='barbaz')
        self.background_category2, created = BackgroundCategory.objects.get_or_create(election=self.election2,
                                                                    name='FooBar')


    def test_get_async_create_background_category_with_login(self):
        self.client.login(username='joe', password='doe')
        response = self.client.get(reverse('async_create_background_category',
                                    kwargs={'election_pk': self.election.pk}))
        self.assertEqual(response.status_code, 405)

    def test_get_async_create_background_category_without_login(self):
        response = self.client.get(reverse('async_create_background_category',
                                    kwargs={'election_pk': self.election.pk}))
        self.assertEqual(response.status_code, 302)


    def test_post_async_create_background_category_without_login(self):
        params = {'value': 'Bar'}
        response = self.client.post(reverse('async_create_background_category',
                                    kwargs={'election_pk': self.election.pk}),
                                    params)

        self.assertEquals(response.status_code, 302)

    def test_post_async_create_background_category_with_login_stranger_election(self):
        self.client.login(username='joe', password='doe')

        params = {'value': 'Bar'}
        response = self.client.post(reverse('async_create_background_category',
                                    kwargs={'election_pk': self.election2.pk}),
                                    params)
        self.assertEquals(response.status_code, 404)

    def test_post_async_create_background_category_logged(self):
        self.client.login(username='joe', password='doe')

        params = {'value': 'Bar'}
        response = self.client.post(reverse('async_create_background_category',
                                    kwargs={'election_pk': self.election.pk}),
                                    params,
                                    follow=True)

        self.assertEquals(response.status_code, 200)

        background_categories = self.election.backgroundcategory_set.all()
        background_categories_names = [ background_category.name for background_category in background_categories]

        self.assertTrue(params['value'] in background_categories_names)

        background_category = self.election.backgroundcategory_set.get(name=params['value'])
        self.assertEquals(response.content, '{"pk": %d, "name": "%s"}' % (background_category.pk, params['value']))
