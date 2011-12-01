from django.conf import settings
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import IntegrityError

from elections.models import Election, BackgroundCategory
# from elections.forms import BackgroundCategoryForm


class BackgroundCategoryModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='joe', password='doe', email='joe@doe.cl')
        self.election, created = Election.objects.get_or_create(name='BarBaz',
                                                            owner=self.user,
                                                            slug='barbaz')

    def test_create_background_category(self):
        background_category, created = BackgroundCategory.objects.get_or_create(election=self.election,
                                                                    name='foo',
                                                                    slug='foo')
        self.assertTrue(created)
        self.assertEqual(background_category.name, 'foo')
        self.assertEqual(background_category.election, self.election)
        self.assertEqual(background_category.slug, 'foo')

    def test_create_background_category_with_same_slug(self):
        background_category, created = BackgroundCategory.objects.get_or_create(election=self.election,
                                                                    name='foo',
                                                                    slug='foo')
        self.assertRaises(IntegrityError, BackgroundCategory.objects.create,
                      name='fooabr', slug='foo', election=self.election)