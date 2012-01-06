from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save

# Create your models here.

class Profile(models.Model):
    name = models.CharField(max_length=255)
    biography = models.TextField()

    user = models.ForeignKey('auth.User')
    
    @models.permalink
    def get_absolute_url(self):
        return ('profiles_profile_detail', (), { 'username': self.user.username })


def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance, name=instance.username)

post_save.connect(create_user_profile, sender=User)
