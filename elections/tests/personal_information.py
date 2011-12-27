import os
from django.conf import settings
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import IntegrityError

from elections.models import PersonalInformation, Candidate, Election
from elections.forms import CandidatePersonalInformationFormset

dirname = os.path.dirname(os.path.abspath(__file__))

class PersonalInformationModelTest(TestCase):
    def setUp(self):
        self.user, created = User.objects.get_or_create(username='joe')
        self.election, created = Election.objects.get_or_create(name='BarBaz',
                                                           owner=self.user,
                                                           slug='barbaz',
                                                           description='esta es una descripcion')

        self.candidate = Candidate.objects.create(name='Juan Candidato', election=self.election)

    def test_create_personal_information(self):
        personal_information, created = PersonalInformation.objects.get_or_create(
                                                            label='Nombre',
                                                            value='Juan',
                                                            candidate=self.candidate)
        self.assertTrue(created)
        self.assertEqual(personal_information.label, 'Nombre')
        self.assertEqual(personal_information.value, 'Juan')
        self.assertEqual(personal_information.candidate, self.candidate)


##Ya no se usa
#class CreateCandidatePersonalInformationViewTest(TestCase):
#    def setUp(self):
#        self.user = User.objects.create_user(username='joe', password='doe', email='asd@asd.cl')
#        self.election, created = Election.objects.get_or_create(name='BarBaz',
#                                                           owner=self.user,
#                                                           slug='barbaz',
#                                                           description='esta es una descripcion')
#
#        self.candidate, created = Candidate.objects.get_or_create(first_name='Juan',
#                                                                  last_name='Candidato',
#                                                                  slug='juan-candidato',
#                                                                  election=self.election)
#
#    def test_create_candidate_with_personal_information_by_user_success(self):
#        self.client.login(username='joe', password='doe')
#        request = self.client.get(reverse('candidate_create', kwargs={'election_slug': self.election.slug}))
#
#        self.assertTrue('personal_information_formset' in request.context)
#        self.assertTrue(isinstance(request.context['personal_information_formset'], CandidatePersonalInformationFormset))
#
#
#    def test_post_candidate_create_with_personal_information_logged(self):
#        self.client.login(username='joe', password='doe')
#
#        f = open(os.path.join(dirname, 'media/dummy.jpg'), 'rb')
#        params = {'first_name': 'Juan', 'last_name': 'Candidato',
#                  'slug': 'nuevo_candidato_slug', 'photo': f,
#                  'form-TOTAL_FORMS': u'2',
#                  'form-INITIAL_FORMS': u'0',
#                  'form-MAX_NUM_FORMS': u'',
#                  'form-0-label': 'Foo',
#                  'form-0-value': 'Bar',
#                  'form-1-label': 'Foo2',
#                  'form-1-value': 'Bar2',
#                  'link-TOTAL_FORMS': u'0',
#                  'link-INITIAL_FORMS': u'0',
#                  'link-MAX_NUM_FORMS': u'',}
#        response = self.client.post(reverse('candidate_create', kwargs={'election_slug': self.election.slug}), params, follow=True)
#        f.seek(0)
#
#        candidate = Candidate.objects.get(slug=params['slug'])
#        self.assertEqual(candidate.personalinformation_set.count(), 2)
#
#        personal_information = candidate.personalinformation_set.all()[0]
#        self.assertEqual(personal_information.label, params['form-0-label'])
#        self.assertEqual(personal_information.value, params['form-0-value'])
#
#        personal_information = candidate.personalinformation_set.all()[1]
#        self.assertEqual(personal_information.label, params['form-1-label'])
#        self.assertEqual(personal_information.value, params['form-1-value'])
#
