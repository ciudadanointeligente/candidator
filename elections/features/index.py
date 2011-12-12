#-*- coding: utf-8 -*-
import os
from lettuce import *
from django.core.urlresolvers import reverse
from django.test.client import Client
from django.contrib.auth.models import User
from django.conf import settings
from elections.forms import *

dirname = os.path.dirname(os.path.abspath(__file__))


@before.all
def set_browser():
    world.browser = Client()

@before.each_scenario
def set_user(scenario):
    world.user = User.objects.create_user(username='userone', password='userone', email='userone@doe.cl')


@after.each_scenario
def delete_user(scenario):
    world.user.delete()

@step(u'Given I as user "([^"]*)" create the election "([^"]*)" con slug "([^"]*)"')
def given_i_as_user_group1_create_the_election_group2(step, username, election_name, slug):
    world.browser.login(username=username, password='userone')
    f = open('elections/features/media/dummy.jpg', 'rb')
    params = {'name': election_name, 'slug': slug, 'description': 'esta es una descripcion', 'logo': f}
    response = world.browser.post(reverse('election_create'), params, follow=True)
    f.close()
    assert isinstance(response.context['form'],CandidateForm)


@step(u'When I access "([^"]*)"')
def when_i_access_group1(step, address):
    world.response = world.browser.get(address)

@step(u'Then I get the response code (\d+)')
def then_i_get_the_response_code_d(step, status_code):
    response_status_code = world.response.status_code
    assert response_status_code == int(status_code), 'Got the response code '+str(response_status_code)

@step(u'Given I access the url "([^"]*)"')
def given_i_access_the_url_group1(step, address):
    world.response = world.browser.get(address)
