from django.test import TestCase
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test.client import Client

from django.db import IntegrityError

from elections.models import Candidate, Election, Category, Question, Answer
from elections.forms import QuestionForm, CategoryForm, ElectionForm, CategoryUpdateForm

class CategoryModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='joe', password='doe', email='joe@doe.cl')
        self.election, created = Election.objects.get_or_create(name='BarBaz',
                                                            owner=self.user,
                                                            slug='barbaz')

    def test_create_category(self):
        category = Category.objects.create(name='FooCat', election=self.election)

        self.assertEqual(category.name, 'FooCat')
        self.assertEqual(category.slug, 'foocat')
        self.assertEqual(category.election, self.election)

    def test_create_category_with_same_name(self):
        category = Category.objects.get_or_create(name='FooCat', election=self.election)
        self.assertRaises(IntegrityError, Category.objects.create,
                          name='FooCat', election=self.election)

    def test_update_category(self):
        category = Category.objects.create(name='FooCat', election=self.election)
        new_category_name = 'FooBar'
        category.name = new_category_name
        category.save()
        updated_category = Category.objects.get(slug='foocat', election=self.election)
        self.assertEqual(updated_category.name, new_category_name)


class CategoryCreateViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='joe', password='doe', email='joe@doe.cl')
        self.election = Election.objects.create(name='BarBaz',
                                                            owner=self.user,
                                                            slug='barbaz')


    def test_create_category_by_user_without_login(self):
        request = self.client.get(reverse('category_create',
                                    kwargs={'election_slug': self.election.slug}))
        self.assertEquals(request.status_code, 302)

    def test_create_category_by_user_success(self):
        self.client.login(username='joe', password='doe')
        request = self.client.get(reverse('category_create',
                                    kwargs={'election_slug': self.election.slug}))

        self.assertEqual(request.status_code, 200)
        self.assertTrue('form' in request.context)
        self.assertTrue(isinstance(request.context['form'], CategoryForm))
        self.assertTrue('election' in request.context)
        self.assertTrue(isinstance(request.context['election'], Election))

    def test_post_category_create_with_same_slug(self):
        category = Category.objects.create(name="Bar1", election=self.election)

        self.client.login(username='joe', password='doe')
        params = {'name': 'Bar'}
        response = self.client.post(reverse('category_create',
                                        kwargs={'election_slug': self.election.slug}),
                                    params, follow=True)

        self.assertEquals(response.status_code, 200)


    def test_post_category_create_without_login(self):
        params = {'name': 'BarBaz'}
        response = self.client.post(reverse('category_create',
                                        kwargs={'election_slug': self.election.slug}),
                                    params)

        self.assertEquals(response.status_code, 302)

    def test_get_category_create_with_login_stranger_election(self):
        self.client.login(username='joe', password='doe')
        response = self.client.get(reverse('category_create',
                                    kwargs={'election_slug': 'strager_election_slug'}))
        self.assertEquals(response.status_code, 404)

    def test_post_category_create_with_login_stranger_election(self):
        self.client.login(username='joe', password='doe')

        params = {'name': 'Bar'}
        response = self.client.post(reverse('category_create',
                                        kwargs={'election_slug': 'strager_election_slug'}),
                                    params)
        self.assertEquals(response.status_code, 404)

    def test_post_category_create_logged(self):
        self.client.login(username='joe', password='doe')

        params = {'name': 'BarBaz'}
        response = self.client.post(reverse('category_create',
                                        kwargs={'election_slug': self.election.slug}),
                                    params,
                                    follow=True)

        self.assertEquals(response.status_code, 200)
        qs = Category.objects.filter(name='BarBaz')
        self.assertEquals(qs.count(), 1)
        category = qs.get()
        self.assertEquals(category.name, 'BarBaz')
        self.assertEquals(category.slug, 'barbaz')
        self.assertEquals(category.election, self.election)

        self.assertRedirects(response, reverse('category_create',
                                               kwargs={'election_slug': self.election.slug}))

class CategoryUpdateViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='joe', password='doe', email='joe@doe.cl')
        self.election = Election.objects.create(name='BarBaz',
                                                            owner=self.user,
                                                            slug='barbaz')
        self.category = Category.objects.create(name="Bar1", slug="bar", election=self.election)


    def test_update_category_by_user_without_login(self):
        request = self.client.get(reverse('category_update',
                                    kwargs={'slug': self.category.slug,
                                            'election_slug': self.election.slug}))
        self.assertEquals(request.status_code, 302)

    def test_update_category_by_user_success(self):
        self.client.login(username='joe', password='doe')
        request = self.client.get(reverse('category_update',
                                    kwargs={'slug': self.category.slug,
                                            'election_slug': self.election.slug}))

        # print request.context
        self.assertEqual(request.status_code, 200)

        self.assertTrue('form' in request.context)
        self.assertTrue(isinstance(request.context['form'], CategoryUpdateForm))
        self.assertEqual(request.context['form'].initial['name'], self.category.name)
        self.assertTrue('election' in request.context)
        self.assertTrue(isinstance(request.context['election'], Election))


    def test_post_category_update_without_login(self):
        params = {'name': 'BarBaz'}
        response = self.client.post(reverse('category_update',
                                        kwargs={'slug': self.election.slug,
                                                'election_slug': self.election.slug}),
                                    params)

        self.assertEquals(response.status_code, 302)

    def test_get_category_update_with_login_stranger_election(self):
        user2 = User.objects.create_user(username='doe', password='doe', email='joe@doe.cl')
        election2 = Election.objects.create(name='BarBaz',
                                            owner=user2,
                                            slug='barbaz2')
        category2 = Category.objects.create(name="Bar1", slug="bar2", election=election2)

        self.client.login(username='joe', password='doe')
        response = self.client.get(reverse('category_update',
                                    kwargs={'slug': category2.slug,
                                            'election_slug': election2.slug}))
        self.assertEquals(response.status_code, 404)

    def test_post_category_update_with_login_stranger_election(self):
        user2 = User.objects.create_user(username='doe', password='doe', email='joe@doe.cl')
        election2 = Election.objects.create(name='BarBaz',
                                            owner=user2,
                                            slug='barbaz2')
        category2 = Category.objects.create(name="Bar1", slug="bar2", election=election2)

        self.client.login(username='joe', password='doe')

        params = {'name': 'Bar'}
        response = self.client.post(reverse('category_update',
                                    kwargs={'slug': category2.slug,
                                            'election_slug': election2.slug}),
                                    params)
        self.assertEquals(response.status_code, 404)

    def test_post_category_update_logged(self):
        self.client.login(username='joe', password='doe')

        params = {'name': 'Bar2'}
        response = self.client.post(reverse('category_update',
                                        kwargs={'slug': self.category.slug,
                                                'election_slug': self.election.slug}),
                                    params,
                                    follow=True)

        self.assertEquals(response.status_code, 200)
        qs = Category.objects.filter(slug=self.category.slug, election=self.election)
        self.assertEquals(qs.count(), 1)
        category = qs.get()
        self.assertEquals(category.name, params['name'])

        self.assertRedirects(response, reverse('election_detail',
                                               kwargs={'username':self.user.username, 'slug': self.election.slug}))


class AsyncDeleteCategoryTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='joe', password='doe', email='joe@doe.cl')
        self.election, created = Election.objects.get_or_create(name='BarBaz',
                                                           owner=self.user,
                                                           slug='barbaz',
                                                           description='esta es una descripcion')

        self.category = Category.objects.create(name="Bar1", slug="bar", election=self.election)


    def test_post_with_login(self):
        self.client.login(username='joe', password='doe')

        request = self.client.post(reverse('async_delete_category',
                                kwargs={'category_pk': self.category.pk}),
                                        {})
        self.assertEquals(request.status_code, 200)

    def test_post_without_login(self):
        request = self.client.post(reverse('async_delete_category',
                                kwargs={'category_pk': self.category.pk}),
                                        {})
        self.assertEquals(request.status_code, 302)


    def test_get_405(self):
        self.client.login(username='joe', password='doe')
        request = self.client.get(reverse('async_delete_category',
                                kwargs={'category_pk': self.category.pk}))
        self.assertEquals(request.status_code, 405)

    def test_post_with_stranger_candidate(self):
        user2 = User.objects.create_user(username='doe', password='doe', email='joe@doe.cl')
        election2, created = Election.objects.get_or_create(name='BarBaz',
                                                           owner=user2,
                                                           slug='barbaz2',
                                                           description='esta es una descripcion')

        category2 = Category.objects.create(name="Bar1", slug="bar2", election=election2)

        self.client.login(username='joe', password='doe')
        request = self.client.post(reverse('async_delete_category',
                                kwargs={'category_pk': category2.pk}))

        self.assertEquals(request.status_code, 404)

    def test_post_success(self):
        self.client.login(username='joe', password='doe')
        temp_pk = self.category.pk
        request = self.client.post(reverse('async_delete_category',
                                kwargs={'category_pk': self.category.pk}),
                                        {})

        self.assertEquals(request.status_code, 200)
        self.assertEquals(request.content, '{"result": "OK"}')

        self.assertRaises(Category.DoesNotExist, Category.objects.get, pk=temp_pk)
