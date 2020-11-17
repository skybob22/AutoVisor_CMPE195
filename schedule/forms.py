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

############### Student Preference #################
class Select_GE_forms(forms.ModelForm):

    class Meta:
        model = PreferredCourse
        fields = ['course']


class Select_ELEC_forms(forms.ModelForm):

    class Meta:
        model = PreferredCourse
        fields = ['course']


class Select_GEN_forms(forms.ModelForm):

    class Meta:
        model = Student
        fields = ['startTerm', 'startYear',
                  'numSemesters', 'currentTerm', 'currentYear']
