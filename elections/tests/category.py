from django.test import TestCase
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test.client import Client

from django.db import IntegrityError

from elections.models import Candidate, Election, Category, Question, Answer
from elections.forms import QuestionForm, CategoryForm, ElectionForm

class CategoryModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='joe', password='doe', email='joe@doe.cl')
        self.election, created = Election.objects.get_or_create(name='BarBaz',
                                                            owner=self.user,
                                                            slug='barbaz')

    def test_create_category(self):
        category, created = Category.objects.get_or_create(name='FooCat',
                                                            slug='foocat',
                                                            election=self.election)

        self.assertEqual(category.name, 'FooCat')
        self.assertEqual(category.slug, 'foocat')
        self.assertEqual(category.election, self.election)

    def test_create_category_with_same_slug(self):
        category, created = Category.objects.get_or_create(name='FooCat',
                                                            slug='foocat',
                                                            election=self.election)
        self.assertRaises(IntegrityError, Category.objects.create,
                          name='FooBar', slug='foocat', election=self.election)


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

        self.assertTrue('form' in request.context)
        self.assertTrue(isinstance(request.context['form'], CategoryForm))

    def test_post_category_create_with_same_slug(self):
        category = Category.objects.create(name="Bar1", slug="bar", election=self.election)

        self.client.login(username='joe', password='doe')
        params = {'name': 'Bar', 'slug': 'bar'}
        response = self.client.post(reverse('category_create',
                                        kwargs={'election_slug': self.election.slug}),
                                    params)

        self.assertEquals(response.status_code, 200)
        self.assertFormError(response, 'form', 'slug','Ya tienes una categoria con ese slug.' )


    def test_post_category_create_without_login(self):
        params = {'name': 'BarBaz', 'slug': 'barbaz'}
        response = self.client.post(reverse('category_create',
                                        kwargs={'election_slug': self.election.slug}),
                                    params)

        self.assertEquals(response.status_code, 302)

    def test_post_category_create_logged(self):
        self.client.login(username='joe', password='doe')

        params = {'name': 'BarBaz', 'slug': 'barbaz'}
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

        self.assertRedirects(response, reverse('election_detail',
                                               kwargs={'username':self.user.username, 'slug': self.election.slug}))
