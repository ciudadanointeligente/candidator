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
					"Algarrobo", 
					"BORIS COLJA", 
					
					"IND",
					"pacto wena onda amigui",
					"SI",
					"20",
					"1900-1990asdasd",
					"19028209324dsfsdf",
					"http://www.facebook.com/fieraferoz",
					"fieraferoz"
					],[
					"Algarrobo", 
					"PRUEBA", 
					
					"NO SOY IND",
					"pacto wena onda amigui",
					"NO",
					"0",
					"", 
					"",
					"http://www.facebook.com/fieraferoz",
					"fieraferoz"
					],[
					"otra comuna", 
					"PRUEBA2", 
					
					"NO SOY IND",
					"pacto wena onda amigui",
					"NO",
					"0",
					"", 
					"",
					"http://www.facebook.com/fieraferoz",
					"fieraferoz"
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
		self.styles = "un estilo"
		self.loader = Loader('ciudadanointeligente', self.questions, self.styles)
		processCandidates(self.user.username, self.candidates, self.questions, self.styles)

	def test_execute_command(self):
		command = Command()
		command.handle(self.user.username
			,'elections/tests/media/candidatos.csv'
			, 'elections/tests/media/questions.csv'
			, 'elections/tests/media/style.css')
		reader = open('elections/tests/media/style.css', 'rb')
		style = reader.read()
		self.assertEquals(Election.objects.count(),5)

		self.assertEquals(Election.objects.filter(name=u"COMUNA1").count(),1)
		self.assertEquals(Election.objects.get(name=u"COMUNA1").candidate_set.count(), 2)
		self.assertEquals(Election.objects.get(name=u"COMUNA1").category_set.count(), 2)
		self.assertEquals(Election.objects.get(name=u"COMUNA1").category_set.all()[0].question_set.count(), 1)
		self.assertEquals(Election.objects.get(name=u"COMUNA2").custom_style, style)
		self.assertEquals(Election.objects.get(name=u"COMUNA1").custom_style, style)



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
					"Algarrobo", 
					"BORIS COLJA", 
					"IND",
					"pacto wena onda amigui",
					"SI",
					"20",
					"1900-1990asdasd",
					"19028209324dsfsdf",
					"http://www.facebook.com/boris-colja",
					"boris"
					]


		self.line2 = [
					"Algarrobo", 
					"Fiera", 
					"NO SOY IND",
					"pacto wena onda amigui",
					"NO",
					"0",
					"", 
					"",
					"http://www.facebook.com/fieraferoz",
					"fieraferoz"
					]

		self.line3 = [
					"Algarrobo", 
					"Fieripipooo", 
					"NO SOY IND",
					"pacto wena onda amigui",
					"NO",
					"0",
					"", 
					"",
					"",
					""
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
		self.styles = u"un estilo"
		self.loader = Loader('ciudadanointeligente', self.lines, self.styles)

	def test_creates_a_new_election(self):
		
		
		election = self.loader.getElection(self.line)

		self.assertEquals(election.name, u"Algarrobo")
		self.assertEquals(election.owner, self.user)
		self.assertEquals(election.custom_style, self.styles)


	def test_get_candidate(self):
		election = self.loader.getElection(self.line)
		candidate = self.loader.getCandidate(self.line)
		self.assertEquals(candidate.name, u"BORIS COLJA")
		self.assertEquals(candidate.election, election)
		self.assertTrue( u"Partido" in candidate.get_personal_data)
		self.assertTrue( u"Pacto" in candidate.get_personal_data)
		self.assertTrue( u"¿Va a reelección?" in candidate.get_personal_data)
		self.assertTrue( u"Número de años que ha sido alcalde" in candidate.get_personal_data)
		self.assertTrue( u"Períodos como alcalde" in candidate.get_personal_data)
		self.assertTrue( u"Elecciones anteriores" in candidate.get_personal_data)
		self.assertEquals(candidate.get_personal_data[u'Partido'], u'IND')
		self.assertEquals(candidate.get_personal_data[u'Pacto'], u'pacto wena onda amigui')
		self.assertEquals(candidate.get_personal_data[u'¿Va a reelección?'], u'SI')
		self.assertEquals(candidate.get_personal_data[u'Número de años que ha sido alcalde'], u'20')
		self.assertEquals(candidate.get_personal_data[u'Períodos como alcalde'], u'1900-1990asdasd')
		self.assertEquals(candidate.get_personal_data[u'Elecciones anteriores'], u'19028209324dsfsdf')
		self.assertEquals(candidate.link_set.count(), 2)
		self.assertEquals(candidate.link_set.get(name=u"@boris").url, u"https://twitter.com/boris")
		self.assertEquals(candidate.link_set.get(name=u"BORIS COLJA").url, u"http://www.facebook.com/boris-colja")
		self.assertFalse(candidate.has_answered)
		self.assertEquals(election.backgroundcategory_set.count(), 1)
		self.assertEquals(election.backgroundcategory_set.all()[0].name, u"Otros")
		self.assertEquals(election.backgroundcategory_set.all()[0].background_set.count(), 1)
		self.assertEquals(election.backgroundcategory_set.all()[0].background_set.all()[0].name , u"Aclaraciones al cuestionario")
		self.assertEquals(candidate.backgroundcandidate_set.count(), 1)
		self.assertEquals(candidate.backgroundcandidate_set.all()[0].value, u"Sin aclaraciones")


	def test_get_candidate_with_no_links(self):
		election = self.loader.getElection(self.line3)
		candidate = self.loader.getCandidate(self.line3)
		self.assertEquals(candidate.link_set.count(), 0)
		self.assertFalse(candidate.has_answered)



	def test_deletes_previous_personal_data(self):
		candidate = self.loader.getCandidate(self.line)

		self.assertEquals(len(candidate.get_personal_data), 6)
		self.assertEquals(candidate.get_personal_data[u'Partido'], u'IND')

	def test_create_only_one_personal_data_for_the_election(self):
		candidate = self.loader.getCandidate(self.line)
		candidate = self.loader.getCandidate(self.line2)

		self.assertEquals(candidate.election.personaldata_set.filter(label=u"Partido").count(), 1)

	def test_election_has_only_one_background_category(self):
		candidate = self.loader.getCandidate(self.line)

		self.assertEquals(candidate.election.backgroundcategory_set.count(), 1)



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