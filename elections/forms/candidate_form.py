from django import forms
from django.forms import formsets
from django.forms.formsets import formset_factory
from elections.models import Candidate, PersonalInformation, Link

class CandidateForm(forms.ModelForm):
    class Meta:
        model = Candidate
        exclude = ('election', 'answers', 'personal_data', 'background')
    class Media:
        js = ('jquery.slug.js', 'jquery.formset.js', )
        css = {
            'all': ('css/wizard-forms.css',)
            }


class CandidateUpdateForm(forms.ModelForm):
    class Meta:
        model = Candidate
        exclude = ('slug', 'election', 'answers', 'personal_data', 'background')
    class Media:
        js = ('jquery.formset.js', )


class CandidatePersonalInformationForm(forms.ModelForm):
    class Meta:
        model = PersonalInformation
        exclude = ('candidate', )

CandidatePersonalInformationFormset = formsets.formset_factory(CandidatePersonalInformationForm, extra=1)


class CandidateLinkForm(forms.ModelForm):
    class Meta:
        model = Link
        exclude = ('candidate', )

CandidateLinkFormset = formsets.formset_factory(CandidateLinkForm, extra=1)