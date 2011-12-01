from django.conf import settings
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import IntegrityError

from elections.models import Election, BackgroundCategory, Background
from elections.forms import BackgroundForm


class BackgroundModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='joe', password='doe', email='joe@doe.cl')
        self.election, created = Election.objects.get_or_create(name='BarBaz',
                                                            owner=self.user,
                                                            slug='barbaz')
        self.background_category, created = BackgroundCategory.objects.get_or_create(election=self.election,
                                                                    name='FooBar',
                                                                    slug='foobar')

    def test_create_background(self):
        background, created = Background.objects.get_or_create(category=self.background_category,
                                                                name='foo',
                                                                slug='foo')
        self.assertTrue(created)
        self.assertEqual(background.name, 'foo')
        self.assertEqual(background.category, self.background_category)
        self.assertEqual(background.slug, 'foo')

    def test_create_background_with_same_slug(self):
        background, created = Background.objects.get_or_create(category=self.background_category,
                                                                name='foo',
                                                                slug='foo')
        self.assertRaises(IntegrityError, Background.objects.create,
                      name='fooabr', slug='foo', category=self.background_category)

class BackgroundCreateView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='joe', password='doe', email='joe@doe.cl')
        self.election, created = Election.objects.get_or_create(name='BarBaz',
                                                            owner=self.user,
                                                            slug='barbaz')
        self.background_category, created = BackgroundCategory.objects.get_or_create(election=self.election,
                                                                    name='FooBar',
                                                                    slug='foobar')

    def test_create_background_by_user_without_login(self):
        request = self.client.get(reverse('background_create',
                                    kwargs={'background_category_slug': self.background_category.slug}))
        self.assertEquals(request.status_code, 302)

    def test_create_background_by_user_success(self):
        self.client.login(username='joe', password='doe')
        request = self.client.get(reverse('background_create',
                                    kwargs={'background_category_slug': self.background_category.slug}))

        self.assertEqual(request.status_code, 200)
        self.assertTrue('form' in request.context)
        self.assertTrue(isinstance(request.context['form'], BackgroundForm))
        self.assertTrue('background_category' in request.context)
        self.assertTrue(isinstance(request.context['background_category'], BackgroundCategory))

    def test_post_background_create_with_same_slug(self):
        background, created = Background.objects.get_or_create(category=self.background_category,
                                                                    name='foo',
                                                                    slug='foo')
        self.client.login(username='joe', password='doe')
        params = {'name': 'Bar', 'slug': 'foo'}
        response = self.client.post(reverse('background_create',
                                        kwargs={'background_category_slug': self.background_category.slug}),
                                    params)

        self.assertEquals(response.status_code, 200)
        self.assertFormError(response, 'form', 'slug','Ya tienes un antecedente con ese slug.' )


    def test_post_background_create_without_login(self):
        params = {'name': 'Bar', 'slug': 'bar'}
        response = self.client.post(reverse('background_create',
                                        kwargs={'background_category_slug': self.background_category.slug}),
                                    params)

        self.assertEquals(response.status_code, 302)

    def test_get_background_create_with_login_stranger_background_category(self):
        self.client.login(username='joe', password='doe')
        response = self.client.get(reverse('background_create',
                                    kwargs={'background_category_slug': 'strager_background_category_slug'}))
        self.assertEquals(response.status_code, 404)

    def test_post_background_create_with_login_stranger_background_category(self):
        self.client.login(username='joe', password='doe')

        params = {'name': 'Bar', 'slug': 'bar'}
        response = self.client.post(reverse('background_create',
                                        kwargs={'background_category_slug': 'strager_background_category_slug'}),
                                    params)
        self.assertEquals(response.status_code, 404)

    def test_post_background_create_logged(self):
        self.client.login(username='joe', password='doe')

        params = {'name': 'Bar', 'slug': 'bar'}
        response = self.client.post(reverse('background_create',
                                        kwargs={'background_category_slug': self.background_category.slug}),
                                    params,
                                    follow=True)

        self.assertEquals(response.status_code, 200)
        qs = Background.objects.filter(name='Bar')
        self.assertEquals(qs.count(), 1)
        background = qs.get()
        self.assertEqual(background.name, params['name'])
        self.assertEqual(background.category, self.background_category)
        self.assertEqual(background.slug, params['slug'])

        self.assertRedirects(response, reverse('background_category_create',
                                               kwargs={'election_slug': self.election.slug}))