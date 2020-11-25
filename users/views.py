from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import *
from schedule.models import Student, Transcript


# Create your views here.
def register(request):
	if request.method == 'POST':
		form = UserRegisterForm(request.POST)
		if form.is_valid():
			form.save()
			username = form.cleaned_data.get('username')
			messages.success(request, f'Account Created for {username}! You are now able to log in.')
			return redirect('login')
	else:
		form = UserRegisterForm()
	return render(request, 'users/register.html', {'form': form})

@login_required #decorator adds functionality
def profile(request):
	if request.method == 'POST':
		u_form = UserUpdateForm(request.POST, instance=request.user)
		p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
		if u_form.is_valid() and p_form.is_valid():
			u_form.save()
			p_form.save()
			messages.success(request, f'You account has been updated!')
			return redirect('profile')
	else:
		u_form = UserUpdateForm(instance=request.user)
		p_form = ProfileUpdateForm(instance=request.user.profile)

	context = {
		'u_form': u_form,
		'p_form': p_form
	}

	return render(request, 'users/profile.html', context)

@login_required #decorator adds functionality
def student(request):
	s_form = StudentInfoForm(request.POST or None)
	if s_form.is_valid():
		obj = s_form.save()
		obj.user = request.user
		obj.save()
		transcript = Transcript()
		transcript.save()
		obj.transcript = transcript
		obj.save()
		messages.success(request, f'You Student Information has been created!')



	context = {
		's_form': s_form ,

	}



	return render(request, 'users/student.html', context)
