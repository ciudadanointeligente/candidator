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
        election, created = Election.objects.get_or_create(name='election',
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
                                                            election=election,
                                                            slug='foo-cat')
        category2, created = Category.objects.get_or_create(name='FooCat2',
                                                            election=election,
                                                            slug='foo-cat-2')
        question1, created = Question.objects.get_or_create(question='FooQuestion',
                                                            category=category1)
        question2, created = Question.objects.get_or_create(question='BarQuestion',
                                                            category=category2)
        answer1_1, created = Answer.objects.get_or_create(question=question1,
                                                        caption='BarAnswer1Question1')
        answer1_2, created = Answer.objects.get_or_create(question=question2,
                                                        caption='BarAnswer1Question2')
        answer2_1, created = Answer.objects.get_or_create(question=question1,
                                                        caption='BarAnswer2uestion1')
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
    
    def test_reverse_routing_medianaranja1_correctly(self):
        url = reverse("medianaranja1",kwargs={'my_user': 'joe', 'election_slug':'barbaz'})
        expected = "/joe/barbaz/medianaranja"
        self.assertEqual(url,expected)

    def test_answers_form(self):
        answers = [self.answer1_1.pk, self.answer1_2.pk]
        importances = [5, 3]
        importances_by_category = [5, 3]
        factor_question1 = (answers[0] == self.answer1_1.pk) * importances[0]      
        factor_question2 = (answers[1] == self.answer1_2.pk) * importances[1]
        score_category1 = factor_question1 * 100.0 / importances_by_category[0]
        score_category2 = factor_question2 * 100.0 / importances_by_category[1]
        global_score = (factor_question1 + factor_question2) * 100.0 / sum(importances_by_category)
        url = reverse("medianaranja2",kwargs={'user': 'joe', 'election':'barbaz'})
        response = self.client.post(url, {'question-0': answers[0], 'question-1': answers[1], 'importance-0': importances[0], 'importance-1': importances[1]})
        expected_winner = [global_score,[score_category1,score_category1], self.candidate1]
        self.assertEqual(response.context['winner'],expected_winner)
        
    def test_get_score(self):
        answers = [[self.answer1_1], [self.answer1_2]]
        no_answers = [[], []]
        importances = [5, 3]
        get_score1 = self.candidate1.get_score(answers, importances)
        get_score2 = self.candidate2.get_score(answers, importances)
        get_score3 = self.candidate1.get_score(no_answers, importances)
        get_score4 = self.candidate2.get_score(no_answers, importances)
        get_score1_expected = (100.0, [100.0,100.0])
        get_score2_expected = (0, [0.0, 0.0])

        self.assertEqual(get_score1_expected, get_score1)
        self.assertEqual(get_score2_expected, get_score2)
        self.assertEqual(get_score2_expected, get_score3)
        self.assertEqual(get_score2_expected, get_score4)
