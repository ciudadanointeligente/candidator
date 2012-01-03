# encoding=UTF-8
from django.core.files.base import File
import os
from django.conf import settings
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import IntegrityError

from elections.models import Election, Candidate, Category, PersonalData, BackgroundCategory, Background
from elections.forms import ElectionForm, ElectionUpdateForm, PersonalDataForm, BackgroundCategoryForm, BackgroundForm, QuestionForm

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





class ElectionDetailViewTest(TestCase):
    def test_detail_existing_election_view(self):
        user = User.objects.create(username='foobar')
        election = Election.objects.create(name='elec foo', slug='elec-foo', owner=user)
        response = self.client.get(reverse('election_detail',
                                           kwargs={
                                               'username': user.username,
                                               'slug': election.slug}))
        self.assertEquals(response.status_code, 200)
        self.assertTrue('election' in response.context)
        self.assertEquals(response.context['election'], election)

    def test_detail_non_existing_election_view(self):
        user = User.objects.create(username='foobar')
        response = self.client.get(reverse('election_detail',
                                           kwargs={
                                               'username': user.username,
                                               'slug': 'asd-asd'}))
        self.assertEquals(response.status_code, 404)

    def test_detail_non_existing_election_for_user_view(self):
        user = User.objects.create(username='foobar')
        user2 = User.objects.create(username='barbaz')
        election = Election.objects.create(name='elec foo', slug='elec-foo', owner=user2)
        response = self.client.get(reverse('election_detail',
                                           kwargs={
                                               'username': user.username,
                                               'slug': election.slug}))
        self.assertEquals(response.status_code, 404)


class ElectionCompareViewTest(TestCase):
    def test_compare_existing_election_view(self):
        user = User.objects.create(username='foobar')
        election = Election.objects.create(name='elec foo', slug='elec-foo', owner=user)
        response = self.client.get(reverse('election_compare',
                                           kwargs={
                                               'username': user.username,
                                               'slug': election.slug}))
        self.assertEquals(response.status_code, 200)
        self.assertTrue('election' in response.context)
        self.assertEquals(response.context['election'], election)

    def test_compare_non_existing_election_view(self):
        user = User.objects.create(username='foobar')
        response = self.client.get(reverse('election_compare',
                                           kwargs={
                                               'username': user.username,
                                               'slug': 'asd-asd'}))
        self.assertEquals(response.status_code, 404)

    def test_compare_non_existing_election_for_user_view(self):
        user = User.objects.create(username='foobar')
        user2 = User.objects.create(username='barbaz')
        election = Election.objects.create(name='elec foo', slug='elec-foo', owner=user2)
        response = self.client.get(reverse('election_compare',
                                           kwargs={
                                               'username': user.username,
                                               'slug': election.slug}))
        self.assertEquals(response.status_code, 404)

    def test_compare_one_candidate_view(self):
        user = User.objects.create(username='foobar')
        election = Election.objects.create(name='elec foo', slug='elec-foo', owner=user)
        f = open(os.path.join(dirname, 'media/dummy.jpg'), 'rb')
        candidate = Candidate.objects.create(name='bar baz', election=election, photo=File(f))
        response = self.client.get(reverse('election_compare_one_candidate',
                                           kwargs={
                                               'username': user.username,
                                               'slug': election.slug,
                                               'first_candidate_slug': candidate.slug}))
        self.assertEquals(response.status_code, 200)

    def test_compare_one_candidate_mismatch_view(self):
        user = User.objects.create(username='foobar')
        election = Election.objects.create(name='elec foo', slug='elec-foo', owner=user)
        candidate = Candidate.objects.create(name='bar baz', election=election)
        response = self.client.get(reverse('election_compare_one_candidate',
                                           kwargs={
                                               'username': user.username,
                                               'slug': election.slug,
                                               'first_candidate_slug': 'asdf'}))
        self.assertEquals(response.status_code, 404)

    def test_compare_two_candidates_view(self):
        user = User.objects.create(username='foobar')
        election = Election.objects.create(name='elec foo', slug='elec-foo', owner=user)
        f = open(os.path.join(dirname, 'media/dummy.jpg'), 'rb')
        first_candidate = Candidate.objects.create(name='bar baz', election=election, photo=File(f))
        second_candidate = Candidate.objects.create(name='tar taz', election=election, photo=File(f))
        category = Category.objects.create(name='asdf', election=election, slug='asdf')
        response = self.client.get(reverse('election_compare_two_candidates',
                                           kwargs={
                                               'username': user.username,
                                               'slug': election.slug,
                                               'first_candidate_slug': first_candidate.slug,
                                               'second_candidate_slug': second_candidate.slug,
                                               'category_slug': category}))
        self.assertEquals(response.status_code, 200)

    def test_compare_one_candidate_two_times(self):
        user = User.objects.create(username='foobar')
        election = Election.objects.create(name='elec foo', slug='elec-foo', owner=user)
        f = open(os.path.join(dirname, 'media/dummy.jpg'), 'rb')
        first_candidate = Candidate.objects.create(name='bar baz', election=election, photo=File(f))
        second_candidate = first_candidate
        category = Category.objects.create(name='asdf', election=election, slug='asdf')
        response = self.client.get(reverse('election_compare_two_candidates',
                                           kwargs={
                                               'username': user.username,
                                               'slug': election.slug,
                                               'first_candidate_slug': first_candidate.slug,
                                               'second_candidate_slug': second_candidate.slug,
                                               'category_slug': category}))
        self.assertEquals(response.status_code, 404)


    def test_compare_two_candidates_category_mismatch_view(self):
        user = User.objects.create(username='foobar')
        election = Election.objects.create(name='elec foo', slug='elec-foo', owner=user)
        first_candidate = Candidate.objects.create(name='bar baz', election=election)
        second_candidate = Candidate.objects.create(name='tar taz', election=election)
        category = Category.objects.create(name='asdf', election=election, slug='asdf')
        response = self.client.get(reverse('election_compare_two_candidates',
                                           kwargs={
                                               'username': user.username,
                                               'slug': election.slug,
                                               'first_candidate_slug': first_candidate.slug,
                                               'second_candidate_slug': second_candidate.slug,
                                               'category_slug': 'asdf2'}))
        self.assertEquals(response.status_code, 404)

    def test_compare_two_candidates_first_candidate_mismatch_view(self):
        user = User.objects.create(username='foobar')
        election = Election.objects.create(name='elec foo', slug='elec-foo', owner=user)
        first_candidate = Candidate.objects.create(name='bar baz', election=election)
        second_candidate = Candidate.objects.create(name='tar taz', election=election)
        category = Category.objects.create(name='asdf', election=election, slug='asdf')
        response = self.client.get(reverse('election_compare_two_candidates',
                                           kwargs={
                                               'username': user.username,
                                               'slug': election.slug,
                                               'first_candidate_slug': 'asdf',
                                               'second_candidate_slug': second_candidate.slug,
                                               'category_slug': category}))
        self.assertEquals(response.status_code, 404)

    def test_compare_two_candidates_second_candidate_mismatch_view(self):
        user = User.objects.create(username='foobar')
        election = Election.objects.create(name='elec foo', slug='elec-foo', owner=user)
        first_candidate = Candidate.objects.create(name='bar baz', election=election)
        second_candidate = Candidate.objects.create(name='tar taz', election=election)
        category = Category.objects.create(name='asdf', election=election, slug='asdf')
        response = self.client.get(reverse('election_compare_two_candidates',
                                           kwargs={
                                               'username': user.username,
                                               'slug': election.slug,
                                               'first_candidate_slug': first_candidate.slug,
                                               'second_candidate_slug': 'asdf',
                                               'category_slug': category}))
        self.assertEquals(response.status_code, 404)


class ElectionCreateViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='joe', password='doe', email='joe@doe.cl')

    def test_create_election_by_user_without_login(self):
        request = self.client.get(reverse('election_create'))
        self.assertEquals(request.status_code, 302)

    def test_create_election_by_user_success(self):
        self.client.login(username='joe', password='doe')
        request = self.client.get(reverse('election_create'))

        self.assertTrue('form' in request.context)
        self.assertTrue(isinstance(request.context['form'], ElectionForm))

    def test_post_election_create_with_same_slug(self):
        election = Election.objects.create(name='BarBaz1', slug='barbaz', description='whatever', owner=self.user)

        self.client.login(username='joe', password='doe')
        f = open(os.path.join(dirname, 'media/dummy.jpg'), 'rb')
        params = {'name': 'BarBaz', 'slug': 'barbaz', 'description': 'esta es una descripcion', 'logo': f}
        response = self.client.post(reverse('election_create'), params)
        f.close()

        self.assertEquals(response.status_code, 200)
        self.assertFormError(response, 'form', 'slug', 'Ya tienes una eleccion con ese slug.')


    def test_post_election_create_without_login(self):
        f = open(os.path.join(dirname, 'media/dummy.jpg'), 'rb')
        params = {'name': 'BarBaz', 'slug': 'barbaz', 'description': 'esta es una descripcion', 'logo': f}
        response = self.client.post(reverse('election_create'), params)
        f.close()

        self.assertEquals(response.status_code, 302)

    def test_post_election_create_logged(self):
        self.client.login(username='joe', password='doe')

        f = open(os.path.join(dirname, 'media/dummy.jpg'), 'rb')
        params = {'name': 'BarBaz', 'slug': 'barbaz', 'description': 'esta es una descripcion', 'logo': f}
        response = self.client.post(reverse('election_create'), params, follow=True)
        f.seek(0)

        self.assertEquals(response.status_code, 200)
        qs = Election.objects.filter(name='BarBaz')
        self.assertEquals(qs.count(), 1)
        election = qs.get()
        self.assertEquals(election.name, 'BarBaz')
        self.assertEquals(election.slug, 'barbaz')
        self.assertEquals(election.description, 'esta es una descripcion')
        self.assertEquals(f.read(), election.logo.file.read())

        os.unlink(election.logo.path)
        self.assertEquals(election.owner, self.user)
        self.assertRedirects(response, reverse('candidate_create',
                                               kwargs={'election_slug': election.slug}))


class ElectionUpdateViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='joe', password='doe', email='joe@doe.cl')
        self.election = Election.objects.create(name='elec foo', slug='eleccion-la-florida', owner=self.user)

    def test_update_election_by_user_without_login(self):
        request = self.client.get(reverse('election_update', kwargs={'slug': self.election.slug}))
        self.assertEquals(request.status_code, 302)

    def test_update_election_by_user_success(self):
        self.client.login(username='joe', password='doe')
        request = self.client.get(reverse('election_update', kwargs={'slug': self.election.slug}))

        self.assertTrue('form' in request.context)
        self.assertTrue(isinstance(request.context['form'], ElectionUpdateForm))

    def test_post_election_update_without_login(self):
        f = open(os.path.join(dirname, 'media/dummy.jpg'), 'rb')
        params = {'name': 'BarBaz', 'description': 'esta es una descripcion', 'logo': f}
        response = self.client.post(reverse('election_update', kwargs={'slug': self.election.slug}), params)
        f.close()

        self.assertEquals(response.status_code, 302)

    def test_get_election_update_strager_election(self):
        self.client.login(username='joe', password='doe')

        user2 = User.objects.create_user(username='Doe', password='doe', email='joe@doe.cl')
        election2 = Election.objects.create(name='foobar', slug='foobarbar', owner=user2)

        response = self.client.get(reverse('election_update',
                                    kwargs={'slug': election2.slug}))
        self.assertEqual(response.status_code, 404)

    def test_post_election_update_stranger_election(self):
        self.client.login(username='joe', password='doe')

        user2 = User.objects.create_user(username='Doe', password='doe', email='joe@doe.cl')
        election2 = Election.objects.create(name='foobar', slug='foobarbar', owner=user2)

        f = open(os.path.join(dirname, 'media/dummy.jpg'), 'rb')
        params = {'name': 'BarBaz', 'description': 'esta es una descripcion', 'logo': f}
        response = self.client.post(reverse('election_update',
                                        kwargs={'slug': election2.slug}),
                                    params)
        f.seek(0)
        self.assertEqual(response.status_code, 404)

    def test_post_election_update_logged(self):
        self.client.login(username='joe', password='doe')

        f = open(os.path.join(dirname, 'media/dummy.jpg'), 'rb')
        params = {'name': 'BarBaz', 'description': 'esta es una descripcion', 'logo': f}
        response = self.client.post(reverse('election_update', kwargs={'slug': self.election.slug}), params, follow=True)
        f.seek(0)

        self.assertEquals(response.status_code, 200)
        qs = Election.objects.filter(name='BarBaz')
        self.assertEquals(qs.count(), 1)
        election = qs.get()
        self.assertEquals(election.name, 'BarBaz')
        self.assertEquals(election.slug, self.election.slug)
        self.assertEquals(election.description, 'esta es una descripcion')
        self.assertEquals(f.read(), election.logo.file.read())

        os.unlink(election.logo.path)
        self.assertEquals(election.owner, self.user)
        self.assertRedirects(response, reverse('election_update',
                                               kwargs={'slug': election.slug}))


class ElectionUrlsTest(TestCase):
    def test_create_url(self):
        expected = '/election/create'
        result = reverse('election_create')
        self.assertEquals(result, expected)

    def test_pre_create_url(self):
        expected = '/election/pre_create'
        result = reverse('election_pre_create')
        self.assertEquals(result, expected)

    def test_detail_url(self):
        expected = '/juanito/eleccion-la-florida/'
        result = reverse('election_detail', kwargs={'username': 'juanito', 'slug': 'eleccion-la-florida'})
        self.assertEquals(result, expected)

    def test_compare_url(self):
        expected = '/juanito/eleccion-la-florida/compare'
        result = reverse('election_compare', kwargs={'username': 'juanito', 'slug': 'eleccion-la-florida'})
        self.assertEquals(result, expected)

    def test_compare_one_candidate_url(self):
        expected = '/juanito/eleccion-la-florida/compare/my-candidate'
        result = reverse('election_compare_one_candidate', kwargs={'username': 'juanito', 'slug': 'eleccion-la-florida', 'first_candidate_slug':'my-candidate'})
        self.assertEquals(result, expected)

    def test_compare_two_candidates_url(self):
        expected = '/juanito/eleccion-la-florida/compare/my-candidate/other-candidate/this-category'
        result = reverse('election_compare_two_candidates', kwargs={'username': 'juanito', 'slug': 'eleccion-la-florida', 'first_candidate_slug':'my-candidate', 'second_candidate_slug':'other-candidate', 'category_slug':'this-category'})
        self.assertEquals(result, expected)

    def test_update_url(self):
        expected = '/election/eleccion-la-florida/update'
        result = reverse('election_update', kwargs={'slug': 'eleccion-la-florida'})
        self.assertEquals(result, expected)

    def test_profiles_url(self):
        expected = '/juanito/eleccion-la-florida/profiles'
        result = reverse('election_detail_profiles', kwargs={'username': 'juanito', 'slug': 'eleccion-la-florida'})
        self.assertEquals(result, expected)

    def test_profiles_url(self):
        expected = '/juanito/eleccion-la-florida/admin'
        result = reverse('election_detail_admin', kwargs={'username': 'juanito', 'slug': 'eleccion-la-florida'})
        self.assertEquals(result, expected)

class PrePersonalDataViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='joe', password='doe', email='joe@doe.cl')
        self.election = Election.objects.create(name='elec foo', slug='eleccion-la-florida', owner=self.user)

    def test_context(self):
        self.client.login(username='joe', password='doe')

        response = self.client.get(reverse('pre_personaldata', kwargs={'election_slug': self.election.slug}))
        self.assertEquals(response.status_code, 200)
        self.assertTrue('election' in response.context)
        self.assertEquals(response.context['election'], self.election)


PASSWORD = 'password'


class ElectionUpdateDataViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='Joe', password=PASSWORD, email='joe@doe.cl')
        self.election = Election.objects.create(name='Foo', owner=self.user, slug='foo')
        self.url = reverse('election_update_data', kwargs={'slug': self.election.slug})

    def test_get_not_logged(self):
        response = self.client.get(self.url)
        self.assertRedirects(response, settings.LOGIN_URL + '?next=' + self.url)
        
    def test_get_not_owned_election(self):
        stranger_user = User.objects.create_user(username='John', password=PASSWORD, email='john@doe.cl')
        self.client.login(username=stranger_user.username, password=PASSWORD)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)

    def test_get_non_existing_election(self):
        url = reverse('election_update_data', kwargs={'slug': 'random_slug'})
        self.client.login(username=self.user.username, password=PASSWORD)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_get_owned_election(self):
        self.client.login(username=self.user.username, password=PASSWORD)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('election' in response.context)
        self.assertEqual(response.context['election'], self.election)
        self.assertTemplateUsed(response, 'elections/election_update_data.html')

        self.assertTrue('personaldata_form' in response.context)
        self.assertIsInstance(response.context['personaldata_form'], PersonalDataForm)

        self.assertTrue('backgroundcategory_form' in response.context)
        self.assertIsInstance(response.context['backgroundcategory_form'], BackgroundCategoryForm)
        
        self.assertTrue('background_form' in response.context)
        self.assertIsInstance(response.context['background_form'], BackgroundForm)

        self.assertTrue('question_form' in response.context)
        self.assertIsInstance(response.context['question_form'], QuestionForm)
