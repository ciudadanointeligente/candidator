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

# Import forms
from elections.forms import PersonalDataForm, PersonalDataCandidateForm

# Import models
from elections.models import Election, Candidate, PersonalData


# PersonalData Views
class PersonalDataCreateView(CreateView):
    model = PersonalData
    form_class = PersonalDataForm
    
    def get_template_names(self):
        return ['elections/wizard/step_three.html']

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(PersonalDataCreateView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(PersonalDataCreateView, self).get_context_data(**kwargs)
        context['election'] = get_object_or_404(Election, slug=self.kwargs['election_slug'], owner=self.request.user)
        return context

    def get_success_url(self):
        return reverse('personal_data_create', kwargs={'election_slug': self.kwargs['election_slug']})

    def form_valid(self, form):
        self.object = form.save(commit=False)
        election = get_object_or_404(Election, slug=self.kwargs['election_slug'], owner=self.request.user)
        self.object.election = election
        return super(PersonalDataCreateView, self).form_valid(form)

@login_required
@require_http_methods(['GET', 'POST'])
def personal_data_candidate_create(request, candidate_pk, personal_data_pk):
    candidate = get_object_or_404(Candidate, pk=candidate_pk, election__owner=request.user)
    personal_data = get_object_or_404(PersonalData, pk=personal_data_pk, election__owner=request.user)

    if request.POST:
        value = request.POST.get('value', None)
        candidate.add_personal_data(personal_data, value)

        return HttpResponse(json.dumps({"value": value}),
                            content_type='application/json')
    form = PersonalDataCandidateForm()
    return render_to_response(\
            'elections/personal_data_associate.html',
            {'candidate': candidate, 'personal_data': personal_data, 'form':form},
            context_instance=RequestContext(request))


@login_required
@require_http_methods(['POST'])
def async_delete_personal_data(request, personal_data_pk):
    personal_data = get_object_or_404(PersonalData, pk = personal_data_pk, election__owner=request.user)
    personal_data.delete()
    json_dictionary = {"result":"OK"}
    return HttpResponse(json.dumps(json_dictionary),content_type='application/json')


@login_required
@require_http_methods(['POST'])
def async_create_personal_data(request, election_pk):
    election = get_object_or_404(Election, pk=election_pk, owner=request.user)

    value = request.POST.get('value', None)
    personal_data = PersonalData(label=value, election=election)
    personal_data.save()
    return HttpResponse(json.dumps({"pk": personal_data.pk, "label": personal_data.label}),
                        content_type='application/json')
