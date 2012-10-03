# coding= utf-8
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from elections.models import Election, Candidate, PersonalData, Category, Question, Answer, BackgroundCategory, Background, Link
import csv
from django.core.urlresolvers import reverse

class Loader(object):
	def __init__(self,username, lines, styles):
		self.user = User.objects.get(username=username)
		self.lines = lines
		self.styles = styles

	def getElection(self, line):
		election_name = line[0].decode('utf-8').strip()
		election, created = Election.objects.get_or_create(name=election_name, owner=self.user)
		
		if(created):
			election.custom_style = self.styles
			election.save()
			embedded_url = reverse('election_detail_embeded',kwargs={'username': election.owner.username,'slug': election.slug})
			
			[category.delete() for category in election.category_set.all()]
			[personal_data.delete() for personal_data in election.personaldata_set.all()]
			[background_category.delete() for background_category in election.backgroundcategory_set.all()]
			parser = QuestionsParser(election)
			parser.createQuestions(self.lines)
		return election


	def getCandidate(self, line):
		candidate_name = line[1].decode('utf-8').strip()
		election = self.getElection(line)
		candidate, created = Candidate.objects.get_or_create(name=candidate_name, election=election, has_answered=False)
		partido = line[2].decode('utf-8').strip()
		personal_data, created_personal_data = PersonalData.objects.get_or_create(label=u"Partido", election=election)
		candidate.add_personal_data(personal_data, partido)
		pacto = line[3].decode('utf-8').strip()
		personal_data, created_personal_data = PersonalData.objects.get_or_create(label=u"Pacto", election=election)
		candidate.add_personal_data(personal_data, pacto)
		reeleccion = line[4].decode('utf-8').strip()
		personal_data, created_personal_data = PersonalData.objects.get_or_create(label=u"¿Va a Reelección?", election=election)
		candidate.add_personal_data(personal_data, reeleccion)
		agnos = line[5].decode('utf-8').strip()
		personal_data, created_personal_data = PersonalData.objects.get_or_create(label=u"Número de años que ha sido Alcalde", election=election)
		candidate.add_personal_data(personal_data, agnos)
		periodos = line[6].decode('utf-8').strip()
		personal_data, created_personal_data = PersonalData.objects.get_or_create(label=u"Períodos en los que ha sido Alcalde", election=election)
		candidate.add_personal_data(personal_data, periodos)
		postulaciones_previas = line[7].decode('utf-8').strip()
		personal_data, created_personal_data = PersonalData.objects.get_or_create(label=u"Elecciones en las que ha postulado para ser Alcalde", election=election)
		candidate.add_personal_data(personal_data, postulaciones_previas)



		facebook_address = line[8].decode('utf-8').strip()
		if facebook_address:
			facebook = Link.objects.create(name=candidate.name, url=facebook_address, candidate=candidate)


		twitter_username = line[9].decode('utf-8').strip()
		if twitter_username:
			twitter = Link.objects.create(name=u'@'+twitter_username, url=u"https://twitter.com/"+twitter_username, candidate=candidate)
		

		return candidate


class QuestionsParser(object):
	def __init__(self, election):
		self.election = election

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


class Command(BaseCommand):
	args = '<username> <candidates csv file> <questions csv file> <css file for custom>'
	def handle(self, *args, **options):
		username = args[0]
		reader = open(args[3], 'rb')
		style = reader.read()
		lines_for_election_loader = csv.reader(open(args[1], 'rb'), delimiter=',')
		lines_for_question_loader = []
		questions_reader = csv.reader(open(args[2], 'rb'), delimiter=',')
		for question_line in questions_reader:
			lines_for_question_loader.append(question_line)
		processCandidates(username, lines_for_election_loader, lines_for_question_loader,style)
		


def processCandidates(username, lines_for_election_loader, lines_for_question_loader, styles):
	loader = Loader(username, lines_for_question_loader, styles)
	for candidate_line in lines_for_election_loader:
		candidate = loader.getCandidate(candidate_line)

	
