from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
from datetime import date

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

	class Meta:
		ordering = ('name',)

	def __str__(self):
		return str(self.name)

class Department(models.Model):
	abrv = models.TextField(primary_key=True)
	name = models.TextField()

	class Meta:
		ordering = ('abrv',)

	def __str__(self):
		return str(self.abrv)




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
	('Z','Z'),
	('US1','US1'),
	('US2','US2'),
	('US3','US3')
)

class GEArea(models.Model):
	area = models.CharField(max_length=3,choices=GE_AREAS,unique=True)

	class Meta:
		ordering = ('area',)

	def __str__(self):
		return self.area

class PrereqGrade(models.Model):
	course = models.ForeignKey('Course',on_delete=models.CASCADE,related_name='The_Course')
	prereq = models.ForeignKey('Course',on_delete=models.CASCADE,related_name='The_Prereq')
	grade = models.CharField(max_length=2,choices=GRADES,default='C-')

	class Meta:
		unique_together = ('course','prereq',)
		ordering = ('course','prereq',)

	def __str__(self):
		return str(self.course) + ' -> ' + str(self.prereq)

#Duplicated PrereqGrade with different name due to requirements using "Trhough" attribute for many-to-many
class OptionalPrereqGrade(models.Model):
	course = models.ForeignKey('Course', on_delete=models.CASCADE, related_name='The_Optional_Course')
	prereq = models.ForeignKey('Course', on_delete=models.CASCADE, related_name='The_Optional_Prereq')
	grade = models.CharField(max_length=2, choices=GRADES, default='C-')

	class Meta:
		unique_together = ('course', 'prereq',)
		ordering = ('course', 'prereq',)

	def __str__(self):
		return str(self.course) + ' -> ' + str(self.prereq)

class Course(models.Model):
	id = models.AutoField(primary_key=True)
	department = models.ForeignKey('Department',on_delete=models.RESTRICT)
	courseID = models.TextField()
	numUnits = models.IntegerField(default=3)
	prereqs = models.ManyToManyField('self',symmetrical=False,blank=True,related_name='Prerequisites',through='PrereqGrade')
	coreqs = models.ManyToManyField('self',symmetrical=False,blank=True,related_name='Corequisites')
	GEArea = models.ManyToManyField('GEArea', symmetrical=False, blank=True,related_name='GE_Areas')

	#Optional fields used for handling edge cases such as Senior Project Courses and 100W
	unitPrereq = models.IntegerField(default=0) #How many units must be taken before taking class
	requiresWST = models.BooleanField(default=False)
	isCapstone = models.BooleanField(default=False)
	isAlternateCapstone = models.BooleanField(default=False)

	#For handling Prereqs and Coreqs where N of the options must be taken (i.e Corequisite with CMPE195A OR EE198A, etc.)
	NOfPrereqs = models.ManyToManyField('self',symmetrical=False,blank=True,related_name='Optional_Prerequisites',through='OptionalPrereqGrade')
	NPrereqs = models.IntegerField(default=0)
	NOfCoreqs = models.ManyToManyField('self', symmetrical=False, blank=True, related_name='Optional_Corequisites')
	NCoreqs = models.IntegerField(default=0)

	#For handling GE Prerequisites (Certain GE Areas need to be taken first)
	GEPrereqs = models.ManyToManyField('GEArea', symmetrical=False, blank=True,related_name='GE_Prerequisites')


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
		ordering = ('school','courseID',)

	def __str__(self):
		return str(self.school) + ': ' + str(self.courseID)

class Articulation(models.Model):
	id = models.AutoField(primary_key=True)
	course = models.ForeignKey('TransferCourse',on_delete=models.CASCADE)
	SJSUCourse = models.ForeignKey('Course',on_delete=models.CASCADE)

	class Meta:
		unique_together = ('course','SJSUCourse',)
		ordering = ('course','SJSUCourse',)

	def __str__(self):
		return str(self.course) + " = SJSU: " + str(self.SJSUCourse)





#====================Catalogs====================#

class GERequirement(models.Model):
	reqID = models.AutoField(primary_key=True)
	GEAreas = models.ManyToManyField('GEArea',symmetrical=False)
	#Normally one of these will be Null
	#If numCourses not null, needs N courses in that area
	#If numUnits not null, needs N units in that area
	numCourses = models.IntegerField(blank=True,default=None,null=True)
	numUnits = models.IntegerField(blank=True,default=None,null=True)
	#If both not null, needs N courses worth that many units each
	#If both null, then just must be completed, no unit/course # requirement
	allowOverlap = models.BooleanField(default=False)
	#For single-GE areas, allowOverlap=False means if already used, cant be used again
	#For classes with Multiple GE area's (e.g ENGR100W), ignore this field, can be used for all listed areas

	class Meta:
		#TODO: Figure out how to sort by many-to-many field
		pass

	def __str__(self):
		areas = []
		for area in self.GEAreas.all():
			areas.append(str(area))
		return ','.join(areas)


TERMS = (
	('Spring','Spring'),
	('Fall','Fall'),
)

class CatalogueGrade(models.Model):
	course = models.ForeignKey('Course',on_delete=models.CASCADE)
	catalogue = models.ForeignKey('Catalogue',on_delete=models.CASCADE)
	grade = models.CharField(max_length=2,choices=GRADES,default='C-')
	GEReqID = models.ManyToManyField('GERequirement',symmetrical=False,blank=True)

	class Meta:
		unique_together = ('course','catalogue',)
		ordering = ('catalogue','course',)

	def __str__(self):
		return str(self.catalogue) + ': ' + str(self.course)


class Catalogue(models.Model):
	id = models.AutoField(primary_key=True)
	department = models.ForeignKey('Department',on_delete=models.RESTRICT)
	term = models.CharField(max_length=6,choices=TERMS)
	year = models.IntegerField()
	techUnits = models.IntegerField(default=7)
	courses = models.ManyToManyField('Course',symmetrical=False,through='CatalogueGrade',blank=True)
	GEReqs = models.ManyToManyField('GERequirement',symmetrical=False,blank=True)

	class Meta:
		#Ensure that the combination of department
		unique_together = ('department','year','term',)
		ordering = ('department','year','term')

	def __str__(self):
		return str(self.department) + ' ' + str(self.term) + ' ' + str(self.year) + ''

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
		ordering = ('department','course',)

	def __str__(self):
		return str(self.department) + ': ' + str(self.course)





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
	GEReqID = models.ManyToManyField('GERequirement',symmetrical=False,blank=True)

	class Meta:
		unique_together = ('course','transcript',)
		ordering = ('transcript','course',)

	def __str__(self):
		return str(self.transcript) + ': ' + str(self.course)

class TransferGrade(models.Model):
	course = models.ForeignKey('TransferCourse',on_delete=models.RESTRICT)
	transcript = models.ForeignKey('Transcript',on_delete=models.CASCADE)
	grade = models.CharField(max_length=2,choices=GRADES,default='F')
	courseType = models.CharField(max_length=13,choices=CLASS_TYPE,default='General')

	class Meta:
		unique_together = ('course','transcript',)
		ordering = ('transcript','course',)

	def __str__(self):
		return str(self.transcript) + ': ' + str(self.course)

class Transcript(models.Model):
	id = models.AutoField(primary_key=True)
	coursesTaken = models.ManyToManyField('Course',symmetrical=False,through='TranscriptGrade',blank=True)
	coursesTransfered = models.ManyToManyField('TransferCourse',symmetrical=False,through='TransferGrade',blank=True)
	WSTPassed = models.BooleanField(default=False)

	class Meta:
		#TODO: Figure out how to reference student with symetrical one-to-one
		pass

	def __str__(self):
		try:
			return str(self.student.user)
		except:
			return 'Unlinked Transcript: ' + str(self.id)






#====================Roadmap Fields====================#
class SemesterSchedule(models.Model):
	id = models.AutoField(primary_key=True)
	term = models.CharField(max_length=6,choices=TERMS)
	year = models.IntegerField()
	courses = models.ManyToManyField('Course',symmetrical=False,blank=True)
	transferCourses = models.ManyToManyField('TransferCourse',symmetrical=False,blank=True)

	class Meta:
		#TODO: Figure out how to reference roadmap with symetrical many-to-many
		pass

	def __str__(self):
		try:
			roadmap = Roadmap.objects.get(semesterSchedules__id=self.id)
			return str(roadmap) + ": " + str(self.term) + ' ' + str(self.year)
		except:
			return 'Unlinked SemesterSchedule: ' + str(self.id)

class Roadmap(models.Model):
	id = models.AutoField(primary_key=True)
	semesterSchedules = models.ManyToManyField('SemesterSchedule',symmetrical=False,related_name='From_Roadmap',blank=True)

	class Meta:
		#TODO: Figure out how to reference student with symetrical one-to-one
		pass

	def __str__(self):
		try:
			return str(self.student.user)
		except:
			return 'Unlinked Roadmap: ' + str(self.id)






#====================Student Base Class====================#
class PreferredCourse(models.Model):
	course = models.ForeignKey('Course',on_delete=models.CASCADE)
	student = models.ForeignKey('Student',on_delete=models.CASCADE)
	reqID = models.ManyToManyField('GERequirement',default=None,blank=True)
	courseType = models.CharField(max_length=13, choices=CLASS_TYPE, default='General')

	class Meta:
		ordering = ('student','course',)

	def __str__(self):
		return str(self.student) + ': ' + str(self.course)

class Student(models.Model):
	#TODO: Add reference from User
	id = models.AutoField(auto_created=True, primary_key=True)
	studentID = models.CharField(max_length=9,unique=True)
	user = models.OneToOneField(User, default=None, null=True, on_delete=models.CASCADE)
	startTerm = models.CharField(max_length=6,choices=TERMS,default='Fall')
	startYear = models.IntegerField(default=date.today().year)
	numSemesters = models.IntegerField(default=8)

	currentTerm = models.CharField(max_length=6, choices=TERMS, default='Fall')
	currentYear = models.IntegerField(default=date.today().year)

	catalogue = models.ForeignKey('Catalogue',on_delete=models.RESTRICT)
	prefCourseList = models.ManyToManyField('Course', symmetrical=False, blank=True, through='PreferredCourse')
	separateSV = models.BooleanField(default=False)
	roadmap = models.OneToOneField('Roadmap',on_delete=models.SET_NULL,default=None,blank=True,null=True)
	transcript = models.OneToOneField('Transcript',on_delete=models.SET_NULL,default=None,blank=True,null=True)

	friends = models.ManyToManyField('self',symmetrical=True,related_name='AcceptedFriends',blank=True)
	friendRequests = models.ManyToManyField('self',symmetrical=False,related_name='RequestFriends',blank=True)

	class Meta:
		#TODO: Order by user name later
		ordering = ('studentID',)

	def __str__(self):
		#TODO: Get student name from user later
		return str(self.user) + ': ' + str(self.studentID)

