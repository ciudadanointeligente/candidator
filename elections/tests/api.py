from django.test import TestCase
from django.contrib.auth.models import User
from django.db import models
from tastypie.models import ApiKey
from elections.models import Election, Candidate, Category, PersonalData, \
                             BackgroundCategory, Background, PersonalDataCandidate
#from tastypie.models import create_api_key
from tastypie.test import ResourceTestCase

class CandidateResourceCase(ResourceTestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='doe',
                                                password='joe',
                                                email='doe@joe.cl')
        self.user_api_key = ApiKey.objects.create(user=self.user)
        self.not_user = User.objects.create_user(username='joe',
                                                password='joe',
                                                email='doe@joe.cl')
        self.not_user_api_key = ApiKey.objects.create(user=self.not_user)
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
                                                            election=self.election)
    def get_credentials(self):
        return self.create_apikey(username=self.user.username, api_key=self.user.api_key)

    def test_get_candidates_per_election(self):
        url = reverse('api_candidates_list',kwargs={ 'pk':self.election.id })
        resp = self.api_client.get(url, format='json', authentication=self.get_credentials())
        self.assertValidJSONResponse(resp)

        self.assertEqual(len(self.deserialize(resp)['objects']), 2)
        
        #print self.user.api_key
        #print self.election.id


    ## . tengo api key ------ SI
    ## . tengo id de eleccion --- SI
    ## . GET http://127.0.0.1:8000/api/v1/candidates/?election=3&api_key=204db7bcfafb2deb7506b89eb3b9b715b09905c9
    ## . devuelve lista de candidatos
    ## . deberia devolver: id, name, slug, photo, personal_data??
