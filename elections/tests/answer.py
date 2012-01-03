from django.conf import settings
from django.test import TestCase
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test.client import Client
from django.utils import simplejson

from elections.models import Candidate, Election, Category, Question, Answer
from elections.forms import AnswerForm


class AnswersTest(TestCase):
    def test_create_answer(self):
        user, created = User.objects.get_or_create(username='joe')
        election, created = Election.objects.get_or_create(name='BarBaz',
                                                            owner=user,
                                                            slug='barbaz')
        category, created = Category.objects.get_or_create(name='FooCat',
                                                            election=election)
        question, created = Question.objects.get_or_create(question='Foo',
                                                            category=category)
        answer = Answer.objects.create(question=question, caption='Bar')
        self.assertEquals(answer.caption, 'Bar')
        self.assertEquals(answer.question, question)

class AnswerCreateViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='joe', password='doe', email='joe@doe.cl')
        self.election, created = Election.objects.get_or_create(name='BarBaz',
                                                                owner=self.user,
                                                                slug='barbaz')
        self.category, created = Category.objects.get_or_create(name='FooCat',
                                                                election=self.election)
        self.question, created = Question.objects.get_or_create(question='Foo',
                                                                category=self.category)

    def test_create_answer_by_user_without_login(self):
        request = self.client.get(reverse('answer_create',
                                    kwargs={'question_pk': self.question.pk}))
        self.assertEquals(request.status_code, 302)

    def test_create_answer_by_user_success(self):
        self.client.login(username='joe', password='doe')
        request = self.client.get(reverse('answer_create',
                                    kwargs={'question_pk': self.question.pk}))

        self.assertEqual(request.status_code, 200)
        self.assertTrue('form' in request.context)
        self.assertTrue(isinstance(request.context['form'], AnswerForm))
        self.assertTrue('question' in request.context)
        self.assertTrue(isinstance(request.context['question'], Question))

    def test_post_answer_create_without_login(self):
        params = {'caption': 'Bar'}
        response = self.client.post(reverse('answer_create',
                                        kwargs={'question_pk': self.question.pk}),
                                    params)

        self.assertEquals(response.status_code, 302)

    def test_get_answer_create_with_login_stranger_background_category(self):
        self.client.login(username='joe', password='doe')
        response = self.client.get(reverse('answer_create',
                                    kwargs={'question_pk': 97965678765}))
        self.assertEquals(response.status_code, 404)

    def test_post_answer_create_with_login_stranger_background_category(self):
        self.client.login(username='joe', password='doe')

        params = {'caption': 'Bar'}
        response = self.client.post(reverse('answer_create',
                                        kwargs={'question_pk': 23678543567}),
                                    params)
        self.assertEquals(response.status_code, 404)

    def test_post_answer_create_logged(self):
        self.client.login(username='joe', password='doe')

        params = {'caption': 'Bar'}
        response = self.client.post(reverse('answer_create',
                                        kwargs={'question_pk': self.question.pk}),
                                    params,
                                    follow=True)

        self.assertEquals(response.status_code, 200)
        qs = Answer.objects.filter(caption=params['caption'])
        self.assertEquals(qs.count(), 1)
        answer = qs.get()
        self.assertEqual(answer.caption, params['caption'])
        self.assertEqual(answer.question, self.question)

        self.assertRedirects(response, reverse('category_create',
                                               kwargs={'election_slug': self.election.slug}))


class CreateAnswerWithCategoryAjax(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='joe', password='joe', email='joe@doe.cl')
        self.user2 = User.objects.create_user(username='doe', password='joe', email='dow@doe.cl')
        self.election = Election.objects.create(name='BarBaz',
            owner=self.user,
            slug='barbaz')
        self.category = Category.objects.create(name='FooCat',
            election=self.election)
        self.question = Question.objects.create(question='Foo',
            category=self.category)

        self.url = reverse('answer_create_ajax', kwargs={'question_pk': self.question.pk})

    def test_post_without_login(self):
        params = {'caption': 'Foo bar'}
        response = self.client.post(self.url, params, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 403)

    def test_post_to_not_owned_election(self):
        self.client.login(username=self.user2.username, password='joe')
        params = {'caption': 'Foo bar'}
        response = self.client.post(self.url, params, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 403)

    def test_non_existing_question(self):
        url = reverse('answer_create_ajax', kwargs={'question_pk': 0})
        self.client.login(username=self.user.username, password='joe')
        params = {'caption': 'Foo bar'}
        response = self.client.post(url, params, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 404)

    def test_post_as_election_owner(self):
        self.client.login(username=self.user.username, password='joe')
        params = {'caption': 'Foo bar'}
        response = self.client.post(self.url, params, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        answer = Answer.objects.filter(question=self.question)
        self.assertEqual(answer.count(), 1)
        answer = answer.get()
        self.assertEqual(answer.caption, params['caption'])
        self.assertEqual(simplejson.loads(response.content),
                {'pk': answer.pk, 'caption': answer.caption, 'question': self.question.pk})
        self.assertEqual(response['Content-Type'], 'application/json')

    def test_post_invalid_answer(self):
        self.client.login(username=self.user.username, password='joe')
        params = {}

        response = self.client.post(self.url, params, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)

        answer = Answer.objects.filter(question=self.question)
        self.assertEqual(answer.count(), 0)

        self.assertTrue('error' in simplejson.loads(response.content))
        self.assertEqual(response['Content-Type'], 'application/json')

    def test_get_no_ajax(self):
        self.client.login(username=self.user.username, password='joe')
        params = {'caption': 'Foo bar'}
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 400)
        response = self.client.post(self.url, params)
        self.assertEqual(response.status_code, 400)
