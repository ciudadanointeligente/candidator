# encoding=UTF-8
from django.core.files.base import File
import json
import os
from django.conf import settings
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import IntegrityError
from django.template import Template, Context
import json
from django.utils.translation import ugettext as _

from candidator.models import Election, Candidate, Category, PersonalData, \
                             BackgroundCategory, Background, PersonalDataCandidate, \
                             Question, Answer, BackgroundCandidate, Link, Visitor, \
                             VisitorAnswer

import random
import string
from django.core.exceptions import ValidationError 
from datetime import datetime
from django.utils.timezone import now
nownow = now()

dirname = os.path.dirname(os.path.abspath(__file__))
class ElectionModelTest(TestCase):
    def test_create_election(self):
        user, created = User.objects.get_or_create(username='joe')
        election, created = Election.objects.get_or_create(name='BarBaz',
                                                           owner=user,
                                                           slug='barbaz',
                                                           description='esta es una descripcion',
                                                           date='27 de Diciembre')
        self.assertTrue(created)
        self.assertEqual(election.name, 'BarBaz')
        self.assertEqual(election.owner, user)
        self.assertEqual(election.slug, 'barbaz')
        self.assertEqual(election.date, '27 de Diciembre')
        self.assertEqual(election.description, 'esta es una descripcion')
        self.assertEqual(election.published,False)
        self.assertEqual(election.custom_style, '')
        self.assertEqual(election.highlighted, False)
        self.assertEquals(election.__unicode__(), election.name)

    def test_create_an_election_with_utf8(self):
        user, created = User.objects.get_or_create(username='joe')
        election, created = Election.objects.get_or_create(name=u'البرلمان المغربي',
                                                           owner=user,
                                                           description=u'هذا هو وصف',
                                                           date='27 de Diciembre')
        self.assertTrue(created)
        self.assertTrue(election.slug)

    def test_create_election_with_dependent_displaying_personal_data(self):
        user, created = User.objects.get_or_create(username='joe')
        election, created = Election.objects.get_or_create(name='BarBaz',
                                                           owner=user,
                                                           slug='barbaz',
                                                           description='esta es una descripcion',
                                                           date='27 de Diciembre')


        self.assertTrue(election.should_display_empty_personal_data)

    def test_create_election_without_slug(self):
        user, created = User.objects.get_or_create(username='joe')
        election, created = Election.objects.get_or_create(name='BarBaz',
                                                           owner=user,
                                                           description='esta es una descripcion',
                                                           date='27 de Diciembre')

        self.assertTrue(created)
        self.assertEqual(election.slug,'barbaz')


    def test_create_two_elections_same_name_without_slug(self):
        user, created = User.objects.get_or_create(username='joe')
        election1, created1 = Election.objects.get_or_create(name='BarBaz',
                                                           owner=user,
                                                           description='esta es una descripcion1',
                                                           date='27 de Diciembre')

        election2, created2 = Election.objects.get_or_create(name='BarBaz',
                                                           owner=user,
                                                           description='esta es una descripcion2',
                                                           date='27 de Diciembre')

        self.assertTrue(created2)
        self.assertEqual(election2.name, 'BarBaz')
        self.assertEqual(election2.slug,'barbaz2')

        election3, created3 = Election.objects.get_or_create(name='BarBaz',
                                                           owner=user,
                                                           description='esta es una descripcion3',
                                                           date='27 de Diciembre')

        self.assertTrue(created3)
        self.assertEqual(election3.name, 'BarBaz')
        self.assertEqual(election3.slug,'barbaz3')

    def test_create_two_elections_same_name_without_slug_and_one_with_another(self):
        user, created = User.objects.get_or_create(username='joe')
        election1, created1 = Election.objects.get_or_create(name='BarBaz',
                                                           owner=user,
                                                           description='esta es una descripcion1',
                                                           date='27 de Diciembre')

        election2, created2 = Election.objects.get_or_create(name='BarBaz2',
                                                           owner=user,
                                                           description='esta es una descripcion2',
                                                           date='27 de Diciembre')

        self.assertTrue(created2)
        self.assertEqual(election2.name, 'BarBaz2')
        self.assertEqual(election2.slug,'barbaz2')

        election3, created3 = Election.objects.get_or_create(name='BarBaz',
                                                           owner=user,
                                                           description='esta es una descripcion3',
                                                           date='27 de Diciembre')

        self.assertTrue(created3)
        self.assertEqual(election3.name, 'BarBaz')
        self.assertEqual(election3.slug,'barbaz3')




    def test_edit_embeded_style_for_election(self):
        user, created = User.objects.get_or_create(username='joe')
        election, created = Election.objects.get_or_create(name='BarBaz',
                                                           owner=user,
                                                           slug='barbaz',
                                                           description='esta es una descripcion',
                                                           date='27 de Diciembre')


        election.custom_style = "body {color:red;}"
        election.save()

        the_same_election= Election.objects.get(id=election.id)
        self.assertEqual(the_same_election.custom_style, election.custom_style)  

    def test_create_two_election_by_same_user_with_same_slug(self):
        user = User.objects.create_user(username='joe', password='doe', email='joe@doe.cl')
        election = Election.objects.create(name='BarBaz',
                                                    owner=user,
                                                    slug='barbaz',
                                                    description='esta es una descripcion')

        self.assertRaises(IntegrityError, Election.objects.create,
                          name='FooBar', owner=user, slug='barbaz', description='whatever')

    def test_edit_election(self):
        user = User.objects.create_user(username='joe', password='doe', email='joe@doe.cl')
        election, created = Election.objects.get_or_create(name='BarBaz',
                                                           owner=user,
                                                           slug = 'barbaz',
                                                           description='esta es una descripcion')
        election.name = 'Barba'
        election.save()
        election2 = Election.objects.get(slug='barbaz', owner=user)
        self.assertEquals(election.name, election2.name)

    def test_create_default_data(self):
        user = User.objects.create_user(username='joe', password='doe', email='joe@doe.cl')
        election = Election.objects.create(name='Foo', owner=user, description='Lorem ipsum')
        datas = PersonalData.objects.filter(election=election)
        self.assertEqual(datas.count(), 4)
        self.assertEqual(datas.filter(label=u'Edad').count(), 1)
        self.assertEqual(datas.filter(label=u'Estado civil').count(), 1)
        self.assertEqual(datas.filter(label=u'Profesión').count(), 1)
        self.assertEqual(datas.filter(label=u'Género').count(), 1)

    def test_create_default_background_categories(self):
        user = User.objects.create_user(username='joe', password='doe', email='joe@doe.cl')
        election = Election.objects.create(name='Foo', owner=user, description='Lorem ipsum')
        categories = BackgroundCategory.objects.filter(election=election)
        self.assertEqual(categories.count(), 2)
        self.assertEqual(categories.filter(name=u'Educación').count(), 1)
        self.assertEqual(categories.filter(name=u'Antecedentes laborales').count(), 1)
        category = categories.get(name=u'Educación')
        backgrounds = Background.objects.filter(category=category)
        self.assertEqual(backgrounds.count(), 3)
        self.assertEqual(backgrounds.filter(name=u'Educación primaria').count(), 1)
        self.assertEqual(backgrounds.filter(name=u'Educación secundaria').count(), 1)
        self.assertEqual(backgrounds.filter(name=u'Educación superior').count(), 1)
        category = categories.get(name=u'Antecedentes laborales')
        backgrounds = Background.objects.filter(category=category)
        self.assertEqual(backgrounds.filter(name=u'Último trabajo').count(), 1)
        

    def test_create_default_categories_questions_and_answers(self):
        user = User.objects.create_user(username='joe', password='doe', email='joe@doe.cl')
        election = Election.objects.create(name='Foo', owner=user, description='Lorem ipsum')
        question_categories = Category.objects.filter(election=election)
        self.assertEquals(question_categories.count(),1)
        self.assertEquals(question_categories[0].name,u'Educación')
        questions = question_categories[0].question_set.all()
        self.assertEquals(questions.count(),2)
        self.assertEquals(questions[0].question,u'¿Crees que Chile debe tener una educación gratuita?')

        first_question = questions[0]
        self.assertEquals(first_question.answer_set.count(),2)
        self.assertEquals(first_question.answer_set.all()[0].caption,u"Sí")
        self.assertEquals(first_question.answer_set.all()[1].caption,u"No")
        self.assertEquals(questions[1].question,u'¿Estas de acuerdo con la desmunicipalización?')

        second_question = questions[1]
        self.assertEquals(second_question.answer_set.count(),2)
        self.assertEquals(second_question.answer_set.all()[0].caption,u"Sí")
        self.assertEquals(second_question.answer_set.all()[1].caption,u"No")


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
        self.assertEquals(answer.__unicode__(), u"Bar Q:Foo C:FooCat E:BarBaz")


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


class BackgroundModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='joe', password='doe', email='joe@doe.cl')
        self.election, created = Election.objects.get_or_create(name='BarBaz',
                                                            owner=self.user,
                                                            slug='barbaz')
        self.background_category, created = BackgroundCategory.objects.get_or_create(election=self.election,
                                                                    name='FooBar')

    def test_create_background(self):
        background, created = Background.objects.get_or_create(category=self.background_category,
                                                                name='foo')
        self.assertTrue(created)
        self.assertEqual(background.name, 'foo')
        self.assertEqual(background.category, self.background_category)
        self.assertEquals(background.__unicode__(), u"FooBar (BarBaz): foo (BarBaz)")

class BackgroundCandidateModelTest(TestCase):
    def test_background_candidate_create(self):
        self.user = User.objects.create_user(username='joe', password='doe', email='joe@doe.cl')
        self.election, created = Election.objects.get_or_create(name='BarBaz',
                                                            owner=self.user,
                                                            slug='barbaz')
        self.background_category, created = BackgroundCategory.objects.get_or_create(election=self.election,
                                                                    name='FooBar')

        self.background, created = Background.objects.get_or_create(category=self.background_category,
                                                                name='foo')

        self.candidate, created = Candidate.objects.get_or_create(name='Juan Candidato',
                                                            election=self.election)

        background_candidate, created = BackgroundCandidate.objects.get_or_create(candidate=self.candidate,
                                                                                       background=self.background,
                                                                                       value='new_value')

        self.assertEqual(background_candidate.candidate, self.candidate)
        self.assertEqual(background_candidate.background, self.background)
        self.assertEqual(background_candidate.value, 'new_value')
        self.assertEquals(background_candidate.__unicode__(), u'Juan Candidato in foo: new_value')


class BackgroundCategoryModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='joe', password='doe', email='joe@doe.cl')
        self.election, created = Election.objects.get_or_create(name='BarBaz',
                                                            owner=self.user,
                                                            slug='barbaz')

    def test_create_background_category(self):
        background_category, created = BackgroundCategory.objects.get_or_create(election=self.election,
                                                                    name='foo')
        self.assertTrue(created)
        self.assertEqual(background_category.name, 'foo')
        self.assertEqual(background_category.election, self.election)


class CandidateModelTest(TestCase):
    def setUp(self):
        self.user, created = User.objects.get_or_create(username='joe')
        self.election, created = Election.objects.get_or_create(name='BarBaz',
                                                           owner=self.user,
                                                           slug='barbaz',
                                                           description='esta es una descripcion')
        #deleting all background categories by default
        for backgroundcategory in self.election.backgroundcategory_set.all():
            backgroundcategory.delete()

    def test_create_candidate(self):
        candidate, created = Candidate.objects.get_or_create(name='Juan Candidato',
                                                            election=self.election)

        self.assertTrue(created)
        self.assertEqual(candidate.name, 'Juan Candidato')
        self.assertEqual(candidate.slug, 'juan-candidato')
        self.assertTrue(candidate.has_answered)
        self.assertEqual(candidate.election, self.election)
        self.assertEqual(candidate.__unicode__(), candidate.name)


    def test_create_candidate_with_a_non_utf8_name(self):
        candidate = Candidate.objects.create(name=u'مرشح واحد',
                                                election=self.election)
        self.assertTrue(candidate)
        self.assertEqual(candidate.name, u'مرشح واحد')
        self.assertTrue(candidate.slug)



    def test_update_candidate(self):
        candidate, created = Candidate.objects.get_or_create(name='Juan Candidato',
                                                            election=self.election)

        candidate.name = 'nuevo_nombre'
        candidate.save()

        candidate2 = Candidate.objects.get(slug='juan-candidato', election=self.election)
        self.assertEqual(candidate2.name, 'nuevo_nombre')

    def test_create_two_candidate_with_same_election_with_same_name(self):
        candidate = Candidate.objects.create(name='Juan Candidato',
                                            election=self.election)

        self.assertRaises(IntegrityError, Candidate.objects.create,
                          name='Juan Candidato', election=self.election)

    def test_create_two_candidate_with_same_slug_in_different_election(self):
        candidate = Candidate.objects.create(name='Juan Candidato',
                                            election=self.election)
        election2, created = Election.objects.get_or_create(name='BarBaz2',
                                                           owner=self.user,
                                                           description='esta es una descripcion')
        candidate2 = Candidate.objects.create(name='Juan Candidato',
                                            election=election2)
        self.assertEqual(candidate.slug, candidate2.slug)
    def test_personal_data(self):
        candidate, created = Candidate.objects.get_or_create(name='Juan Candidato',
                                                            election=self.election)

        personal_data, created = PersonalData.objects.get_or_create(election=self.election,
                                                                    label='foo')
        personal_data_candidate = PersonalDataCandidate.objects.create(candidate=candidate,
                                                                                       personal_data=personal_data,
                                                                                       value='new_value')


        self.assertEqual(personal_data_candidate.__unicode__(), u"Juan Candidato - foo")



    def test_get_personal_data(self):
        candidate, created = Candidate.objects.get_or_create(name='Juan Candidato',
                                                            election=self.election)

        personal_data, created = PersonalData.objects.get_or_create(election=self.election,
                                                                    label='foo')
        personal_data_candidate, created = PersonalDataCandidate.objects.get_or_create(candidate=candidate,
                                                                                       personal_data=personal_data,
                                                                                       value='new_value')

        personal_data_set = candidate.get_personal_data
        self.assertTrue('foo' in personal_data_set)
        self.assertEqual('new_value', personal_data_set['foo'])

    def test_get_personal_data_with_no_values(self):
        candidate, created = Candidate.objects.get_or_create(name='Juan Candidato',
            election=self.election)

        personal_data, created = PersonalData.objects.get_or_create(election=self.election,
            label='foo')

        #And I will not create the value for that personal data
        personal_data_set = candidate.get_personal_data
        self.assertTrue('foo' in personal_data_set)
        self.assertTrue(personal_data_set['foo'] is None)

    def test_get_repeated_backgrounds(self):
        candidate = Candidate.objects.create(name='Juan Candidato',
                                            election=self.election)
        background_category = BackgroundCategory.objects.create(election=self.election,
                                                                    name='FooBar')
        background_category2 = BackgroundCategory.objects.create(election=self.election,
                                                                    name='FooBar')
        backgrounds = candidate.get_background
        self.assertEqual(len(backgrounds), 2)

    def test_get_background(self):
        candidate = Candidate.objects.create(name='Juan Candidato',
                                            election=self.election)
        background_category, created = BackgroundCategory.objects.get_or_create(election=self.election,
                                                                    name='FooBar')
        background, created = Background.objects.get_or_create(category=background_category,
                                                                name='foo')
        background2, created = Background.objects.get_or_create(category=background_category,
                                                                name='foo2')
        background_category2, created = BackgroundCategory.objects.get_or_create(election=self.election,
                                                                    name='FooBar2')
        background3, created = Background.objects.get_or_create(category=background_category2,
                                                                name='foo3')


        background_data_candidate, created = BackgroundCandidate.objects.get_or_create(candidate=candidate,
                                                                                  background=background,
                                                                                  value="BarFoo")
        background_data_candidate2, created  = BackgroundCandidate.objects.get_or_create(candidate=candidate,
                                                                                  background=background2,
                                                                                  value="BarFoo2")
        background_data_candidate3, created  = BackgroundCandidate.objects.get_or_create(candidate=candidate,
                                                                                  background=background3,
                                                                                  value="BarFoo3")

        expected_dict = {
        1: {'name':'FooBar',
            'backgrounds': {
                1: {'name': 'foo', 'value': 'BarFoo'}, 
                2: {'name':'foo2', 'value': 'BarFoo2'}
                }
            },
        2: {'name': 'FooBar2',
            'backgrounds': {
                1: {'name':'foo3', 'value':'BarFoo3'}
                }
            }
        }
        self.assertEqual(candidate.get_background, expected_dict)
        
    def test_get_what_the_candidate_answered_when_has_been_answered(self):
        candidate = Candidate.objects.create(name='Juan Candidato',
                                            election=self.election)
        background_category, created = BackgroundCategory.objects.get_or_create(election=self.election,
                                                                    name='FooBar')
        background, created = Background.objects.get_or_create(category=background_category,
                                                                name='foo')
        background_data_candidate, created = BackgroundCandidate.objects.get_or_create\
                                            (candidate=candidate,\
                                            background=background,\
                                            value="BarFoo")
        what_the_candidate_answered = candidate.get_answer_for_background(background)
        expected_answer = "BarFoo"
        self.assertEqual(what_the_candidate_answered, expected_answer)
        
    def test_get_backgrounds_even_if_they_havent_been_answered_by_the_candidate(self):
        candidate = Candidate.objects.create(name='Juan Candidato',
                                            election=self.election)
        background_category, created = BackgroundCategory.objects.get_or_create(election=self.election,
                                                                    name='FooBar')
        background, created = Background.objects.get_or_create(category=background_category,
                                                                name='foo')
        background2, created = Background.objects.get_or_create(category=background_category,
                                                                name='foo2')
        background_category2, created = BackgroundCategory.objects.get_or_create(election=self.election,
                                                                    name='FooBar2')
        background3, created = Background.objects.get_or_create(category=background_category2,
                                                                name='foo3')
                                                                                 
        expected_dict = {
        1: {'name':'FooBar',
            'backgrounds': {
                1: {'name': 'foo', 'value': None}, 
                2: {'name':'foo2', 'value': None}
                }
            },
        2: {'name': 'FooBar2',
            'backgrounds': {
                1: {'name':'foo3', 'value':None}
                }
            }
        }

        self.assertEqual(candidate.get_background, expected_dict)
        
        

    def test_add_personal_data(self):
        candidate, created = Candidate.objects.get_or_create(name='Juan Candidato',
                                                            election=self.election)

        personal_data, created = PersonalData.objects.get_or_create(election=self.election,
                                                                    label='foo')
        personal_data2, created = PersonalData.objects.get_or_create(election=self.election,
                                                                    label='foo2')

        candidate.add_personal_data(personal_data, 'new_value')
        self.assertTrue('foo' in candidate.get_personal_data)
        self.assertEqual('new_value',candidate.get_personal_data['foo'])

        candidate.add_personal_data(personal_data, 'new_value2')

        self.assertTrue('foo' in candidate.get_personal_data)
        self.assertEqual('new_value2', candidate.get_personal_data['foo'])

        candidate.add_personal_data(personal_data2, 'new_value3')

        self.assertTrue('foo' in candidate.get_personal_data)
        self.assertEqual('new_value2', candidate.get_personal_data['foo'])
        self.assertTrue('foo2' in candidate.get_personal_data)
        self.assertEqual('new_value3', candidate.get_personal_data['foo2'])


    def test_add_background(self):
        candidate = Candidate.objects.create(name='Juan Candidato',
                                            election=self.election)
        background_category, created = BackgroundCategory.objects.get_or_create(election=self.election,
                                                                    name='FooBar')
        background, created = Background.objects.get_or_create(category=background_category,
                                                                name='foo')

        background2, created = Background.objects.get_or_create(category=background_category,
                                                                name='foo2')

        candidate.add_background(background, 'BarFoo')

        expected_dict = {
        1: {'name':'FooBar',
            'backgrounds': {
                1: {'name': 'foo', 'value': 'BarFoo'}, 
                2: {'name':'foo2', 'value': None}
                }
            },
        }
        self.assertEqual(candidate.get_background, expected_dict)

        candidate.add_background(background, 'BarFoo2')
        expected_dict = {
        1: {'name':'FooBar',
            'backgrounds': {
                1: {'name': 'foo', 'value': 'BarFoo2'}, 
                2: {'name':'foo2', 'value': None}
                }
            }
        }
        self.assertEqual(candidate.get_background, expected_dict)

        candidate.add_background(background2, 'BarFoo3')
        expected_dict = {
        1: {'name':'FooBar',
            'backgrounds': {
                1: {'name': 'foo', 'value': 'BarFoo2'}, 
                2: {'name':'foo2', 'value': 'BarFoo3'}
                }
            },
        }
        self.assertEqual(candidate.get_background, expected_dict)

    def test_get_questions_by_category(self):
        candidate = Candidate.objects.create(name='Juan Candidato',
                                            election=self.election)
        category, created = Category.objects.get_or_create(name='FooCat',
                                                            election=self.election,
                                                            slug='foo-cat')
        question, created = Question.objects.get_or_create(question='FooQuestion',
                                                            category=category)
        real_questions = candidate.get_questions_by_category(category)
        expected_questions = [question]
        self.assertEqual(real_questions[0].question, expected_questions[0].question)
        self.assertEqual(real_questions[0].category, expected_questions[0].category)

    def test_get_answer_by_question(self):
        candidate = Candidate.objects.create(name='Juan Candidato',
                                            election=self.election)
        category, created = Category.objects.get_or_create(name='FooCat',
                                                            election=self.election,
                                                            slug='foo-cat')
        question, created = Question.objects.get_or_create(question='FooQuestion',
                                                            category=category)
        another_question, created = Question.objects.get_or_create(question='BarQuestion',
                                                            category=category)
        answer, created = Answer.objects.get_or_create(question=question,
                                                        caption='BarAnswer1Question')
        candidate.associate_answer(answer)
        real_answer_1 = candidate.get_answer_by_question(question)
        real_answer_2 = candidate.get_answer_by_question(another_question)
        expected_answer_1 = answer
        expected_answer_2 = "no answer"
        self.assertEqual(real_answer_1, expected_answer_1)
        self.assertEqual(real_answer_2, expected_answer_2)

    def test_get_all_answers_by_category(self):
        candidate = Candidate.objects.create(name='Juan Candidato',
                                            election=self.election)
        category, created = Category.objects.get_or_create(name='FooCat',
                                                            election=self.election,
                                                            slug='foo-cat')
        question1, created = Question.objects.get_or_create(question='FooQuestion1',
                                                            category=category)
        question2, created = Question.objects.get_or_create(question='FooQuestion2',
                                                            category=category)
        answer1, created = Answer.objects.get_or_create(question=question1,
                                                        caption='BarAnswerQuestion1')
        answer2, created = Answer.objects.get_or_create(question=question2,
                                                        caption='BarAnswerQuestion2')
        candidate.associate_answer(answer1)
        candidate.associate_answer(answer2)
        expected_result = [(question1, answer1), (question2, answer2)]
        real_result = candidate.get_all_answers_by_category(category)

        self.assertEqual(real_result, expected_result)

    def test_get_answers_two_candidates(self):
        candidate1 = Candidate.objects.create(name='Juan Candidato',
                                            election=self.election)
        candidate2 = Candidate.objects.create(name='Mario Candidato',
                                            election=self.election)
        category, created = Category.objects.get_or_create(name='FooCat',
                                                            election=self.election,
                                                            slug='foo-cat')
        question, created = Question.objects.get_or_create(question='FooQuestion',
                                                            category=category)
        answer1, created = Answer.objects.get_or_create(question=question,
                                                        caption='BarAnswer1Question')
        answer2, created = Answer.objects.get_or_create(question=question,
                                                        caption='BarAnswer2Question')
        candidate1.associate_answer(answer1)
        candidate2.associate_answer(answer2)
        real_result = [(question, answer1, answer2)]
        expected_result = candidate1.get_answers_two_candidates(candidate2, category)
        self.assertEqual(real_result, expected_result)


class CategoryModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='joe', password='doe', email='joe@doe.cl')
        self.election, created = Election.objects.get_or_create(name='BarBaz',
                                                            owner=self.user,
                                                            slug='barbaz')

    def test_create_category(self):
        category = Category.objects.create(name='FooCat', election=self.election)

        self.assertEqual(category.name, 'FooCat')
        self.assertEqual(category.slug, 'foocat')
        self.assertEqual(category.election, self.election)
        self.assertEqual(category.order, 1)
        self.assertEqual(category.__unicode__(), u"FooCat")

    def test_create_category_with_same_name(self):
        category = Category.objects.get_or_create(name='FooCat', election=self.election)
        self.assertRaises(IntegrityError, Category.objects.create,
                          name='FooCat', election=self.election)

    def test_update_category(self):
        category = Category.objects.create(name='FooCat', election=self.election)
        new_category_name = 'FooBar'
        category.name = new_category_name
        category.save()
        updated_category = Category.objects.get(slug='foocat', election=self.election)
        self.assertEqual(updated_category.name, new_category_name)

    def test_category_name_cannot_be_empty(self):
        category = Category.objects.create(name='', election=self.election)
        try:
            category.full_clean()
            self.fail('The category name can be empty')
        except ValidationError:
            pass

    def test_ordered_categories(self):
        [category.delete() for category in self.election.category_set.all()]
        category2 = Category.objects.create(name=u'seccond election', election=self.election, order=2)
        category1 = Category.objects.create(name=u'first election', election=self.election, order=1)

        categories = Category.objects.filter(election=self.election)
        self.assertEquals(categories[0].name, u'first election')
        self.assertEquals(categories[1].name, u'seccond election')

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
        self.assertEquals(question.__unicode__(), u"Foo - FooCat (BarBaz)")


    def test_cannot_create_empty_question(self):
        user, created = User.objects.get_or_create(username='joe')
        election, created = Election.objects.get_or_create(name='BarBaz',
                                                            owner=user,
                                                            slug='barbaz')
        category, created = Category.objects.get_or_create(name='FooCat',
                                                           slug='foocat',
                                                            election=election)
        question = Question(question='', category=category)

        with self.assertRaises(ValidationError) as e:
            question.full_clean()
            expected_error = {'question':[u'This field cannot be blank.']}
            self.assertEqual(e.message_dict,expected_error)


class TestMediaNaranja(TestCase):

    def setUp(self):
        user, created = User.objects.get_or_create(username='joe')
        election, created = Election.objects.get_or_create(name='election',
                                                            owner=user,
                                                            slug='barbaz')
        #deleting default categories
        for category in election.category_set.all():
            category.delete()
        #end of deleting default categories
        candidate1 = Candidate.objects.create(name='BarBaz', election=election)
        candidate2 = Candidate.objects.create(name='FooFoo', election=election)
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
    
    def test_get_number_of_questions_by_category(self):
        number_by_questions_expected = [1,1]
        number_by_questions = self.candidate1.get_number_of_questions_by_category()
        number_by_questions2 = self.candidate2.get_number_of_questions_by_category()
        self.assertEqual(number_by_questions_expected, number_by_questions)
        self.assertEqual(number_by_questions_expected, number_by_questions2)

    def test_get_importances_by_category(self):
        importances = [5, 3]
        importances_by_category_expected = [5,3]
        importances_by_category = self.candidate1.get_importances_by_category(importances)
        importances_by_category2 = self.candidate2.get_importances_by_category(importances)
        self.assertEqual(importances_by_category_expected, importances_by_category)
        self.assertEqual(importances_by_category_expected, importances_by_category2)

    def test_get_sum_importances_by_category(self):
        answers = [[self.answer1_1], [self.answer1_2]]
        importances = [5, 3]
        sum_importances_by_category_expected = [5,3]
        sum_importances_by_category_expected2 = [0,0]
        sum_importances_by_category = self.candidate1.get_sum_importances_by_category(answers, importances)
        sum_importances_by_category2 = self.candidate2.get_sum_importances_by_category(answers, importances)
        self.assertEqual(sum_importances_by_category_expected, sum_importances_by_category)
        self.assertEqual(sum_importances_by_category_expected2, sum_importances_by_category2)

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

    def test_get_score_with_zero_importances(self):
        answers = [[self.answer1_1], [self.answer1_2]]
        importances = [0, 0]

        get_score = self.candidate1.get_score(answers, importances)
        expected_score = (0, [0.0, 0.0])

        self.assertEqual(expected_score,get_score)


class TestMediaNaranjaWithNoCategories(TestCase):


    def setUp(self):
        user, created = User.objects.get_or_create(username='joe')
        election, created = Election.objects.get_or_create(name='election',
            owner=user,
            slug='barbaz')
        #deleting default categories
        for category in election.category_set.all():
            category.delete()
        #end of deleting default categories
        self.candidate1 = Candidate.objects.create(name='BarBaz', election=election)
        self.candidate2 = Candidate.objects.create(name='FooFoo', election=election)



    def test_get_score_without_categories(self):
        answers = []
        importances = []
        get_score = self.candidate1.get_score(answers,importances)
        expected_score = (0,[])
        self.assertEqual(expected_score,get_score)


class LinkModelTest(TestCase):
    def setUp(self):
        self.user, created = User.objects.get_or_create(username='joe')
        self.election, created = Election.objects.get_or_create(name='BarBaz',
                                                           owner=self.user,
                                                           slug='barbaz',
                                                           description='esta es una descripcion')

        self.candidate, created = Candidate.objects.get_or_create(name='Juan Candidato',
                                                                  election=self.election)

    def test_create_link(self):
        link, created = Link.objects.get_or_create(
                                                    name='Google',
                                                    url='http://www.google.com',
                                                    candidate=self.candidate)
        self.assertTrue(created)
        self.assertEqual(link.name, 'Google')
        self.assertEqual(link.url, 'http://www.google.com')
        self.assertEqual(link.candidate, self.candidate)
        self.assertEqual(link.__unicode__(), u"Google (http://www.google.com)")

    def test_does_not_create_an_empty_link(self):
        link = Link(name="", url="", candidate=self.candidate)
        try:
            link.full_clean()
            self.fail('The link name can not be empty')
        except ValidationError as e:
            expected_error = {'name':[u'This field cannot be blank.'], 'url':[u'This field cannot be blank.']}
            self.assertEqual(e.message_dict,expected_error)

        
        link = Link(name="", url="http://www.google.com", candidate=self.candidate)
        try:
            link.full_clean()
            self.fail('The link name can not be empty')
        except ValidationError as e:
            expected_error = {'name':[u'This field cannot be blank.']}
            self.assertEqual(e.message_dict,expected_error)


        link = Link(name="Twitter", url="", candidate=self.candidate)
        try:
            link.full_clean()
            self.fail('The url not can be empty')
        except ValidationError as e:
            expected_error = {'url':[u'This field cannot be blank.']}
            self.assertEqual(e.message_dict,expected_error)

    def test_http_prefixes(self):
        link, created = Link.objects.get_or_create(
                                                    name = 'Twitter',
                                                    url = 'www.twitter.com',
                                                    candidate = self.candidate)

        link2, created = Link.objects.get_or_create(
                                                    name = 'Twitter',
                                                    url = 'http://www.twitter.com',
                                                    candidate = self.candidate)
        self.assertTrue(created)
        self.assertEqual(link.http_prefix, 'http://www.twitter.com')
        self.assertEqual(link2.http_prefix, 'http://www.twitter.com')

    def test_css_classess(self):
        link, created = Link.objects.get_or_create(
                                                    name='Facebook',
                                                    url='http://www.facebook.com',
                                                    candidate=self.candidate)
        self.assertTrue(created)
        self.assertEqual(link.css_class, 'facebook')

        link, created = Link.objects.get_or_create(
                                                    name='Twitter',
                                                    url='http://www.twitter.com',
                                                    candidate=self.candidate)
        self.assertTrue(created)
        self.assertEqual(link.css_class, 'twitter')


class PersonalDataModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='joe', password='doe', email='joe@doe.cl')
        self.election, created = Election.objects.get_or_create(name='BarBaz',
                                                            owner=self.user,
                                                            slug='barbaz')

    def test_create_personal_data(self):
        personal_data, created = PersonalData.objects.get_or_create(election=self.election,
                                                                    label='foo')
        self.assertTrue(created)
        self.assertEqual(personal_data.label, 'foo')
        self.assertEqual(personal_data.election, self.election)
        self.assertEqual(personal_data.__unicode__(), u"foo (BarBaz)")

class VisitorTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='joe', password='doe', email='joe@doe.cl')
        self.election, created = Election.objects.get_or_create(name='BarBaz',
                                                            owner=self.user,
                                                            slug='barbaz')


    def test_create_model(self):
        
        visitor = Visitor.objects.create(
            election=self.election,
            election_url="http://google.com",
            datestamp=nownow)

        self.assertEquals(visitor.election, self.election)
        self.assertEquals(visitor.election_url, 'http://google.com')
        self.assertTrue(visitor.datestamp)
        self.assertIsInstance(visitor.datestamp, datetime)


        self.assertEquals(visitor.__unicode__(), unicode(visitor.datestamp) + u" - http://google.com")



class VisitorAnswerTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='joe', password='doe', email='joe@doe.cl')
        self.election, created = Election.objects.get_or_create(name='BarBaz',
                                                            owner=self.user,
                                                            slug='barbaz')
        self.category, created = Category.objects.get_or_create(name='FooCat',
                                                            election=self.election)
        self.question, created = Question.objects.get_or_create(question='Foo',
                                                            category=self.category)
        self.answer = Answer.objects.create(question=self.question, caption='Answer')

        self.visitor = visitor = Visitor.objects.create(
            election=self.election,
            election_url="http://google.com",
            datestamp=nownow)


    def test_instanciate_a_visitor_answer(self):
        visitor_answer = VisitorAnswer.objects.create(
            visitor=self.visitor,
            answer=self.answer,
            answer_importance=1
            )

        self.assertEquals(visitor_answer.visitor, self.visitor)
        self.assertEquals(visitor_answer.question_text, u"Foo")
        self.assertEquals(visitor_answer.question_category_text, u"FooCat")
        self.assertEquals(visitor_answer.answer_text, u"Answer")
        self.assertEquals(visitor_answer.answer_importance, 1)