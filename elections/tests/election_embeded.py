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

from elections.models import Election, Candidate, Category, PersonalData, BackgroundCategory, Background, PersonalDataCandidate
from elections.forms import ElectionForm, ElectionUpdateForm, PersonalDataForm, BackgroundCategoryForm, BackgroundForm, QuestionForm, CategoryForm, ElectionLogoUpdateForm
from elections.views import ElectionRedirectView, ElectionDetailView

dirname = os.path.dirname(os.path.abspath(__file__))



class ElectionEmbededDetail(TestCase):
	def setUp(self):
		self.user = User.objects.create(username='foobar')
		self.election = Election.objects.create(name='elec foo', slug='elec-foo', owner=self.user)
		f = open(os.path.join(dirname, 'media/dummy.jpg'), 'rb')
		self.candidate_one = Candidate.objects.create(name='bar baz', election = self.election, photo=File(f))
		self.candidate_two = Candidate.objects.create(name='foo fii', election = self.election, photo=File(f))
		self.category = Category.objects.create(name='asdf', election=self.election, slug='asdf')

	def test_detail_embeded_view_url(self):
		
		url = reverse('election_detail_embeded',kwargs={'username': self.user.username,'slug': self.election.slug})
		response = self.client.get(url)
		self.assertEquals(response.status_code, 200)
		self.assertTemplateUsed(response, "elections/base_embed.html")
		self.assertTemplateNotUsed(response, "elections/election_detail.html")
		self.assertTemplateUsed(response, "elections/base_embed.html")

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
		self.assertTemplateUsed(response, "elections/base_embed.html")
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
		self.assertTemplateUsed(response, "elections/base_embed.html")

		resolver_match = resolve(url)
		self.assertEquals(resolver_match.func.__module__,"candidator.elections.views.medianaranja_views")

	def test_compare_view(self):
		url = reverse('election_compare_embeded',kwargs={'username': self.user.username,'slug': self.election.slug})

		response = self.client.get(url)
		self.assertEqual(response.status_code, 200)
		self.assertTemplateNotUsed(response, "elections/election_compare.html")
		self.assertTemplateUsed(response, "elections/embeded/election_compare.html")
		self.assertTemplateUsed(response, "elections/base_embed.html")


	def test_compare_view_with_two_candidates_and_category(self):
		url = reverse('election_compare_two_candidates_embeded',kwargs={
			'username': self.user.username,
			'slug': self.election.slug,
			'first_candidate_slug':self.candidate_one.slug,
			'second_candidate_slug':self.candidate_two.slug,
			'category_slug':self.category.slug

			})

		response = self.client.get(url)

		self.assertEquals(response.status_code, 200)
		self.assertTemplateNotUsed(response, "elections/election_compare.html")
		self.assertTemplateUsed(response, "elections/embeded/election_compare.html")
		self.assertTemplateUsed(response, "elections/base_embed.html")


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
		self.assertTemplateUsed(response, "elections/base_embed.html")

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
		self.assertTemplateUsed(response, "elections/base_embed.html")












