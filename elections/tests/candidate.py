import os
from django.conf import settings
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import IntegrityError

from elections.models import Candidate, Election, BackgroundCategory, Background,\
                                BackgroundCandidate, PersonalData, PersonalDataCandidate,\
                                Category, Question, Answer
from elections.forms import CandidateUpdateForm, CandidateForm

dirname = os.path.dirname(os.path.abspath(__file__))


class CandidateModelTest(TestCase):
    def setUp(self):
        self.user, created = User.objects.get_or_create(username='joe')
        self.election, created = Election.objects.get_or_create(name='BarBaz',
                                                           owner=self.user,
                                                           slug='barbaz',
                                                           description='esta es una descripcion')

    def test_create_candidate(self):
        candidate, created = Candidate.objects.get_or_create(name='Juan Candidato',
                                                            election=self.election)

        self.assertTrue(created)
        self.assertEqual(candidate.name, 'Juan Candidato')
        self.assertEqual(candidate.slug, 'juan-candidato')
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
        self.assertEqual(personal_data_set, {'foo': 'new_value'})

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

        expected_dict = {'FooBar' : {'foo': 'BarFoo', 'foo2': 'BarFoo2'},
                         'FooBar2' : {'foo3': 'BarFoo3'}}
        self.assertEqual(candidate.get_background, expected_dict)

    def test_add_personal_data(self):
        candidate, created = Candidate.objects.get_or_create(name='Juan Candidato',
                                                            election=self.election)

        personal_data, created = PersonalData.objects.get_or_create(election=self.election,
                                                                    label='foo')
        personal_data2, created = PersonalData.objects.get_or_create(election=self.election,
                                                                    label='foo2')

        candidate.add_personal_data(personal_data, 'new_value')
        self.assertEqual(candidate.get_personal_data, {'foo': 'new_value'})

        candidate.add_personal_data(personal_data, 'new_value2')
        self.assertEqual(candidate.get_personal_data, {'foo': 'new_value2'})

        candidate.add_personal_data(personal_data2, 'new_value3')
        self.assertEqual(candidate.get_personal_data, {'foo': 'new_value2', 'foo2':'new_value3'})


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
        expected = {'FooBar' : {'foo': 'BarFoo'}}
        self.assertEqual(candidate.get_background, expected)

        candidate.add_background(background, 'BarFoo2')
        expected = {'FooBar' : {'foo': 'BarFoo2'}}
        self.assertEqual(candidate.get_background, expected)

        candidate.add_background(background2, 'BarFoo3')
        expected = {'FooBar' : {'foo': 'BarFoo2', 'foo2':'BarFoo3'}}
        self.assertEqual(candidate.get_background, expected)

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
        self.assertTrue('election' in request.context)
        self.assertTrue(isinstance(request.context['election'], Election))

    def test_post_candidate_create_with_same_slug(self):
        candidate = Candidate.objects.create(name='Juan Candidato',
                                            election=self.election)
        self.client.login(username='joe', password='doe')

        f = open(os.path.join(dirname, 'media/dummy.jpg'), 'rb')
        params = {'name': 'first', 'last_name': 'last',
                  'slug': candidate.slug, 'photo': f,
                  'form-TOTAL_FORMS': u'0',
                  'form-INITIAL_FORMS': u'0',
                  'form-MAX_NUM_FORMS': u'',
                  'link-TOTAL_FORMS': u'0',
                  'link-INITIAL_FORMS': u'0',
                  'link-MAX_NUM_FORMS': u'',
                  }
        response = self.client.post(reverse('candidate_create', kwargs={'election_slug': self.election.slug}), params)
        f.close()

        self.assertEquals(response.status_code, 200)
        self.assertFormError(response, 'form', 'slug','Ya tienes un candidato con ese slug.' )

        # falta revisar que no funcione el formulario

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

    def test_post_candidate_create_logged(self):
        self.client.login(username='joe', password='doe')

        f = open(os.path.join(dirname, 'media/dummy.jpg'), 'rb')
        params = {'name': 'Juan Candidato', 'last_name': 'Candidato',
                  'slug': 'juan-candidato', 'photo': f,
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
