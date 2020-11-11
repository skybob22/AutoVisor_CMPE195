from .models import *

##
# @brief Gets a tuple of all the grades better than the specified grade
# @param lowGrade the lowest grade you are willing to accept
# @return The tuple of grades higher than, and including the input grade
##
def gradeOrBetter(lowGrade):
    #List of existing grades (In order)
    GRADES = ('A+','A','A-','B+','B','B-','C+','C','C-','D+','D','D-','F')

    gradeList = []
    for grade in GRADES:
        gradeList.append(grade)
        if grade == lowGrade:
            break
    return tuple(gradeList)

##
# @brief Gets the weighted GPA of the logged in user
# @param user The currently logged in user
# @return The users GPA on a scale from 0.0-4.0
##
def getGPA(user):
    GPA_WEIGHT = {
        'A+': 4.0,
        'A': 4.0,
        'A-': 3.7,
        'B+': 3.3,
        'B': 3.0,
        'B-': 2.7,
        'C+': 2.3,
        'C': 2.0,
        'C-': 1.7,
        'D+': 1.3,
        'D': 1.0,
        'D-': 0.0,
        'F': 0.0
    }

    unitsTaken = 0
    totalGradePoints = 0
    for courseGrade in TranscriptGrade.objects.filter(transcript=user.student.transcript):
        courseUnits = courseGrade.course.numUnits
        unitsTaken = unitsTaken + courseUnits
        totalGradePoints = totalGradePoints + (GPA_WEIGHT[courseGrade.grade] * courseUnits)
    #TODO: Account for transfer classes
    return totalGradePoints/unitsTaken

##
# @brief Gets the number of units that the student has taken
# @param user The currently logged in user
# @return The number of units
##
def getUnitsTaken(user):
    unitsTaken = 0
    for courseGrade in TranscriptGrade.objects.filter(transcript=user.student.transcript).filter(grade__in=gradeOrBetter('C-')):
        unitsTaken = unitsTaken + courseGrade.course.numUnits
    #TODO: Account for transfer classes
    return unitsTaken

##
# @brief Gets all the classes that the user has passed that fulfill a GE requirement
# @param user The logged in user
# @return A Django Queryset of type 'Course' containing all the classes the user has passed
##
def getPassedGE(user):

    completedGECourses = TranscriptGrade.objects.filter(transcript=user.student.transcript).filter(GEReqID__isnull=False).filter(grade__in=gradeOrBetter('C-'))
    return completedGECourses

##
# @brief Gets all the GE area that the user has not taken, and has not planned to take
# @param user The logged in user
# @return A Django Queryset of type 'Course' containing all the classes that fulfill GE requirements that the user has passed
##
def getMissingGE(user):
    completedGECourses = getPassedGE(user)
    completedGEAreas = completedGECourses.values('GEReqID')
    GENotCompleted = user.student.catalogue.GEReqs.exclude(reqID__in=completedGEAreas)

    plannedGECourses = PreferredCourse.objects.filter(student=user.student).filter(reqID__isnull=False)
    plannedGEAreas = plannedGECourses.values('reqID')
    GENotAccounted = GENotCompleted.exclude(reqID__in=plannedGEAreas)

    #TODO: Account for single-requirement GE, like Area B, C, etc.
    # Then check for multi-area. Has "C1 AND C2" been completed?

    return GENotAccounted

    #return querySet
        # If list is empty, procede
        # If list is not empty, warn user and do not continue

        # Also can be used on dynamic page as list of preference to fill

##
# @brief Gets all the tech electives that the user has passed
# @parm user The logged in user
# @return  Django Queryset of the tech electives that the user has passed
##
def getPassedTech(user):

    completedTechElectives = TranscriptGrade.objects.filter(transcript=user.student.transcript).filter(courseType='Tech Elective').filter(grade__in=gradeOrBetter('C-'))
    return completedTechElectives

##
# @brief Gets the number of units worth of tech electives that the user has not taken or plans to take
# @parma user The logged in user
# @return The number of units the user needs to schedule/choose
##
def getMissingTech(user):
    numUnitsTaken = 0

    completedTechElectives = getPassedTech(user)
    for courseGrade in completedTechElectives:
        numUnitsTaken = numUnitsTaken + courseGrade.course.numUnits

    plannedTechElectives = PreferredCourse.objects.filter(student=user.student).filter(courseType='Tech Elective')
    for plannedCourse in plannedTechElectives:
        numUnitsTaken = numUnitsTaken + plannedCourse.course.numUnits

    unitsRequired = user.student.catalogue.techUnits
    unitsUnaccounted = unitsRequired - numUnitsTaken

    return unitsUnaccounted

    # Return number
        # If number is zero or negative, continue all classes fulfilled
        # If posative, do not continue, warn User

        # Can also be used on dynamic page to get number of units needed to select

##
# @brief Gets all the classes that the user has passed
# @param user The logged in user
# @return A Django Queryset of type 'Course' containing all the classes that the user has passed
def getPassedClasses(user):

    coursesTaken = TranscriptGrade.objects.filter(transcript=user.student.transcript)
    coursesPassed = Course.objects.none()

    for trGrade in coursesTaken:

        #Check the core classes
        catGrade = CatalogueGrade.objects.filter(catalogue=user.student.catalogue).filter(course=trGrade.course)
        if len(catGrade) > 0 and trGrade.grade in gradeOrBetter(catGrade.get().grade):
            #Is a core class, has a required grade
            courseQuery = Course.objects.filter(id=catGrade.get().course.id)
            coursesPassed = (coursesPassed | courseQuery)
        elif trGrade.grade in gradeOrBetter('C-'):
            courseQuery = Course.objects.filter(id=trGrade.course.id)
            coursesPassed = (coursesPassed | courseQuery)

    return coursesPassed