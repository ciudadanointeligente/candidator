import os
from django.db import models
from django.conf import settings
from django.forms import ModelForm
from django_extensions.db.fields import AutoSlugField

# Create your models here.


class Election(models.Model):
    name = models.CharField(max_length=255)
    #slug = AutoSlugField(max_length=50, unique=True, populate_from=('slug_edit',))
    slug = models.CharField(max_length=255)
    owner = models.ForeignKey('auth.User')
    description = models.TextField(max_length=10000)
    logo = models.ImageField(upload_to = 'logos/', null =True, blank = True)

    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        unique_together = ('slug', 'owner')

    def admin_image(self):
        img_dir = os.path.join(settings.USER_FILES, str(self.logo))
        return '<img src = "%s"/>' % img_dir
    admin_image.allow_tags = True

    def __unicode__(self):
        return u"%s" % self.name


class Candidate(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    slug = models.CharField(max_length=255)
    election = models.ForeignKey('Election')
    answers = models.ManyToManyField('Answer', blank=True)

    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    def associate_answer(self, answer):
        old_answers = self.answers.filter(question=answer.question).all()
        new_answers = []
        for ans in self.answers.all():
            if ans not in old_answers:
                new_answers.append(ans)
        new_answers.append(answer)
        self.answers = new_answers
        self.save()

    @property
    def name(self):
        return u"%(first_name)s %(last_name)s" % {
            'first_name': self.first_name,
            'last_name': self.last_name
        }

    def __unicode__(self):
        return self.name


class PersonalInformation(models.Model):
    label = models.CharField(max_length=255)
    answer = models.CharField(max_length=255)
    candidate = models.ForeignKey('Candidate')

    def __unicode__(self):
        return u"%s" % self.label


class Link(models.Model):
    link_description = models.CharField(max_length=255)
    URL = models.CharField(max_length=255)
    candidate = models.ForeignKey('Candidate')

    def __unicode__(self):
        return u"%s" % self.link_description


class Category(models.Model):
    name = models.CharField(max_length=255)
    election = models.ForeignKey('Election')

    def __unicode__(self):
        return u"%s" % self.name


class Question(models.Model):
    question = models.CharField(max_length=255)
    category = models.ForeignKey('Category')

    def __unicode__(self):
        return u"%s" % self.question


class Answer(models.Model):
    caption = models.CharField(max_length=255)
    question = models.ForeignKey('Question')

    def __unicode__(self):
        return u"%s" % self.caption
