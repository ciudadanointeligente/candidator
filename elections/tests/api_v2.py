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

        self.category1 = Category.objects.create(
            name=u"Category 01", 
            election=self.election, 
            slug="category-01")

        self.category2 = Category.objects.create(
            name=u"Another category", 
            election=self.election, 
            slug="another-category")

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