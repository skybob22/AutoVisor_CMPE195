from .models import *
import datetime

##
# @brief Gets a tuple of all the grades better than the specified grade
# @param lowGrade the lowest grade you are willing to accept
# @return The tuple of grades higher than, and including the input grade
##
def gradeOrBetter(lowGrade):
    # List of existing grades (In order)
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
    # TODO: Account for transfer classes
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
    # TODO: Account for transfer classes
    return unitsTaken

##
# @brief Gets all the GE area that the user has not taken, and has not planned to take
# @param user The logged in user
# @param countPlanned Whether to count planned GEs as "completed"
# @param countInProgress Whether to count in-progress GEs as "completed"
# Note: if countPlanned is set to true, the result will also include in-progress classes
# @return A Django Queryset of type 'Course' containing all the classes that fulfill GE requirements that the user has passed
##
def getMissingGEAreas(user,countPlanned=True,countInProgress=True):
    AllGECourses = Course.objects.filter(GEArea__isnull=False).distinct()

    catalogGEs = Catalogue.objects.get(id=user.student.catalogue.id).GEReqs.all()
    singleReqs = GERequirement.objects.filter(reqID__in=catalogGEs).filter(allowOverlap=False).all()
    multiReqs = GERequirement.objects.filter(reqID__in=catalogGEs).filter(allowOverlap=True).all()

    # Get all the courses that the user has already passed
    completedGEGrades = TranscriptGrade.objects.filter(transcript=user.student.transcript).filter(
        grade__in=gradeOrBetter('C-')).filter(course__id__in=AllGECourses)
    completedGECourses = Course.objects.filter(id__in=completedGEGrades.values('course'))

    if countInProgress and user.student.roadmap:
        # Assume any classes in progress will be passed to avoid rescheduling them again in the future
        currentYear,currentTerm = dateToSemester(datetime.date.today())
        studentSchedules = SemesterSchedule.objects.filter(id__in=user.student.roadmap.semesterSchedules.all())
        currentSemSchedule = studentSchedules.filter(year=currentYear).filter(term=currentTerm)
        currentGEs = Course.objects.filter(id__in=AllGECourses).filter(id__in=currentSemSchedule.values('courses'))
        if len(currentSemSchedule) > 0:
            # Student has roadmap for the current semester
            completedGECourses = (completedGECourses | Course.objects.filter(id__in=currentGEs))

    # Count GEs covered by major classes as "Completed" even if they are not, since the user does not need to pick them
    if user.student.separateSV:
        capstoneClasses = (Course.objects.filter(isCapstone=True) | Course.objects.filter(department='ENGR').filter(courseID__contains='195'))
        coreGECourses = Course.objects.filter(id__in=user.student.catalogue.courses.all()).filter(id__in=AllGECourses).exclude(id__in=capstoneClasses)
    else:
        coreGECourses = Course.objects.filter(id__in=user.student.catalogue.courses.all()).filter(id__in=AllGECourses)
    finishedGECourses = (completedGECourses | (coreGECourses.exclude(id__in=completedGECourses.values('id'))))


    # If countPlanned is True, assume classes that are planned to take as complete
    # This can be used to distinguish between GEs that ARE COMPLETE, vs ones that WILL BE TAKEN
    if countPlanned:
        plannedCourses = Course.objects.filter(id__in=user.student.prefCourseList.all()).filter(id__in=AllGECourses).exclude(id__in=finishedGECourses)
        finishedGECourses = (finishedGECourses | plannedCourses)

    # Set up data structures for tracking requirements
    uncompletedRequirements = dict()
    for requirement in (singleReqs | multiReqs):
        uncompletedRequirements[requirement] = [requirement.numCourses,requirement.numUnits]

    for requirement in list(uncompletedRequirements.keys()):
        satisfyingCourses = finishedGECourses.filter(GEArea__in=requirement.GEAreas.all()).distinct()
        if requirement.numUnits is None and requirement.numCourses is None:
            # Number of units/courses does not matter, only that area is fulfilled
            if len(satisfyingCourses) > 0:
                uncompletedRequirements.pop(requirement)
        elif requirement.numUnits is not None and requirement.numCourses is None:
            # Number of courses doesn't matter, but need to take a certain number of units
            totalUnits = 0
            for course in satisfyingCourses.all():
                totalUnits += course.numUnits

            if totalUnits >= requirement.numUnits:
                uncompletedRequirements.pop(requirement)
            else:
                uncompletedRequirements[requirement][1] -= totalUnits

        elif requirement.numUnits is None and requirement.numCourses is not None:
            # Number of units doesn't matter, but certain number of courses need to be taken
            if len(satisfyingCourses) >= requirement.numCourses:
                uncompletedRequirements.pop(requirement)
            else:
                uncompletedRequirements[requirement][0] -= len(satisfyingCourses)

        elif requirement.numUnits is not None and requirement.numCourses is not None:
            # Requirement dicates at least numCourses classes which must be at lean numUnits units
            satisfyingCourses = satisfyingCourses.filter(numUnits__gte=requirement.numUnits)
            if len(satisfyingCourses) >= requirement.numCourses:
                uncompletedRequirements.pop(requirement)
            else:
                uncompletedRequirements[requirement][0] -= len(satisfyingCourses)

    #Array formatted as tuple(requirement,numCourses,numUnits)
    requirementArray = []
    for requirement, values in uncompletedRequirements.items():
        requirementArray.append((requirement, values[0], values[1]))

    return (uncompletedRequirements)

##
# @brief Gets the number of units worth of tech electives that the user has not taken or plans to take
# @parma user The logged in user
# @param countPlanned Whether to count planned tech electives as "completed"
# @param countInProgress Whether to count in-progress tech electives as "completed"
# Note: if countPlanned is set to true, the result will also include in-progress classes
# @return The number of units the user needs to schedule/choose
##
def getMissingTech(user,countPlanned=True,countInProgress=True):
    numUnitsTaken = 0

    majorTechElectives = Course.objects.filter(id__in=TechElective.objects.filter(department=user.student.catalogue.department).values('course'))

    completedTechElectives = TranscriptGrade.objects.filter(transcript=user.student.transcript).filter(course__id__in=majorTechElectives).filter(grade__in=gradeOrBetter('C-'))
    for courseGrade in completedTechElectives:
        numUnitsTaken += courseGrade.course.numUnits

    if countInProgress and user.student.roadmap:
        currentYear, currentTerm = dateToSemester(datetime.date.today())
        studentSchedules = SemesterSchedule.objects.filter(id__in=user.student.roadmap.semesterSchedules.all())
        currentSemSchedule = studentSchedules.filter(year=currentYear).filter(term=currentTerm)
        currentTechElectives = majorTechElectives.filter(id__in=currentSemSchedule.values('courses'))
        for course in currentTechElectives:
            numUnitsTaken += course.numUnits



    if countPlanned:
        plannedTechElectives = PreferredCourse.objects.filter(student=user.student).filter(course__id__in=majorTechElectives)
        if countInProgress and user.student.roadmap:
            # Make sure to not double-count planned units
            plannedTechElectives = plannedTechElectives.exclude(course__id__in=currentTechElectives)
        for elective in plannedTechElectives:
            numUnitsTaken += elective.course.numUnits

    unitsRequired = user.student.catalogue.techUnits
    unitsUnaccounted = unitsRequired - numUnitsTaken

    return unitsUnaccounted if unitsUnaccounted > 0 else 0

##
# @brief Gets all the classes that the user has passed
# @param user The logged in user
# @param countInProgress Whether to treat in-progress classes as passed
# @return A Django Queryset of type 'Course' containing all the classes that the user has passed
def getPassedClasses(user,countInProgress=False):
    # TODO: Implement countInProgress

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

    if countInProgress and user.student.roadmap:
        currentYear, currentTerm = dateToSemester(datetime.date.today())
        studentSchedules = SemesterSchedule.objects.filter(id__in=user.student.roadmap.semesterSchedules.all())
        currentSemSchedule = studentSchedules.filter(year=currentYear).filter(term=currentTerm)
        currentClasses = Course.objects.filter(id__in=currentSemSchedule.values('courses'))
        coursesPassed = (coursesPassed | currentClasses)

    return coursesPassed

##
# @brief Gets the courses in the indexed semester based on the user's start date
# @param The index from the user's start date
# @return The courses in that semester (in a python list)
##
def getCoursesInSemester(user,index):
    currentYear,currentTerm = indexToSemester(index,startYear=user.student.startYear,startTerm=user.student.startTerm)
    studentSchedules = SemesterSchedule.objects.filter(id__in=user.student.roadmap.semesterSchedules.all())
    currentSemSchedule = studentSchedules.filter(year=currentYear).filter(term=currentTerm)
    currentClasses = Course.objects.filter(id__in=currentSemSchedule.values('courses'))

    classList = [i for i in currentClasses.all()]
    classList.sort(key=str)

    return classList

##
# @brief Converts a python date object into a semester
# @param A python date object
# @return The semester that the date most closely corresponds to
# Format is (year, term)
# If in the middle of semester, returns current semester
# If not in middle of semester, returns previous semester
##
def dateToSemester(date,includeOffSemester=False):
    #Dates matter, but year doesn't for comparison, so all years set to 1970
    SPRING_START_DATE = datetime.date(1970,1,27)
    SPRING_END_DATE = datetime.date(1970,5,25)
    SUMMER_START_DATE = None
    SUMMER_END_DATE = None
    FALL_START_DATE = datetime.date(1970,8,19)
    FALL_END_DATE = datetime.date(1970,12,15)
    WINTER_START_DATE = None
    WINTER_END_DATE = None

    modDate = date
    modDate.replace(year=1970)
    if includeOffSemester:
        pass

    if SPRING_START_DATE <= modDate and modDate < FALL_START_DATE:
        #Spring semester of current year
        return date.year,'Spring'
    elif FALL_START_DATE <= modDate:
        #Fall semester of current year
        return date.year,'Fall'
    elif modDate < SPRING_START_DATE:
        #Fall semester of last year
        return date.year-1,'Fall'

##
# @brief Converts a semester index (0,1,2,etc.) into year/term format given the starting semester
# @param index The semester index
# @param startyear, the year of the student's first semester
# @param startTerm which term the student started (Spring/Fall)
# @return The semester in the format year,term
##
def indexToSemester(index,startYear,startTerm):
    if startTerm == 'Spring':
        offset = 0
    elif startTerm == 'Fall':
        offset = 1
    else:
        offset = 0
    index += offset

    year = startYear
    #Handles negative indicies
    while index < -1:
        year -= 1
        index = index + 2

    while index > 1:
        year += 1
        index = index - 2

    if index == 0:
        return year,'Spring'
    else:
        if index < 0:
            year = year + index
        return year,'Fall'

##
# @brief Converts a semester (i.e 2019, Spring) into a semester index based on the provided start date
# @param year The year
# @param term The term (Spring,Fall)
# @param startDate The user's starting date
# @return the index of that semester
##
def semesterToIndex(year,term,startyear,startTerm):
    if startTerm == 'Spring':
        offset = 0
    elif startTerm == 'Fall':
        offset = 1
    else:
        offset = 0

    index = 2 * (year-startyear)
    if term == 'Fall':
        index += 1
    index -= offset

    return index