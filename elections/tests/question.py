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
                                    kwargs={'election_slug': self.election.slug}))
        self.assertEquals(request.status_code, 302)

    def test_create_question_by_user_success(self):
        self.client.login(username='joe', password='doe')
        request = self.client.get(reverse('question_create',
                                    kwargs={'election_slug': self.election.slug}))

        self.assertEqual(request.status_code, 200)
        self.assertTrue('form' in request.context)
        self.assertTrue(isinstance(request.context['form'], QuestionForm))
        self.assertTrue('election' in request.context)
        self.assertTrue(isinstance(request.context['election'], Election))

    def test_post_question_create_without_login(self):
        params = {'question': 'BarBaz', 'new_category': 'NewCategory', 'category': None}
        response = self.client.post(reverse('question_create',
                                    kwargs={'election_slug': self.election.slug}), params)

        self.assertEquals(response.status_code, 302)

    def test_get_question_create_with_login_stranger_election(self):
        user2 = User.objects.create_user(username='doe', password='doe', email='joe@doe.cl')
        election2 = Election.objects.create(name='BarBaz',
                                            owner=user2,
                                            slug='barbaz2')

        self.client.login(username='joe', password='doe')
        response = self.client.get(reverse('question_create',
                                    kwargs={'election_slug': election2.slug}))
        self.assertEquals(response.status_code, 404)

    def test_post_question_create_with_login_stranger_election(self):
        user2 = User.objects.create_user(username='doe', password='doe', email='joe@doe.cl')
        election2 = Election.objects.create(name='BarBaz',
                                            owner=user2,
                                            slug='barbaz2')

        self.client.login(username='joe', password='doe')

        params = {'question': 'BarBaz', 'new_category': 'NewCategory', 'category': None}
        response = self.client.post(reverse('question_create',
                                    kwargs={'election_slug': election2.slug}), params)
        self.assertEquals(response.status_code, 404)

    def test_post_question_create_logged_into_new_category(self):
        self.client.login(username='joe', password='doe')

        params = {'question': 'BarBaz', 'new_category': 'NewCategory'}
        response = self.client.post(reverse('question_create',
                                        kwargs={'election_slug': self.election.slug}),
                                    params,
                                    follow=True)

        self.assertEquals(response.status_code, 200)
        qs = Question.objects.filter(question=params['question'])
        self.assertEquals(qs.count(), 1)
        question = qs.get()
        self.assertEquals(question.question, params['question'])

        category = Category.objects.get(name=params['new_category']);
        self.assertEquals(question.category, category)

        self.assertRedirects(response, reverse('question_create',
                                               kwargs={'election_slug': self.election.slug}))

    def test_post_question_create_logged_into_existing_category(self):
        self.client.login(username='joe', password='doe')
        category, created = Category.objects.get_or_create(name='FooCat', election=self.election)

        params = {'question': 'BarBaz', 'new_category': '', 'category': category.pk}
        response = self.client.post(reverse('question_create',
                                    kwargs={'election_slug': self.election.slug}),
                                    params,
                                    follow=True)

        self.assertEquals(response.status_code, 200)
        qs = Question.objects.filter(question=params['question'])
        self.assertEquals(qs.count(), 1)
        question = qs.get()
        self.assertEquals(question.question, params['question'])

        self.assertEquals(question.category.pk, params['category'])

        self.assertRedirects(response, reverse('question_create',
                                               kwargs={'election_slug': self.election.slug}))

    def test_post_question_create_logged_into_nothing(self):
        self.client.login(username='joe', password='doe')
        category, created = Category.objects.get_or_create(name='FooCat', election=self.election)

        params = {'question': 'BarBaz'}
        response = self.client.post(reverse('question_create',
                                    kwargs={'election_slug': self.election.slug}),
                                    params)

        self.assertEquals(response.status_code, 200)
        self.assertFormError(response, 'form', 'category', 'Este campo es obligatorio.')


class AsyncDeleteQuestionTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='joe', password='doe', email='joe@doe.cl')
        self.election, created = Election.objects.get_or_create(name='BarBaz',
                                                           owner=self.user,
                                                           slug='barbaz',
                                                           description='esta es una descripcion')

        self.category = Category.objects.create(name="Bar1", slug="bar", election=self.election)
        self.question = Question.objects.create(question='Fooo', category=self.category)

    def test_post_with_login(self):
        self.client.login(username='joe', password='doe')

        request = self.client.post(reverse('async_delete_question',
                                kwargs={'question_pk': self.question.pk}),
                                        {})
        self.assertEquals(request.status_code, 200)

    def test_post_without_login(self):
        request = self.client.post(reverse('async_delete_question',
                                kwargs={'question_pk': self.question.pk}),
                                        {})
        self.assertEquals(request.status_code, 302)


    def test_get_405(self):
        self.client.login(username='joe', password='doe')
        request = self.client.get(reverse('async_delete_question',
                                kwargs={'question_pk': self.question.pk}))
        self.assertEquals(request.status_code, 405)

    def test_post_with_stranger_candidate(self):
        user2 = User.objects.create_user(username='doe', password='doe', email='joe@doe.cl')
        election2, created = Election.objects.get_or_create(name='BarBaz',
                                                           owner=user2,
                                                           slug='barbaz2',
                                                           description='esta es una descripcion')

        category2 = Category.objects.create(name="Bar1", slug="bar2", election=election2)
        question2 = Question.objects.create(question='Foo', category=category2)

        self.client.login(username='joe', password='doe')
        request = self.client.post(reverse('async_delete_question',
                                kwargs={'question_pk': question2.pk}))

        self.assertEquals(request.status_code, 404)

    def test_post_success(self):
        self.client.login(username='joe', password='doe')
        temp_pk = self.question.pk
        request = self.client.post(reverse('async_delete_question',
                                kwargs={'question_pk': self.question.pk}),
                                        {})

        self.assertEquals(request.status_code, 200)
        self.assertEquals(request.content, '{"result": "OK"}')

        self.assertRaises(Question.DoesNotExist, Question.objects.get, pk=temp_pk)
