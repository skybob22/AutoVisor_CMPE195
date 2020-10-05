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

class Course(models.Model):
	department = models.TextField()
	courseID = models.TextField()
	id = models.AutoField(primary_key=True)

	class Meta: 
		unique_together = ('department', 'courseID', )

	def __str__(self):
		return self.department + ' ' + self.courseID	

