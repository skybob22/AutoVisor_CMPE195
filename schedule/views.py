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
	student = Student.objects.get(user=request.user)
	context = {
		'posts': Post.objects.all(),
		'student': student
	}
	return render(request, 'schedule/home.html', context)


def about(request):
	return render(request, 'schedule/about.html', {'title': 'About'})

semList=''

@login_required
def roadmap(request):
	if Student.objects.filter(user=request.user).exists() is False:
		return redirect("student")
	rp = 'Please Click to Generate Roadmap!'
	if(request.GET.get('print_btn')):
		global semList
		semList = generateRoadmap(request.user)
		student = Student.objects.get(user=request.user)
		rp = 'Generating Roadmap... Please Wait.'
		return redirect("roadmap_generated")
	return render(request, 'schedule/roadmap.html', {'rp': rp})

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
	d_form = TranscriptGradeDeleteForm(request.POST, user=request.user)
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
def preferredCourse_delete(request):
	if Student.objects.filter(user=request.user).exists() is False:
		return redirect("student")
	student = Student.objects.get(user=request.user)
	preferred = student.prefCourseList
	p_form = PreferredCourseDeleteForm(request.POST, user=request.user)
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
	return render(request, 'schedule/community.html', {'title': 'Roadmap'})

@login_required
def transcript(request):
	if Student.objects.filter(user=request.user).exists() is False:
		return redirect("student")
	student = Student.objects.get(user=request.user)
	transcript = student.transcript
	transcriptGrade = TranscriptGrade.objects.filter(transcript=transcript)

	context = {
		'transcriptGrades': transcriptGrade
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

########### Student Preference ###################


@login_required
def Preference(request):
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
    student = Student.objects.get(user=request.user)
    GE_CourseList = student.prefCourseList
    z_form = Select_GE_forms(request.POST or None)
    if z_form.is_valid():
        obj = z_form.save(commit=False)
        obj.prefCourseList = GE_CourseList
        obj.save()
        messages.success(
            request, f'Your Student GE Preference Information has been updated!')
        return render(request, 'schedule/GE_Pref.html')
    context = {
        'z_form': z_form
    }
    return render(request, 'schedule/GE_Pref.html', context)


@login_required
def Elec_Pref(request):
    student = Student.objects.get(user=request.user)
    Elec_List = student.prefCourseList
    y_form = Select_ELEC_forms(request.POST or None)
    if y_form.is_valid():
        obj = y_form.save(commit=False)
        obj.prefCourseList = Elec_List
        obj.save()
        messages.success(
            request, f'Your Student Technical Elective Preference Information has been updated!')
        return render(request, 'schedule/Elec_Pref.html')
    context = {
        'y_form': y_form
    }
    return render(request, 'schedule/Elec_Pref.html', context)


@login_required
def General_Pref(request):
    if Student.objects.filter(user=request.user).exists() is False:
        return redirect("student")
    student = Student.objects.get(user=request.user)
    q_form = Select_GEN_forms(request.POST or None)
    if q_form.is_valid():
        q_form =  Select_GEN_forms(request.POST, instance = student)
        q_form.save()
        messages.success(
            request, f'Your Student Preference Information has been updated!')
        return render(request, 'schedule/General_Pref.html')
    context = {
        'q_form': q_form
    }
    return render(request, 'schedule/General_Pref.html', context)
