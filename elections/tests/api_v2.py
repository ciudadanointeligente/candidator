# -*- coding: utf-8 -*-
from django.test import TestCase
from django.contrib.auth.models import User
from django.db import models
from elections.models import Election, Candidate, Category, PersonalData, \
                             BackgroundCategory, Background, PersonalDataCandidate, \
                             Question, Answer, Link, BackgroundCandidate
from elections.api import BackgroundResource
from tastypie.test import ResourceTestCase, TestApiClient
from django.core import serializers
from django.core.urlresolvers import reverse
from django.utils.unittest import skip
from django.contrib.sites.models import Site

class ApiV2TestCase(ResourceTestCase):
    def setUp(self):
        super(ApiV2TestCase, self).setUp()
        self.user = User.objects.create_user(username='the_user',
                                                password='joe',
                                                email='doe@joe.cl')

        self.user2 = User.objects.create_user(username='the_user_2',
                                                password='joe_2',
                                                email='doe@joe.cl')
        # delete all elections
        Election.objects.filter(owner=self.user).delete()

        #create an election
        self.election, created = Election.objects.get_or_create(name='Election user 1',
                                                            owner=self.user,
                                                            slug='name-of-election',
                                                            published=True)

        self.election2, created = Election.objects.get_or_create(name='Election user 2',
                                                            owner=self.user2,
                                                            slug='election-user-2',
                                                            published=True)
        #delete category created by default
        self.election.category_set.all().delete()
        self.election2.category_set.all().delete()

        self.personal_data1 = PersonalData.objects.create(
            label = u"Age", 
            election = self.election)

        self.personal_data2 = PersonalData.objects.create(
            label = u"Le Profession", 
            election = self.election)

        self.candidate = Candidate.objects.create(
            name = u"Le Candidate 01",
            election = self.election
            )

        self.candidate2 = Candidate.objects.create(
            name = u"Candidate 02",
            election = self.election2
            )

        self.category1 = Category.objects.create(
            name = u"Category 01", 
            election = self.election, 
            slug = "category-01")

        self.category2 = Category.objects.create(
            name = u"Another category", 
            election = self.election, 
            slug = "another-category")

        self.question_category_1 = Question.objects.create(
            category = self.category1,
            question = u"Question 1 for category 01")

        self.question_category_2 = Question.objects.create(
            category = self.category2,
            question = u"Question 1 for category 02")

        self.answer_for_question_1 = Answer.objects.create(
            question = self.question_category_1,
            caption = u"Answer for question 1")

        self.answer_for_question_2 = Answer.objects.create(
            question = self.question_category_2,
            caption = u"Answer for question 2")

        self.age = PersonalDataCandidate.objects.create(
            personal_data = self.personal_data1, 
            candidate = self.candidate, 
            value = u"31")

        self.profession = PersonalDataCandidate.objects.create(
            personal_data = self.personal_data2, 
            candidate = self.candidate, 
            value = u"Constructor")

        self.background_category_education = BackgroundCategory.objects.create(
            name = u"Education",
            election = self.election
            )

        self.background_school = Background.objects.create(
            name = u"School",
            category = self.background_category_education
            )

        self.background_candidate = BackgroundCandidate.objects.create(
            candidate = self.candidate,
            background = self.background_school,
            value = u"Primary High School Musical"
            )

        self.api_client = TestApiClient()
        #self.data = {'format': 'json', 'username': self.user.username, 'api_key':self.user.api_key.key}

    def get_credentials(self):
        return self.create_apikey(username=self.user.username, api_key=self.user.api_key.key)

    def test_get_all_my_elections_unauthorized(self):
        response = self.api_client.get('/api/v2/election/', format='json')
        self.assertHttpUnauthorized(response)

    def test_get_elections_valid_json(self):
        response = self.api_client.get(
            '/api/v2/election/', 
            format='json', 
            authentication=self.get_credentials())
        self.assertValidJSONResponse(response)

    def test_get_my_elections(self):
        response = self.api_client.get(
            '/api/v2/election/', 
            format='json', 
            authentication=self.get_credentials())
        elections = self.deserialize(response)['objects']
        self.assertEquals(len(elections),1)
        the_election = elections[0]
        self.assertEquals(the_election['id'],self.election.id)

    #categories
    def test_get_categories_valid_json(self):
        response = self.api_client.get(
            '/api/v2/category/', 
            format='json', 
            authentication=self.get_credentials())
        self.assertValidJSONResponse(response)

    #@skip('aun no es testetado')
    def test_get_all_categories(self):
        response = self.api_client.get(
            '/api/v2/category/', 
            format='json', 
            authentication=self.get_credentials())
        categories = self.deserialize(response)['objects']
        
        self.assertEquals(len(categories),2)
        the_category = categories[0]
        self.assertEquals(the_category['id'],self.category1.id)
        self.assertEquals(the_category['name'],self.category1.name)
        the_category2 = categories[1]
        self.assertEquals(the_category2['id'],self.category2.id)
        self.assertEquals(the_category2['name'],self.category2.name)

        self.assertTrue(the_category.has_key("questions"))
        self.assertTrue(the_category["questions"][0].has_key("resource_uri"))
        self.assertEqual(the_category["questions"][0]["resource_uri"], "/api/v2/question/{0}/".format(self.question_category_1.id))

    def test_get_all_questions(self):
        response = self.api_client.get(
            '/api/v2/question/', 
            format='json', 
            authentication=self.get_credentials())

        questions = self.deserialize(response)['objects']

        self.assertEquals(len(questions),2)
        the_question = questions[0]
        self.assertTrue(the_question.has_key('question'))
        self.assertTrue(the_question.has_key('resource_uri'))
        self.assertEqual(the_question["resource_uri"], "/api/v2/question/{0}/".format(self.question_category_1.id))

    def test_get_all_answers(self):
        self.candidate.associate_answer(self.answer_for_question_1)

        response = self.api_client.get(
            '/api/v2/answer/', 
            format='json', 
            authentication=self.get_credentials())

        answers = self.deserialize(response)['objects']
        
        self.assertEquals(len(answers),2)
        the_answer = answers[0]
        self.assertTrue(the_answer.has_key('caption'))
        self.assertTrue(the_answer.has_key('resource_uri'))
        self.assertEqual(the_answer["resource_uri"], "/api/v2/answer/{0}/".format(self.answer_for_question_1.id))
        self.assertTrue(the_answer.has_key('candidates'))
        self.assertEquals(len(the_answer["candidates"]), 1)
        self.assertTrue(isinstance(the_answer["candidates"][0], unicode))

    def test_get_personal_data_candidate(self):
        response = self.api_client.get(
            '/api/v2/personal_data_candidate/', 
            format='json', 
            authentication=self.get_credentials())

        self.assertHttpOK(response)
        personal_data_candidate = self.deserialize(response)['objects']
        # print personal_data_candidate[0]
        self.assertTrue(personal_data_candidate[0].has_key('candidate'))
        self.assertTrue(personal_data_candidate[0]['candidate'])
        self.assertTrue(personal_data_candidate[0].has_key('personal_data'))
        self.assertTrue(personal_data_candidate[0]['personal_data'])
        self.assertTrue(personal_data_candidate[0].has_key('value'))

    def test_get_personal_data(self):
        response = self.api_client.get(
            '/api/v2/personal_data/', 
            format='json', 
            authentication=self.get_credentials())

        self.assertHttpOK(response)


    def test_get_backgrounds_candidate(self):
        response = self.api_client.get(
            '/api/v2/backgrounds_candidate/', 
            format='json', 
            authentication=self.get_credentials())

        self.assertHttpOK(response)
        backgrounds_candidate = self.deserialize(response)['objects']
        # print(backgrounds_candidate)
        self.assertTrue(backgrounds_candidate[0].has_key('value'))

    def test_backgrounds_candidate_detail(self):
        response = self.api_client.get(
            '/api/v2/backgrounds_candidate/{0}/'.format(self.background_candidate.id), 
            format='json', 
            authentication=self.get_credentials())

        self.assertHttpOK(response)
        the_background_candidate = self.deserialize(response)
        self.assertEqual(the_background_candidate['value'], self.background_candidate.value)


    # @skip('alguna razon')
    def test_get_all_candidates(self):
        response = self.api_client.get(
            '/api/v2/candidate/', 
            format='json', 
            authentication=self.get_credentials())

        self.assertHttpOK(response)
        candidates = self.deserialize(response)['objects']
        
        self.assertEquals(len(candidates),2)
        the_candidate = candidates[0]
        # print(the_candidate)
        self.assertTrue(the_candidate.has_key('slug'))
        self.assertFalse(the_candidate.has_key('personal_data'))
        self.assertTrue(the_candidate.has_key('personal_data_candidate'))
        self.assertTrue(isinstance(the_candidate["personal_data_candidate"][0], unicode))
        self.assertFalse(the_candidate.has_key('backgrounds'))
        self.assertTrue(the_candidate.has_key('backgrounds_candidate'))
        self.assertTrue(isinstance(the_candidate["backgrounds_candidate"][0], unicode))
        # self.assertTrue(the_candidate["personal_data"][0].has_key('label'))