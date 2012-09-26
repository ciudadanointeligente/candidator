# -*- coding: utf-8 -*-


from django.test import TestCase
from elections.management.commands.elections_loader import *
from django.contrib.auth.models import User

class QuestionsParserTestCase(TestCase):
	def setUp(self):
		self.lines = [
			["category","la categoria1"],
			["question","la pregunta1"],
			["answer","respuesta 1"],
			["answer","respuesta 2"],
			["category","la categoria2"],
			["question","la pregunta2"],
			["answer","respuesta 3"],
			["answer","respuesta 4"],
		]
		self.user = User.objects.create_user(username='ciudadanointeligente',
                                                password='fci',
                                                email='fci@ciudadanointeligente.cl')
		self.election = Election.objects.create(owner=self.user, name="Elección para molestar a Marcel")
		[category.delete() for category in self.election.category_set.all()]

	def test_create_categories(self):
		parser = QuestionsParser(self.election)
		parser.createQuestions(self.lines)
		election_after_questions_created = Election.objects.get(pk=self.election.pk)
		
		self.assertEquals(election_after_questions_created.category_set.count(), 2 )
		self.assertEquals(election_after_questions_created.category_set.all()[0].name, u"la categoria1")
		self.assertEquals(election_after_questions_created.category_set.all()[1].name, u"la categoria2")

	def test_create_questions(self):
		parser = QuestionsParser(self.election)
		parser.createQuestions(self.lines)
		election_after_questions_created = Election.objects.get(pk=self.election.pk)

		first_category_questions = election_after_questions_created.category_set.all()[0].question_set.all()

		self.assertEquals(first_category_questions.count(), 1)
		self.assertEquals(first_category_questions[0].question, u"la pregunta1")

		second_category_questions = election_after_questions_created.category_set.all()[1].question_set.all()

		self.assertEquals(second_category_questions.count(), 1)
		self.assertEquals(second_category_questions[0].question, u"la pregunta2")


	def test_create_answer(self):
		parser = QuestionsParser(self.election)
		parser.createQuestions(self.lines)
		election = Election.objects.get(pk=self.election.pk)

		first_category_questions = election.category_set.all()[0].question_set.all()
		second_category_questions = election.category_set.all()[1].question_set.all()

		self.assertEquals(first_category_questions[0].answer_set.count(), 2)
		self.assertEquals(first_category_questions[0].answer_set.all()[0].caption, u"respuesta 1")
		self.assertEquals(first_category_questions[0].answer_set.all()[1].caption, u"respuesta 2")

		self.assertEquals(second_category_questions[0].answer_set.count(), 2)
		self.assertEquals(second_category_questions[0].answer_set.all()[0].caption, u"respuesta 3")
		self.assertEquals(second_category_questions[0].answer_set.all()[1].caption, u"respuesta 4")


class ElectionLoaderIntegrationTestCase(TestCase):
	def setUp(self):
		self.candidates = [[
					"BORIS COLJA", 
					"Algarrobo", 
					"IND",
					"bcolja@gmail.com", 
					"http://boljaconsejal.cl", 
					"boris.colja.en.facebook",
					"boris_colja_twitter", 
					"12/9/2012",
					"12/9/2012",
					"12/9/2012"
					],[
					"PRUEBA", 
					"Algarrobo", 
					"NO SOY IND",
					"prueba@gmail.com", 
					"http://boljaconsejal.cl", 
					"boris.colja.en.facebook",
					"boris_colja_twitter", 
					"12/9/2012",
					"12/9/2012",
					"12/9/2012"
					],[
					"PRUEBA2", 
					"otra comuna", 
					"NO SOY IND",
					"prueba2@gmail.com", 
					"http://boljaconsejal.cl", 
					"boris.colja.en.facebook",
					"boris_colja_twitter", 
					"12/9/2012",
					"12/9/2012",
					"12/9/2012"
					]]
		self.questions = [
			["category","la categoria1"],
			["question","la pregunta1"],
			["answer","respuesta 1"],
			["answer","respuesta 2"],
			["category","la categoria2"],
			["question","la pregunta2"],
			["answer","respuesta 3"],
			["answer","respuesta 4"],
		]

		self.user = User.objects.create_user(username='ciudadanointeligente',
                                                password='fci',
                                                email='fci@ciudadanointeligente.cl')

		self.loader = Loader('ciudadanointeligente', self.questions)
		processCandidates(self.user.username, self.candidates, self.questions)

	def test_creates_two_elections_based_on_the_list_of_candidates(self):
		algarrobo = Election.objects.get(slug=u"algarrobo")
		otra_comuna = Election.objects.get(slug=u"otra-comuna")

		self.assertEquals(algarrobo.category_set.count(), 2)
		self.assertEquals(otra_comuna.category_set.count(), 2)


	def test_creates_questions_and_answers(self):
		algarrobo = Election.objects.get(slug=u"algarrobo")

		self.assertEquals(algarrobo.category_set.all()[0].name, u"la categoria1")
		self.assertEquals(algarrobo.category_set.all()[0].question_set.all()[0].question, u"la pregunta1")
		self.assertEquals(algarrobo.category_set.all()[0].question_set.all()[0].answer_set.all()[0].caption, u"respuesta 1")
		self.assertEquals(algarrobo.category_set.all()[0].question_set.all()[0].answer_set.all()[1].caption, u"respuesta 2")
		self.assertEquals(algarrobo.category_set.all()[1].name, u"la categoria2")
		self.assertEquals(algarrobo.category_set.all()[1].question_set.all()[0].question, u"la pregunta2")
		self.assertEquals(algarrobo.category_set.all()[1].question_set.all()[0].answer_set.all()[0].caption, u"respuesta 3")
		self.assertEquals(algarrobo.category_set.all()[1].question_set.all()[0].answer_set.all()[1].caption, u"respuesta 4")


	def test_creates_questions_and_answers_for_otra_comuna(self):
		otra_comuna = Election.objects.get(slug=u"otra-comuna")
		
		self.assertEquals(otra_comuna.category_set.all()[0].name, u"la categoria1")
		self.assertEquals(otra_comuna.category_set.all()[0].question_set.all()[0].question, u"la pregunta1")
		self.assertEquals(otra_comuna.category_set.all()[0].question_set.all()[0].answer_set.all()[0].caption, u"respuesta 1")
		self.assertEquals(otra_comuna.category_set.all()[0].question_set.all()[0].answer_set.all()[1].caption, u"respuesta 2")
		self.assertEquals(otra_comuna.category_set.all()[1].name, u"la categoria2")
		self.assertEquals(otra_comuna.category_set.all()[1].question_set.all()[0].question, u"la pregunta2")
		self.assertEquals(otra_comuna.category_set.all()[1].question_set.all()[0].answer_set.all()[0].caption, u"respuesta 3")
		self.assertEquals(otra_comuna.category_set.all()[1].question_set.all()[0].answer_set.all()[1].caption, u"respuesta 4")




class ElectionLoaderTestCase(TestCase):
	def setUp(self):
		self.line = [
					"BORIS COLJA", 
					"Algarrobo", 
					"IND",
					"bcolja@gmail.com", 
					"http://boljaconsejal.cl", 
					"boris.colja.en.facebook",
					"boris_colja_twitter", 
					"12/9/2012",
					"12/9/2012",
					"12/9/2012"
					]
		self.lines = [
			["category","la categoria1"],
			["question","la pregunta1"],
			["answer","respuesta 1"],
			["answer","respuesta 2"],
			["category","la categoria2"],
			["question","la pregunta2"],
			["answer","respuesta 3"],
			["answer","respuesta 4"],
		]

		self.user = User.objects.create_user(username='ciudadanointeligente',
                                                password='fci',
                                                email='fci@ciudadanointeligente.cl')

		self.loader = Loader('ciudadanointeligente', self.lines)

	def test_creates_a_new_election(self):
		
		
		election = self.loader.getElection(self.line)
		self.assertEquals(election.name, u"Algarrobo")
		self.assertEquals(election.owner, self.user)


	def test_get_candidate(self):
		election = self.loader.getElection(self.line)
		candidate = self.loader.getCandidate(self.line)
		self.assertEquals(candidate.name, u"BORIS COLJA")
		self.assertEquals(candidate.election, election)
		self.assertTrue( u"Partido" in candidate.get_personal_data)
		self.assertEquals(candidate.get_personal_data[u'Partido'], u'IND')


	def test_create_questions_by_default_for_the_election(self):
		election = self.loader.getElection(self.line)
		


		first_category_questions = election.category_set.all()[0].question_set.all()
		second_category_questions = election.category_set.all()[1].question_set.all()

		self.assertEquals(election.category_set.count(), 2 )

		self.assertEquals(first_category_questions[0].answer_set.count(), 2)
		self.assertEquals(first_category_questions[0].answer_set.all()[0].caption, u"respuesta 1")
		self.assertEquals(first_category_questions[0].answer_set.all()[1].caption, u"respuesta 2")

		self.assertEquals(second_category_questions[0].answer_set.count(), 2)
		self.assertEquals(second_category_questions[0].answer_set.all()[0].caption, u"respuesta 3")
		self.assertEquals(second_category_questions[0].answer_set.all()[1].caption, u"respuesta 4")