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
        js = ('jquery.slug.js', )
        css = {
            'all': ('css/wizard-forms.css',)
            }


class ElectionUpdateForm(forms.ModelForm):
    class Meta:
        model = Election
        exclude = ('owner', 'slug')


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        exclude = ('election')
    class Media:
        js = ('jquery.slug.js', )


class CategoryUpdateForm(forms.ModelForm):
    class Meta:
        model = Category
        exclude = ('election', 'slug')


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        exclude = ('category')


class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        exclude = ('question')


class PersonalDataForm(forms.ModelForm):
    class Meta:
        model = PersonalData
        exclude = ('election')
    class Media:
        js = ('jquery.formset.js', )

class PersonalDataCandidateForm(forms.ModelForm):
    class Meta:
        model = PersonalDataCandidate
        exclude = ('candidate', 'personal_data')
    class Media:
        js = ('jquery.formset.js', )

class BackgroundCategoryForm(forms.ModelForm):
    class Meta:
        model = BackgroundCategory
        exclude = ('election')
    class Media:
        js = ('jquery.formset.js', )


class BackgroundForm(forms.ModelForm):
    class Meta:
        model = Background
        exclude = ('category')

class BackgroundCandidateForm(forms.ModelForm):
    class Meta:
        model = BackgroundCandidate
        exclude = ('candidate', 'background')
