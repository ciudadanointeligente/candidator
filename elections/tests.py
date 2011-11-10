"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from elections.models import Candidate

class CandidateTest(TestCase):
    def test_name_property(self):
        candidate = Candidate()
        candidate.first_name = 'Juanito'
        candidate.last_name = 'Perez'

        expected_name = 'Juanito Perez'

        self.assertEqual(candidate.name, expected_name)
