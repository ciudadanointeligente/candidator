from django import forms
from django.forms import formsets
from django.forms.formsets import formset_factory
from elections.models import Candidate, Category, Election,\
                PersonalInformation, Link, PersonalData,\
                BackgroundCategory, Background, Question


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

class CandidateForm(forms.ModelForm):
    class Meta:
        model = Candidate
        exclude = ('election', 'answers')
    class Media:
        js = ('jquery.slug.js', 'jquery.formset.js', )


class PersonalDataForm(forms.ModelForm):
    class Meta:
        model = PersonalData
        exclude = ('election')
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


class CandidateUpdateForm(forms.ModelForm):
    class Meta:
        model = Candidate
        exclude = ('slug', 'election', 'answers')
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


class ElectionForm(forms.ModelForm):
    class Meta:
        model = Election
        exclude = ('owner')
    class Media:
        js = ('jquery.slug.js', )


class ElectionUpdateForm(forms.ModelForm):
    class Meta:
        model = Election
        exclude = ('owner', 'slug')


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        exclude = ('category')


class MediaNaranjaForm(forms.Form):
    question = forms.IntegerField(widget=forms.HiddenInput)
    answers = forms.ChoiceField()
    importance = forms.ChoiceField(choices=((1, 'poco'), (2, 'harto')))

    def __init__(self, *args, **kwargs):
        super(MediaNaranjaForm, self).__init__(*args, **kwargs)

    def set_question(self, question):
        self.fields['answers'].choices = ((a.pk, a.caption) for a in question.answer_set.all())
        self.fields['answers'].label = question.question
        self.fields['question'] = question.pk


def question_formset_factory(category):
    '''

    '''
    max_num = category.question_set.count()
    questions = category.question_set.all()
    initial = [{'question': question.pk} for question in questions]
    prefix = category.name
    MediaNaranjaFormSet = formset_factory(MediaNaranjaForm, extra=0, max_num=max_num)
    formset = MediaNaranjaFormSet(initial=initial, prefix=prefix)
    index = 0
    for form in formset:
        form.set_question(questions[index])
        index += 1
    return formset



