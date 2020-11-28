from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.contrib import messages
from .models import *
from .forms import *
from django.contrib.auth.decorators import login_required
from .algorithm import generateRoadmap





# Create your views here.
def home(request):
	load_button = True
	if request.user.is_authenticated:
		if Student.objects.filter(user=request.user).exists():
			load_button = False
	context = {
		'posts': Post.objects.all(),
		'load_button': load_button
	}
	return render(request, 'schedule/home.html', context)


def about(request):
	return render(request, 'schedule/about.html', {'title': 'About'})

semList=''

@login_required
def roadmap(request):
	rp1 = ''
	if Student.objects.filter(user=request.user).exists() is False:
		return redirect("student")
	student = Student.objects.get(user=request.user)
	if len(getMissingGEAreas(user=request.user)):
		rp1 = 'Please Fill Out Your GE Preferences Before Generating Roadmap'
	rp2 = 'Please Click to Generate Roadmap!'
	rp3 = 'Please Click to View Roadmap!'

	global semList
	if(request.GET.get('gen_btn')):
		semList = generateRoadmap(request.user)
		rp2 = 'Generating Roadmap... Please Wait.'
		return redirect("roadmap_generated")
	if(request.GET.get('view_btn')):
		semList = generateRoadmap(request.user, genNew=True, rescheduleCurrent=False)
		rp3 = 'Loading Roadmap... Please Wait.'
		return redirect("roadmap_generated")

	context = {
		'rp1': rp1,
		'rp2': rp2,
		'rp3': rp3
	}
	return render(request, 'schedule/roadmap.html', context)

@login_required
def roadmap_generated(request):
    if Student.objects.filter(user=request.user).exists() is False:
        return redirect("student")
    return render(request,'schedule/roadmap_detail.html',{})

@login_required
def roadmap_detail(request):
	if Student.objects.filter(user=request.user).exists() is False:
		return redirect("student")
	global semList
	student = Student.objects.get(user=request.user)
	roadmap = student.roadmap
	context = {
		'semSchedules': semList
	}
	print(semList)
	return render(request, 'schedule/roadmap_detail.html', context)

@login_required
def transcript_detail(request):
	if Student.objects.filter(user=request.user).exists() is False:
		return redirect("student")
	student = Student.objects.get(user=request.user)
	transcript = student.transcript
	transcriptGrade = TranscriptGrade.objects.filter(transcript=transcript)

	context = {
		'transcriptGrades': transcriptGrade
	}
	return render(request, 'schedule/transcript_detail.html', context)

@login_required
def index(request):
	if Student.objects.filter(user=request.user).exists() is False:
		return redirect("student")
	return render(request,'schedule/transcript.html',{})

@login_required
def transcriptGrade_delete(request):
	if Student.objects.filter(user=request.user).exists() is False:
		return redirect("student")
	student = Student.objects.get(user=request.user)
	transcript = student.transcript
	d_form = TranscriptGradeDeleteForm(request.POST or None, user=request.user)
	if d_form.is_valid():
		data = d_form.cleaned_data['course']
		transcriptGrade = TranscriptGrade.objects.get(transcript=transcript, course=data.course)
		messages.success(request,(transcriptGrade.course, 'has been deleted!'))
		transcriptGrade.delete()
		return redirect("index")

	context = {
			'd_form': d_form
	}
	return render(request, 'schedule/transcriptGrade_delete.html',  context)

@login_required
def transferGrade_delete(request):
	if Student.objects.filter(user=request.user).exists() is False:
		return redirect("student")
	student = Student.objects.get(user=request.user)
	transcript = student.transcript
	g_form = TransferGradeDeleteForm(request.POST or None, user=request.user)
	if g_form.is_valid():
		data = g_form.cleaned_data['course']
		transferGrade = TransferGrade.objects.get(transcript=transcript, course=data.course)
		messages.success(request,(transferGrade.course, 'has been deleted!'))
		transferGrade.delete()
		return redirect("index")

	context = {
			'g_form': g_form
	}
	return render(request, 'schedule/transferGrade_delete.html',  context)

@login_required
def preferredCourse_delete(request):
	if Student.objects.filter(user=request.user).exists() is False:
		return redirect("student")
	student = Student.objects.get(user=request.user)
	preferred = student.prefCourseList
	p_form = PreferredCourseDeleteForm(request.POST or None, user=request.user)
	if p_form.is_valid():
		data = p_form.cleaned_data['course']
		preferredCourse = PreferredCourse.objects.get(student = student, course=data.course)
		messages.success(request,(preferredCourse.course, 'has been deleted!'))
		preferredCourse.delete()
		return redirect("Preference")

	context = {
			'p_form': p_form
	}
	return render(request, 'schedule/preferredCourse_delete.html',  context)

@login_required
def community(request):
	if Student.objects.filter(user=request.user).exists() is False:
		return redirect("student")
	student = Student.objects.get(user=request.user)
	context = {
		'student': student
	}
	return render(request, 'schedule/community.html', context)

@login_required
def community_portal(request):
	if Student.objects.filter(user=request.user).exists() is False:
		return redirect("student")
	return render(request, 'schedule/community.html', {})

@login_required
def send_friendreq(request):
	if Student.objects.filter(user=request.user).exists() is False:
		return redirect("student")
	student = Student.objects.get(user=request.user)
	z_form = Send_Friend_Form(request.POST or None)
	if z_form.is_valid():
		data = z_form.cleaned_data['request_ID']
		temp = student.addFriend(data)
		if temp is None:
			messages.warning(request, 'Student ID does not exist!')
		else:
			messages.success(request,'Friend request has been sent to '+str(temp))

		return redirect("community_portal")

	context = {
		'z_form': z_form
	}

	return render(request, 'schedule/send_friendreq.html', context)

@login_required
def accept_friendreq(request):
	student = Student.objects.get(user=request.user)
	friendreqs = student.friendRequests
	a_form = Accept_Friend_Form(request.POST or None, user=request.user)
	if a_form.is_valid():
		data = a_form.cleaned_data['friendRequests']
		print(data)
		student.acceptFriend(data)
		messages.success(request,(data.user, ' is now your Friend!'))
		return redirect("community_portal")

	context = {
			'a_form': a_form
	}
	return render(request, 'schedule/accept_friendreq.html', context)


@login_required
def decline_friendreq(request):
	student = Student.objects.get(user=request.user)
	friendreqs = student.friendRequests
	y_form = Accept_Friend_Form(request.POST or None, user=request.user)
	if y_form.is_valid():
		data = y_form.cleaned_data['friendRequests']
		print(data)
		student.declineFriend(data)
		messages.success(request,(data.user, ' is now Declined!'))
		return redirect("community_portal")

	context = {
			'y_form': y_form
	}
	return render(request, 'schedule/decline_friendreq.html', context)


@login_required
def delete_friend(request):
	student = Student.objects.get(user=request.user)
	friends = student.friends
	t_form = Delete_Friend_Form(request.POST or None, user=request.user)
	if t_form.is_valid():
		data = t_form.cleaned_data['friends']
		print(data)
		student.deleteFriend(data)
		messages.success(request,(data.user, ' is now Deleted!'))
		return redirect("community_portal")

	context = {
			't_form': t_form
	}
	return render(request, 'schedule/delete_friend.html',  context)


@login_required
def transcript(request):
	if Student.objects.filter(user=request.user).exists() is False:
		return redirect("student")
	student = Student.objects.get(user=request.user)
	transcript = student.transcript
	transcriptGrade = TranscriptGrade.objects.filter(transcript=transcript)
	transferGrade = TransferGrade.objects.filter(transcript=transcript)
	context = {
		'transcriptGrades': transcriptGrade,
		'transferGrades': transferGrade
	}
	return render(request, 'schedule/transcript.html', context)



@login_required
def Add_course(request):
	if Student.objects.filter(user=request.user).exists() is False:
		return redirect("student")
	student = Student.objects.get(user=request.user)
	transcript = student.transcript
	x_form = Select_Department_CMPE_Form(request.POST or None)
	if x_form.is_valid():
		obj = x_form.save(commit=False)
		obj.transcript = transcript
		obj.save()
		messages.success(request,(obj.course, 'has been added!'))
		return redirect("index")

	context = {
		'x_form': x_form
	}
	return render(request, 'schedule/Add_course.html', context)

@login_required
def TransferCourseAdd(request):
	if Student.objects.filter(user=request.user).exists() is False:
		return redirect("student")
	student = Student.objects.get(user=request.user)
	transcript = student.transcript
	t_form = TransferCourseAddForm(request.POST or None)
	if t_form.is_valid():
		obj = t_form.save(commit=False)
		obj.transcript = transcript
		obj.save()
		messages.success(request,('Transfer Course has been added!'))
		return redirect("index")

	context = {
		't_form': t_form
	}
	return render(request, 'schedule/Add_TransferCourse.html', context)
########### Student Preference ###################


@login_required
def Preference(request):
	if Student.objects.filter(user=request.user).exists() is False:
		return redirect("student")
	student = Student.objects.get(user=request.user)
	preferredCourse = PreferredCourse.objects.filter(student=student)
	context = {
		'student': student,
		'preferredCourses': preferredCourse
	}
	return render(request, 'schedule/Preference.html', context)

# Todo: Form a connection to the database to save the values from the forms
@login_required
def GE_Pref(request):
	if Student.objects.filter(user=request.user).exists() is False:
		return redirect("student")
	student = Student.objects.get(user=request.user)
	preferred = student.prefCourseList
	reqList = getMissingGEAreas(user=request.user)

	tlist = []
	for item in reqList:
		temp = item[0]
		z_form = Select_GE_forms(request.POST or None, user=request.user, GEReq=temp)
		tlist.append((z_form, temp))

	valid = True
	for z_form,_ in tlist:
		if not z_form.is_valid():
			valid = False

	if valid:
		for z_form,_ in tlist:
			a = z_form
			data = z_form.cleaned_data['course']
			if data is None or data in preferred.all():
				continue

			preferred.add(data)
			student.save()
		messages.success(request, 'Your Student GE Preference Information has been updated!')
		return redirect("Preference")


	context = {
		'tlist': tlist
	}
	return render(request, 'schedule/GE_Pref.html', context)


@login_required
def Elec_Pref(request):
	if Student.objects.filter(user=request.user).exists() is False:
		return redirect("student")
	student = Student.objects.get(user=request.user)
	preferred = student.prefCourseList
	y_form = Select_ELEC_forms(request.POST or None, user=request.user)
	if y_form.is_valid():
		data = y_form.cleaned_data['course']
		preferred.add(data)
		student.save()
		messages.success(request, (str(data), 'has been deleted!'))
		return redirect("Preference")
	context = {
		'y_form': y_form
	}
	return render(request, 'schedule/Elec_Pref.html', context)


@login_required
def General_Pref(request):
	if Student.objects.filter(user=request.user).exists() is False:
		return redirect("student")
	student = Student.objects.get(user=request.user)
	q_form = Select_GEN_forms(request.POST or None, instance=student)
	if q_form.is_valid():
		q_form = Select_GEN_forms(request.POST or None, instance = student)
		q_form.save()
		messages.success(request, 'Your Student Preference Information has been updated!')
		return redirect("Preference")
	context = {
	'q_form': q_form
	}
	return render(request, 'schedule/General_Pref.html', context)
