from django import forms

from models import Report


class ReportForm(forms.ModelForm):
    class Meta:
        model=Report
        exclude=('content_object', 'object_id', 'content_type', 'owner')
