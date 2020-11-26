from django import forms
from .models import *
from .util import *

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

class PreferredCourseDeleteForm(forms.Form):

    class Meta:
        model = PreferredCourse
        fields = ['course']
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(PreferredCourseDeleteForm, self).__init__(*args, **kwargs)
        self.fields['course'].queryset = PreferredCourse.objects.filter(student=self.user.student)

    course = forms.ModelChoiceField(queryset=None)

class UserPreferenceForm(forms.ModelForm):
    course = forms.ModelMultipleChoiceField(queryset=Course.objects.all())

class Send_Friend_Form(forms.Form):
    request_ID = forms.CharField()
    
############### Student Preference #################
class Select_GE_forms(forms.Form):

    class Meta:
        model = Course
        fields = ['course']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        GEReq = kwargs.pop('GEReq')
        super(Select_GE_forms, self).__init__(*args, **kwargs)
        course = Course.objects.none()


        # temp is a tuple of (GErequirement, numofCourses, numUnits)
        for area in GEReq.GEAreas.all():
            course = (course | getGECourses(area, user=self.user).exclude(id__in=course))

        self.fields['course'].queryset = course

    course = forms.ModelChoiceField(queryset=None) #can add required = False


class Select_ELEC_forms(forms.Form):

    class Meta:
        model = TechElective
        fields = ['course']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(Select_ELEC_forms, self).__init__(*args, **kwargs)
        self.fields['course'].queryset = getTechElectives(user=self.user)

    course = forms.ModelChoiceField(queryset=None)


class Select_GEN_forms(forms.ModelForm):

    class Meta:
        model = Student
        fields = ['startTerm', 'startYear',
                  'numSemesters', 'currentTerm', 'currentYear']
