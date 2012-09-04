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
from django.utils.translation import ugettext as _

from django.core.urlresolvers import resolve

from elections.models import Election, Candidate, Category, PersonalData, BackgroundCategory, Background, PersonalDataCandidate, Question, Answer
from elections.forms import ElectionForm, ElectionUpdateForm, PersonalDataForm, BackgroundCategoryForm, BackgroundForm, QuestionForm, CategoryForm, ElectionLogoUpdateForm
from elections.views import ElectionRedirectView, ElectionDetailView

dirname = os.path.dirname(os.path.abspath(__file__))



class ElectionEmbededDetail(TestCase):
	def setUp(self):
		self.user = User.objects.create(username='foobar')
		self.election = Election.objects.create(name='elec foo', slug='elec-foo', owner=self.user, published=True)
		#Deleting default categories
		for category in self.election.category_set.all():
			category.delete()
		#end of deleting
		f = open(os.path.join(dirname, 'media/dummy.jpg'), 'rb')
		self.candidate_one = Candidate.objects.create(name='bar baz', election = self.election, photo=File(f))
		self.candidate_two = Candidate.objects.create(name='foo fii', election = self.election, photo=File(f))
		self.category1, created = Category.objects.get_or_create(name='FooCat',
																election=self.election,
																slug='foo-cat')
		self.category2, created = Category.objects.get_or_create(name='FooCat2',
																election=self.election,
																slug='foo-cat-2')
		self.question1, created = Question.objects.get_or_create(question='FooQuestion',
																category=self.category1)
		self.question2, created = Question.objects.get_or_create(question='BarQuestion',
																category=self.category2)
		self.answer1_1, created = Answer.objects.get_or_create(question=self.question1,
																caption='BarAnswer1Question1')
		self.answer1_2, created = Answer.objects.get_or_create(question=self.question2,
																caption='BarAnswer1Question2')
		self.answer2_1, created = Answer.objects.get_or_create(question=self.question1,
																caption='BarAnswer2uestion1')
		self.answer2_2, created = Answer.objects.get_or_create(question=self.question2,
																caption='BarAnswer2Question2')

		self.candidate_one.associate_answer(self.answer1_1)
		self.candidate_one.associate_answer(self.answer1_2)
		self.candidate_two.associate_answer(self.answer2_1)
		self.candidate_two.associate_answer(self.answer2_2)

	def test_detail_embeded_view_url(self):
		
		url = reverse('election_detail_embeded',kwargs={'username': self.user.username,'slug': self.election.slug})
		response = self.client.get(url)
		self.assertEquals(response.status_code, 200)
		self.assertTemplateUsed(response, "elections/embeded/base_embed.html")
		self.assertTemplateNotUsed(response, "elections/election_detail.html")
		self.assertTemplateUsed(response, "elections/embeded/election_detail_profiles.html")

		self.assertTrue('election' in response.context)
		self.assertEquals(response.context['election'], self.election)

		resolver_match = resolve(url)
		view = ElectionDetailView.as_view()

		self.assertEquals(resolver_match.func.__module__,view.__module__)
		self.assertEquals(resolver_match.func.__name__,view.__name__)





	def test_profiles_view(self):
		url = reverse('election_detail_profiles_embeded',kwargs={'username': self.user.username,'slug': self.election.slug})
		response = self.client.get(url)
		self.assertEquals(response.status_code, 200)
		self.assertTemplateUsed(response, "elections/embeded/base_embed.html")
		self.assertTemplateNotUsed(response, "elections/election_detail_profiles.html")
		self.assertTrue('election' in response.context)
		self.assertEquals(response.context['election'], self.election)
		resolver_match = resolve(url)
		view = ElectionDetailView.as_view()

		self.assertEquals(resolver_match.func.__module__,view.__module__)
		self.assertEquals(resolver_match.func.__name__,view.__name__)

	def test_medianaranja_view(self):
		url = reverse('medianaranja1_embeded',kwargs={'username': self.user.username,'election_slug': self.election.slug})

		response = self.client.get(url)
		self.assertEqual(response.status_code, 200)

		self.assertTrue('stt' in response.context)
		self.assertTrue('election' in response.context)
		self.assertEqual(self.election, response.context['election'])
		
		self.assertTemplateNotUsed(response, "medianaranja1.html")
		self.assertTemplateUsed(response, "elections/embeded/medianaranja1.html")
		self.assertTemplateUsed(response, "elections/embeded/base_embed.html")

		resolver_match = resolve(url)
		self.assertEquals(resolver_match.func.__module__,"candidator.elections.views.medianaranja_views")


	def test_medianaranja_to_answer_view(self):
		answers = [self.answer1_1.pk, self.answer1_2.pk]
		questions_ids = [self.answer1_1.question.pk, self.answer1_2.question.pk]
		importances = [5,3]
		importances_by_category = [5,3]
		factor_question1 = ( answers[0] == self.answer1_1.pk) * importances[0]
		factor_question2 = ( answers[1] == self.answer1_2.pk) * importances[1]
		score_category1 = factor_question1 * 100.0 / importances_by_category[0]
		score_category2 = factor_question2 * 100.0 / importances_by_category[1]
		global_score = (factor_question1 + factor_question2) * 100.0 / sum(importances_by_category)
		url = reverse('medianaranja1_embeded',kwargs={'username': self.user.username,'election_slug': self.election.slug})
		response = self.client.post(url, {'question-0': answers[0], 'question-1': answers[1], \
			'importance-0': importances[0], 'importance-1': importances[1],\
			'question-id-0': questions_ids[0], 'question-id-1': questions_ids[1]})
		expected_winner = [global_score, [score_category1, score_category1], self.candidate_one]
		self.assertEqual(response.context['winner'], expected_winner)
		self.assertEqual(response.status_code, 200)
		self.assertTemplateNotUsed(response, "medianaranja2.html")
		self.assertTemplateUsed(response, "elections/embeded/medianaranja2.html")
		self.assertTemplateUsed(response, "elections/embeded/base_embed.html")

		resolver_match = resolve(url)
		self.assertEquals(resolver_match.func.__module__,"candidator.elections.views.medianaranja_views")

	def test_medianaranja_embeded_does_not_require_csrf_token(self):
		from django.test import Client
		csrf_client = Client(enforce_csrf_checks=True)

		answers = [self.answer1_1.pk, self.answer1_2.pk]
		questions_ids = [self.answer1_1.question.pk, self.answer1_2.question.pk]
		importances = [5,3]
		importances_by_category = [5,3]
		factor_question1 = ( answers[0] == self.answer1_1.pk) * importances[0]
		factor_question2 = ( answers[1] == self.answer1_2.pk) * importances[1]
		score_category1 = factor_question1 * 100.0 / importances_by_category[0]
		score_category2 = factor_question2 * 100.0 / importances_by_category[1]
		global_score = (factor_question1 + factor_question2) * 100.0 / sum(importances_by_category)
		url = reverse('medianaranja1_embeded',kwargs={'username': self.user.username,'election_slug': self.election.slug})
		response = csrf_client.post(url, {'question-0': answers[0], 'question-1': answers[1], \
			'importance-0': importances[0], 'importance-1': importances[1],\
			'question-id-0': questions_ids[0], 'question-id-1': questions_ids[1]})


		self.assertEqual(response.status_code, 200)



	def test_compare_view(self):
		url = reverse('election_compare_embeded',kwargs={'username': self.user.username,'slug': self.election.slug})

		response = self.client.get(url)
		self.assertEqual(response.status_code, 200)
		self.assertTemplateNotUsed(response, "elections/election_compare.html")
		self.assertTemplateUsed(response, "elections/embeded/election_compare.html")
		self.assertTemplateUsed(response, "elections/embeded/base_embed.html")


	def test_compare_view_with_two_candidates_and_category(self):
		url = reverse('election_compare_two_candidates_embeded',kwargs={
			'username': self.user.username,
			'slug': self.election.slug,
			'first_candidate_slug':self.candidate_one.slug,
			'second_candidate_slug':self.candidate_two.slug,
			'category_slug':self.category1.slug

			})

		response = self.client.get(url)

		self.assertEquals(response.status_code, 200)
		self.assertTemplateNotUsed(response, "elections/election_compare.html")
		self.assertTemplateUsed(response, "elections/embeded/election_compare.html")
		self.assertTemplateUsed(response, "elections/embeded/base_embed.html")


	def test_compare_view_with_two_candidates_and_no_category(self):
		url = reverse('election_compare_two_candidates_and_no_category_embeded',kwargs={
			'username': self.user.username,
			'slug': self.election.slug,
			'first_candidate_slug':self.candidate_one.slug,
			'second_candidate_slug':self.candidate_two.slug

			})

		response = self.client.get(url)

		self.assertEquals(response.status_code, 200)
		self.assertTemplateNotUsed(response, "elections/election_compare.html")
		self.assertTemplateUsed(response, "elections/embeded/election_compare.html")
		self.assertTemplateUsed(response, "elections/embeded/base_embed.html")

	def test_compare_view_with_one_candidate_no_category(self):
		url = reverse('election_compare_one_candidate_embeded',kwargs={
			'username': self.user.username,
			'slug': self.election.slug,
			'first_candidate_slug':self.candidate_one.slug

			})
		response = self.client.get(url)

		self.assertEquals(response.status_code, 200)
		self.assertTemplateNotUsed(response, "elections/election_compare.html")
		self.assertTemplateUsed(response, "elections/embeded/election_compare.html")
		self.assertTemplateUsed(response, "elections/embeded/base_embed.html")


	def test_display_candidate_profile(self):
		url = reverse('candidate_detail_embeded',kwargs={
			'username': self.user.username,
			'election_slug': self.election.slug,
			'slug':self.candidate_one.slug
			})
		response = self.client.get(url)
		self.assertEquals(response.status_code, 200)
		self.assertTemplateNotUsed(response, "elections/candidate_detail.html")
		self.assertTemplateUsed(response, "elections/embeded/candidate_detail.html")
		self.assertTemplateUsed(response, "elections/embeded/base_embed.html")


	def test_display_election_about(self):
		url = reverse('election_about_embeded',kwargs={
			'username': self.user.username,
			'slug': self.election.slug
			})
		response = self.client.get(url)
		self.assertEquals(response.status_code, 200)
		self.assertTemplateUsed(response, "elections/embeded/base_embed.html")
		self.assertTemplateUsed(response, "elections/embeded/about.html")
		self.assertTemplateNotUsed(response, "elections/election_about.html")
		self.assertTemplateNotUsed(response, "elections/base.html")











