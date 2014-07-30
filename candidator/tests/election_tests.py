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
                             BackgroundCategory, Background, PersonalDataCandidate

import random
import string

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