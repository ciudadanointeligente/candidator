from django.conf import settings
from django.test import TestCase
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test.client import Client
from django.utils import simplejson

from elections.models import Candidate, Election, Category, Question, Answer
from elections.forms import AnswerForm
from django.core.exceptions import ValidationError

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


    def test_cannot_create_empty_answer(self):
        user, created = User.objects.get_or_create(username='joe')
        election, created = Election.objects.get_or_create(name='BarBaz',
                                                            owner=user,
                                                            slug='barbaz')
        category, created = Category.objects.get_or_create(name='FooCat',
                                                            election=election)
        question, created = Question.objects.get_or_create(question='Foo',
                                                            category=category)
        answer = Answer(question=question, caption='')

        with self.assertRaises(ValidationError) as e:
            answer.full_clean()
            expected_error = {'caption':[u'This field cannot be blank.']}
            self.assertEqual(e.message_dict,expected_error)           


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

    def test_post_empty_answer(self):
        self.client.login(username=self.user.username, password='joe')
        params = {'caption': ''}

        response = self.client.post(self.url, params, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)

        answer = Answer.objects.filter(question=self.question)
        self.assertEqual(answer.count(), 0)

        self.assertTrue('error' in simplejson.loads(response.content))
        expected_error = {u'error':{u'caption':[u'This field is required.']}}
        self.assertEqual(simplejson.loads(response.content), expected_error)
        self.assertEqual(response['Content-Type'], 'application/json')


class AsyncDeleteAnswerTest(TestCase):
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
        self.answer = Answer.objects.create(caption='The first answer',
                question = self.question)

        self.url = reverse('answer_delete_ajax', kwargs={'pk':
            self.answer.pk})
        
        self.assertEqual(Answer.objects.filter(pk=self.answer.pk).count(),1)


    def test_delete_correctly_an_answer(self):
        previous_count = Answer.objects.all().count()
        self.client.login(username=self.user.username, password='joe')
        response = self.client.post(self.url)
        count_after_deletion_of_one_answer = Answer.objects.all().count()
        self.assertEqual(Answer.objects.filter(pk=self.answer.pk).count(),0)
        self.assertEqual(count_after_deletion_of_one_answer, previous_count - 1)

    def test_delete_only_by_owner(self):
        self.client.login(username=self.user2.username, password='joe')
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 404)

    def test_if_answer_does_not_exist_get_404(self):
        self.client.login(username=self.user.username, password='joe')
        unexistentid = 199999
        url = reverse('answer_delete_ajax', kwargs={'pk': \
                unexistentid})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)
