from django.db import models

# Create your models here.

class Election(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField()
    owner = models.ForeignKey('auth.User')

    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)


    def __unicode__(self):
        return u"%s" % self.name


class Candidate(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    slug = models.SlugField()
    election = models.ForeignKey('Election')

    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

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

class CandidateProfileData(models.Model):
    election = models.ForeignKey('Election')
    data_name = models.CharField(max_length=255)
    #TODO: add the data type

class CandidateProfile(models.Model):
    candidate = models.ForeignKey('Candidate')
    profile_data = models.ForeignKey('CandidateProfileData')
    value = models.CharField(max_length=255)



    
    
