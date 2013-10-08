# -*- coding: utf-8 -*-


from django.test import TestCase
from elections.models import InformationSource
from django.contrib.auth.models import User
from elections.models import Candidate, Election, Category, Question, Answer
from django.db.models import Q
from django.core.exceptions import ValidationError

class InformationSourceTestCase(TestCase):
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
        self.question, created = Question.objects.get_or_create(question='Foo',
                                                            category=self.categories[0])
        question2, created = Question.objects.get_or_create(question='Foo',
                                                            category=category2)
        self.answer, created = Answer.objects.get_or_create(question=self.question,
                                                       caption='Bar')
        self.answer2, created = Answer.objects.get_or_create(question=question2,
                                                       caption='Bar')


        self.candidate.associate_answer(self.answer2)

    def test_create_an_information_source(self):

        information_source = InformationSource.objects.create(
            question=self.question, 
            candidate=self.candidate, 
            content=u'We saw this answer at el mostrador')

        self.assertTrue(information_source)
        self.assertEquals(information_source.question, self.question)
        self.assertEquals(information_source.candidate, self.candidate)
        self.assertEquals(information_source.content, u'We saw this answer at el mostrador')
