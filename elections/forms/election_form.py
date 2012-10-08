# -*- coding: utf-8 -*-
from django import forms
from django.forms.util import ErrorList
from django.forms import formsets, ImageField, FileInput
from django.forms.formsets import formset_factory
from elections.models import Category, Election, PersonalData,\
                BackgroundCategory, Background, Question, Answer,\
                PersonalDataCandidate, BackgroundCandidate


class ElectionForm(forms.ModelForm):
    class Meta:
        model = Election
        exclude = ('owner', 'slug')
    class Media:
        js = ('js/jquery.slug.js', )
        css = { 'all': ('css/wizard-forms.css',) }


class ElectionUpdateForm(forms.ModelForm):
    class Meta:
        model = Election
        exclude = ('owner', 'slug', 'published')


class ElectionStyleUpdateForm(forms.ModelForm):
    class Meta:
        model = Election
        exclude = ('owner', 'slug', 'name', 'description', 'information_source','logo','created_at', 'updated_at','date', 'published')



        
class ElectionLogoUpdateForm(forms.ModelForm):
    logo = ImageField(widget=FileInput)
    def __init__(self, election, *args, **kwargs):
        self.election = election
        super(ElectionLogoUpdateForm, self).__init__(*args, **kwargs)


    class Meta:
        model = Election
        fields = ('logo',)

    def save(self, commit=True):
        self.election.logo = self.cleaned_data['logo']
        if commit:
            self.election.save()
        return self.election
    

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        exclude = ('election', 'slug', 'order')
    class Media:
        js = ('js/jquery.slug.js', )
        css = { 'all': ('css/wizard-forms.css',) }


class CategoryUpdateForm(forms.ModelForm):
    class Meta:
        model = Category
        exclude = ('election', 'slug', 'order')


class QuestionForm(forms.ModelForm):
    new_category = forms.CharField(required=False)

    def __init__(self,*args,**kwargs):
        self.election = kwargs.pop('election')
        super(QuestionForm, self).__init__(*args,**kwargs)
        # Se puede cambiar el queryset del modelo:
        self.fields['category'].queryset = Category.objects.filter(election = self.election)

        choices = [(choice[0], choice[1]) for choice in self.fields['category'].choices]
        empty_choice = choices.pop(0)
        choices.append((empty_choice[0], u'-- Nueva categoría --'))
        self.fields['category'].choices = choices
        self.fields['category'].initial = 0

        # Se puede sobreescribir el required del modelo:
        self.fields['category'].required = False

    def clean(self):
        if 'category' in self.cleaned_data and self.cleaned_data['category'] is None:
            if 'new_category' in self.cleaned_data and len(self.cleaned_data['new_category'].strip()):
                self.cleaned_data['category'], created = Category.objects.get_or_create(name=self.cleaned_data['new_category'], election=self.election)
            else:
                msg = 'Este campo es obligatorio.'
                self._errors['category'] = ErrorList([msg])
                del self.cleaned_data['category']
        return self.cleaned_data


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
