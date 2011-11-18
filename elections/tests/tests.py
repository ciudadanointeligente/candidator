"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from elections.models import Candidate, Election, Category, Question, Answer
from elections.forms import question_formset_factory, QuestionForm, CategoryForm


class QuestionFormTest(TestCase):
    '''
    TODO: Test for QuestionForm
    '''
    def test_question_factory(self):
        user, created = User.objects.get_or_create(username='foo')
        election, created = Election.objects.get_or_create(name='foo', owner=user)
        category, created = Category.objects.get_or_create(name='foo', election=election)
        question1, created = Question.objects.get_or_create(question='bar', category=category)
        answers = [
            Answer.objects.create(caption='si', question=question1),
            Answer.objects.create(caption='no', question=question1),
        ]
        question_choices = [(a.pk, a.caption) for a in answers]
        question2, created = Question.objects.get_or_create(question='baz', category=category)
        formset = question_formset_factory(category)

        self.assertEquals(formset.max_num, 2)
        self.assertEquals(formset.total_form_count(), 2)
        form = formset[0]
        self.assertTrue(isinstance(form, QuestionForm))
        self.assertEquals(form.fields['answers'].choices, question_choices)
        self.assertEquals(form.fields['question'], question1.pk)

        form = formset[1]
        self.assertTrue(isinstance(form, QuestionForm))
        self.assertEquals(form.fields['answers'].choices, [])
        self.assertEquals(form.fields['question'], question2.pk)


class CandidateTest(TestCase):
    def test_create_candidate(self):
        user, created = User.objects.get_or_create(username='joe')
        election, created = Election.objects.get_or_create(name='BarBaz',
                                                            owner=user,
                                                            slug='barbaz')
        candidate, created = Candidate.objects.get_or_create(first_name='Foo',
                                                            last_name='Bar',
                                                            election=election,
                                                            slug='foobar')
        self.assertEqual(candidate.first_name, 'Foo')
        self.assertEqual(candidate.last_name, 'Bar')
        self.assertEqual(candidate.slug, 'foobar')
        self.assertEqual(candidate.election, election)

    def test_name_property(self):
        candidate = Candidate()
        candidate.first_name = 'Juanito'
        candidate.last_name = 'Perez'

        expected_name = 'Juanito Perez'

        self.assertEqual(candidate.name, expected_name)

class ElectionTest(TestCase):
    def test_create_election(self):
        user, created = User.objects.get_or_create(username='joe')
        election, created = Election.objects.get_or_create(name='BarBaz',
                                                            owner=user,
                                                            slug='barbaz',
                                                            description='esta es una descripcion')

        self.assertEqual(election.name, 'BarBaz')
        self.assertEqual(election.owner, user)
        self.assertEqual(election.slug, 'barbaz')
        self.assertEquals(election.description, 'esta es una descripcion')

    def test_create_election_by_user_without_login(self):
        user, created = User.objects.get_or_create(username='joe')
        request = self.client.get(reverse('create_election',
                                            kwargs={'my_user': user}))
        self.assertEquals(request.status_code, 302)

    def test_create_election_by_user_success(self):
        user, created = User.objects.get_or_create(username='joe')
        self.client.login(username='joe', password='doe')
        request = self.client.get(reverse('create_election',
                                            kwargs={'my_user': user}))
        self.assertEqual(request.status_code, 200)

        form = ElectionForm()
        self.assertTrue(request.context.has_key('form'))
        self.assertEquals(request.context['form'], form)

    def test_create_two_election_by_same_user_with_same_slug(self):
        user, created = User.objects.get_or_create(username='joe')
        election, created = Election.objects.get_or_create(name='BarBaz',
                                                            owner=user,
                                                            slug='barbaz',
                                                            description='esta es una descripcion')
                                            
        try:
            election2, created = Election.objects.get_or_create(name='BarBaz2',
                                                                owner=user,
                                                                slug='barbaz',
                                                                description='esta es una descripcion2')
        except:
            created = False
            
        self.assertFalse(created)

    
class CategoryTest(TestCase):
    def setUp(self):
        self.user, created = User.objects.get_or_create(username='joe', password='doe')
        self.election, created = Election.objects.get_or_create(name='BarBaz',
                                                            owner=self.user,
                                                            slug='barbaz')

    def test_create_category(self):
        category, created = Category.objects.get_or_create(name='FooCat',
                                                            election=self.election)

        self.assertEqual(category.name, 'FooCat')
        self.assertEqual(category.election, self.election)

    def test_get_add_category_by_user_without_login(self):
        request = self.client.get(reverse('add_category',
                                            kwargs={'election_slug': self.election.slug}))
        self.assertEquals(request.status_code, 302)

    def test_get_add_category_by_user_election_not_owned_by_user(self):
        user2 , created = User.objects.get_or_create(username='doe', password='doe')
        election2, created = Election.objects.get_or_create(name='FooBar',
                                                            owner=user2,
                                                            slug='foobar')
        self.client.login(username='joe', password='doe')
        request = self.client.get(reverse('add_category',
                                            kwargs={'election_slug': election2.slug}))
        self.assertEqual(request.status_code, 404)

    def test_get_add_category_by_user_success(self):
        self.client.login(username='joe', password='doe')
        request = self.client.get(reverse('add_category',
                                            kwargs={'election_slug': self.election.slug}))
        self.assertEqual(request.status_code, 200)

        form = CategoryForm()
        self.assertTrue(request.context.has_key('form'))
        self.assertEquals(request.context['form'], form)

    def test_post_add_category_by_user_without_login(self):
        request = self.client.post(reverse('add_category',
                                            kwargs={'election_slug': self.election.slug}))
        self.assertEquals(request.status_code, 302)

    def test_post_add_category_by_user_election_not_owned_by_user(self):
        user2 , created = User.objects.get_or_create(username='doe', password='doe')
        election2, created = Election.objects.get_or_create(name='FooBar',
                                                            owner=user2,
                                                            slug='foobar')
        self.client.login(username='joe', password='doe')
        request = self.client.post(reverse('add_category',
                                            kwargs={'election_slug': election2.slug}))
        self.assertEqual(request.status_code, 404)

    def test_post_add_category_success(self):
        new_category_name = 'FooCat'

        self.client.login(username='joe', password='doe')
        request=self.client.post(reverse('add_category',
                                            kwargs={'election_slug': self.election.slug}),
                                 {'name': new_category_name})

        self.assertEqual(request.status_code, 200)

        self.assertTrue(request.context.has_key('category'))
        self.assertEquals(request.context['category'], new_category_name)

        categories = [ str(c) for c in self.election.category_set.all()]
        self.assertTrue(new_category_name in categories)


class QuestionsTest(TestCase):
    def test_create_question(self):
        user, created = User.objects.get_or_create(username='joe')
        election, created = Election.objects.get_or_create(name='BarBaz',
                                                            owner=user,
                                                            slug='barbaz')
        category, created = Category.objects.get_or_create(name='FooCat',
                                                            election=election)
        question = Question.objects.create(question='Foo', category=category)
        self.assertEquals(question.question, 'Foo')
        self.assertEquals(question.category, category)


class AnswersTest(TestCase):
    def test_create_answer(self):
        user, created = User.objects.get_or_create(username='joe')
        election, created = Election.objects.get_or_create(name='BarBaz',
                                                            owner=user,
                                                            slug='barbaz')
        category, created = Category.objects.get_or_create(name='FooCat',
                                                            election=election)
        question, created = Question.objects.get_or_create(question='Foo',
                                                            category=category)
        answer = Answer.objects.create(question=question, caption='Bar')
        self.assertEquals(answer.caption, 'Bar')
        self.assertEquals(answer.question, question)


class CandidateAnswerTest(TestCase):
    def setUp(self):
        #TODO: make pretty
        user, created = User.objects.get_or_create(username='joe')
        election, created = Election.objects.get_or_create(name='BarBaz',
                                                            owner=user,
                                                            slug='barbaz')
        candidate, created = Candidate.objects.get_or_create(first_name='Bar',
                                                            last_name='Baz',
                                                            election=election,
                                                            slug='barbaz')
        category, created = Category.objects.get_or_create(name='FooCat',
                                                            election=election)
        question, created = Question.objects.get_or_create(question='Foo',
                                                            category=category)
        question2, created = Question.objects.get_or_create(question='Bar',
                                                            category=category)
        answer, created = Answer.objects.get_or_create(question=question,
                                                        caption='Bar')
        answer2, created = Answer.objects.get_or_create(question=question,
                                                        caption='Bar')
        answer3, created = Answer.objects.get_or_create(question=question2,
                                                        caption='Bar')
        self.user = user
        self.election = election
        self.candidate = candidate
        self.category = category
        self.question = question
        self.question2 = question2
        self.answer = answer
        self.answer2 = answer2
        self.answer3 = answer3

    def test_associate_candidate_answer(self):
        self.candidate.associate_answer(self.answer)
        self.assertEquals(list(self.candidate.answers.all()), [self.answer])

    def test_associate_candidate_answer_same_question(self):
        self.candidate.associate_answer(self.answer)
        self.candidate.associate_answer(self.answer2)
        self.assertEquals(list(self.candidate.answers.all()), [self.answer2])

    def test_associate_candidate_second_answer(self):
        self.candidate.associate_answer(self.answer2)
        self.candidate.associate_answer(self.answer3)
        self.assertEquals(list(self.candidate.answers.all()),
                            [self.answer2, self.answer3])


class AssociateCandidatesAnswersTest(TestCase):
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
        self.candidate, created = Candidate.objects.get_or_create(
                                                            first_name='Bar',
                                                            last_name='Baz',
                                                            election=self.election,
                                                            slug='barbaz')
        self.candidate2, created = Candidate.objects.get_or_create(
                                                            first_name='Bar',
                                                            last_name='Baz',
                                                            election=self.election2,
                                                            slug='barbaz')
        categories = [
            Category.objects.get_or_create(election=self.election,
                                            name='Cat1'),
            Category.objects.get_or_create(election=self.election,
                                            name='Cat2'),
        ]
        self.categories = [cat for cat, created in categories]
        category2, created = Category.objects.get_or_create(election=self.election2,
                                                     name='Cat2')
        question, created = Question.objects.get_or_create(question='Foo',
                                                            category=self.categories[0])
        question2, created = Question.objects.get_or_create(question='Foo',
                                                            category=category2)
        self.answer, created = Answer.objects.get_or_create(question=question,
                                                       caption='Bar')
        self.answer2, created = Answer.objects.get_or_create(question=question2,
                                                       caption='Bar')

    def test_get_associate_answers_to_candidate_view(self):
        # GET without login
        request = self.client.get(reverse('associate_answer_candidate',
                                            kwargs={'slug': self.candidate2.slug,
                                                    'election_slug': self.election.slug}))
        self.assertEquals(request.status_code, 302)

        # GET of non existing candidate/user pair associated with the logged in user
        self.client.login(username='joe', password='joe')
        request = self.client.get(reverse('associate_answer_candidate',
                                            kwargs={'slug': self.candidate2.slug,
                                                    'election_slug': self.election.slug}))
        self.assertEquals(request.status_code, 404)

        # GET of existing candidate/user pair associated with the logged in user
        self.client.login(username='doe', password='joe')
        request=self.client.get(reverse('associate_answer_candidate',
                                            kwargs={'slug': self.candidate.slug,
                                                    'election_slug': self.election.slug}))
        self.assertEquals(request.status_code, 200)

        self.assertTrue(request.context.has_key('candidate'))
        self.assertEquals(request.context['candidate'], self.candidate)

        self.assertTrue(request.context.has_key('categories'))
        self.assertEquals(list(request.context['categories'].all()), self.categories)

    def test_post_associate_answer_to_candidate_view(self):
        request = self.client.post(reverse('associate_answer_candidate',
                                            kwargs={'slug': self.candidate2.slug,
                                                    'election_slug': self.election.slug}),
                                 {'answer': self.answer.pk})
        self.assertEquals(request.status_code, 302)

        self.client.login(username='joe', password='joe')
        request = self.client.post(reverse('associate_answer_candidate',
                                            kwargs={'slug': self.candidate2.slug,
                                                     'election_slug': self.election.slug}),
                                 {'answer': self.answer.pk})
        self.assertEquals(request.status_code, 404)

        self.client.login(username='doe', password='joe')
        request=self.client.post(reverse('associate_answer_candidate',
                                            kwargs={'slug': self.candidate.slug,
                                                    'election_slug': self.election.slug}),
                                 {'answer': self.answer.pk})
        self.assertEquals(request.status_code, 200)
        self.assertEquals(request.content, '{"answer": %d}' % self.answer.pk)
        self.assertEquals(list(self.candidate.answers.all()), [self.answer])

        self.client.login(username='doe', password='joe')
        request=self.client.post(reverse('associate_answer_candidate',
                                         kwargs={'slug': self.candidate.slug,
                                                 'election_slug': self.election.slug}),
                                 {'answer': self.answer2.pk})
        self.assertEquals(request.status_code, 404)


class TestRedirection(TestCase):
    def test_reverse_routing_elections_correctly(self):
        from django.contrib.auth.models import User
        from django.core.urlresolvers import reverse
        user, created = User.objects.get_or_create(username="otroUsuario")
        election, created = Election.objects.get_or_create(name="mi nueva eleccion",slug="mi-nueva-eleccion",owner=user)
        url = reverse("medianaranja1",kwargs={'my_user': 'otroUsuario', 'election_slug':'mi-nueva-eleccion'})
        expected = "/otroUsuario/mi-nueva-eleccion/medianaranja/"
        self.assertEqual(url,expected)
