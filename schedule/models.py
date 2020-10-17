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





#====================College Information====================#
class College(models.Model):
	name = models.CharField(max_length=50,primary_key=True)

class Department(models.Model):
	abrv = models.TextField(primary_key=True)
	name = models.TextField()

	def __str__(self):
		return self.abrv




#====================Courses and Prereqs====================#

GRADES = (
	('A+','A+'),
	('A','A'),
	('A-','A-'),
	('B+','B+'),
	('B','B'),
	('B-','B-'),
	('C+','C+'),
	('C','C'),
	('C-','C-'),
	('D+','D+'),
	('D','D'),
	('D-','D-'),
	('F','F')
)

GE_AREAS = (
	('A1','A1'),
	('A2','A2'),
	('A3','A3'),
	('B1','B1'),
	('B2','B2'),
	('B3','B3'),
	('B4','B4'),
	('C1','C1'),
	('C2','C2'),
	('D1','D1'),
	('D2','D2'),
	('D3','D3'),
	('E','E'),
	('R','R'),
	('S','S'),
	('V','V'),
	('Z','Z')
)

class GEArea(models.Model):
	area = models.CharField(max_length=2,choices=GE_AREAS)

	def __str__(self):
		return self.area 

class PrereqGrade(models.Model):
	course = models.ForeignKey('Course',on_delete=models.CASCADE,related_name='The_Course')
	prereq = models.ForeignKey('Course',on_delete=models.CASCADE,related_name='The_Prereq')
	grade = models.CharField(max_length=2,choices=GRADES,default='C')

	class Meta:
		unique_together = ('course','prereq',)

	def __str__(self):
		return str(self.course) + ' -> ' + str(self.prereq)

class Course(models.Model):
	id = models.AutoField(primary_key=True)
	department = models.ForeignKey('Department',on_delete=models.RESTRICT)
	courseID = models.TextField()
	numUnits = models.IntegerField(default=3)
	prereqs = models.ManyToManyField('self',symmetrical=False,blank=True,related_name='Prerequisites',through='PrereqGrade')
	coreqs = models.ManyToManyField('self',symmetrical=False,blank=True,related_name='Corequisites')
	GEArea = models.ManyToManyField('GEArea', symmetrical=False, blank=True)

	class Meta:
		#Ensure that the combination of department and courseID is unique, pseudo-primary key
		unique_together = ('department', 'courseID', )
		ordering = ('department', 'courseID', )

	def __str__(self):
		return str(self.department) + ' ' + self.courseID

	def addPrereq(self,newPrereq,grade='C-'):
		prObject = PrereqGrade(course=self,prereq=newPrereq,grade=grade)
		prObject.save()

	def removePrereq(self,prereqCourse):
		prQuery = PrereqGrade.objects.filter(course=self).filter(prereq=prereqCourse)
		if(prQuery.count() > 0):
			prQuery.get().delete()

	def getPrereqs(self):
		prereqList = []
		for prereqClass in self.prereqs.all():
			grade = PrereqGrade.objects.filter(course=self).get(prereq=prereqClass).grade
			prereqList.append((prereqClass,grade))
		return prereqList





#====================Transfer Classes====================#
class TransferCourse(models.Model):
	id = models.AutoField(primary_key=True)
	school = models.ForeignKey('College',on_delete=models.RESTRICT)
	courseID = models.CharField(max_length=30)
	numUnits = models.IntegerField(default=3)

	class Meta:
		unique_together = ('school','courseID',)

class Articulation(models.Model):
	id = models.AutoField(primary_key=True)
	course = models.ForeignKey('TransferCourse',on_delete=models.CASCADE)
	SJSUCourse = models.ForeignKey('Course',on_delete=models.CASCADE)

	class Meta:
		unique_together = ('course','SJSUCourse',)





#====================Catalogs====================#

class GERequirement(models.Model):
	reqID = models.AutoField(primary_key=True)
	GEAreas =  models.ManyToManyField('GEArea',symmetrical=False)
	numCourses = models.IntegerField()


TERMS = (
	('Spring','Spring'),
	('Summer','Summer'),
	('Fall','Fall'),
	('Winter','Winter')
)

class CatalogueGrade(models.Model):
	course = models.ForeignKey('Course',on_delete=models.CASCADE)
	catalogue = models.ForeignKey('Catalogue',on_delete=models.CASCADE)
	grade = models.CharField(max_length=2,choices=GRADES,default='C-')
	GEReqID = models.ForeignKey('GERequirement',default=None,blank=True,null=True,on_delete=models.SET_NULL)

	def __str__(self):
		return str(self.catalogue) + ': ' + str(self.course)  


class Catalogue(models.Model):
	id = models.AutoField(primary_key=True)
	department = models.ForeignKey('Department',on_delete=models.RESTRICT)
	term = models.CharField(max_length=6,choices=TERMS)
	year = models.IntegerField()
	techUnits = models.IntegerField(default=7)
	courses = models.ManyToManyField('Course',symmetrical=False,through='CatalogueGrade')
	GEReqs = models.ManyToManyField('GERequirement',symmetrical=False)

	class Meta:
		#Ensure that the combination of department
		unique_together = ('department','year','term',)

	def __str__(self):
		return str(self.department) + ' ' + str(self.term) + ' ' + str(self.year) + ':'

	def addCourse(self,newCourse,grade='C-'):
		#TODO: Add GE Req checking
		cgObject = CatalogueGrade(catalogue=self,course=newCourse,grade=grade)
		cgObject.save()

	def removeCourse(self,reqCourse):
		cgQuery = CatalogueGrade.objects.filter(course=reqCourse).filter(catalogue=self)
		if(cgQuery.count() > 0):
			cgQuery.get().delete()

	def getCourses(self):
		courseList = []
		for reqCourse in self.courses.all():
			courseList.append()
		return courseList

class TechElective(models.Model):
	id = models.AutoField(primary_key=True)
	department = models.ForeignKey('Department',on_delete=models.CASCADE)
	course = models.ForeignKey('Course',on_delete=models.CASCADE)

	class Meta:
		unique_together = ('department','course',)





#====================User Transcripts====================#
CLASS_TYPE = (
	('General','General'),
	('GE','GE'),
	('Lower Div','Lower Div'),
	('Upper Div','Upper Div'),
	('Tech Elective','Tech Elective')
)

class TranscriptGrade(models.Model):
	course = models.ForeignKey('Course',on_delete=models.RESTRICT)
	transcript = models.ForeignKey('Transcript',on_delete=models.CASCADE)
	grade = models.CharField(max_length=2,choices=GRADES,default='F')
	courseType = models.CharField(max_length=13,choices=CLASS_TYPE,default='General')
	GEReqID = models.ForeignKey('GERequirement',default=None,blank=True,null=True,on_delete=models.SET_NULL)

class TransferGrade(models.Model):
	course = models.ForeignKey('TransferCourse',on_delete=models.RESTRICT)
	transcript = models.ForeignKey('Transcript',on_delete=models.CASCADE)
	grade = models.CharField(max_length=2,choices=GRADES,default='F')
	courseType = models.CharField(max_length=13,choices=CLASS_TYPE,default='General')

class Transcript(models.Model):
	id = models.AutoField(primary_key=True)
	coursesTaken = models.ManyToManyField('Course',symmetrical=False,through='TranscriptGrade')
	coursesTransfered = models.ManyToManyField('TransferCourse',symmetrical=False,through='TransferGrade')
	WSTPassed = models.BooleanField(default=False)





#====================Roadmap Fields====================#
class SemesterSchedule(models.Model):
	id = models.AutoField(primary_key=True)
	term = models.CharField(max_length=6,choices=TERMS)
	year = models.IntegerField()
	courses = models.ManyToManyField('Course',symmetrical=False)
	transferCourses = models.ManyToManyField('TransferCourse',symmetrical=False)

class Roadmap(models.Model):
	id = models.AutoField(primary_key=True)
	semesterSchedules = models.ManyToManyField('SemesterSchedule',symmetrical=True)






#====================Student Base Class====================#
class Student(models.Model):
	#TODO: Add reference from User
	studentID = models.CharField(max_length=9,primary_key=True)

	catalog = models.ForeignKey('Catalogue',on_delete=models.RESTRICT)
	roadmap = models.OneToOneField('Roadmap',on_delete=models.SET_NULL,default=None,blank=True,null=True)
	transcript = models.OneToOneField('Transcript',on_delete=models.SET_NULL,default=None,blank=True,null=True)

	friends = models.ManyToManyField('self',symmetrical=True,related_name='AcceptedFriends')
	friendRequests = models.ManyToManyField('self',symmetrical=False,related_name='RequestFriends')
