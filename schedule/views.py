from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.contrib import messages
from .models import *
from .forms import *
from django.contrib.auth.decorators import login_required
from .algorithm import generateRoadmap





########### Create views here ###################
@login_required
def index(request):
	if Student.objects.filter(user=request.user).exists() is False:
		return redirect("student")
	return render(request,'schedule/transcript.html',{})

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




########### Roadmap Features ###################
semList=''
@login_required
def roadmap(request):
	rp1 = ''
	if Student.objects.filter(user=request.user).exists() is False:
		return redirect("student")
	student = Student.objects.get(user=request.user)
	if len(getMissingGEAreas(user=request.user)):
		rp1 = 'Please Fill Out Your GE Preferences Before Generating Roadmap'
	rp2 = 'Please Click to View Roadmap!'
	rp3 = 'Please Click to Generate Roadmap!'

	global semList
	if (request.GET.get('view_btn')):
		semList = generateRoadmap(request.user)
		rp2 = 'Loading Roadmap... Please Wait.'
		return redirect("roadmap_generated")
	if(request.GET.get('gen_btn')):
		semList = generateRoadmap(request.user,genNew=True,rescheduleCurrent=False)
		rp3 = 'Generating Roadmap... Please Wait.'
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
	return render(request, 'schedule/roadmap_detail.html', context)




########### Community Features ###################
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
		temp = student.addFriend(sID=data)
		if temp is None:
			messages.warning(request, 'Student ID does not exist!')
		else:
			messages.success(request,'Friend request has been sent to {0}'.format(str(temp.user)))

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
		student.acceptFriend(student=data)
		messages.success(request,'{0} is now your friend!'.format(str(data.user)))
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
		student.declineFriend(student=data)
		messages.success(request,'Request from {0} has been declined!'.format(str(data.user)))
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
		student.deleteFriend(student=data)
		messages.success(request,'{0} is no longer your friend!'.format(str(data.user)))
		return redirect("community_portal")

	context = {
			't_form': t_form
	}
	return render(request, 'schedule/delete_friend.html',  context)




########### Transcript Management ###################
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
		messages.success(request,'{0} has been added!'.format(str(obj.course)))
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
		messages.success(request,'Transfer Course has been added!')
		return redirect("index")

	context = {
		't_form': t_form
	}
	return render(request, 'schedule/Add_TransferCourse.html', context)

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
		messages.success(request,'{0} has been deleted!'.format(str(transcriptGrade.course)))
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
		transferGrade = TransferGrade.objects.get(transcript=transcript, course=data)
		messages.success(request,'{0} has been deleted!'.format(str(transferGrade.course)))
		transferGrade.delete()
		return redirect("index")

	context = {
			'g_form': g_form
	}
	return render(request, 'schedule/transferGrade_delete.html',  context)

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
	reqList = getMissingGE_NoOverlap(user=request.user)

	tlist = []
	for i in range(len(reqList)):
		item = reqList[i]
		temp = item[0]
		z_form = Select_GE_forms(request.POST or None,user=request.user,GEReq=temp,prefix=str(i))
		tlist.append((z_form, temp))

	if len(tlist) == 0:
		messages.info(request, 'All GEs are accounted for')
		return redirect("Preference")

	valid = True
	for z_form,_ in tlist:
		if not z_form.is_valid():
			valid = False

	if valid:
		for z_form,_ in tlist:
			if not z_form.is_valid():
				continue
			data = z_form.cleaned_data['course']
			if data is None or data in preferred.all():
				continue

			preferred.add(data)
			student.save()
		addMsg = 'There are still additional GE areas to add' if len(getMissingGE_NoOverlap(request.user)) > 0 else 'All GEs accounted for'
		messages.success(request, 'Your GE Preferences have been updated! {0}'.format(addMsg))
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
		techNeeded = getMissingTech(request.user)
		addMsg = 'You still need {0} more tech elective unit(s)'.format(techNeeded) if techNeeded > 0 else 'All tech electives accounted for'
		messages.success(request, '{0} has been added! {1}'.format(str(data),addMsg))
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

		#If the preferences are changed to no longer take seperate SV, remove any SV courses from planned courses
		if not student.separateSV:
			SVCourses = getGECourses(GEArea.objects.get(area='S')) | getGECourses(GEArea.objects.get(area='V'))
			for prefCourse in PreferredCourse.objects.filter(student=student).filter(course__id__in=SVCourses).all():
				student.prefCourseList.remove(prefCourse.course)
				student.save()
		messages.success(request, 'General preferences have been updated!')
		return redirect("Preference")
	context = {
	'q_form': q_form
	}
	return render(request, 'schedule/General_Pref.html', context)

@login_required
def preferredCourse_delete(request):
	if Student.objects.filter(user=request.user).exists() is False:
		return redirect("student")
	student = Student.objects.get(user=request.user)
	preferred = student.prefCourseList
	p_form = PreferredCourseDeleteForm(request.POST or None, user=request.user)
	if p_form.is_valid():
		data = p_form.cleaned_data['course']
		preferredCourse = PreferredCourse.objects.get(student=student, course=data)
		messages.success(request,'{0} has been deleted!'.format(str(preferredCourse.course)))
		preferredCourse.delete()
		return redirect("Preference")

	context = {
			'p_form': p_form
	}
	return render(request, 'schedule/preferredCourse_delete.html',  context)