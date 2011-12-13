from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.forms import formsets
from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext
from django.template.context import RequestContext
from django.utils import simplejson as json
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods
from django.views.generic import CreateView, DetailView, UpdateView

from elections.forms import CandidateForm, CandidateUpdateForm, CategoryForm, ElectionForm,\
                  CandidatePersonalInformationForm, CandidatePersonalInformationFormset,\
                  CandidateLinkFormset, ElectionUpdateForm, CategoryUpdateForm,\
                  PersonalDataForm, BackgroundCategoryForm, BackgroundForm, QuestionForm

from elections.models import Election, Candidate, Answer, PersonalInformation,\
                   Link, Category, Question, PersonalData,\
                   BackgroundCategory, Background

