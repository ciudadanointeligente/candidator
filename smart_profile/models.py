# encoding=UTF-8
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from tastypie.models import create_api_key

# Create your models here.

class Profile(models.Model):
    name = models.CharField(u'Nombre', max_length=255)
    biography = models.TextField(u'Cuéntanos un poco sobre tí...')

    user = models.ForeignKey('auth.User')
    
    @models.permalink
    def get_absolute_url(self):
        return ('profiles_profile_detail', (), { 'username': self.user.username })


def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance, name=instance.username)

models.signals.post_save.connect(create_api_key, sender=User)
post_save.connect(create_user_profile, sender=User)
