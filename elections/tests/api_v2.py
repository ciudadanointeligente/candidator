# -*- coding: utf-8 -*-
from django.test import TestCase
from django.contrib.auth.models import User
from django.db import models
from elections.models import Election, Candidate, Category, PersonalData, \
                             BackgroundCategory, Background, PersonalDataCandidate, \
                             Question, Answer, Link, BackgroundCandidate, InformationSource
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
            election = self.election
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
            question = u"Te gusta the beatles?")

        self.question_category_2 = Question.objects.create(
            category = self.category2,
            question = u"Comerías limón con ají?")

        self.answer_for_question_1 = Answer.objects.create(
            question = self.question_category_1,
            caption = u"Si")

        self.answer_for_question_3 = Answer.objects.create(
            question = self.question_category_1,
            caption = u"No")

        self.answer_for_question_2 = Answer.objects.create(
            question = self.question_category_2,
            caption = u"Talvez")

        self.answer_for_question_4 = Answer.objects.create(
            question = self.question_category_2,
            caption = u"Quizás")

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

        self.link_twitter = Link.objects.create(
            name = u"Twitter",
            url = u"https://www.twitter.com/#el_twitter",
            candidate = self.candidate)

        self.candidate.associate_answer(self.answer_for_question_1)
        self.candidate.associate_answer(self.answer_for_question_2)

        
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
        # print the_election["background"]
        self.assertEquals(the_election['id'],self.election.id)
        self.assertTrue(the_election.has_key('candidates'))
        self.assertTrue(isinstance(the_election["candidates"][0], unicode))
        self.assertTrue(the_election.has_key('categories'))
        self.assertTrue(isinstance(the_election["categories"][0], unicode))
        self.assertTrue(the_election.has_key('background_categories'))
        self.assertTrue(isinstance(the_election["background_categories"][0], unicode))
        self.assertTrue(the_election.has_key('personal_data'))
        self.assertTrue(isinstance(the_election["personal_data"][0], unicode))
        

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
        self.assertTrue(isinstance(the_category["questions"][0], unicode))

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
        self.assertTrue(the_question.has_key('category'))
        self.assertTrue(isinstance(the_question["category"], unicode))
        self.assertEquals(the_question["category"], "/api/v2/category/{0}/".format(self.question_category_1.category.id))

    def test_get_all_answers(self):
        self.candidate.associate_answer(self.answer_for_question_1)

        response = self.api_client.get(
            '/api/v2/answer/', 
            format='json', 
            authentication=self.get_credentials())

        answers = self.deserialize(response)['objects']
        
        self.assertEquals(len(answers),Answer.objects.count())
        the_answer = answers[0]
        self.assertTrue(the_answer.has_key('caption'))
        self.assertTrue(the_answer.has_key('resource_uri'))
        self.assertEqual(the_answer["resource_uri"], "/api/v2/answer/{0}/".format(self.answer_for_question_1.id))
        self.assertTrue(the_answer.has_key('candidates'))
        self.assertEquals(len(the_answer["candidates"]), 1)
        self.assertTrue(isinstance(the_answer["candidates"][0], unicode))
        self.assertTrue(the_answer.has_key('question'))
        self.assertTrue(isinstance(the_answer["question"], unicode))
        self.assertEquals(the_answer["question"], "/api/v2/question/{0}/".format(self.answer_for_question_1.question.id))

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

    def test_get_background(self):
        response = self.api_client.get(
            '/api/v2/background/', 
            format='json', 
            authentication=self.get_credentials())

        self.assertHttpOK(response)
        background = self.deserialize(response)['objects']
        self.assertIn('background_category', background[0])

    def test_get_first_background(self):
        response = self.api_client.get(
            '/api/v2/background/{0}/'.format(self.background_school.id), 
            format='json', 
            authentication=self.get_credentials())

        self.assertHttpOK(response)
        background = self.deserialize(response)
        expected_resource_uri = "/api/v2/background_category/{0}/".format(
            self.background_school.category.id
            )
        self.assertEquals(background["background_category"],expected_resource_uri)


    def test_get_backgrounds_candidate(self):
        response = self.api_client.get(
            '/api/v2/backgrounds_candidate/', 
            format='json', 
            authentication=self.get_credentials())

        self.assertHttpOK(response)
        backgrounds_candidate = self.deserialize(response)['objects']
        # print(backgrounds_candidate)
        self.assertTrue(backgrounds_candidate[0].has_key('value'))
        self.assertIn('background', backgrounds_candidate[0])

    def test_backgrounds_candidate_detail(self):
        response = self.api_client.get(
            '/api/v2/backgrounds_candidate/{0}/'.format(self.background_candidate.id), 
            format='json', 
            authentication=self.get_credentials())

        self.assertHttpOK(response)
        the_background_candidate = self.deserialize(response)
        self.assertEqual(the_background_candidate['value'], self.background_candidate.value)
        self.assertIn("background",the_background_candidate)


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
        self.assertTrue(the_candidate.has_key('links'))
        self.assertTrue(isinstance(the_candidate["links"][0], unicode))
        self.assertTrue(the_candidate.has_key('answers'))
        self.assertTrue(isinstance(the_candidate["answers"][0], unicode))



    def test_get_background_category(self):
        response = self.api_client.get(
            '/api/v2/background_category/', 
            format='json', 
            authentication=self.get_credentials())

        self.assertHttpOK(response)
        background_category = self.deserialize(response)['objects']
        the_background_category = background_category[0]
        
        self.assertTrue(the_background_category.has_key('name'))
        self.assertTrue(the_background_category.has_key('background'))
        self.assertTrue(isinstance(the_background_category["background"][0], unicode))

    def test_get_links(self):
        response = self.api_client.get(
            '/api/v2/link/', 
            format='json', 
            authentication=self.get_credentials())

        self.assertHttpOK(response)
        link = self.deserialize(response)['objects']
        # print link
        the_link = link[0]
        self.assertTrue(the_link.has_key('name'))
        self.assertTrue(the_link.has_key('url'))

    def test_answer_filtering(self):
        filter_data = {
            'question': self.question_category_1.id
        }

        response = self.api_client.get(
            '/api/v2/answer/', 
            format='json', 
            authentication=self.get_credentials(),
            data=filter_data)
        
        self.assertHttpOK(response)
        answer = self.deserialize(response)['objects']
        self.assertEquals(len(answer), Answer.objects.filter(question=self.question_category_1).count())
        self.assertEquals( answer[0]['id'] , self.answer_for_question_1.id )

    # @skip('ignore')
    def test_answer_filtering_two_param(self):
        filter_data = {
            # 'question': self.question_category_1.id,
            'candidate__id': self.candidate.id
        }

        response = self.api_client.get(
            '/api/v2/answer/', 
            format='json', 
            authentication=self.get_credentials(),
            data=filter_data)
        # print response

        self.assertHttpOK(response)
        answer = self.deserialize(response)['objects']

        # self.assertEquals(len(answer), 1)
        self.assertEquals( answer[0]['id'] , self.answer_for_question_1.id )

    def test_filter_candidate(self):
        filter_data = {
            'id' : self.candidate.id
        }

        response = self.api_client.get(
            '/api/v2/candidate/', 
            format='json', 
            authentication=self.get_credentials(),
            data=filter_data)
        self.assertHttpOK(response)
        candidate = self.deserialize(response)['objects']
        self.assertEquals( len(candidate), 1)
        self.assertEquals( candidate[0]['id'], self.candidate.id )

    #@skip('')
    def test_media_naranja_post(self):
        answers = [self.answer_for_question_1.pk, self.answer_for_question_2.pk]
        questions_ids = [self.question_category_1.id, self.question_category_2.id]
        importances = [5, 3]
        importances_by_category = [5, 3]
        factor_question1 = (answers[0] == self.answer_for_question_1.pk) * importances[0]
        factor_question2 = (answers[1] == self.answer_for_question_2.pk) * importances[1]
        score_category1 = factor_question1 * 100.0 / importances_by_category[0]
        score_category2 = factor_question2 * 100.0 / importances_by_category[1]
        global_score = (factor_question1 + factor_question2) * 100.0 / sum(importances_by_category)
        response = self.api_client.post('/api/v2/medianaranja/', 
            format='json', 
            authentication=self.get_credentials(),
            data = {
                'data' : {
                    'question-0': answers[0], 'question-1': answers[1], \
                    'importance-0': importances[0], 'importance-1': importances[1],\
                    'question-id-0': questions_ids[0], 'question-id-1': questions_ids[1]
                    },\
                'election-id' : self.election.id
            }
        )
        expected_winner = {
                'global_score':global_score, 
                'category_score':[
                    {
                    'category':self.question_category_1.category.name,
                    'score': score_category1
                    },
                    {
                    'category':self.question_category_2.category.name,
                    'score': score_category2
                    },
                ],
                'candidate':self.candidate.id
                }
        expected_others = [
                {
                'global_score':0.0, 
                'category_score':[
                    {
                    'category':self.question_category_1.category.name,
                    'score': 0.0
                    },
                    {
                    'category':self.question_category_2.category.name,
                    'score': 0.0
                    },
                ],
                'candidate':self.candidate2.id
                }
        ]
        #de nuevo
        self.assertHttpCreated(response)
        self.assertValidJSON(response.content)

        candidates = self.deserialize(response)
        self.assertIn('winner', candidates)
        self.assertEquals(candidates['winner'],expected_winner)
        self.assertEquals(candidates['others'],expected_others)

    def test_media_naranja_post_jsonp(self):
        answers = [self.answer_for_question_1.pk, self.answer_for_question_2.pk]
        questions_ids = [self.question_category_1.id, self.question_category_2.id]
        importances = [5, 3]
        importances_by_category = [5, 3]
        factor_question1 = (answers[0] == self.answer_for_question_1.pk) * importances[0]
        factor_question2 = (answers[1] == self.answer_for_question_2.pk) * importances[1]
        score_category1 = factor_question1 * 100.0 / importances_by_category[0]
        score_category2 = factor_question2 * 100.0 / importances_by_category[1]
        global_score = (factor_question1 + factor_question2) * 100.0 / sum(importances_by_category)
        response = self.api_client.post('/api/v2/medianaranja/?callback=callback', 
            format='json', 
            authentication=self.get_credentials(),
            data = {
                
                'data' : {
                    'question-0': answers[0], 'question-1': answers[1], \
                    'importance-0': importances[0], 'importance-1': importances[1],\
                    'question-id-0': questions_ids[0], 'question-id-1': questions_ids[1]
                    },\
                'election-id' : self.election.id
            }
        )
        expected_winner = {
                'global_score':global_score, 
                'category_score':[
                    {
                    'category':self.question_category_1.category.name,
                    'score': score_category1
                    },
                    {
                    'category':self.question_category_2.category.name,
                    'score': score_category2
                    },
                ],
                'candidate':self.candidate.id
                }
        expected_others = [
                {
                'global_score':0.0, 
                'category_score':[
                    {
                    'category':self.question_category_1.category.name,
                    'score': 0.0
                    },
                    {
                    'category':self.question_category_2.category.name,
                    'score': 0.0
                    },
                ],
                'candidate':self.candidate2.id
                }
        ]

        self.assertTrue(response.content.startswith("callback("))
        content = response.content

        content = content.strip("callback(")

    def test_get_information_source(self):
        information_source = InformationSource.objects.create(
            candidate=self.candidate,
            question=self.question_category_1,
            content=u"Tomé esta información desde una página web")

        response = self.api_client.get(
            '/api/v2/information_source/', 
            format='json', 
            authentication=self.get_credentials())

        self.assertHttpOK(response)
        information_source_dict = self.deserialize(response)['objects'][0]
        self.assertEquals(information_source_dict['candidate'], '/api/v2/candidate/{0}/'.format(self.candidate.id))
        self.assertEquals(information_source_dict['question'], '/api/v2/question/{0}/'.format(self.question_category_1.id))
        self.assertEquals(information_source_dict['content'], information_source.content)


        response_question = self.api_client.get(
            information_source_dict['question'], 
            format='json', 
            authentication=self.get_credentials())


        self.assertHttpOK(response_question)
        question_dict = self.deserialize(response_question)

        self.assertIn('information_sources', question_dict)
        self.assertEquals(len(question_dict['information_sources']), 1)
        self.assertEquals(question_dict['information_sources'][0], '/api/v2/information_source/{0}/'.format(information_source.id))

        