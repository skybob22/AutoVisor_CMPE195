from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse

# Create your models here.
class Post(models.Model):
	title = models.CharField(max_length=100)
	content = models.TextField()
	date_posted = models.DateTimeField(default=timezone.now)
	author = models.ForeignKey(User, on_delete=models.CASCADE)

	def __str__(self):
		return self.title

	def get_absolute_url(self):
		return reverse('post-detail', kwargs={'pk': self.pk})

class Department(models.Model):
	abrv = models.TextField(primary_key=True)
	name = models.TextField()

	def __str__(self):
		return self.abrv

class Course(models.Model):
	id = models.AutoField(primary_key=True)
	department = models.ForeignKey(Department,on_delete=models.RESTRICT)
	courseID = models.TextField()
	prereqs = models.ManyToManyField('self',symmetrical=False,blank=True,related_name='Prerequisites')
	coreqs = models.ManyToManyField('self',symmetrical=False,blank=True,related_name='Corequisites')

	class Meta:
		unique_together = ('department', 'courseID', )

	def __str__(self):
		return str(self.department) + ' ' + self.courseID

class Catalogue(models.Model):
	id = models.AutoField(primary_key=True)
	department = models.ForeignKey(Department,on_delete=models.RESTRICT)
	year = models.IntegerField()
	courses = models.ManyToManyField(Course,symmetrical=False)

	class Meta:
		unique_together = ('department','year',)

	def __str__(self):
		retStr = str(department) + ' ' + str(year) + ':'
		for course in self.courses.all():
			retStr = retStr + str(course) + ','
		return retStr;
