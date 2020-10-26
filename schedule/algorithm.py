from .models import *




##
# @brief Generates a roadmap for the user based on preferences
# @param user The logged in user
##
def generateRoadmap(user):
    pass
    # This is the algorithm flow, not purely "Call this function to do thing"

    # Have user enter desired GEs and Tech electives
        # Have some kind dynamic web portal
        # Check list of GE requirements
        # Find which ones are not fulfilled
            # Ask user to enter preference for those ones

    # Before generating roadmap, make sure all GE reqs and tech electives are met between preferred courses and transcript


    missingGE = getMissingGE(user)
    missingTech = getMissingTech(user)

    #All classes are accounted for
    courseGraph = Graph(user)
    generator = RoadMapGenerator(user,courseGraph)
    gen0 = generator.getGen0()

    return missingTech

    # Run genetic algorithm
    # Save to database
    # Display to user

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
        if catGrade and trGrade.grade in gradeOrBetter(catGrade.get().grade):
            #Is a core class, has a required grade
            courseQuery = Course.objects.filter(id=catGrade.get().course.id)
            coursesPassed = (coursesPassed | courseQuery)
        elif trGrade.grade in gradeOrBetter('C-'):
            courseQuery = Course.objects.filter(id=trGrade.course.id)
            coursesPassed = (coursesPassed | courseQuery)

    return coursesPassed


class Graph:
    class Node:
        def __init__(self):
            self.preReqs = []
            self.coReqs = []
            self.postReqs = []

            self.SJSUCourse = None
            self.TransferCourse = None

            self.max_sem_level = None

        def __str__(self):
            if self.TransferCourse is not None:
                return str(self.TransferCourse)
            elif self.SJSUCourse is not None:
                return str(self.SJSUCourse)
            else:
                return 'No Course Available'

        def __eq__(self,other):
            return self.SJSUCourse.id == other.SJSUCourse.id

        def __hash__(self):
            return hash(str(self.SJSUCourse))

    def __init__(self,user):
        self.user = user

        self.nodes = dict() #Key = 'CMPE 135', value = Node()
        self.rootNodes = set()
        self._createGraph()

    def _createGraph(self):
        pass
        # Grab all classes in the catalogue (copy of list)?
        # Add on to list with GEs and Tech electives

        passedClasses = getPassedClasses(self.user)
        self.passedClasses = passedClasses

        coreToTake = self.user.student.catalogue.courses.exclude(id__in=passedClasses.values('id'))
        optionalToTake = self.user.student.prefCourseList.exclude(id__in=passedClasses.values('id'))

        #Combine list to get all the courses to take, discarding duplicates
        toSchedule = (coreToTake | (optionalToTake.exclude(id__in=coreToTake.values('id'))))

        # Check courses from transfer that articulate

        for course in toSchedule:
            self._addCourse(course)

        pass



    def _addCourse(self,course):
        if self._userPassed(course):
            return None

        #Create new node
        courseNode = Graph.Node()
        #Is course Transfer
        if type(course) == TransferCourse:
            pass
        else:
            courseNode.SJSUCourse = course

        #Check if node already exists
        if str(courseNode) in self.nodes:
            return self.nodes[str(courseNode)]

        #Node isn't in graph, continue
        self.nodes[str(courseNode)] = courseNode

        for coReq in course.coreqs.all():
            coReqNode = self._addCourse(coReq)
            if coReqNode:
                courseNode.coReqs.append(coReqNode)

        if len(course.prereqs.all()) > 0:
            for preReq in course.prereqs.all():
                preReqNode = self._addCourse(preReq)
                if preReqNode:
                    courseNode.preReqs.append(preReqNode)
                    preReqNode.postReqs.append(courseNode)
        else:
            isRoot = True
            for coReq in courseNode.coReqs:
                if coReq not in self.rootNodes:
                    isRoot = False
            if isRoot:
                self.rootNodes.add(courseNode)

        return courseNode

    def _userPassed(self,course):
        return len(self.passedClasses.filter(id=course.id)) > 0


class RoadMapGenerator:
    def __init__(self,user,graph):
        self.user = user
        self.graph = graph

    def getGen0(self):
        num_semester_left = self.user.student.numYears * 2

        roadmap = [[] for y in range(num_semester_left)]
        for key,node in self.graph.nodes.items():
            longest_chain = self._traverse(node)
            node.max_sem_level = num_semester_left - len(longest_chain)

            for coReqNode in node.coReqs:
                if not coReqNode.max_sem_level:
                    coReq_longest_chain = self._traverse(coReqNode)
                    coReqNode.max_sem_level = num_semester_left - len(coReq_longest_chain)
                if coReqNode.max_sem_level < node.max_sem_level:
                    node.max_sem_level = coReqNode.max_sem_level
            if node.max_sem_level < 0:
                raise UserWarning("Not enough time left to complete class")

            #Very rudimentary generation 0 schedule, based on prereq levels
            roadmap[node.max_sem_level].append(node)

        #TODO: Try to push classes up the heierarchy that don't have prereqs
        # To even out the number of classes per semester
        return roadmap

    def _traverse(self,node):
        courseList = []

        if not node.postReqs:
            courseList.append(node)
            return courseList
        else:
            for postReqNode in node.postReqs:
                retList = self._traverse(postReqNode)
                if len(retList) > len(courseList):
                    courseList = retList
            courseList.insert(0,node)
            return courseList

    def _getLongestChain(self,node):
            longestChain = []
            for rootNode in self.graph.rootNodes:
                retList = self._traverse(rootNode)
                if len(retList) > len(longestChain):
                    longestChain = retList
            return longestChain






    def _geneticAlgorithm(self):
        pass
        # Run genetic algorithm (requires fitness function)
        # Optimizes array of arrays to be better
        # (Tentative) ex. min 20 generations & fitness above 85%
