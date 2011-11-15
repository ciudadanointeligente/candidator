"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from elections.models import Candidate, Election, Category, Question, Answer


class CandidateTest(TestCase):
    def test_name_property(self):
        candidate = Candidate()
        candidate.first_name = 'Juanito'
        candidate.last_name = 'Perez'

        expected_name = 'Juanito Perez'

        self.assertEqual(candidate.name, expected_name)


class QuestionsTest(TestCase):
    def test_create_question(self):
        user, created = User.objects.get_or_create(username='joe')
        election, created = Election.objects.get_or_create(name='BarBaz',
                                                            owner=user,
                                                            slug='barbaz')
        category, created = Category.objects.get_or_create(name='FooCat',
                                                            election=election)
        question = Question.objects.create(question='Foo', category=category)
        self.assertEquals(question.question, 'Foo')
        self.assertEquals(question.category, category)


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
        answer = Answer.objects.create(question=question, answer='Bar')
        self.assertEquals(answer.answer, 'Bar')
        self.assertEquals(answer.question, question)


class CandidateAnswerTest(TestCase):
    def setUp(self):
        #TODO: make pretty
        user, created = User.objects.get_or_create(username='joe')
        election, created = Election.objects.get_or_create(name='BarBaz',
                                                            owner=user,
                                                            slug='barbaz')
        candidate, created = Candidate.objects.get_or_create(first_name='Bar',
                                                            last_name='Baz',
                                                            election=election,
                                                            slug='barbaz')
        category, created = Category.objects.get_or_create(name='FooCat',
                                                            election=election)
        question, created = Question.objects.get_or_create(question='Foo',
                                                            category=category)
        question2, created = Question.objects.get_or_create(question='Bar',
                                                            category=category)
        answer, created = Answer.objects.get_or_create(question=question,
                                                        answer='Bar')
        answer2, created = Answer.objects.get_or_create(question=question,
                                                        answer='Bar')
        answer3, created = Answer.objects.get_or_create(question=question2,
                                                        answer='Bar')
        self.user = user
        self.election = election
        self.candidate = candidate
        self.category = category
        self.question = question
        self.question2 = question2
        self.answer = answer
        self.answer2 = answer2
        self.answer3 = answer3

    def test_associate_candidate_answer(self):
        self.candidate.associate_answer(self.answer)
        self.assertEquals(list(self.candidate.answers.all()), [self.answer])

    def test_associate_candidate_answer_same_question(self):
        self.candidate.associate_answer(self.answer)
        self.candidate.associate_answer(self.answer2)
        self.assertEquals(list(self.candidate.answers.all()), [self.answer2])

    def test_associate_candidate_second_answer(self):
        self.candidate.associate_answer(self.answer2)
        self.candidate.associate_answer(self.answer3)
        self.assertEquals(list(self.candidate.answers.all()),
                            [self.answer2, self.answer3])


class AssociateCandidatesAnswersTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='doe', 
                                                password='joe', 
                                                email='doe@joe.cl')
        self.not_user = User.objects.create_user(username='joe', 
                                                password='joe', 
                                                email='doe@joe.cl')
        self.election, created = Election.objects.get_or_create(name='BarBaz',
                                                            owner=self.user,
                                                            slug='barbaz')
        self.election2, created = Election.objects.get_or_create(name='BarBaz2',
                                                            owner=self.user,
                                                            slug='barbaz2')
        self.candidate, created = Candidate.objects.get_or_create(
                                                            first_name='Bar',
                                                            last_name='Baz',
                                                            election=self.election,
                                                            slug='barbaz')
        self.candidate2, created = Candidate.objects.get_or_create(
                                                            first_name='Bar',
                                                            last_name='Baz',
                                                            election=self.election2,
                                                            slug='barbaz')
        categories = [
            Category.objects.get_or_create(election=self.election,
                                            name='Cat1'),
            Category.objects.get_or_create(election=self.election,
                                            name='Cat2'),
        ]
        self.categories = [cat for cat, created in categories]
        category2, created = Category.objects.get_or_create(election=self.election2,
                                                     name='Cat2')
        question, created = Question.objects.get_or_create(question='Foo',
                                                            category=self.categories[0])
        question2, created = Question.objects.get_or_create(question='Foo',
                                                            category=category2)
        self.answer, created = Answer.objects.get_or_create(question=question,
                                                       answer='Bar')
        self.answer2, created = Answer.objects.get_or_create(question=question2,
                                                       answer='Bar')

    def test_get_associate_answers_to_candidate_view(self):
        request = self.client.get(reverse('associate_answer_candidate', 
                                            kwargs={'slug': self.candidate2.slug,
                                                    'election_slug': self.election.slug}))
        self.assertEquals(request.status_code, 302)

        self.client.login(username='joe', password='joe')
        request = self.client.get(reverse('associate_answer_candidate', 
                                            kwargs={'slug': self.candidate2.slug,
                                                    'election_slug': self.election.slug}))
        self.assertEquals(request.status_code, 404)

        self.client.login(username='doe', password='joe')
        request=self.client.get(reverse('associate_answer_candidate',
                                            kwargs={'slug': self.candidate.slug,
                                                    'election_slug': self.election.slug}))
        self.assertEquals(request.status_code, 200)

        self.assertTrue(request.context.has_key('candidate'))
        self.assertEquals(request.context['candidate'], self.candidate)

        self.assertTrue(request.context.has_key('categories'))
        self.assertEquals(list(request.context['categories'].all()), self.categories)
    
    def test_post_associate_answer_to_candidate_view(self):
        request = self.client.post(reverse('associate_answer_candidate', 
                                            kwargs={'slug': self.candidate2.slug,
                                                    'election_slug': self.election.slug}),
                                 {'answer': self.answer.pk})
        self.assertEquals(request.status_code, 302)

        self.client.login(username='joe', password='joe')
        request = self.client.post(reverse('associate_answer_candidate', 
                                            kwargs={'slug': self.candidate2.slug,
                                                     'election_slug': self.election.slug}),
                                 {'answer': self.answer.pk})
        self.assertEquals(request.status_code, 404)

        self.client.login(username='doe', password='joe')
        request=self.client.post(reverse('associate_answer_candidate',
                                            kwargs={'slug': self.candidate.slug,
                                                    'election_slug': self.election.slug}),
                                 {'answer': self.answer.pk})
        self.assertEquals(request.status_code, 200)
        self.assertEquals(request.content, '{"answer": %d}' % self.answer.pk)
        self.assertEquals(list(self.candidate.answers.all()), [self.answer])

        self.client.login(username='doe', password='joe')
        request=self.client.post(reverse('associate_answer_candidate',
                                         kwargs={'slug': self.candidate.slug,
                                                 'election_slug': self.election.slug}),
                                 {'answer': self.answer2.pk})
        self.assertEquals(request.status_code, 404)
