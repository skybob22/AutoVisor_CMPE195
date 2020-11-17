from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.contrib import messages
from .models import *
from .forms import *
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.decorators import login_required
from .algorithm import generateRoadmap

# from django.http import HttpResponse




posts = [
	{
		'author': 'Daniel',
		'title': 'First Post',
		'content': 'First Post content',
		'date_posted': 'July 27, 2020'
	},
	{
		'author': 'Sarah',
		'title': 'Second Post',
		'content': 'Second Post content',
		'date_posted': 'July 28, 2020'
	}

]

# Create your views here.
def home(request):
	context = {
		'posts': Post.objects.all()
	}
	return render(request, 'schedule/home.html', context)

class PostListView(ListView):
	model = Post
	template_name = 'schedule/home.html' # <app>/<model>_<viewtype>.html
	context_object_name = 'posts'
	ordering = ['-date_posted']
	paginate_by = 5

class UserPostListView(ListView):
	model = Post
	template_name = 'schedule/user_posts.html' # <app>/<model>_<viewtype>.html
	context_object_name = 'posts'
	ordering = ['-date_posted']
	paginate_by = 5

	def get_queryset(self):
		user = get_object_or_404(User, username=self.kwargs.get('username'))
		return Post.objects.filter(author=user).order_by('-date_posted')

class PostDetailView(DetailView):
	model = Post

class PostCreateView(LoginRequiredMixin, CreateView):
	model = Post
	fields = ['title', 'content']

	def form_valid(self, form):
		form.instance.author = self.request.user
		return super().form_valid(form)

class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
	model = Post
	fields = ['title', 'content']

	def form_valid(self, form):
		form.instance.author = self.request.user
		return super().form_valid(form)

	def test_func(self):
		post = self.get_object()
		if self.request.user == post.author:
			return True
		return False

class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
	model = Post
	success_url = '/'

	def test_func(self):
		post = self.get_object()
		if self.request.user == post.author:
			return True
		return False



def about(request):
	return render(request, 'schedule/about.html', {'title': 'About'})


# @login_required
# def transcript(request):
# 	return render(request, 'schedule/transcript.html', {'title': 'Transcript'})

@login_required
def roadmap(request):
	rp = 'Not Clicked Yet!'
	if(request.GET.get('print_btn')):
		semList = generateRoadmap(request.user)
		student = Student.objects.get(user=request.user)
		rp = 'Clicked'
	return render(request, 'schedule/roadmap.html', {'rp': rp})

@login_required
def roadmap_detail(request):
	student = Student.objects.get(user=request.user)
	roadmap = student.roadmap


	context = {
		'semSchedules': roadmap.semesterSchedules.all()
	}
	return render(request, 'schedule/roadmap_detail.html', context)

@login_required
def transcript_detail(request):
	student = Student.objects.get(user=request.user)
	transcript = student.transcript
	transcriptGrade = TranscriptGrade.objects.filter(transcript=transcript)

	context = {
		'transcriptGrades': transcriptGrade
	}
	return render(request, 'schedule/transcript_detail.html', context)

@login_required
def index(request):
    return render(request,'schedule/transcript.html',{})

@login_required
def transcriptGrade_delete(request):
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
def community(request):
	return render(request, 'schedule/community.html', {'title': 'Roadmap'})

@login_required
def transcript(request):
	student = Student.objects.get(user=request.user)
	transcript = student.transcript
	transcriptGrade = TranscriptGrade.objects.filter(transcript=transcript)

	context = {
		'transcriptGrades': transcriptGrade
	}
	return render(request, 'schedule/transcript.html', context)



@login_required
def Add_course(request):
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
