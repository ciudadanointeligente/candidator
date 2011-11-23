from django.test import TestCase
from django.contrib.auth import authenticate, login
from django.core.urlresolvers import reverse
from django.test.client import Client

# Imported models
from elections.models import Election, Candidate, Category, Question, Answer
from django.contrib.auth.models import User

class TestMediaNaranja(TestCase):

    def setUp(self):
        user, created = User.objects.get_or_create(username='joe')
        election, created = Election.objects.get_or_create(name='BarBaz',
                                                            owner=user,
                                                            slug='barbaz')
        candidate1, created = Candidate.objects.get_or_create(first_name='Bar',
                                                            last_name='Baz',
                                                            election=election,
                                                            slug='barbaz')
        candidate2, created = Candidate.objects.get_or_create(first_name='Foo',
                                                            last_name='Foo',
                                                            election=election,
                                                            slug='foofoo')
        category1, created = Category.objects.get_or_create(name='FooCat',
                                                            election=election)
        category2, created = Category.objects.get_or_create(name='FooCat2',
                                                            election=election)
        question1, created = Question.objects.get_or_create(question='FooQuestion',
                                                            category=category1)
        question2, created = Question.objects.get_or_create(question='BarQuestion',
                                                            category=category2)
        answer1_1, created = Answer.objects.get_or_create(question=question1,
                                                        caption='BarAnswer1Question1')
        answer1_2, created = Answer.objects.get_or_create(question=question1,
                                                        caption='BarAnswer2Question2')
        answer2_1, created = Answer.objects.get_or_create(question=question2,
                                                        caption='BarAnswer1Question2')
        answer2_2, created = Answer.objects.get_or_create(question=question2,
                                                        caption='BarAnswer2Question2')

        self.user = user
        self.election = election
        self.candidate1 = candidate1
        self.candidate2 = candidate2
        self.category1 = category1
        self.category2 = category2
        self.question1 = question1
        self.question2 = question2
        self.answer1_1 = answer1_1
        self.answer1_2 = answer1_2
        self.answer2_1 = answer2_1
        self.answer2_2 = answer2_2

        candidate1.associate_answer(self.answer1_1)
        candidate1.associate_answer(self.answer1_2)
        candidate2.associate_answer(self.answer2_1)
        candidate2.associate_answer(self.answer2_2)

    def test_answers_form(self):
        answers = [self.answer1_1.pk, self.answer1_2.pk]
        importances = [5, 3]
        url = reverse("medianaranja2",kwargs={'user': 'joe', 'election':'barbaz'})
        response = self.client.post(url, answers, importances)
        expected_winner = {'candidate': (self.candidate1, 100), 'scores_by_category': [(self.category1, 100), (self.category2, 100)]}
        self.assertEqual(response.context['winner'],expected_winner)
