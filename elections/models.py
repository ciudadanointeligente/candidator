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


# Create your models here.
class Election(models.Model):
    name = models.CharField(max_length=255, verbose_name=_("NOMBRE:"))
    slug = models.CharField(max_length=255, verbose_name=_("Con este link podras acceder a la eleccion:"))
    owner = models.ForeignKey('auth.User')
    description = models.TextField(_(u"DESCRIPCIÓN DE LA ELECCIÓN:"), max_length=10000)
    logo = models.ImageField(upload_to = 'logos/', blank = True, verbose_name="por último escoge una imagen que la represente:")
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    date = models.CharField(max_length=255, verbose_name=_(u"FECHA DE LA ELECCIÓN:"), blank=True)

    class Meta:
        unique_together = ('owner', 'slug')

    def __unicode__(self):
        return u"%s" % self.name


class Candidate(models.Model):
    name = models.CharField(max_length=255, verbose_name="Nombre:")
    slug = models.CharField(max_length=255, blank=True)
    photo = models.ImageField(upload_to = 'photos/', blank = True)

    election = models.ForeignKey('Election')
    answers = models.ManyToManyField('Answer', blank=True)

    personal_data = models.ManyToManyField('PersonalData', through='PersonalDataCandidate')
    background = models.ManyToManyField('Background', through='BackgroundCandidate')

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
            scores_by_category.append(sum_by_category[i]*100.0/importances_by_category[i])
        return ((sum(sum_by_category)*100.0/sum(importances)),scores_by_category)

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
        for background in self.background.all():
            backgrounds[background.category.name] = {}

        for background in self.background.all():
            backgrounds[background.category.name][background.name] = self.backgroundcandidate_set.get(background=background).value

        return backgrounds

    @property
    def get_personal_data(self):
        pd_dict = {}
        for pd in self.personal_data.all():
            pd_dict[pd.label] = self.personaldatacandidate_set.get(personal_data = pd).value
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
    value = models.CharField(max_length=255)

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
    value = models.CharField(max_length=255)

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

    #TODO: test
    @property
    def http_prefix(self):
        if self.url[0:7] == "http://":
            return self.url
        else:
            return "http://"+self.url


class Category(models.Model):
    name = models.CharField(max_length=255)
    election = models.ForeignKey('Election')
    slug = models.CharField(max_length=255, blank=True)

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

