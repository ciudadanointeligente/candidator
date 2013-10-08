# -*- coding: utf-8 -*-

import os
import re
from django.db import models
from django.conf import settings
from django.forms import ModelForm
from django_extensions.db.fields import AutoSlugField
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import slugify
from django.db.models.signals import  post_save
from django.dispatch.dispatcher import receiver


facebook_regexp = re.compile(r"^https?://[^/]*(facebook\.com|fb\.com|fb\.me)(/.*|/?)")
twitter_regexp = re.compile(r"^https?://[^/]*(t\.co|twitter\.com)(/.*|/?)")
http_regexp = re.compile(r"^(ht|f)tps?://.*")


# Create your models here.
class Election(models.Model):
    name = models.CharField(max_length=255, verbose_name=_(u"NOMBRE DE LA ELECCIÓN:"))
    slug = models.CharField(max_length=255, verbose_name=_("Con este link podras acceder a la eleccion:"))
    owner = models.ForeignKey('auth.User')
    description = models.TextField(_(u"DESCRIPCIÓN DE LA ELECCIÓN:"), max_length=10000)
    information_source = models.TextField(_(u"DE DONDE OBTUVISTE LA INFORMACIÓN:"), max_length=10000, blank = True)
    logo = models.ImageField(upload_to = 'logos/', blank = True, verbose_name=_(u"por último escoge una imagen que la represente:"))
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    date = models.CharField(max_length=255, verbose_name=_(u"fecha en que ocurrirá:"), blank=True)
    published = models.BooleanField(default=False)
    custom_style = models.TextField(blank=True)
    highlighted = models.BooleanField(default=False)
    use_default_media_naranja_option = models.BooleanField(default=True) #Default option "Ninguna de las anteriores" in media naranja
    should_display_empty_personal_data = models.BooleanField(default=True, verbose_name=_(u"debe mostrar los datos personales vacíos:"))
    

    class Meta:
        unique_together = ('owner', 'slug')

    def __unicode__(self):
        return u"%s" % self.name
    
    def set_slug(self):
        if not self.slug and self.name and self.owner:
            existing_elections = Election.objects.all().filter(owner= self.owner, name=self.name)
            slug = slugify(self.name)
            not_unique_slug = Election.objects.all().filter(owner= self.owner).filter(slug=slug).exists()
            previous_elections = 1
            temporary_slug = slug
            while not_unique_slug:
                temporary_slug = slug
                previous_elections += 1
                temporary_slug += str(previous_elections)
                not_unique_slug = Election.objects.all().filter(owner= self.owner).filter(slug=temporary_slug).exists()
            slug = temporary_slug
            self.slug = slug

    def __init__(self, *args, **kwargs):
        super(Election, self).__init__(*args, **kwargs)
        self.set_slug()
        
        
        

    @models.permalink
    def get_absolute_url(self):
        return ('election_detail', None, {'username': self.owner.username, 'slug': self.slug})

class Candidate(models.Model):
    name = models.CharField(max_length=255, verbose_name=_(u"Nombre:"))
    slug = models.CharField(max_length=255, blank=True)
    photo = models.ImageField(upload_to = 'photos/', blank = True)

    election = models.ForeignKey('Election')
    answers = models.ManyToManyField('Answer', blank=True)

    personal_data = models.ManyToManyField('PersonalData', through='PersonalDataCandidate')
    background = models.ManyToManyField('Background', through='BackgroundCandidate')
    has_answered = models.BooleanField(default=True, verbose_name=_("Has answered?"))
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)


    def save(self, *args, **kwargs):
        if self.pk is None:
            self.slug = slug = slugify(self.name)
            counter = 1
            while True:
                try:
                    Candidate.objects.get(slug=self.slug, election=self.election)
                    self.slug = slug + str(counter)
                    counter += 1
                except self.DoesNotExist:
                    break

        super(Candidate, self).save(*args, **kwargs)

    class Meta:
        unique_together = (('slug', 'election'), ('name', 'election'))

    def associate_answer(self, answer):
        old_answers = self.answers.filter(question=answer.question).all()
        new_answers = []
        for ans in self.answers.all():
            if ans not in old_answers:
                new_answers.append(ans)
        new_answers.append(answer)
        self.answers = new_answers
        self.save()

    def get_number_of_questions_by_category(self):
        number_of_questions = [] # Number of questions per category
        categories = Category.objects.filter(election=self.election)
        for category in categories:
            questions = Question.objects.filter(category=category)
            number_of_questions.append(len(questions))
        return number_of_questions

    def get_importances_by_category(self, importances):
        number_of_questions = self.get_number_of_questions_by_category()
        importances_by_category = []
        index = 0
        for num in number_of_questions:
            category_importance = 0.0
            for i in range(num):
                category_importance += importances[index]
                index += 1
            importances_by_category.append(category_importance)
        return importances_by_category

    def get_sum_importances_by_category(self, answers, importances):
        categories = Category.objects.filter(election=self.election)
        sum_by_category = [0]*len(categories)
        candidate_answers = self.answers.all() # Candidate answers
        index = 0
        # example answers = [[], [], [<Answer: Si>], [<Answer: Si>]]
        for x in reversed(answers):
            if len(x) != 0:
                if x[0] in candidate_answers:
                    factor = 1
                    value = factor * importances[len(importances)-index-1]
                    pos = list(categories.all()).index(x[0].question.category)
                    sum_by_category[pos] += value
                else:
                    factor = 0
            else:
                factor = 0
            index += 1
        return sum_by_category

    def get_score(self, answers, importances):
        sum_by_category = self.get_sum_importances_by_category(answers, importances)
        importances_by_category = self.get_importances_by_category(importances)
        scores_by_category = []
        for i in range(len(sum_by_category)):
            if importances_by_category[i] != 0:
                scores_by_category.append(sum_by_category[i]*100.0/importances_by_category[i])
            else:
                scores_by_category.append(0)
        if len(importances) > 0:
            try:
                return ((sum(sum_by_category)*100.0/sum(importances)),scores_by_category)
            except :
                return (0,scores_by_category)
        else:
            return (0,scores_by_category)

    def add_background(self, background, value):
        bcs = BackgroundCandidate.objects.filter(background=background, candidate=self)
        if len(bcs) > 0:
            for bc in bcs:
                bc.delete()
        background_candidate = BackgroundCandidate(background=background, candidate=self, value=value)
        background_candidate.save()

    def add_personal_data(self, personal_data, value):
        pdc = PersonalDataCandidate.objects.filter(personal_data=personal_data, candidate=self)
        if len(pdc) > 0:
            for pd in pdc:
                pd.delete()
        personal_data = PersonalDataCandidate(personal_data=personal_data, candidate=self, value=value)
        personal_data.save()

    @property
    def get_background(self):
        backgrounds = {}
        category_counter = 0
        for backgroundcategory in self.election.backgroundcategory_set.all():
            category_counter = category_counter + 1
            backgrounds[category_counter] = {'name':backgroundcategory.name, 'backgrounds':None}
            temporary_backgrounds = {}
            backgrounds_counter = 0
            for background in backgroundcategory.background_set.all():
                backgrounds_counter = backgrounds_counter + 1
                what_the_candidate_answered = self.get_answer_for_background(background)
                temporary_backgrounds[backgrounds_counter] = {
                                                    'name':background.name, 
                                                    'value':what_the_candidate_answered
                                                    }
            backgrounds[category_counter]['backgrounds'] = temporary_backgrounds
        return backgrounds
        
        
    def get_answer_for_background(self, background):
        try:
            return self.backgroundcandidate_set.get(background=background).value
        except:
            return None

    @property
    def get_personal_data(self):
        pd_dict = {}
        for pd in self.election.personaldata_set.all():
            try:
                pd_dict[pd.label] = self.personaldatacandidate_set.get(personal_data = pd).value
            except :
                pd_dict[pd.label] = None
        return pd_dict

    def get_questions_by_category(self, category):
        return category.question_set.all()

    def get_answer_by_question(self, question):
        candidate_answers = self.answers
        for answer in candidate_answers.all():
            if answer.question == question:
                return answer
        return "no answer"

    def get_all_answers_by_category(self, category):
        all_answers = []
        all_questions = self.get_questions_by_category(category)
        for question in all_questions:
            candidate_answer = self.get_answer_by_question(question)
            all_answers.append((question, candidate_answer))
        return all_answers

    def get_answers_two_candidates(self, candidate, category):
        all_answers = []
        all_questions = self.get_questions_by_category(category)
        for question in all_questions:
            first_candidate_answer = self.get_answer_by_question(question)
            second_candidate_answer = candidate.get_answer_by_question(question)
            all_answers.append((question,first_candidate_answer,second_candidate_answer))
        return all_answers

    def __unicode__(self):
        return self.name


class PersonalData(models.Model):
    label = models.CharField(_('Nuevo dato personal'),max_length=255)
    election = models.ForeignKey('Election')

    def __unicode__(self):
        return u'%s (%s)' % (self.label, self.election)


class PersonalDataCandidate(models.Model):
    candidate = models.ForeignKey(Candidate)
    personal_data = models.ForeignKey(PersonalData)
    value = models.TextField(max_length=2000)

    def __unicode__(self):
        return self.candidate.name + " - " + self.personal_data.label


class BackgroundCategory(models.Model):
    name = models.CharField(_(u"Nueva categoría de antecedentes"), max_length=255)
    election = models.ForeignKey('Election')

    def __unicode__(self):
        return u'%s (%s)' % (self.name, self.election)


class Background(models.Model):
    name = models.CharField(max_length=255)
    category = models.ForeignKey('BackgroundCategory')
    def __unicode__(self):
        return u'%s: %s (%s)' % (self.category, self.name, self.category.election)

class BackgroundCandidate(models.Model):
    candidate = models.ForeignKey('Candidate')
    background = models.ForeignKey('Background')
    value = models.CharField(max_length=2000)

    def __unicode__(self):
        return u'%s: %s' % (self.candidate, self.value)



class Link(models.Model):
    name = models.CharField(max_length=255)
    url = models.CharField(max_length=255)
    candidate = models.ForeignKey('Candidate')

    @property
    def css_class(self):
        if facebook_regexp.match(self.url):
            return "facebook"
        elif twitter_regexp.match(self.url):
            return "twitter"

    def __unicode__(self):
        return u"%s (%s)" % (self.name, self.url)

    @property
    def http_prefix(self):
        if http_regexp.match(self.url):
            return self.url
        else:
            return "http://"+self.url


class Category(models.Model):
    name = models.CharField(max_length=255)
    election = models.ForeignKey('Election')
    slug = models.CharField(max_length=255, blank=True)
    order = models.PositiveIntegerField(default=1)

    def save(self, *args, **kwargs):
        if self.pk is None:
            self.slug = slug = slugify(self.name)
            counter = 1
            while True:
                try:
                    Category.objects.get(slug=self.slug, election=self.election)
                    self.slug = slug + str(counter)
                    counter += 1
                except self.DoesNotExist:
                    break

        super(Category, self).save(*args, **kwargs)

    class Meta:
        unique_together = (('election', 'slug'), ('name', 'election'))
        verbose_name_plural = 'Categories'
        ordering = ['order']

    def __unicode__(self):
        return u"%s" % self.name


class Question(models.Model):
    question = models.CharField(max_length=255, verbose_name=_("PREGUNTA:"))
    category = models.ForeignKey('Category', verbose_name=_("CATEGORIA:"))

    def __unicode__(self):
        return u"%s" % self.question


class Answer(models.Model):
    caption = models.CharField(max_length=255)
    question = models.ForeignKey('Question')

    def __unicode__(self):
        return u"%s" % self.caption

class Visitor(models.Model):
    election = models.ForeignKey('Election')
    election_url = models.CharField(max_length=255)
    datestamp = models.DateTimeField(auto_now=True)
    def __unicode__(self):
        return str(self.datestamp) + ' - ' + self.election_url 
        
class VisitorAnswer(models.Model):
    """docstring for VisitorAnswer"""
    visitor = models.ForeignKey('Visitor')
    answer_text = models.CharField(max_length=255)
    question_text = models.CharField(max_length=255)
    question_category_text = models.CharField(max_length=255)
    answer_importance = models.IntegerField()
    def __init__(self, *args, **kwargs):
        if 'answer' in kwargs:
            kwargs['answer_text'] = kwargs['answer'].caption
            kwargs['question_text'] = kwargs['answer'].question.question
            kwargs['question_category_text'] = kwargs['answer'].question.category.name
            del kwargs['answer']
        super(VisitorAnswer, self).__init__(*args, **kwargs)

class VisitorScore(models.Model):
    visitor = models.ForeignKey('Visitor')
    candidate_name = models.CharField(max_length=255)
    score = models.IntegerField()

class CategoryScore(models.Model):
    visitor_score = models.ForeignKey('VisitorScore')
    category_score = models.IntegerField()
    category_name = models.CharField(max_length=255)       

    



@receiver(post_save, sender=Election)
def create_default_personaldata(sender, instance, created, **kwargs):
    if created:
        for label in settings.DEFAULT_PERSONAL_DATA:
            PersonalData.objects.create(label=label, election=instance)

@receiver(post_save, sender=Election)
def create_default_backgrounds(sender, instance, created, **kwargs):
    if created:
        for name in settings.DEFAULT_BACKGROUND_CATEGORIES:
            category = BackgroundCategory.objects.create(name=name, election=instance)
            for background in settings.DEFAULT_BACKGROUND_CATEGORIES[name]:
                Background.objects.create(name=background, category=category)

@receiver(post_save, sender=Election)
def create_default_questions(sender, instance, created, **kwargs):
    if created:
        for default_category in settings.DEFAULT_QUESTIONS:
            category = Category.objects.create(name=default_category['Category'], election=instance)
            for default_question in default_category['Questions']:
                question = Question.objects.create(question=default_question['question'],category=category)
                for default_answer in default_question['answers']:
                    Answer.objects.create(question=question, caption=default_answer)


class InformationSource(models.Model):
    question = models.ForeignKey(Question)
    candidate = models.ForeignKey(Candidate)
    content = models.TextField()