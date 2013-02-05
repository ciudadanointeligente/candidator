import os
from django.conf import settings
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import IntegrityError
from django.utils import simplejson as json, simplejson

from elections.models import Candidate, Election, BackgroundCategory, Background,\
                                BackgroundCandidate, PersonalData, PersonalDataCandidate,\
                                Category, Question, Answer
from elections.forms import CandidateUpdateForm, CandidateForm, CandidateLinkForm, BackgroundCandidateForm, PersonalDataCandidateForm, AnswerForm, CandidatePhotoForm

dirname = os.path.dirname(os.path.abspath(__file__))

PASSWORD = 'password'


class CandidateTagsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(name='Joe', password=PASSWORD, email='joe@doe.cl')
        self.election = Election.objects.create(name='Foo', owner=self.user, slug='foo')
        self.candidate = Candidate.objects.create(name='John Candidate', election=self.election)
        self.personal_data = PersonalData.objects.create(election=self.election, label='foo')
        self.personal_data_candidate = PersonalDataCandidate.objects.create(personal_data=self.personal_data,
                                                                            candidate=self.candidate,
                                                                            value='bar')
        self.background_category = BackgroundCategory.objects.create(name='foo', election=self.election)
        self.background = Background.objects.create(name='foo', category=self.background_category)
        self.background_candidate = BackgroundCandidate.objects.create(value='var', background=self.background, candidate=self.candidate)

    def test_value_for_candidate_and_personal_data(self):
        self.candidate.associate_answer(self.answer)
        template = Template('{% load election_tags %}{% value_for_candidate_and_personal_data candidate personal_data %}')
        context = Context({"candidate": self.candidate, "personal_data": self.personal_data})
        self.assertEqual(template.render(context), self.personal_data_candidate.value)

    def test_value_for_candidate_and_background(self):
        self.candidate.associate_answer(self.answer)
        template = Template('{% load election_tags %}{% value_for_candidate_and_background candidate background %}')
        context = Context({"candidate": self.candidate, "background": self.background})
        self.assertEqual(template.render(context), self.background_candidate.value)


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


class CandidateDetailViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='foobar')
        self.election, created = Election.objects.get_or_create(name='BarBaz',
                                                           owner=self.user,
                                                           slug='barbaz',
                                                           description='esta es una descripcion')

        self.candidate = Candidate.objects.create(name='Juan Candidato',
                                                    election=self.election,
                                                    photo='photos/dummy.jpg')

    def test_detail_existing_candidate_view(self):
        response = self.client.get(reverse('candidate_detail',
                                            kwargs={
                                               'username': self.user.username,
                                               'election_slug': self.election.slug,
                                               'slug': self.candidate.slug}))

        self.assertEquals(response.status_code, 200)
        self.assertTrue('candidate' in response.context)
        self.assertEquals(response.context['candidate'], self.candidate)

    def test_detail_non_existing_candidate_view(self):
        response = self.client.get(reverse('candidate_detail',
                                           kwargs={
                                               'username': self.user.username,
                                               'election_slug': self.election.slug,
                                               'slug': 'asd-asd'}))
        self.assertEquals(response.status_code, 404)

    def test_detail_non_existing_candidate_for_user_view(self):
        election, created = Election.objects.get_or_create(name='AsdAsd',
                                                           owner=self.user,
                                                           slug='asdasd',
                                                           description='esta es una descripcion dos')
        response = self.client.get(reverse('candidate_detail',
                                           kwargs={
                                               'username': self.user.username,
                                               'election_slug': election.slug,
                                               'slug': self.candidate.slug}))
        self.assertEquals(response.status_code, 404)

        '''
        TODO: distintos usuarios, mismo slug de eleccion,
                mismo slug de candidato (inexistente en uno, pero existente en otra)
        '''


class CandidateCreateViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='joe', password='doe', email='joe@doe.cl')
        self.election, created = Election.objects.get_or_create(name='BarBaz',
                                                           owner=self.user,
                                                           slug='barbaz',
                                                           description='esta es una descripcion')

    def test_create_candidate_by_user_without_login(self):
        request = self.client.get(reverse('candidate_create', kwargs={'election_slug': self.election.slug}))

        self.assertEquals(request.status_code, 302)

    def test_create_candidate_by_user_success(self):
        self.client.login(username='joe', password='doe')
        request = self.client.get(reverse('candidate_create', kwargs={'election_slug': self.election.slug}))

        self.assertTrue('form' in request.context)
        self.assertTrue(isinstance(request.context['form'], CandidateForm))
        self.assertFalse('has_answered' in request.context['form'].fields)
        self.assertTrue('election' in request.context)
        self.assertTrue(isinstance(request.context['election'], Election))

    def test_post_candidate_create_with_same_slug(self):
        candidate = Candidate.objects.create(name='Juan Candidato',
                                            election=self.election)
        self.client.login(username='joe', password='doe')

        f = open(os.path.join(dirname, 'media/dummy.jpg'), 'rb')
        params = {'name': candidate.name,
                  'photo': f,
                  'form-TOTAL_FORMS': u'0',
                  'form-INITIAL_FORMS': u'0',
                  'form-MAX_NUM_FORMS': u'',
                  'link-TOTAL_FORMS': u'0',
                  'link-INITIAL_FORMS': u'0',
                  'link-MAX_NUM_FORMS': u'',
                  }
        response = self.client.post(reverse('candidate_create', kwargs={'election_slug': self.election.slug}), params,
            follow=True)
        f.close()
        self.assertEquals(response.status_code, 200)

        # falta revisar que no tenga errores

    def test_post_candidate_create_without_login(self):
        f = open(os.path.join(dirname, 'media/dummy.jpg'), 'rb')
        params = {'name': 'Juan Candidato', 'last_name': 'Candidato',
                  'slug': 'juan-candidato', 'photo': f,
                  'form-TOTAL_FORMS': u'0',
                  'form-INITIAL_FORMS': u'0',
                  'form-MAX_NUM_FORMS': u'',
                  'link-TOTAL_FORMS': u'0',
                  'link-INITIAL_FORMS': u'0',
                  'link-MAX_NUM_FORMS': u'',}
        response = self.client.post(reverse('candidate_create', kwargs={'election_slug': self.election.slug}), params)
        f.close()

        self.assertEquals(response.status_code, 302)

    def test_get_candidate_create_with_login_stranger_election(self):
        self.client.login(username='joe', password='doe')
        response = self.client.get(reverse('candidate_create',
                                    kwargs={'election_slug': 'strager_election_slug'}))
        self.assertEquals(response.status_code, 404)

    def test_post_candidate_create_with_login_stranger_election(self):
        user2 = User.objects.create_user(username='joe2', password='doe', email='joe@doe.cl')
        election2, created = Election.objects.get_or_create(name='BarBaz',
                                                           owner=user2,
                                                           slug='barbaz2',
                                                           description='esta es una descripcion')

        f = open(os.path.join(dirname, 'media/dummy.jpg'), 'rb')
        self.client.login(username='joe', password='doe')

        params = {'name': 'Juan Candidato', 'last_name': 'Candidato',
                  'slug': 'juan-candidato', 'photo': f,
                  'form-TOTAL_FORMS': u'0',
                  'form-INITIAL_FORMS': u'0',
                  'form-MAX_NUM_FORMS': u'',
                  'link-TOTAL_FORMS': u'0',
                  'link-INITIAL_FORMS': u'0',
                  'link-MAX_NUM_FORMS': u'',}
        response = self.client.post(reverse('candidate_create',
                                        kwargs={'election_slug': election2.slug}),
                                    params)
        f.close()

        self.assertEquals(response.status_code, 404)

    def test_if_the_request_is_sent_from_create_alone_it_redirects_to_it_create_alone(self):
        self.client.login(username='joe', password='doe')

        f = open(os.path.join(dirname, 'media/dummy.jpg'), 'rb')
        params = {'name': 'Juan Candidato',
                  'photo': f,
                  'form-TOTAL_FORMS': u'0',
                  'form-INITIAL_FORMS': u'0',
                  'form-MAX_NUM_FORMS': u'',
                  'link-TOTAL_FORMS': u'0',
                  'link-INITIAL_FORMS': u'0',
                  'link-MAX_NUM_FORMS': u'',}
        response = self.client.post(reverse('candidate_create_alone', kwargs={'election_slug': self.election.slug}), params, follow=True)
        f.seek(0)


        self.assertTemplateUsed(response, 'elections/updating/candidates.html')

    def test_post_candidate_create_logged(self):
        self.client.login(username='joe', password='doe')

        f = open(os.path.join(dirname, 'media/dummy.jpg'), 'rb')
        params = {'name': 'Juan Candidato',
                  'photo': f,
                  'form-TOTAL_FORMS': u'0',
                  'form-INITIAL_FORMS': u'0',
                  'form-MAX_NUM_FORMS': u'',
                  'link-TOTAL_FORMS': u'0',
                  'link-INITIAL_FORMS': u'0',
                  'link-MAX_NUM_FORMS': u'',}
        response = self.client.post(reverse('candidate_create', kwargs={'election_slug': self.election.slug}), params, follow=True)
        f.seek(0)


        self.assertEquals(response.status_code, 200)
        qs = Candidate.objects.filter(election= self.election, slug='juan-candidato')
        self.assertEquals(qs.count(), 1)
        candidate = qs.get()
        self.assertEquals(candidate.name, params['name'])
        # The CandidateForm doesnt contain the photo field
        # self.assertEquals(f.read(), candidate.photo.file.read())
        f.close()
        # os.unlink(candidate.photo.path)
        self.assertEquals(candidate.election, self.election)
        self.assertRedirects(response, reverse('candidate_create',
                                               kwargs={'election_slug': candidate.election.slug}))



    def test_renders_step_two_of_the_wizard(self):
        self.client.login(username='joe', password='doe')
        response = self.client.get(reverse('candidate_create', kwargs={'election_slug': self.election.slug}))
        self.assertTemplateUsed(response,'elections/wizard/step_two.html')

class CandidateUpdateViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='joe', password='doe', email='joe@doe.cl')
        self.election, created = Election.objects.get_or_create(name='BarBaz',
                                                           owner=self.user,
                                                           slug='barbaz',
                                                           description='esta es una descripcion')

        self.candidate, created = Candidate.objects.get_or_create(name='Juan Candidato',
                                            election=self.election)


    def test_update_candidate_by_user_without_login(self):
        request = self.client.get(reverse('candidate_update', kwargs={'slug': self.candidate.slug, 'election_slug': self.election.slug}))

        self.assertEquals(request.status_code, 302)

    def test_update_candidate_by_user_success(self):
        self.client.login(username='joe', password='doe')
        request = self.client.get(reverse('candidate_update', kwargs={'slug': self.candidate.slug, 'election_slug': self.election.slug}))

        self.assertTrue('form' in request.context)
        self.assertTrue(isinstance(request.context['form'], CandidateUpdateForm))
        self.assertFalse('has_answered' in request.context['form'].fields)
        self.assertTrue('name' in request.context['form'].initial)
        self.assertEquals(request.context['form'].initial['name'], 'Juan Candidato')

    def test_post_candidate_update_without_login(self):
        f = open(os.path.join(dirname, 'media/dummy.jpg'), 'rb')
        params = {'name': 'Juan Candidato', 'last_name': 'Candidato',
                  'photo': f,}
        response = self.client.post(reverse('candidate_update', kwargs={'slug': self.candidate.slug, 'election_slug': self.election.slug}), params)
        f.close()

        self.assertEquals(response.status_code, 302)

    def test_get_candidate_update_with_login_stranger_election(self):


        user2 = User.objects.create_user(username='doe', password='doe', email='joe@doe.cl')
        election2, created = Election.objects.get_or_create(name='BarBaz',
                                                           owner=user2,
                                                           slug='barbaz3',
                                                           description='esta es una descripcion')

        candidate2, created = Candidate.objects.get_or_create(name='Juan Candidato',
                                            election=election2)

        self.client.login(username='joe', password='doe')
        response = self.client.get(reverse('candidate_update',
                                    kwargs={'slug': candidate2.slug, 'election_slug': election2.slug}))
        self.assertEquals(response.status_code, 404)

    def test_post_candidate_update_with_login_stranger_election(self):
        f = open(os.path.join(dirname, 'media/dummy.jpg'), 'rb')


        user2 = User.objects.create_user(username='doe', password='doe', email='joe@doe.cl')
        election2, created = Election.objects.get_or_create(name='BarBaz',
                                                           owner=user2,
                                                           slug='barbaz2',
                                                           description='esta es una descripcion')

        candidate2, created = Candidate.objects.get_or_create(name='Juan Candidato',
                                            election=election2)

        params = {'name': 'Juan Candidato', 'last_name': 'Candidato',
                  'photo': f,}

        self.client.login(username='joe', password='doe')
        response = self.client.post(reverse('candidate_update',
                                        kwargs={'slug': candidate2.slug, 'election_slug': election2.slug}),
                                    params)
        f.close()

        self.assertEquals(response.status_code, 404)

    def test_post_candidate_update_logged(self):
        self.client.login(username='joe', password='doe')

        f = open(os.path.join(dirname, 'media/dummy.jpg'), 'rb')
        params = {'name': 'Juanito', 'last_name': 'Candidato',
                  'photo': f,}
        response = self.client.post(reverse('candidate_update', kwargs={'slug': self.candidate.slug, 'election_slug': self.election.slug}), params, follow=True)
        f.seek(0)

        self.assertEquals(response.status_code, 200)
        qs = Candidate.objects.filter(election= self.election, slug='juan-candidato')
        self.assertEquals(qs.count(), 1)
        candidate = qs.get()
        self.assertEquals(candidate.name, params['name'])
        self.assertEquals(f.read(), candidate.photo.file.read())
        f.close()
        os.unlink(candidate.photo.path)
        self.assertEquals(candidate.election, self.election)
        self.assertRedirects(response, reverse('candidate_update',
                                               kwargs={'slug': self.candidate.slug, 'election_slug': candidate.election.slug}))


class CandidateUrlsTest(TestCase):
    def test_create_url(self):
        expected = '/bar-baz/candidate/create'
        result = reverse('candidate_create', kwargs={'election_slug': 'bar-baz'})
        self.assertEquals(result, expected)

    def test_detail_url(self):
        expected = '/juanito/bar-baz/juan-candidato'
        result = reverse('candidate_detail', kwargs={'username': 'juanito', 'election_slug': 'bar-baz', 'slug': 'juan-candidato'})
        self.assertEquals(result, expected)


class CandidateDataUpdateTest(TestCase):
     def setUp(self):
         self.user = User.objects.create_user(username='joe', password='doe', email='joe@doe.cl')
         self.election, created = Election.objects.get_or_create(name='BarBaz',
                                                            owner=self.user,
                                                            slug='barbaz',
                                                            description='esta es una descripcion')

         self.candidate, created = Candidate.objects.get_or_create(name='Juan Candidato',
                                             election=self.election,
                                             photo='photos/dummy.jpg')

     def test_get_update_candidate_data_by_user_without_login(self):
         request = self.client.get(reverse('candidate_data_update', kwargs={'slug': self.candidate.slug, 'election_slug': self.election.slug}))

         self.assertEquals(request.status_code, 302)

     def test_get_update_candidate_data_by_user_success(self):
         self.client.login(username='joe', password='doe')
         request = self.client.get(reverse('candidate_data_update', kwargs={'slug': self.candidate.slug, 'election_slug': self.election.slug}))


         self.assertTrue('candidate' in request.context)
         self.assertEqual(request.context['candidate'], self.candidate)
         self.assertTrue('election' in request.context)
         self.assertEqual(request.context['election'], self.election)

     def test_update_candidate_data_strager_candidate(self):
         user2 = User.objects.create_user(username='doe', password='doe', email='joe@doe.cl')
         election2, created = Election.objects.get_or_create(name='BarBaz',
                                                            owner=user2,
                                                            slug='barbaz2',
                                                            description='esta es una descripcion')

         candidate2, created = Candidate.objects.get_or_create(name='Juan Candidato',
                                             election=election2,
                                             photo='photos/dummy.jpg')
         self.client.login(username='joe', password='doe')
         request = self.client.get(reverse('candidate_data_update', kwargs={'slug': candidate2.slug, 'election_slug': election2.slug}))
         
         self.assertEquals(request.status_code, 404)

     def test_post_candidate_data_update_405(self):
         self.client.login(username='joe', password='doe')
         request = self.client.post(reverse('candidate_data_update',
                                     kwargs={'slug': self.candidate.slug,
                                             'election_slug': self.election.slug}),
                                     {'var':'foo'})
         self.assertEquals(request.status_code, 405)


class AsyncDeleteCandidateTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='joe', password='doe', email='joe@doe.cl')
        self.election, created = Election.objects.get_or_create(name='BarBaz',
                                                           owner=self.user,
                                                           slug='barbaz',
                                                           description='esta es una descripcion')

        self.candidate, created = Candidate.objects.get_or_create(name='Juan Candidato',
                                            election=self.election,
                                            photo='photos/dummy.jpg')


    def test_post_with_login(self):
        self.client.login(username='joe', password='doe')
        url = reverse('async_delete_candidate')
        request = self.client.post(url , {'candidate_pk': self.candidate.pk})
        self.assertEquals(request.status_code, 200)

    def test_post_without_login(self):
        request = self.client.post(reverse('async_delete_candidate',
                                kwargs={}), {'candidate_pk': self.candidate.pk})
        self.assertEquals(request.status_code, 302)


    def test_get_405(self):
        self.client.login(username='joe', password='doe')
        request = self.client.get(reverse('async_delete_candidate',
                                kwargs={}),{'candidate_pk': self.candidate.pk})

        self.assertEquals(request.status_code, 405)

    def test_post_with_stranger_candidate(self):
        user2 = User.objects.create_user(username='doe', password='doe', email='joe@doe.cl')
        election2, created = Election.objects.get_or_create(name='BarBaz',
                                                           owner=user2,
                                                           slug='barbaz2',
                                                           description='esta es una descripcion')

        candidate2, created = Candidate.objects.get_or_create(name='Juan Candidato',
                                            election=election2,
                                            photo='photos/dummy.jpg')

        self.client.login(username='joe', password='doe')
        url = reverse('async_delete_candidate')
        request = self.client.post(url,{'candidate_pk': candidate2.pk})

        self.assertEquals(request.status_code, 404)

    def test_post_success(self):
        self.client.login(username='joe', password='doe')
        temp_pk = self.candidate.pk
        request = self.client.post(reverse('async_delete_candidate'),
                                        {'candidate_pk': self.candidate.pk})

        self.assertEquals(request.status_code, 200)
        self.assertEquals(request.content, '{"result": "OK"}')

        self.assertRaises(Candidate.DoesNotExist, Candidate.objects.get, pk=temp_pk)


class CandidateCreateAjaxView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='joe', password='joe', email='joe@doe.cl')
        self.user2 = User.objects.create_user(username='doe', password='joe', email='dow@doe.cl')
        self.election = Election.objects.create(name='BarBaz', owner=self.user, slug='barbaz')
        self.url = reverse('async_create_candidate', kwargs={'election_slug': self.election.slug, })
        self.params = {'name': 'Juan Candidato'}

    def test_create_candidate_asynchronously(self):
        self.client.login(username=self.user.username, password='joe')
        response = self.client.post(self.url,self.params, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.content, '{"result": "OK"}')



    def test_post_without_login(self):
        response = self.client.post(self.url, self.params, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertRedirects(response, settings.LOGIN_URL + '?next=' + self.url)

    def test_post_to_not_owned_election(self):
        self.client.login(username=self.user2.username, password='joe')
        response = self.client.post(self.url, self.params, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 404)

    def test_post_as_election_owner(self):
        self.client.login(username=self.user.username, password='joe')
        response = self.client.post(self.url, self.params, HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        self.assertEqual(response.status_code, 200)
        candidate = Candidate.objects.filter(election=self.election)

        self.assertEqual(candidate.count(), 1)
        candidate = candidate.get()
        self.assertEqual(candidate.name, self.params['name'])
        self.assertEqual(response.content, '{"result": "OK"}')
        self.assertEqual(response['Content-Type'], 'application/json')

    def test_post_as_election_owner_with_same_name(self):
        self.client.login(username=self.user.username, password='joe')
        candidate, created = Candidate.objects.get_or_create(election=self.election, name=self.params['name'])

        response = self.client.post(self.url, self.params, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)

        candidate = Candidate.objects.filter(election=self.election)
        self.assertEqual(candidate.count(), 1)

        self.assertTrue('error' in simplejson.loads(response.content))
        self.assertEqual(response['Content-Type'], 'application/json')

    def test_post_invalid_answer(self):
        self.client.login(username=self.user.username, password='joe')
        params = {}

        response = self.client.post(self.url, params, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)

        candidate = Candidate.objects.filter(election=self.election)
        self.assertEqual(candidate.count(), 0)

        self.assertTrue('error' in simplejson.loads(response.content))
        self.assertEqual(response['Content-Type'], 'application/json')

    def test_get_no_ajax(self):
        self.client.login(username=self.user.username, password='joe')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 400)

PASSWORD = 'doe'
class CandidateUpdateDataViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='joe', password='doe', email='asd@asd.cl')
        self.election, created = Election.objects.get_or_create(name='BarBaz',
                                                          owner=self.user,
                                                          slug='barbaz',
                                                          description='esta es una descripcion')

        self.candidate, created = Candidate.objects.get_or_create(name='Juan Candidato',
                                                                 slug='juan-candidato',
                                                                 election=self.election)
        self.url = reverse('candidate_data_update', kwargs={'election_slug': self.election.slug, 'slug': self.candidate.slug})

    def test_get_not_logged(self):
        response = self.client.get(self.url)
        self.assertRedirects(response, settings.LOGIN_URL + '?next=' + self.url)

    def test_get_not_owned_election(self):
        stranger_user = User.objects.create_user(username='John', password=PASSWORD, email='john@doe.cl')
        self.client.login(username=stranger_user.username, password=PASSWORD)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)

    def test_get_non_existing_candidate(self):
        url = reverse('candidate_data_update', kwargs={'election_slug': self.election.slug, 'slug': 'non_exist'})
        self.client.login(username=self.user.username, password=PASSWORD)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_get_owned_candidate(self):
        self.client.login(username=self.user.username, password=PASSWORD)
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'elections/updating/answers.html')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('election' in response.context)
        self.assertTrue('candidate' in response.context)
        self.assertEqual(response.context['election'], self.election)
        self.assertEqual(response.context['candidate'], self.candidate)


        self.assertTrue('candidate_link_form' in response.context)
        self.assertIsInstance(response.context['candidate_link_form'], CandidateLinkForm)

        self.assertTrue('background_candidate_form' in response.context)
        self.assertIsInstance(response.context['background_candidate_form'], BackgroundCandidateForm)

        self.assertTrue('personal_data_candidate_form' in response.context)
        self.assertIsInstance(response.context['personal_data_candidate_form'], PersonalDataCandidateForm)

        self.assertTrue('answer_form' in response.context)
        self.assertIsInstance(response.context['answer_form'], AnswerForm)


    def test_create_a_link_asynchronously(self):
        self.client.login(username=self.user.username, password=PASSWORD)
        link_name = 'mi link'
        link_url = 'http://milink.com'
        link_details = {
            'link_name': link_name,
            'link_url': link_url,
            'election_slug': self.election.slug,
            'candidate_slug': self.candidate.slug,
            'candidate_name': self.candidate.name,
        }
        url = reverse('link_create_ajax', kwargs={
            'candidate_pk': self.candidate.pk,
            })
        request = self.client.post(url, link_details)
        self.assertEquals(request.status_code, 200)
        self.assertEqual(self.candidate.link_set.count(), 1)
        link = self.candidate.link_set.all()[0]
        self.assertEqual(link.name, link_name)
        self.assertEqual(link.url, link_url)


    def test_post_failed(self):
        self.client.login(username='joe', password='doe')
        link_details = {
            'link_name': "",
            'link_url': "",
            'election_slug': self.election.slug,
            'candidate_slug': self.candidate.slug,
            'candidate_name': self.candidate.name,
        }
        url = reverse('link_create_ajax', kwargs={
            'candidate_pk': self.candidate.pk,
            })
        request = self.client.post(url, link_details)
        self.assertEqual(request.status_code, 200)
        self.assertEqual(self.candidate.link_set.count(), 0)
        body = simplejson.loads(request.content)
        self.assertTrue('name' in body["errors"])
        self.assertTrue('url' in body["errors"])

class MultipleCandidateDataUpdate(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='joe', password='doe', email='asd@asd.cl')
        self.election, created = Election.objects.get_or_create(name='BarBaz',
            owner=self.user,
            slug='barbaz',
            description='esta es una descripcion')

        self.first_candidate, created = Candidate.objects.get_or_create(name='Primer Candidato',
            slug='primer-candidato',
            election=self.election)

        self.second_candidate, created = Candidate.objects.get_or_create(name='Segundo Candidato',
            slug='segundo-candidato',
            election=self.election)

        self.url = reverse('multiple_candidate_data_update', kwargs={'election_slug': self.election.slug})

    def test_get_right_after_filling_their_names_and_showing_a_success_text(self):
        self.client.login(username=self.user.username, password=PASSWORD)
        url = reverse('multiple_candidate_data_update_first_time', kwargs={'election_slug': self.election.slug})
        response = self.client.get(url)
        
        self.assertTemplateUsed(response, 'elections/updating/answers.html')
        self.assertContains(response, '<div class="success">')
        


    def test_get_first_candidate_ordered_by_name(self):
        self.client.login(username=self.user.username, password=PASSWORD)
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'elections/updating/answers.html')
        self.assertEqual(response.status_code, 200)


        self.assertTrue('election' in response.context)
        self.assertTrue('candidate' in response.context)

        self.assertEqual(response.context['election'], self.election)
        self.assertEqual(response.context['candidate'], self.first_candidate)


#This correspond to bug 191
class MultipleCandidateDataUpdateWith0Candidates(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='joe', password='doe', email='asd@asd.cl')
        self.election, created = Election.objects.get_or_create(name='NoCandidatesBarBaz',
            owner=self.user,
            slug='nocandidatesbarbaz',
            description='this election has no candidates')

        self.url = reverse('multiple_candidate_data_update', kwargs={'election_slug': self.election.slug})

    def test_redirect_to_add_new_users_when_candidate_list_is_empty(self):
        self.client.login(username=self.user.username, password=PASSWORD)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 302)


    def test_show_create_new_candidate_html_is_shown(self):
        self.client.login(username=self.user.username, password=PASSWORD)
        response = self.client.get(self.url, follow=True)


        self.assertTemplateUsed(response, 'elections/updating/candidates.html')


class CandidateUpdatePhotoViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='joe', password=PASSWORD, email='joe@exmaple.net')
        self.election = Election.objects.create(name='election', slug='election', owner=self.user)
        self.candidate = Candidate.objects.create(name='candidate', election=self.election)
        self.file = open(os.path.join(dirname, 'media/dummy.jpg'), 'rb')
        self.url = reverse('update_candidate_photo', kwargs={'pk': self.candidate.pk})

    def test_get_not_logged(self):
        response = self.client.get(self.url)
        self.assertRedirects(response, settings.LOGIN_URL + '?next=' + self.url)

    def test_post_not_logged(self):
        response = self.client.post(self.url)
        self.assertRedirects(response, settings.LOGIN_URL + '?next=' + self.url)
    
    def test_get_not_owner(self):
        not_user = User.objects.create_user(username='doe', password=PASSWORD, email='doe@example.net')
        self.client.login(username=not_user.username, password=PASSWORD)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_post_not_owner(self):
        not_user = User.objects.create_user(username='doe', password=PASSWORD, email='doe@example.net')
        self.client.login(username=not_user.username, password=PASSWORD)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 403)
    
    def test_get_owner(self):
        self.client.login(username=self.user.username, password=PASSWORD)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'elections/candidate_photo_form.html')
        self.assertTrue('form' in response.context)
        self.assertIsInstance(response.context['form'], CandidatePhotoForm)
        self.assertTrue('candidate' in response.context)
        self.assertEqual(response.context['candidate'], self.candidate)
    
    def test_post_owner(self):
        self.client.login(username=self.user.username, password=PASSWORD)
        params = {
            'photo': self.file
        }
        response = self.client.post(self.url, params)
        self.file.seek(0)
        self.assertRedirects(response, reverse('candidate_data_update', 
                                       kwargs={'election_slug': self.election.slug, 'slug': self.candidate.slug}))
        candidate = Candidate.objects.get(pk=self.candidate.pk)
        self.assertEqual(candidate.photo.file.read(), self.file.read())
        os.unlink(candidate.photo.path)


class CandidateListAjaxViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='joe', password=PASSWORD, email='joe@exmaple.net')
        self.election = Election.objects.create(name='election', slug='election', owner=self.user)
        self.candidate_one = Candidate.objects.create(name='candidate one', election=self.election)
        self.candidate_two = Candidate.objects.create(name='candidate two', election=self.election)

    def test_get_list_for_a_defined_election(self):
        url_params = {'username':self.user.username,'election_slug':self.election.slug}
        url = reverse('candidate_list_json',kwargs=url_params)
        request_params = {}
        response = self.client.post(url,request_params,HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        candidate_names = json.loads(response.content)
        self.assertTrue(candidate_names.__len__(),2)
        self.assertEquals(candidate_names[0],{'name':'candidate one','id':self.candidate_one.pk})
        self.assertEquals(candidate_names[1],{'name':'candidate two','id':self.candidate_two.pk})


