from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile
from schedule.models import Student
#from django.schedule.models import Student


class UserRegisterForm(UserCreationForm):
	email = forms.EmailField()
	#student = models.OneToOneField('Student',on_delete=models.SET_NULL,default=None,blank=True,null=True)

	class Meta:
		model = User
		fields = ['username', 'email', 'password1', 'password2']

class UserUpdateForm(forms.ModelForm):
	email = forms.EmailField()

	class Meta:
		model = User
		fields = ['username', 'email']

class ProfileUpdateForm(forms.ModelForm):
	class Meta:
		model = Profile
		fields = ['image']

class StudentInfoForm(forms.ModelForm):

	class Meta:
		model = Student
		fields = ['studentID', 'catalogue']
		

