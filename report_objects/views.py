# Create your views here.
from django.views.generic import CreateView
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.http import HttpResponse, Http404

from forms import ReportForm
from models import Report


class ReportCreateView(CreateView):
    model = Report
    form_class = ReportForm

    def dispatch(self, request, *args, **kwargs):
        self.report_object = self._get_report_object(**kwargs)
        return super(ReportCreateView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super(ReportCreateView, self).get_context_data(*args, **kwargs)
        context['report_object'] = self.report_object
        return context

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.content_object = self.report_object
        self.object.save()
        return redirect(self.get_success_url())

    def _get_report_object(self, **kwargs):
        try:
            model_class = ContentType.objects.get(pk=kwargs['content_type']).model_class()
            self.report_object = get_object_or_404(model_class, pk=kwargs['object_id'])
        except ContentType.DoesNotExist:
            raise Http404
        return self.report_object

