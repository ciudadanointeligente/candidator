# coding= utf-8
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from elections.models import Election, Candidate, PersonalData, Category, Question, Answer, BackgroundCategory,\
							 Background, Link, BackgroundCandidate, PersonalDataCandidate, InformationSource
import csv
from django.core.urlresolvers import reverse
from django.db.models import Q

class QuestionsParser(object):
	def __init__(self, election):
		self.election = election
		self.election.backgroundcategory_set.all().delete()
		self.election.personaldata_set.all().delete()

	def createQuestions(self, lines):
		for line in lines:
			if line[0]=="category":
				category_name = line[1].decode('utf-8').strip()
				self.category = Category.objects.create(name=category_name, election=self.election)
			if line[0]=="question":
				question = line[1].decode('utf-8').strip()
				self.question = Question.objects.create(question=question, category=self.category)
			if line[0]=="answer":
				answer = line[1].decode('utf-8').strip()
				self.answer = Answer.objects.create(caption=answer, question=self.question)
			if line[0]=="background history category":
				background_category_name = line[1].decode('utf-8').strip()
				self.background_category = BackgroundCategory.objects.create(name=background_category_name, election=self.election)
			if line[0]=="background history":
				background_history_name = line[1].decode('utf-8').strip()
				self.background_history = Background.objects.create(name=background_history_name, category=self.background_category)
			if line[0]=="personal data":
				personal_data_label = line[1].decode('utf-8').strip()
				self.personal_data = PersonalData.objects.create(label=personal_data_label, election=self.election)

class AnswersLoader(object):
	def __init__(self,username, candidates, questions, styles):
		self.user = User.objects.get(username=username)
		self.lines = candidates
		self.styles = styles
		self.questions = questions
		self.get_definitions()

	def get_definitions(self):
		line0 = self.lines[0]
		line1 = self.lines[1]
		self.definitions = {}
		if len(line0) > 2:
			for i in range(2, len(line0)):
				definition = {"label":line1[i], "type":line0[i]}
				self.definitions[i] = definition


	def get_election(self, line, questions):
		election_name = line[0].decode('utf-8').strip()
		election, created = Election.objects.get_or_create(name=election_name, owner=self.user)

		if(created):
		 	election.custom_style = self.styles
		 	election.save()
		 	election.category_set.all().delete()
		 	parser = QuestionsParser(election)
			parser.createQuestions(questions)
		return election

	def assign_values(self, election, candidate, line):
		for i in range(2,len(line)):
			value = line[i].decode('utf-8').strip()
			label = self.definitions[i]["label"]
			the_type = self.definitions[i]["type"]

			if(the_type == "personal data"):
				try:
					personal_data = PersonalData.objects.get(election=election, label=label)
					PersonalDataCandidate.objects.create(candidate=candidate, personal_data=personal_data, value=value)
				except :
					print "personal data non existent "+label +"| value "+ value
			if (the_type == "background history"):
				try:

					category_name = label.split(" - ")[0]
					label = label.split(" - ")[1]
					category = BackgroundCategory.objects.get(name=category_name, election=election)
					background = Background.objects.get(name=label, category=category)
					BackgroundCandidate.objects.create(candidate=candidate, background=background, value=value)
				except :
					print "background non existent "+label +"| value "+ value

			if (the_type == "link"):
				try:
					if label in ["twitter","facebook"]:
						if (label == "twitter"):
							Link.objects.create(name=u'@'+value, url=u"https://twitter.com/"+value, candidate=candidate)
						if (label == "facebook"):
							Link.objects.create(name=candidate.name, url=value, candidate=candidate)
					else:
						if value:
							Link.objects.create(name=label, url=value, candidate=candidate)

				except:
					print "link non existent "+label +"| value "+ value


			if (the_type == "answer"):
				pre_processed_answer = value.split("<")
				answer_caption = pre_processed_answer.pop(0)
				answer_caption = answer_caption.strip()
				#here there is a bug
				question = Question.objects.get(Q(question=label) & Q(category__election=election))
				#yes here above this
				try:
					answer = Answer.objects.get(Q(question__category__election=election) & Q(question=question) & Q(caption=answer_caption))
					candidate.associate_answer(answer)
					if pre_processed_answer:
						information_source_content = pre_processed_answer[0][:-1]
						InformationSource.objects.create(question=answer.question, candidate=candidate, content=information_source_content)
				except Answer.DoesNotExist, exception:
					if answer_caption:
						print u"The answer '%(answer)s' for question '%(question)s' and candidate %(candidate)s is not defined in the questions csv"%{
						'answer':answer_caption,
						'question':question.question,
						'candidate':candidate.name
						}
				except Answer.MultipleObjectsReturned, exception:
					print u"The answer '%(answer)s' for question '%(question)s' is defined twice in the questions csv"%{
						'answer':answer_caption,
						'question':question.question
						}


	def get_candidate(self, line, election):
		candidate = Candidate.objects.create(name=line[1].decode('utf-8').strip(), election=election)
		return candidate

	def process(self):
		amount_of_lines = len(self.lines)

		for i in range(2, amount_of_lines):
			line = self.lines[i]
			election = self.get_election(line, self.questions)
			candidate = self.get_candidate(line, election)
			self.assign_values(election, candidate, line)




class Command(BaseCommand):
	args = '<username> <candidates csv file> <questions csv file> <css file for custom>'
	def handle(self, *args, **options):
		username = args[0]
		reader = open(args[3], 'rb')
		style = reader.read()
		lines_for_candidates_loader = csv.reader(open(args[1], 'rb'), delimiter=',')
		candidates =[]
		for line in lines_for_candidates_loader:
			candidates.append(line)
		questions_reader = csv.reader(open(args[2], 'rb'), delimiter=',')
		questions = []
		for line in questions_reader:
			questions.append(line)
		loader = AnswersLoader(username, candidates, questions, style)
		loader.process()