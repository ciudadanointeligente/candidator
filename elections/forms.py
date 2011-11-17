from django import forms
from django.forms.formsets import formset_factory
from elections.models import Category

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        exclude = ('election')

class QuestionForm(forms.Form):
    question = forms.IntegerField(widget=forms.HiddenInput)
    answers = forms.ChoiceField()
    importance = forms.ChoiceField(choices=((1, 'poco'), (2, 'harto')))

    def __init__(self, *args, **kwargs):
        super(QuestionForm, self).__init__(*args, **kwargs)

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
    QuestionFormSet = formset_factory(QuestionForm, extra=0, max_num=max_num)
    formset = QuestionFormSet(initial=initial, prefix=prefix)
    index = 0
    for form in formset:
        form.set_question(questions[index])
        index += 1
    return formset
