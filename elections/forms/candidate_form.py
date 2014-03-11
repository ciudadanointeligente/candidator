from django import forms
from django.forms import formsets, ImageField, FileInput
from django.forms.formsets import formset_factory
from elections.models import Candidate, Link, BackgroundCandidate, PersonalDataCandidate, Answer

class CandidateForm(forms.ModelForm):
    class Meta:
        model = Candidate
        exclude = ('election', 'answers', 'personal_data', 'background', 'photo', 'slug', 'has_answered')
    class Media:
        js = ('js/jquery.slug.js', 'js/jquery.formset.js', )
        css = {
            'all': ('css/wizard-forms.css',)
            }
    
class CandidatePhotoForm(forms.ModelForm):
    photo = ImageField(widget=FileInput)
    def __init__(self, candidate, *args, **kwargs):
        self.candidate = candidate
        super(CandidatePhotoForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Candidate
        fields = ('photo',)
    
    def save(self, commit=True):
        self.candidate.photo = self.cleaned_data['photo']
        if commit:
            self.candidate.save()
        return self.candidate

class CandidateUpdateForm(forms.ModelForm):
    class Meta:
        model = Candidate
        exclude = ('slug', 'election', 'answers', 'personal_data', 'background', 'has_answered')
    class Media:
        js = ('js/jquery.formset.js', )


class CandidateLinkForm(forms.ModelForm):
    class Meta:
        model = Link
        exclude = ('candidate', )


class BackgroundCandidateForm(forms.ModelForm):
    class Meta:
        model = BackgroundCandidate
        exclude = ('candidate', )


class PersonalDataCandidateForm(forms.ModelForm):
    class Meta:
        model = PersonalDataCandidate
        exclude = ('candidate', )


#CandidateLinkFormset = formsets.formset_factory(CandidateLinkForm, extra=1)
