from django import forms
from .models import Department, Course, TranscriptGrade

class Select_Department_CMPE_Form(forms.ModelForm):

    class Meta:
        model = TranscriptGrade
        fields = ['course', 'grade']
