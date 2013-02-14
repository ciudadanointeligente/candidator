# -*- coding: utf-8 -*-
from django.test import TestCase
from django.contrib.auth.models import User
from django.db import models
from tastypie.models import ApiKey
from elections.models import Election, Candidate, Category, PersonalData, \
                             BackgroundCategory, Background, PersonalDataCandidate, \
                             Question
from tastypie.test import ResourceTestCase, TestApiClient
from django.core.urlresolvers import reverse

class ApiTestCase(ResourceTestCase):
    
    def setUp(self):
        super(ApiTestCase, self).setUp()
        self.user = User.objects.create_user(username='the_user',
                                                password='joe',
                                                email='doe@joe.cl')
        Election.objects.filter(owner=self.user).delete()
        self.not_user = User.objects.create_user(username='joe',
                                                password='joe',
                                                email='doe@joe.cl')
        self.election, created = Election.objects.get_or_create(name='BarBaz',
                                                            owner=self.user,
                                                            slug='barbaz',
                                                            published=True)
        self.election.category_set.all().delete()

        self.category1 = Category.objects.create(name=u"Pets and phisicians", election=self.election, slug="pets")
        self.category2 = Category.objects.create(name=u"language problemas ", election=self.election, slug="language")
        self.question1 = Question.objects.create(category=self.category1, question=u"¿Cuál es el nombre de la ferocidad?")
        self.question2 = Question.objects.create(category=self.category1, question=u"¿Which one is your favourite colour?")
        self.question3 = Question.objects.create(category=self.category2, question=u"¿Why don't you speak proper english?")

        self.election2, created = Election.objects.get_or_create(name='BarBaz2',
                                                            owner=self.not_user,
                                                            slug='barbaz2',
                                                            published=True)
        self.candidate = Candidate.objects.create(
                                                            name='Bar Baz',
                                                            election=self.election)
        self.candidate2 = Candidate.objects.create(
                                                            name='Fieri',
                                                            election=self.election)
        self.candidate3  = Candidate.objects.create(
                                                            name='Ratón 1',
                                                            election=self.election2)


        self.api_client = TestApiClient()
        self.data = {'format': 'json', 'username': self.user.username, 'api_key':self.user.api_key.key}


    def test_get_all_my_elections(self):
        url = '/api/v1/election/'
        resp = self.api_client.get(url,data = self.data)
        self.assertValidJSONResponse(resp)
        elections = self.deserialize(resp)['objects']
        self.assertEqual(len(elections), 1) #Only my elections
        self.assertTrue(elections[0].has_key("name"))
        self.assertEqual(elections[0]["id"], self.election.id) #I make sure this is the election
        self.assertTrue(elections[0].has_key("id"))
        self.assertTrue(elections[0].has_key("slug"))
        self.assertTrue(elections[0].has_key("description"))
        self.assertTrue(elections[0].has_key("information_source"))
        self.assertTrue(elections[0].has_key("logo"))
        self.assertTrue(elections[0].has_key("published"))
        self.assertFalse(elections[0].has_key("custom_style"))
        self.assertTrue(elections[0].has_key("candidates"))


    def test_get_including_unpublished_elections(self):
        self.election.published = False
        self.election.save()
        url = '/api/v1/election/'
        resp = self.api_client.get(url,data = self.data)
        self.assertValidJSONResponse(resp)
        elections = self.deserialize(resp)['objects']
        self.assertEqual(len(elections), 1) #Only my elections
        self.assertFalse(elections[0]['published'])


    def test_get_candidates_from_elections_owned_by_user(self):
        url = '/api/v1/candidate/'
        resp = self.api_client.get(url,data = self.data)
        self.assertValidJSONResponse(resp)
        candidates = self.deserialize(resp)['objects']
        self.assertEqual(len(candidates), 2)


    def test_get_candidates_per_election(self):
        url = '/api/v1/election/{0}/'.format(self.election.id)
        resp = self.api_client.get(url, data=self.data)

        self.assertValidJSONResponse(resp)
        election = self.deserialize(resp)
        candidates = election['candidates']
        self.assertEqual(len(candidates), 2)
        candidate = candidates[0]
        self.assertTrue(candidate.has_key("id"))
        self.assertTrue(candidate.has_key("name"))
        self.assertTrue(candidate.has_key("slug"))
        self.assertTrue(candidate.has_key("photo"))
        self.assertTrue(candidate.has_key("has_answered"))


    def test_an_election_shows_questions(self):
        url = '/api/v1/election/{0}/'.format(self.election.id)
        resp = self.api_client.get(url, data=self.data)
        election = self.deserialize(resp)

        self.assertTrue(election.has_key("categories"))
        self.assertEquals(len(election["categories"]), 2)

        category = election["categories"][0]

        self.assertEquals(category['name'], u"Pets and phisicians")
        self.assertTrue(category.has_key('questions'))

        self.assertEquals(len(category["questions"]), 2)
        self.assertEquals(category["questions"][0]["question"], u"¿Cuál es el nombre de la ferocidad?")
        self.assertEquals(category["questions"][1]["question"], u"¿Which one is your favourite colour?")