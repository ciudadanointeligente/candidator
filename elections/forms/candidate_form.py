from django import forms
from django.forms import formsets
from django.forms.formsets import formset_factory
from elections.models import Candidate, Link

class CandidateForm(forms.ModelForm):
    class Meta:
        model = Candidate
        exclude = ('election', 'answers', 'personal_data', 'background', 'photo', 'slug')
    class Media:
        js = ('js/jquery.slug.js', 'js/jquery.formset.js', )
        css = {
            'all': ('css/wizard-forms.css',)
            }


class CandidateUpdateForm(forms.ModelForm):
    class Meta:
        model = Candidate
        exclude = ('slug', 'election', 'answers', 'personal_data', 'background')
    class Media:
        js = ('js/jquery.formset.js', )


class CandidateLinkForm(forms.ModelForm):
    class Meta:
        model = Link
        exclude = ('candidate', )

CandidateLinkFormset = formsets.formset_factory(CandidateLinkForm, extra=1)