from django.contrib import admin
#from .models import Post, Course, Catalogue, Department, PrereqGrade, GEArea
from .models import *

# Register your models here.
admin.site.register(Post)
admin.site.register(Course)
admin.site.register(Catalogue)
admin.site.register(Department)
admin.site.register(PrereqGrade)
admin.site.register(GEArea)
admin.site.register(CatalogueGrade)
admin.site.register(GERequirement)


admin.site.register(Student)
admin.site.register(Transcript)
admin.site.register(TranscriptGrade)
admin.site.register(PreferredCourse)
