# encoding=UTF-8
from django.test import TestCase
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test.client import Client
from django.template import Template, Context
from django.utils.translation import ugettext as _

from elections.models import Candidate, Election, Category, Question, Answer
from elections.forms import CategoryForm, ElectionForm


class CandidateTagsTest(TestCase):
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
        self.candidate = Candidate.objects.create(name='Bar Baz',
                                                            election=self.election)
        self.candidate2, created = Candidate.objects.get_or_create(
                                                            name='Bar Baz',
                                                            election=self.election2)
        categories = [
            Category.objects.get_or_create(election=self.election,
                                            name='Cat1',
                                            slug='cat1'),
            Category.objects.get_or_create(election=self.election,
                                            name='Cat2',
                                            slug='cat2'),
        ]
        self.categories = [cat for cat, created in categories]
        category2, created = Category.objects.get_or_create(election=self.election2,
                                                     name='Cat2')
        question, created = Question.objects.get_or_create(question='Foo',
                                                            category=self.categories[0])
        question2, created = Question.objects.get_or_create(question='Foo',
                                                            category=category2)
        self.answer, created = Answer.objects.get_or_create(question=question,
                                                       caption='Bar')
        self.answer2, created = Answer.objects.get_or_create(question=question2,
                                                       caption='Bar')

    def test_answer_for_candidate_and_question(self):
        self.candidate.associate_answer(self.answer)
        template = Template('{% load election_tags %}{% answer_for_candidate_and_question candidate question %}')
        context = Context({"candidate": self.candidate, "question": self.answer.question})
        self.assertEqual(template.render(context), self.answer.caption)

    def test_answer_for_candidate_and_question_no_caption(self):
        template = Template('{% load election_tags %}{% answer_for_candidate_and_question candidate question %}')
        context = Context({"candidate": self.candidate, "question": self.answer.question})
        self.assertEqual(template.render(context), _(u'Aún no hay respuesta'))


        

class CandidateAnswerTest(TestCase):
    def setUp(self):
        #TODO: make pretty
        user, created = User.objects.get_or_create(username='joe')
        election, created = Election.objects.get_or_create(name='BarBaz',
                                                            owner=user,
                                                            slug='barbaz')
        candidate, created = Candidate.objects.get_or_create(name='Bar Baz',
                                                            election=election)
        category, created = Category.objects.get_or_create(name='FooCat',
                                                            election=election)
        question, created = Question.objects.get_or_create(question='Foo',
                                                            category=category)
        question2, created = Question.objects.get_or_create(question='Bar',
                                                            category=category)
        answer, created = Answer.objects.get_or_create(question=question,
                                                        caption='Bar')
        answer2, created = Answer.objects.get_or_create(question=question,
                                                        caption='Bar')
        answer3, created = Answer.objects.get_or_create(question=question2,
                                                        caption='Bar')
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
        #deleting default categories
        for category in self.election.category_set.all():
            category.delete()
        for category in self.election2.category_set.all():
            category.delete()
        #end of deleting default categories
        self.candidate = Candidate.objects.create(name='Bar Baz',
                                                            election=self.election)
        self.candidate2, created = Candidate.objects.get_or_create(
                                                            name='Bar Baz',
                                                            election=self.election2)
        categories = [
            Category.objects.get_or_create(election=self.election,
                                            name='Cat1',
                                            slug='cat1'),
            Category.objects.get_or_create(election=self.election,
                                            name='Cat2',
                                            slug='cat2'),
        ]
        self.categories = [cat for cat, created in categories]
        category2, created = Category.objects.get_or_create(election=self.election2,
                                                     name='Cat2')
        question, created = Question.objects.get_or_create(question='Foo',
                                                            category=self.categories[0])
        question2, created = Question.objects.get_or_create(question='Foo',
                                                            category=category2)
        self.answer, created = Answer.objects.get_or_create(question=question,
                                                       caption='Bar')
        self.answer2, created = Answer.objects.get_or_create(question=question2,
                                                       caption='Bar')

    def test_get_associate_answers_to_candidate_view(self):
        # GET without login
        request = self.client.get(reverse('associate_answer_candidate',
                                            kwargs={'candidate_slug': self.candidate2.slug,
                                                    'election_slug': self.election.slug}))
        self.assertEquals(request.status_code, 302)

        # GET of non existing candidate/user pair associated with the logged in user
        self.client.login(username='joe', password='joe')
        request = self.client.get(reverse('associate_answer_candidate',
                                            kwargs={'candidate_slug': self.candidate2.slug,
                                                    'election_slug': self.election.slug}))
        self.assertEquals(request.status_code, 404)

        # GET of existing candidate/user pair associated with the logged in user
        self.client.login(username='doe', password='joe')
        request=self.client.get(reverse('associate_answer_candidate',
                                            kwargs={'candidate_slug': self.candidate.slug,
                                                    'election_slug': self.election.slug}))
        self.assertEquals(request.status_code, 200)

        self.assertTrue('candidate' in request.context)
        self.assertEquals(request.context['candidate'], self.candidate)

        self.assertTrue('categories' in request.context)
        self.assertEquals(list(request.context['categories'].all()), self.categories)

    def test_post_associate_answer_to_candidate_view(self):
        request = self.client.post(reverse('associate_answer_candidate',
                                            kwargs={'candidate_slug': self.candidate2.slug,
                                                    'election_slug': self.election.slug}),
                                 {'answer': self.answer.pk})
        self.assertEquals(request.status_code, 302)

        self.client.login(username='joe', password='joe')
        request = self.client.post(reverse('associate_answer_candidate',
                                            kwargs={'candidate_slug': self.candidate2.slug,
                                                     'election_slug': self.election.slug}),
                                 {'answer': self.answer.pk})
        self.assertEquals(request.status_code, 404)

        self.client.login(username='doe', password='joe')
        request=self.client.post(reverse('associate_answer_candidate',
                                            kwargs={'candidate_slug': self.candidate.slug,
                                                    'election_slug': self.election.slug}),
                                 {'answer': self.answer.pk})
        self.assertEquals(request.status_code, 200)
        self.assertEquals(request.content, '{"answer": %d}' % self.answer.pk)
        self.assertEquals(list(self.candidate.answers.all()), [self.answer])

        self.client.login(username='doe', password='joe')
        request=self.client.post(reverse('associate_answer_candidate',
                                         kwargs={'candidate_slug': self.candidate.slug,
                                                 'election_slug': self.election.slug}),
                                 {'answer': self.answer2.pk})
        self.assertEquals(request.status_code, 404)


