from django import forms
from .models import *

class Select_Department_CMPE_Form(forms.ModelForm):

    class Meta:
        model = TranscriptGrade
        fields = ['course', 'grade']

class TranscriptGradeDeleteForm(forms.Form):

    class Meta:
        model = TranscriptGrade
        fields = ['course']
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(TranscriptGradeDeleteForm, self).__init__(*args, **kwargs)
        self.fields['course'].queryset = TranscriptGrade.objects.filter(transcript=self.user.student.transcript)

    course = forms.ModelChoiceField(queryset=None)

class UserPreferenceForm(forms.ModelForm):
    course = forms.ModelMultipleChoiceField(queryset=Course.objects.all())
