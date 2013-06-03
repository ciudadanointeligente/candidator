# encoding=UTF-8
from django.core.files.base import File
import json
import os
from django.conf import settings
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import IntegrityError
from elections.forms.election_form import AnswerForm
from django.template import Template, Context
from django.utils import simplejson as json
from django.utils.translation import ugettext as _

from elections.models import Election, Candidate, Category, PersonalData, \
                             BackgroundCategory, Background, PersonalDataCandidate
from elections.forms import ElectionForm, ElectionUpdateForm, PersonalDataForm, \
                            BackgroundCategoryForm, BackgroundForm, QuestionForm, \
                            CategoryForm, ElectionLogoUpdateForm, ElectionStyleUpdateForm
from elections.views import ElectionRedirectView

import random
import string

dirname = os.path.dirname(os.path.abspath(__file__))

class ElectionTagsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='doe',
                                                password='joe',
                                                email='doe@joe.cl')
        self.not_user = User.objects.create_user(username='joe',
                                                password='joe',
                                                email='doe@joe.cl')
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
                                                            election=self.election2)
    
    def test_create_link_for_updating_election_data(self):
        template = Template('{% load election_tags %}{% link_to_updating_this_election user election %}')
        
        
        context = Context({"user": self.user, "election": self.election})
        election_update_url = reverse('election_update',kwargs={'slug':self.election.slug})
        expected_html = u'<span class="goedit"><a href="'+election_update_url+u'">Editar Elección</a></span>'
        
        self.assertEqual(template.render(context), expected_html)     
    
    def test_if_is_not_the_owner(self):
        template = Template('{% load election_tags %}{% link_to_updating_this_election user election %}')
        
        
        context = Context({"user": self.not_user, "election": self.election})
        expected_html = u''
        self.assertEqual(template.render(context), expected_html)
        
        
    def test_if_there_is_no_logged_user(self):
        template = Template('{% load election_tags %}{% link_to_updating_this_election user election %}')
        
        
        context = Context({"user": None, "election": self.election})
        expected_html = u''
        self.assertEqual(template.render(context), expected_html)

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

class ElectionPhotoUpdateViewFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='joe', password=PASSWORD, email='joe@exmaple.net')
        self.user2 = User.objects.create_user(username='pepito', password=PASSWORD, email='pepito@exmaple.net')
        self.election = Election.objects.create(name='election', slug='election', owner=self.user)
        self.url = reverse('update_election_photo', kwargs={'pk': self.election.pk})
        self.new_file = open(os.path.join(dirname, 'media/dummy_logo.jpg'), 'rb')
    
    def test_get_form_as_owner(self):
        self.client.login(username=self.user.username, password=PASSWORD)
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'elections/updating/election_logo_form.html')
        self.assertTrue('form' in response.context)
        self.assertIsInstance(response.context['form'], ElectionLogoUpdateForm)
        self.assertTrue('election' in response.context)
        self.assertEqual(response.context['election'], self.election)

    def test_post_new_image_as_owner(self):
        self.client.login(username=self.user.username, password=PASSWORD)
        data = {
            'logo': self.new_file
        }
        response = self.client.post(self.url, data)
        self.new_file.seek(0)
        self.assertRedirects(response, reverse('election_update', 
                                       kwargs={'slug': self.election.slug}))
        election = Election.objects.get(pk=self.election.pk)
        self.assertEquals(election.logo.file.read(), self.new_file.read())
        os.unlink(election.logo.path)

        
    def test_get_form_as_no_user(self):
        response = self.client.get(self.url)
        self.assertRedirects(response, '/accounts/login/?next=/election/'+str(self.election.pk)+'/update_election_photo')
        
    def test_get_form_as_user_but_no_owner(self):
        self.client.login(username=self.user2.username, password=PASSWORD)
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 404)   



class ElectionCustomStyleUpdateView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='joe', password=PASSWORD, email='joe@exmaple.net')
        self.user2 = User.objects.create_user(username='doe', password=PASSWORD, email='doe@exmaple.net')
        self.election = Election.objects.create(name='election', slug='election', owner=self.user)
        self.url = reverse('update_custom_style', kwargs={'slug': self.election.slug})

    def test_get_form_for_updating_style(self):
        self.client.login(username=self.user.username, password=PASSWORD)
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'elections/updating/election_style_updating.html')
        self.assertTrue('form' in response.context)
        self.assertIsInstance(response.context['form'], ElectionStyleUpdateForm)
        self.assertTrue('election' in response.context)
        self.assertEqual(response.context['election'], self.election)

    def test_post_new_image_as_owner(self):
        self.client.login(username=self.user.username, password=PASSWORD)
        data = {
            'custom_style': 'body {background-color:red;}'
        }
        response = self.client.post(self.url, data)

        self.assertRedirects(response, reverse('update_custom_style', 
                                       kwargs={'slug': self.election.slug}))
        election = Election.objects.get(slug=self.election.slug)
        self.assertEquals(election.custom_style, data['custom_style'])


    def test_get_form_as_no_user(self):
        response = self.client.get(self.url)
        self.assertRedirects(response, '/accounts/login/?next=/election/'+str(self.election.slug)+'/update_style')
        
    def test_get_form_as_user_but_no_owner(self):
        self.client.login(username=self.user2.username, password=PASSWORD)
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 404)

    def test_get_election_created_with_the_same_slug_but_different_users(self):
        fiera = User.objects.create_user(username='Fiera', password='Feroz', email='joe@doe.cl')
        election = Election.objects.create(name='elec foo', slug='foobarbar', owner=fiera)
        user2 = User.objects.create_user(username='Doe', password='doe', email='joe@doe.cl')
        election2 = Election.objects.create(name='foobar', slug='foobarbar', owner=user2)

        self.client.login(username=fiera.username, password='Feroz')
        url = reverse('update_custom_style', kwargs={'slug': election.slug})
        response = self.client.get(reverse('election_update',
                                    kwargs={'slug': election.slug}))

        self.assertEquals(response.status_code, 200) 

    def test_post_election_created_with_the_same_slug_but_different_users(self):
        fiera = User.objects.create_user(username='Fiera', password='Feroz', email='joe@doe.cl')
        election = Election.objects.create(name='elec foo', slug='foobarbar', owner=fiera)
        user2 = User.objects.create_user(username='Doe', password='doe', email='joe@doe.cl')
        election2 = Election.objects.create(name='foobar', slug='foobarbar', owner=user2)

        self.client.login(username=fiera.username, password='Feroz')
        url = reverse('update_custom_style', kwargs={'slug': election.slug})
        data = {
            'custom_style': 'body {background-color:red;}'
        }
        response = self.client.post(url, data)

        self.assertEquals(response.status_code, 302)


class ElectionDetailViewTest(TestCase):
    def test_detail_existing_election_view(self):
        user = User.objects.create(username='foobar')
        election = Election.objects.create(name='elec foo', slug='elec-foo', owner=user, published=True)
        url = reverse('election_detail',
            kwargs={
                'username': user.username,
                'slug': election.slug
            })
        response = self.client.get(url)
        self.assertTemplateUsed(response, "elections/base.html")
        self.assertTemplateUsed(response, "elections/election_detail_profiles.html")
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

    def test_detail_non_existinmeg_election_for_user_view(self):
        user = User.objects.create(username='foobar')
        user2 = User.objects.create(username='barbaz')
        election = Election.objects.create(name='elec foo', slug='elec-foo', owner=user2, published=True)
        response = self.client.get(reverse('election_detail',
                                           kwargs={
                                               'username': user.username,
                                               'slug': election.slug}))
        self.assertEquals(response.status_code, 404)
    def test_detail_non_published_election_for_user_view(self):
        user = User.objects.create(username='foobar')
        election = Election.objects.create(name='elec foo', slug='elec-foo', owner=user)
        response = self.client.get(reverse('election_detail',
                                           kwargs={
                                               'username': user.username,
                                               'slug': election.slug}))
        self.assertEquals(response.status_code, 404)

class ElectionCompareViewTest(TestCase):
    def test_compare_existing_election_view(self):
        user = User.objects.create(username='foobar')
        election = Election.objects.create(name='elec foo', slug='elec-foo', owner=user, published=True)
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

    def test_compare_an_election_with_an_existing_slug(self):
        user = User.objects.create(username='foobar')
        election = Election.objects.create(name='elec foo', slug='elec-foo', owner=user, published=True)
        user2 = User.objects.create(username='barbaz')
        election2 = Election.objects.create(name='elec foo', slug='elec-foo', owner=user2, published=True)
        response = self.client.get(reverse('election_compare',
                                           kwargs={
                                               'username': user.username,
                                               'slug': election.slug}))

        self.assertEquals(response.status_code, 200)


    def test_compare_one_candidate_view(self):
        user = User.objects.create(username='foobar')
        election = Election.objects.create(name='elec foo', slug='elec-foo', owner=user, published=True)
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
        election = Election.objects.create(name='elec foo', slug='elec-foo', owner=user, published=True)
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
        election = Election.objects.create(name='elec foo', slug='elec-foo', owner=user, published=True)
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
        election = Election.objects.create(name='elec foo', slug='elec-foo', owner=user, published=True)
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
        election = Election.objects.create(name='elec foo', slug='elec-foo', owner=user, published=True)
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
        election = Election.objects.create(name='elec foo', slug='elec-foo', owner=user, published=True)
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

    def test_404_election_compare_asynchronous_call(self):
        user = User.objects.create(username='foobar')
        election = Election.objects.create(name='elec foo', slug='elec-foo', owner=user, published=True)
        first_candidate = Candidate.objects.create(name='bar baz', election=election)

        response = self.client.get(reverse('election_compare_asynchronous_call',
                                            kwargs={
                                                'username': user.username,
                                                'slug': election.slug,
                                                'candidate_slug': first_candidate.slug,
                                            }), HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        #405 means method not allowed
        self.assertEqual(response.status_code, 405)


    def test_comparison_with_only_one_candidate_is_being_selected(self):
        user = User.objects.create(username='foobar')
        election = Election.objects.create(name='elec foo', slug='elec-foo', owner=user, published=True)
        f = open(os.path.join(dirname, 'media/dummy.jpg'), 'rb')
        first_candidate = Candidate.objects.create(name='bar baz', election=election, photo=File(f))
        self.personal_data = PersonalData.objects.create(election=election, label='edad')
        self.personal_data_candidate = PersonalDataCandidate.objects.create(personal_data=self.personal_data,
            candidate=first_candidate,
            value=u'miles de años de edad')
        response = self.client.post(reverse('election_compare_asynchronous_call',
            kwargs={
                'username': user.username,
                'slug': election.slug,
                'candidate_slug': first_candidate.slug,
                }))

        self.assertEqual(response.status_code, 200)
        response_json = json.loads(response.content)
        expected_personal_data = {"edad":u"miles de años de edad"}
        self.assertTrue("edad" in response_json["personal_data"])
        self.assertEqual(expected_personal_data["edad"],response_json['personal_data']["edad"])


    def test_comparison_with_only_one_candidate_is_being_selected_and_the_candidate_does_not_have_photo(self):
        user = User.objects.create(username='foobar')
        election = Election.objects.create(name='elec foo', slug='elec-foo', owner=user, published=True)
        first_candidate = Candidate.objects.create(name='bar baz', election=election)


        response = self.client.post(reverse('election_compare_asynchronous_call',
            kwargs={
                'username': user.username,
                'slug': election.slug,
                'candidate_slug': first_candidate.slug,
                }))

        self.assertEqual(response.status_code, 200)

    def test_election_about(self):
        user = User.objects.create(username='foobar')
        election = Election.objects.create(name='elec foo', slug='elec-foo', owner=user)



    def test_comparison_of_two_candidates_with_no_category(self):
        user = User.objects.create(username='foobar')
        election = Election.objects.create(name='elec foo', slug='elec-foo', owner=user, published=True)
        first_candidate = Candidate.objects.create(name='bar baz', election=election)
        second_candidate = Candidate.objects.create(name='sec baz', election=election)
        url = reverse('election_compare_two_candidates_and_no_category',kwargs={
            'username': user.username,
            'slug':election.slug,
            'first_candidate_slug':first_candidate.slug,
            'second_candidate_slug':second_candidate.slug,
        })
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_comparison_of_the_same_candidate_with_no_category(self):
        user = User.objects.create(username='foobar')
        election = Election.objects.create(name='elec foo', slug='elec-foo', owner=user)
        first_candidate = Candidate.objects.create(name='bar baz', election=election)
        url = reverse('election_compare_two_candidates_and_no_category',kwargs={
            'username': user.username,
            'slug':election.slug,
            'first_candidate_slug':first_candidate.slug,
            'second_candidate_slug':first_candidate.slug,
            })
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_get_election_about(self):
        user = User.objects.create(username='foobar')
        election = Election.objects.create( name='elec foo', \
                                            slug='elec-foo', \
                                            owner=user,\
                                            description="This is a description of the election",\
                                            published=True
                                            )
        url = reverse('election_about',kwargs={
            'username': user.username,
            'slug': election.slug
        })
        response = self.client.get(url)
        self.assertContains(response,'election')
        self.assertEqual(response.context['election'], election)
        self.assertTemplateUsed(response, "elections/election_about.html")




class ElectionCreateViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='joe', password='doe', email='joe@doe.cl')



    def test_create_election_by_user_without_login(self):
        response = self.client.get(reverse('election_create'))
        self.assertEquals(response.status_code, 302)

    def test_create_election_by_user_success(self):
        self.client.login(username='joe', password='doe')
        response = self.client.get(reverse('election_create'))

        self.assertTrue('form' in response.context)
        self.assertTrue(isinstance(response.context['form'], ElectionForm))

    def test_post_election_create_with_same_name(self):
        
        election = Election.objects.create(name='BarBaz', description='whatever', owner=self.user)

        self.client.login(username=self.user.username, password='doe')
        f = open(os.path.join(dirname, 'media/dummy.jpg'), 'rb')
        params = {'name': 'BarBaz', 'description': 'esta es una descripcion', 'logo': f,'information_source':'saque la info de un lugar'}
        response = self.client.post(reverse('election_create'), params, follow=True)
        f.close()
        first_election = Election.objects.get(owner=self.user, slug="barbaz")
        second_election = Election.objects.get(owner=self.user, slug="barbaz2")

        self.assertEquals(response.status_code, 200)
        self.assertEquals(Election.objects.filter(owner=self.user, name="BarBaz").count(), 2)
        self.assertEquals(first_election.name, election.name)
        self.assertEquals(second_election.name, params["name"])


        self.assertTemplateUsed(response,'elections/wizard/step_two.html')

    def test_invalid_creation_form(self):
        election_name = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(300))
        #Haciendo que el nombre de la elección tenga más de 255 caractéres
        self.client.login(username=self.user.username, password='doe')
        f = open(os.path.join(dirname, 'media/dummy.jpg'), 'rb')
        params = {'name': election_name, 'description': 'esta es una descripcion', 'logo': f,'information_source':'saque la info de un lugar'}
        response = self.client.post(reverse('election_create'), params, follow=True)
        f.close()
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'elections/wizard/step_one.html')
        self.assertTrue(response.context['form'].errors.has_key('name'))
        


    def test_post_election_create_without_login(self):
        f = open(os.path.join(dirname, 'media/dummy.jpg'), 'rb')
        params = {'name': 'BarBaz', 'slug': 'barbaz', 'description': 'esta es una descripcion', 'logo': f}
        response = self.client.post(reverse('election_create'), params)
        f.close()

        self.assertEquals(response.status_code, 302)

    def test_post_election_create_logged(self):
        self.client.login(username='joe', password='doe')

        f = open(os.path.join(dirname, 'media/dummy.jpg'), 'rb')
        params = {'name': 'BarBaz', 'description': 'esta es una descripcion', 'logo': f,'information_source':'saque la info de un lugar'}
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
        
    def test_template_step_one(self):
        self.client.login(username='joe', password='doe')
        response = self.client.get(reverse('election_create'))
        self.assertTemplateUsed(response,'elections/wizard/step_one.html')

class ElectionUpdateViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='joe', password='doe', email='joe@doe.cl')
        self.election = Election.objects.create(name='elec foo', slug='eleccion-la-florida', owner=self.user)

    def test_update_election_by_user_without_login(self):
        response = self.client.get(reverse('election_update', kwargs={'slug': self.election.slug}))
        self.assertEquals(response.status_code, 302)

    def test_update_election_by_user_success(self):
        self.client.login(username='joe', password='doe')
        response = self.client.get(reverse('election_update', kwargs={'slug': self.election.slug}))

        self.assertTrue('form' in response.context)
        self.assertTrue(isinstance(response.context['form'], ElectionUpdateForm))
        self.assertTrue('election' in response.context)
        self.assertEqual(response.context['election'], self.election)
    
    def test_template_election_basic_information_rendered(self):
        self.client.login(username='joe', password='doe')
        response = self.client.get(reverse('election_update', kwargs={'slug': self.election.slug}))
        
        self.assertTemplateUsed(response,'elections/updating/election_basic_information.html')

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

    def test_get_election_created_with_the_same_slug_but_different_users(self):
        fiera = User.objects.create_user(username='Fiera', password='Feroz', email='joe@doe.cl')
        election = Election.objects.create(name='elec foo', slug='foobarbar', owner=fiera)
        user2 = User.objects.create_user(username='Doe', password='doe', email='joe@doe.cl')
        election2 = Election.objects.create(name='foobar', slug='foobarbar', owner=user2)

        self.client.login(username=fiera.username, password='Feroz')
        response = self.client.get(reverse('election_update',
                                    kwargs={'slug': election.slug}))

        self.assertEquals(response.status_code, 200)


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
        params = {'name': 'BarBaz', 'description': 'esta es una descripcion', 'logo': f,'information_source':u'me contó un pajarito'}
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




    def test_post_election_update_does_not_update_published_status(self):
        published_election = Election.objects.create(name='elec foo', slug='la-terrible-de-eleccion', owner=self.user, published=True)
        self.client.login(username='joe', password='doe')
        f = open(os.path.join(dirname, 'media/dummy.jpg'), 'rb')
        params = {'name': 'BarBaz', 'description': 'esta es una descripcion', 'logo': f,'information_source':u'me contó un pajarito'}
        response = self.client.post(reverse('election_update', kwargs={'slug': published_election.slug}), params, follow=True)
        f.seek(0)
        election = Election.objects.get(id=published_election.id)

        self.assertTrue(election.published)


    def test_it_contains_the_election_full_url(self):
        username = 'joe'
        self.client.login(username=username, password='doe')
        response = self.client.get(reverse('election_update', kwargs={'slug': self.election.slug}))

        self.assertTrue('election_url' in response.context)
        url = response.context['election_url']
        self.assertTrue(url.startswith('http://'))
        self.assertTrue(url.endswith(reverse('election_detail', kwargs={'username':username, 'slug': self.election.slug})))


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
        expected = '/juanito/eleccion-la-florida/gracias'
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



class SharingYourElectionButton(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='joe', password='doe', email='joe@doe.cl')
        self.election = Election.objects.create(name='elec foo', slug='eleccion-la-florida', owner=self.user)

    def test_share_my_election(self):
        self.client.login(username='joe', password='doe')
        expected_url = '/election/eleccion-la-florida/share'
        url = reverse('share_my_election', kwargs={'slug': self.election.slug})
        self.assertEquals(url, expected_url)
        self.assertEqual(self.election.published,False)
        response = self.client.get(url)
        self.election=Election.objects.get(name='elec foo', slug='eleccion-la-florida', owner=self.user)
        self.assertEqual(self.election.published,True)
        self.assertTemplateUsed(response, 'elections/updating/share.html')
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
        self.assertTemplateUsed(response, 'elections/updating/questions.html')

        self.assertTrue('personaldata_form' in response.context)
        self.assertIsInstance(response.context['personaldata_form'], PersonalDataForm)

        self.assertTrue('backgroundcategory_form' in response.context)
        self.assertIsInstance(response.context['backgroundcategory_form'], BackgroundCategoryForm)

        self.assertTrue('background_form' in response.context)
        self.assertIsInstance(response.context['background_form'], BackgroundForm)

        self.assertTrue('question_form' in response.context)
        self.assertIsInstance(response.context['question_form'], QuestionForm)

        self.assertTrue('category_form' in response.context)
        self.assertIsInstance(response.context['category_form'], CategoryForm)

        self.assertTrue('answer_form' in response.context)
        self.assertIsInstance(response.context['answer_form'], AnswerForm)


PASSWORD = 'password'

class ElectionRedirectViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='joe', password=PASSWORD, email='joe@example.net')
        self.election = Election.objects.create(owner=self.user, name='Election', slug='election')
        self.candidate = Candidate.objects.create(election=self.election, name='Candidate')
        self.candidate2 = Candidate.objects.create(election=self.election, name='Candidate2')
        self.url = reverse('election_redirect')

    def test_non_existing_election(self):
        user = User.objects.create_user(username='doe', password=PASSWORD, email='doe@example.net')
        self.client.login(username=user.username, password=PASSWORD)
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('election_create'))

    def test_existing_one_election(self):
        self.client.login(username=self.user.username, password=PASSWORD)
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('candidate_data_update',
                                       kwargs={'election_slug': self.election.slug, 'slug': self.candidate.slug}))

    def test_existing_several_elections(self):
        election = Election.objects.create(name='Another Election', owner=self.user, slug='another-election')
        candidate = Candidate.objects.create(election=election, name='Candidate2')
        self.client.login(username=self.user.username, password=PASSWORD)
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('candidate_data_update',
                                       kwargs={'election_slug': election.slug, 'slug': candidate.slug}))

    def test_existing_election_without_candidates(self):
        election = Election.objects.create(name='Another Election', owner=self.user, slug='another-election', published=True)
        self.client.login(username=self.user.username, password=PASSWORD)
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('election_detail_admin',
                                       kwargs={'slug': election.slug, 'username': self.user.username}))

    def test_not_logged(self):
        response = self.client.get(self.url)
        self.assertRedirects(response, settings.LOGIN_URL + '?next=' + self.url)


class HomeTemplateView(TestCase):
    def test_it_brings_the_last_five_create_elections(self):
        self.user = User.objects.create_user(username='joe', password=PASSWORD, email='joe@example.net')
        election1 = Election.objects.create(owner=self.user, name='Election', slug='election1', published=True)
        election2 = Election.objects.create(owner=self.user, name='Election', slug='election2', published=True)
        election3 = Election.objects.create(owner=self.user, name='Election', slug='election3', published=True)
        election4 = Election.objects.create(owner=self.user, name='Election', slug='election4', published=True)
        election5 = Election.objects.create(owner=self.user, name='Election', slug='election5', published=True)
        election6 = Election.objects.create(owner=self.user, name='Election', slug='election6', published=True)
        self.url = reverse('home')
        response = self.client.get(self.url)
        self.assertTrue('last_elections' in response.context)
        elections = response.context['last_elections']
        self.assertTrue(elections.count() == 5)
        self.assertTrue(elections[0] == election6)

        
    def test_it_brings_the_last_created_and_published_elections(self):
        self.user = User.objects.create_user(username='joe', password=PASSWORD, email='joe@example.net')
        election1 = Election.objects.create(owner=self.user, name='Election', slug='election1', published=True)
        election2 = Election.objects.create(owner=self.user, name='Election', slug='election2', published=True)
        election3 = Election.objects.create(owner=self.user, name='Election', slug='election3')
        election4 = Election.objects.create(owner=self.user, name='Election', slug='election4')
        election5 = Election.objects.create(owner=self.user, name='Election', slug='election5')
        election6 = Election.objects.create(owner=self.user, name='Election', slug='election6')
        self.url = reverse('home')
        response = self.client.get(self.url)
        self.assertTrue('last_elections' in response.context)
        elections = response.context['last_elections']
        self.assertTrue(elections.count() == 2)
        self.assertTrue(elections[0] == election2)
        
    def test_it_brings_the_just_five_highlighted_elections(self):
        self.user = User.objects.create_user(username='joe', password=PASSWORD, email='joe@example.net')
        election1 = Election.objects.create(owner=self.user, name='Election', slug='election1', published=True, highlighted=True)
        election2 = Election.objects.create(owner=self.user, name='Election', slug='election2', published=True, highlighted=True)
        election3 = Election.objects.create(owner=self.user, name='Election', slug='election3', published=True, highlighted=True)
        election4 = Election.objects.create(owner=self.user, name='Election', slug='election4', published=True, highlighted=True)
        election5 = Election.objects.create(owner=self.user, name='Election', slug='election5', published=True, highlighted=True)
        election6 = Election.objects.create(owner=self.user, name='Election', slug='election6', published=True, highlighted=True)
        self.url = reverse('home')
        response = self.client.get(self.url)
        self.assertTrue('highlighted_elections' in response.context)
        elections = response.context['highlighted_elections']
        self.assertTrue(elections.count() == 5)

        
    # def test_it_brings_the_last_created_and_published_elections(self):
    #     self.user = User.objects.create_user(username='joe', password=PASSWORD, email='joe@example.net')
    #     election1 = Election.objects.create(owner=self.user, name='Election', slug='election1', published=True)
    #     election2 = Election.objects.create(owner=self.user, name='Election', slug='election2', published=True)
    #     election3 = Election.objects.create(owner=self.user, name='Election', slug='election3')
    #     election4 = Election.objects.create(owner=self.user, name='Election', slug='election4')
    #     election5 = Election.objects.create(owner=self.user, name='Election', slug='election5')
    #     election6 = Election.objects.create(owner=self.user, name='Election', slug='election6')
    #     self.url = reverse('home')
    #     response = self.client.get(self.url)
    #     self.assertTrue('last_elections' in response.context)
    #     elections = response.context['last_elections']
    #     self.assertTrue(elections.count() == 2)
    #     self.assertTrue(elections[0] == election2)
    #     self.assertTrue('values' in response.context)
    #     self.assertTrue(response.context['values'] == [1,2])
        

class EmbededTestTemplateView(TestCase):

    def test_shows_prueba_html(self):
        url = reverse('prueba_embeded')
        response = self.client.get(url)

        self.assertTemplateUsed(response, 'prueba.html')
        self.assertTrue('embeded_test_web' in response.context)


class UserElectionsViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='joe', password=PASSWORD, email='joe@example.net')
        self.election1 = Election.objects.create(owner=self.user, name='Election', slug='election1', published=True, highlighted=False)
        election2 = Election.objects.create(owner=self.user, name='Election', slug='election2', published=False, highlighted=False)
        self.url = reverse('user_elections',kwargs={ 'username':self.user.username })

    def test_any_user_can_see_another_users_election(self):


        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'elections/users_election_list.html')
        self.assertTrue('elections' in response.context)
        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.context['elections'].count(), 1)
        self.assertEqual(response.context['elections'][0], self.election1 )
        self.assertTrue('owner' in response.context)
        self.assertEqual(response.context['owner'], self.user)



class Municipales2012ElectionTemplateView(TestCase):
    def test_renders_a_html_for_this_new_event(self):
        url = reverse('municipales2012')
        response = self.client.get(url)

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'municipales2012.html')

class TogglePublish(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='joe', password=PASSWORD, email='joe@example.net')
        self.user2 = User.objects.create_user(username='maria', password=PASSWORD, email='maria@example.net')
        self.election1 = Election.objects.create(owner=self.user, name='Election', slug='election1', published=False, highlighted=False)

    def test_to_publish_election(self):
        self.client.login(username=self.user.username, password=PASSWORD)
        url = reverse('toggle_publish',kwargs={ 'pk':self.election1.id })
        response = self.client.post(url)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response['Content-Type'], 'application/json')
        data = json.loads(response.content)
        self.assertEquals(data['id'], self.election1.id)
        self.assertTrue(data['published'])
        election1 = Election.objects.get( id=self.election1.id )
        self.assertTrue(election1.published)

    def test_to_unpublish_election(self):
        self.election1.published = True
        self.election1.save()
        self.client.login(username=self.user.username, password=PASSWORD)
        url = reverse('toggle_publish',kwargs={ 'pk':self.election1.id })
        response = self.client.post(url)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response['Content-Type'], 'application/json')
        data = json.loads(response.content)
        self.assertEquals(data['id'], self.election1.id)
        self.assertFalse(data['published'])
        election1 = Election.objects.get( id=self.election1.id )
        self.assertFalse(election1.published)

    def test_not_logged_to_publish(self):
        url = reverse('toggle_publish',kwargs={ 'pk':self.election1.id })
        response = self.client.post(url)
        self.assertEquals(response.status_code, 401)

    def test_not_owner_to_publish(self):
        self.client.login(username=self.user2.username, password=PASSWORD)
        url = reverse('toggle_publish',kwargs={ 'pk':self.election1.id })
        response = self.client.post(url)
        self.assertEquals(response.status_code, 403)

    def test_get_to_publish(self):
        self.client.login(username=self.user.username, password=PASSWORD)
        url = reverse('toggle_publish',kwargs={ 'pk':self.election1.id })
        response = self.client.get(url)
        self.assertEquals(response.status_code, 405)

    def test_get_to_publish_if_not_logged(self):
        url = reverse('toggle_publish',kwargs={ 'pk':self.election1.id })
        response = self.client.get(url)
        self.assertEquals(response.status_code, 401)


