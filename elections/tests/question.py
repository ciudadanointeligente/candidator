from django.test import TestCase
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test.client import Client


from elections.models import Election, Category, Question
from elections.forms import QuestionForm


class QuestionModelTest(TestCase):
    def test_create_question(self):
        user, created = User.objects.get_or_create(username='joe')
        election, created = Election.objects.get_or_create(name='BarBaz',
                                                            owner=user,
                                                            slug='barbaz')
        category, created = Category.objects.get_or_create(name='FooCat',
                                                           slug='foocat',
                                                            election=election)
        question = Question.objects.create(question='Foo', category=category)
        self.assertEquals(question.question, 'Foo')
        self.assertEquals(question.category, category)

class QuestionCreateViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='joe', password='doe', email='joe@doe.cl')
        self.election = Election.objects.create(name='BarBaz',
                                                owner=self.user,
                                                slug='barbaz')
        self.category, created = Category.objects.get_or_create(name='FooCat',
                                                                slug='foocat',
                                                                election=self.election)


    def test_create_question_by_user_without_login(self):
        request = self.client.get(reverse('question_create',
                                    kwargs={'category_pk': self.category.pk}))
        self.assertEquals(request.status_code, 302)

    def test_create_question_by_user_success(self):
        self.client.login(username='joe', password='doe')
        request = self.client.get(reverse('question_create',
                                    kwargs={'category_pk': self.category.pk}))

        self.assertEqual(request.status_code, 200)
        self.assertTrue('form' in request.context)
        self.assertTrue(isinstance(request.context['form'], QuestionForm))
        self.assertTrue('category' in request.context)
        self.assertTrue(isinstance(request.context['category'], Category))

    def test_post_question_create_without_login(self):
        params = {'question': 'BarBaz'}
        response = self.client.post(reverse('question_create',
                                        kwargs={'category_pk': self.category.pk}),
                                    params)

        self.assertEquals(response.status_code, 302)

    def test_get_question_create_with_login_stranger_category(self):
        user2 = User.objects.create_user(username='doe', password='doe', email='joe@doe.cl')
        election2 = Election.objects.create(name='BarBaz',
                                            owner=user2,
                                            slug='barbaz')
        category2, created = Category.objects.get_or_create(name='FooCat',
                                                            slug='foocat',
                                                            election=election2)

        self.client.login(username='joe', password='doe')
        response = self.client.get(reverse('question_create',
                                    kwargs={'category_pk': category2.pk}))
        self.assertEquals(response.status_code, 404)

    def test_post_question_create_with_login_stranger_category(self):
        user2 = User.objects.create_user(username='doe', password='doe', email='joe@doe.cl')
        election2 = Election.objects.create(name='BarBaz',
                                            owner=user2,
                                            slug='barbaz')
        category2, created = Category.objects.get_or_create(name='FooCat',
                                                            slug='foocat',
                                                            election=election2)

        self.client.login(username='joe', password='doe')

        params = {'question': 'Bar'}
        response = self.client.post(reverse('question_create',
                                        kwargs={'category_pk': category2.pk}),
                                    params)
        self.assertEquals(response.status_code, 404)

    def test_post_question_create_logged(self):
        self.client.login(username='joe', password='doe')

        params = {'question': 'Bar'}
        response = self.client.post(reverse('question_create',
                                        kwargs={'category_pk': self.category.pk}),
                                    params,
                                    follow=True)

        self.assertEquals(response.status_code, 200)
        qs = Question.objects.filter(question=params['question'])
        self.assertEquals(qs.count(), 1)
        question = qs.get()
        self.assertEquals(question.question, params['question'])
        self.assertEquals(question.category, self.category)

        self.assertRedirects(response, reverse('category_create',
                                               kwargs={'election_slug': self.election.slug}))
