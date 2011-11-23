from django.test import TestCase
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test.client import Client


from elections.models import Candidate, Election, Category, Question, Answer
from elections.forms import QuestionForm, CategoryForm, ElectionForm

class CategoryTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='joe', password='doe', email='asd@ad.cl')
        self.election, created = Election.objects.get_or_create(name='BarBaz',
                                                            owner=self.user,
                                                            slug='barbaz')


    def test_create_category(self):
        category, created = Category.objects.get_or_create(name='FooCat',
                                                            election=self.election)

        self.assertEqual(category.name, 'FooCat')
        self.assertEqual(category.election, self.election)

    def test_get_add_category_by_user_without_login(self):
        request = self.client.get(reverse('add_category',
                                            kwargs={'election_slug': self.election.slug}))
        self.assertEquals(request.status_code, 302)

    def test_get_add_category_by_user_election_not_owned_by_user(self):
        user2 , created = User.objects.get_or_create(username='doe', password='doe')
        election2, created = Election.objects.get_or_create(name='FooBar',
                                                            owner=user2,
                                                            slug='foobar')
        self.client.login(username='joe', password='doe')
        request = self.client.get(reverse('add_category',
                                           kwargs={'election_slug': election2.slug}))
        self.assertEqual(request.status_code, 404)

    def test_get_add_category_by_user_success(self):
        self.client.login(username='joe', password='doe')
        request = self.client.get(reverse('add_category',
                                            kwargs={'election_slug': self.election.slug}))
        self.assertEqual(request.status_code, 200)

        form = CategoryForm()
        self.assertTrue(request.context.has_key('form'))
        self.assertTrue(isinstance(request.context['form'], CategoryForm))

    def test_post_add_category_by_user_without_login(self):
        request = self.client.post(reverse('add_category',
                                            kwargs={'election_slug': self.election.slug}))
        self.assertEquals(request.status_code, 302)

    def test_post_add_category_by_user_election_not_owned_by_user(self):
        user2 , created = User.objects.get_or_create(username='doe', password='doe')
        election2, created = Election.objects.get_or_create(name='FooBar',
                                                            owner=user2,
                                                            slug='foobar')
        self.client.login(username='joe', password='doe')
        request = self.client.post(reverse('add_category',
                                            kwargs={'election_slug': election2.slug}))
        self.assertEqual(request.status_code, 404)

    def test_post_add_category_success(self):
        new_category_name = 'FooCat'

        self.client.login(username='joe', password='doe')
        request=self.client.post(reverse('add_category',
                                         kwargs={'election_slug': self.election.slug}),
                                 {'name': new_category_name})

        self.assertEqual(request.status_code, 200)

        self.assertTrue(request.context.has_key('form'))
        self.assertTrue(isinstance(request.context['form'], CategoryForm))
