import os
from django.conf import settings
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import IntegrityError

from elections.models import PersonalInformation, Candidate, Election
# from elections.forms import PersonalInformation


class PersonalInformationModelTest(TestCase):
    def setUp(self):
        self.user, created = User.objects.get_or_create(username='joe')
        self.election, created = Election.objects.get_or_create(name='BarBaz',
                                                           owner=self.user,
                                                           slug='barbaz',
                                                           description='esta es una descripcion')

        self.candidate, created = Candidate.objects.get_or_create(first_name='Juan',
                                                                  last_name='Candidato',
                                                                  slug='juan-candidato',
                                                                  election=self.election)
    def test_create_personal_information(self):
        personal_information, created = PersonalInformation.objects.get_or_create(
                                                            label='Nombre',
                                                            value='Juan',
                                                            candidate=self.candidate)
        self.assertTrue(created)
        self.assertEqual(personal_information.label, 'Nombre')
        self.assertEqual(personal_information.value, 'Juan')
        self.assertEqual(personal_information.candidate, self.candidate)

    def test_create_two_personal_information_with_same_label(self):
        personal_information = PersonalInformation.objects.create(
                                                            label='Nombre',
                                                            value='Juan',
                                                            candidate=self.candidate)

        self.assertRaises(IntegrityError, PersonalInformation.objects.create,
                          label='Nombre', value='Pedro', candidate=self.candidate)
