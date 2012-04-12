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
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, DetailView, UpdateView

# Import forms
from elections.forms import CategoryForm, CategoryUpdateForm

# Import models
from elections.models import Category, Election


# Category views
class CategoryCreateView(CreateView):
    model = Category
    form_class = CategoryForm

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(CategoryCreateView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(CategoryCreateView, self).get_context_data(**kwargs)
        context['election'] = get_object_or_404(Election, slug=self.kwargs['election_slug'], owner=self.request.user)
        return context

    def get_success_url(self):
        return reverse('category_create', kwargs={'election_slug': self.object.election.slug})

    def form_valid(self, form):
        self.object = form.save(commit=False)
        election = get_object_or_404(Election, slug=self.kwargs['election_slug'], owner=self.request.user)
        self.object.election = election

        try:
            self.object.full_clean()
        except ValidationError:
            from django.forms.util import ErrorList
            form._errors["slug"] = ErrorList([u"Ya tienes una categoria con ese slug."])
            return super(CategoryCreateView, self).form_invalid(form)

        return super(CategoryCreateView, self).form_valid(form)

class CategoryUpdateView(UpdateView):
    model = Category
    form_class = CategoryUpdateForm

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(CategoryUpdateView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(CategoryUpdateView, self).get_context_data(**kwargs)
        context['election'] = get_object_or_404(Election, slug=self.kwargs['election_slug'], owner=self.request.user)
        return context

    def get_success_url(self):
        return reverse('election_detail', kwargs={'slug': self.object.election.slug, 'username': self.request.user.username})

    def get_queryset(self):
        return self.model.objects.filter(election__slug=self.kwargs['election_slug'],
                                         slug=self.kwargs['slug'],
                                         election__owner=self.request.user)

    def form_valid(self, form):
        self.object = form.save(commit=False)
        election = get_object_or_404(Election, slug=self.kwargs['election_slug'], owner=self.request.user)
        self.object.election = election
        return super(CategoryUpdateView, self).form_valid(form)


@login_required
@require_POST
def async_delete_category(request, category_pk):
    category = get_object_or_404(Category, pk = category_pk, election__owner = request.user)
    category.delete()
    json_dictionary = {"result":"OK"}
    return HttpResponse(json.dumps(json_dictionary),content_type='application/json')

@login_required
@require_POST
def async_create_category(request, election_pk):
    election = get_object_or_404(Election, pk=election_pk, owner=request.user)

    value = request.POST.get('value', None)
    category = Category(name=value, election=election)
    try:
        category.full_clean()
    except ValidationError, e:
        errors = {'errors': e.messages}
        return HttpResponse(json.dumps(errors),status=412)

    category.save()
    return HttpResponse(json.dumps({"pk": category.pk, "name": category.name}),
                        content_type='application/json')