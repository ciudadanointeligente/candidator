from django import forms
from django.forms import formsets
from django.forms.formsets import formset_factory
from elections.models import Category, Election, PersonalData,\
                BackgroundCategory, Background, Question, Answer,\
                PersonalDataCandidate, BackgroundCandidate


class ElectionForm(forms.ModelForm):
    class Meta:
        model = Election
        exclude = ('owner')
    class Media:
        js = ('js/jquery.slug.js', )
        css = { 'all': ('css/wizard-forms.css',) }


class ElectionUpdateForm(forms.ModelForm):
    class Meta:
        model = Election
        exclude = ('owner', 'slug')


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        exclude = ('election', 'slug')
    class Media:
        js = ('js/jquery.slug.js', )
        css = { 'all': ('css/wizard-forms.css',) }


class CategoryUpdateForm(forms.ModelForm):
    class Meta:
        model = Category
        exclude = ('election', 'slug')


class QuestionForm(forms.ModelForm):
    def __init__(self,*args,**kwargs):
        election = kwargs.pop('election')
        super(QuestionForm, self).__init__(*args,**kwargs)
        self.fields['category'].queryset = Category.objects.filter(election = election)
    new_category = forms.CharField(required=False)
    category = forms.ChoiceField(required=False)
    class Meta:
        model = Question
    class Media:
        css = { 'all': ('css/wizard-forms.css',) }


class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        exclude = ('question')


class PersonalDataForm(forms.ModelForm):
    class Meta:
        model = PersonalData
        exclude = ('election')
    class Media:
        js = ('js/jquery.formset.js', )
        css = { 'all': ('css/wizard-forms.css',) }

class PersonalDataCandidateForm(forms.ModelForm):
    class Meta:
        model = PersonalDataCandidate
        exclude = ('candidate', 'personal_data')
    class Media:
        js = ('js/jquery.formset.js', )

class BackgroundCategoryForm(forms.ModelForm):
    class Meta:
        model = BackgroundCategory
        exclude = ('election')
    class Media:
        js = ('js/jquery.formset.js', )
        css = { 'all': ('css/wizard-forms.css',) }


class BackgroundForm(forms.ModelForm):
    class Meta:
        model = Background
        exclude = ('category')

class BackgroundCandidateForm(forms.ModelForm):
    class Meta:
        model = BackgroundCandidate
        exclude = ('candidate', 'background')
