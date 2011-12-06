
from django.test import TestCase
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test.client import Client


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