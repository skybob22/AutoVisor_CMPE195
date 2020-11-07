from .models import *
from .util import *
import random




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

    tempVar = generator.getRoadmap();
    return tempVar

    #Test return string for testing purposes
    tempStr = 'Your GPA: ' + str(getGPA(user)) + '\n\n'
    tempStr = tempStr + 'Your Schedule:\n'
    for i in range(len(gen0)):
        tempStr = tempStr + 'Semester {0}:\n'.format(i+1)
        for j in range(len(gen0[i])):
            tempStr = tempStr + str(gen0[i][j])
            if j < len(gen0[i])-1:
                tempStr = tempStr + ','
        tempStr = tempStr + '\n\n\n'
    return tempStr

    # Run genetic algorithm
    # Save to database
    # Display to user



class Graph:
    class Node:
        def __init__(self):
            self.preReqs = []
            self.coReqs = []
            self.postReqs = []

            self.SJSUCourse = None
            self.TransferCourse = None

            self.max_sem_level = None

        def getNumUnits(self):
            if self.TransferCourse is None:
                return self.SJSUCourse.numUnits
            else:
                #TODO: Account for transfer courses
                return None

        def getCourse(self):
            if self.TransferCourse is None:
                return self.SJSUCourse
            else:
                return None

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
        self.standby = dict() #Key = 'CMPE 135', value = Node()
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
        if len(self.standby) > 0:
            raise UserWarning("Required Corequisite classes not taken or planned")

    def _updateStandby(self,node):
        for key in list(self.standby.keys()):
            #Forced to do this way to avoid "Dictionary changed size" error
            standbyNode = self.standby[key]
            #Check to see if the new node is a CoReq of any of the listed nodes
            optCoReqList = standbyNode.SJSUCourse.NOfCoreqs.all()
            if node not in standbyNode.coReqs and node.SJSUCourse in optCoReqList:
                numOptCoReq = standbyNode.SJSUCourse.NCoreqs
                foundCoReqs = 0
                #Start by finding how many of the items in the coreq list are actually the optional coreqs
                for coReq in standbyNode.coReqs:
                    if coReq.SJSUCourse in optCoReqList:
                        foundCoReqs = foundCoReqs + 1

                #Add the new node to the coreq list
                standbyNode.coReqs.append(node)
                foundCoReqs = foundCoReqs + 1
                #If there are now enough optional coreqs, remove from standby list
                if foundCoReqs >= numOptCoReq:
                    self.standby.pop(str(standbyNode))

    def _addCourse(self,course):
        if self._userPassed(course):
            return None

        #Create new node
        courseNode = Graph.Node()
        #Is course Transfer
        if type(course) == TransferCourse:
            #TODO: Implement transfer courses
            pass
        else:
            courseNode.SJSUCourse = course

        #Check if node already exists
        if str(courseNode) in self.nodes:
            return self.nodes[str(courseNode)]

        #Node isn't in graph, continue
        self.nodes[str(courseNode)] = courseNode

        #Add coreqs to the graph
        for coReq in course.coreqs.all():
            coReqNode = self._addCourse(coReq)
            if coReqNode is not None:
                courseNode.coReqs.append(coReqNode)

        # Check optional co/prereqs to see if needs to be on standby
        numOptCoReq = course.NCoreqs
        if numOptCoReq > 0:
            foundCoReqs = 0
            for coReq in course.NOfCoreqs.all():
                if foundCoReqs < numOptCoReq and str(coReq) in self.nodes and self.nodes[str(coReq)] not in courseNode.coReqs:
                    courseNode.coReqs.append(self.nodes[str(coReq)])
                    foundCoReqs = foundCoReqs + 1
            if foundCoReqs < numOptCoReq:
                self.standby[str(courseNode)] = courseNode

        #Add prereqs to the map
        if len(course.prereqs.all()) > 0:
            for preReq in course.prereqs.all():
                preReqNode = self._addCourse(preReq)
                if preReqNode is not None:
                    courseNode.preReqs.append(preReqNode)
                    preReqNode.postReqs.append(courseNode)
        else:
            isRoot = True
            for coReq in courseNode.coReqs:
                if coReq not in self.rootNodes:
                    isRoot = False
            if isRoot:
                self.rootNodes.add(courseNode)

        #Now that node is added, update standby nodes in case is optional requirement
        self._updateStandby(courseNode)

        return courseNode

    def _userPassed(self,course):
        return len(self.passedClasses.filter(id=course.id)) > 0





class RoadMapGenerator:
    def __init__(self,user,graph):
        self.user = user
        self.graph = graph

    def _numUnitsInSemester(self,semesterList):
        numUnits = 0
        for courseNode in semesterList:
            numUnits = numUnits + courseNode.getNumUnits()
        return numUnits

    def _getGen0Candidate(self):
        num_semester_left = self.user.student.numYears * 2

        roadmap = [[] for y in range(num_semester_left)]
        for key,node in self.graph.nodes.items():
            longest_chain = self._traverse(node)
            node.max_sem_level = num_semester_left - len(longest_chain)

            for coReqNode in node.coReqs:
                if coReqNode.max_sem_level is None:
                    coReq_longest_chain = self._traverse(coReqNode)
                    coReqNode.max_sem_level = num_semester_left - len(coReq_longest_chain)
                if coReqNode.max_sem_level < node.max_sem_level:
                    node.max_sem_level = coReqNode.max_sem_level
            if node.max_sem_level < 0:
                raise UserWarning("Not enough time left to complete class")

            #Very rudimentary generation 0 schedule, based on prereq levels
            roadmap[node.max_sem_level].append(node)

        #Spread out classes across semester
        roadmap = self._distrubuteClasses(roadmap)
        return roadmap

    def getRoadmap(self,genNew=False,save=True):
        roadmap = []
        if genNew or not self.user.student.roadmap:
            #Generate new roadmap
            gen0 = self._getGen0Candidate()
            #Do genetic aglroithm stuff with multiple gen 0s
            roadmap = gen0

            if save:
                self._saveToDB(roadmap)
        else:
            roadmap = self.user.student.roadmap
        return roadmap

    def _saveToDB(self,semList):
        student = self.user.student

        if student.roadmap:
            oldRoadmap = student.roadmap
            semSchedules = list(oldRoadmap.semesterSchedules.all())
            for i in range(len(semSchedules)):
                semSchedule = semSchedules[i]
                oldRoadmap.semesterSchedules.remove(semSchedule)
                semSchedule.delete()
            student.roadmap = None
            oldRoadmap.delete()

        # Create new roadmap
        newRoadmap = Roadmap()
        newRoadmap.save()

        scheduleList = [None] * len(semList)
        for i in range(len(semList)):
            #TODO: Fix hardcoded semester
            scheduleList[i] = SemesterSchedule(term='Fall', year=2020)
            scheduleList[i].save()
            for course in semList[i]:
                pass
                scheduleList[i].courses.add(course)

        for semSchedule in scheduleList:
            if semSchedule is not None:
                newRoadmap.semesterSchedules.add(semSchedule)

        student.roadmap = newRoadmap
        student.save()

    def _distrubuteClasses(self,roadmap):
        num_semester_left = self.user.student.numYears * 2
        num_units_left = 0
        for key,node in self.graph.nodes.items():
            num_units_left = num_units_left + node.getNumUnits()

        #TODO: This is very inefficient, try to find better way to do it?
        units_per_semester = max(num_units_left/num_semester_left,16)
        units_completed = getUnitsTaken(self.user)
        for _pass in range(len(roadmap)):
            #Have to do multiple passes so that classes "Bubble" up to the top
            for i in range(len(roadmap)-1):
                moveCandidates = []
                for courseNode in roadmap[i+1]:
                    movable = True
                    #Check to make sure Pre-Req has been taken beforehand
                    for prereqNode in courseNode.preReqs:
                        if prereqNode in roadmap[i]:
                            movable = False
                            break
                    #Check to keep Co-Reqs together
                    if len(courseNode.coReqs) > 0:
                        #TODO: Account for moving sets of coreqs,
                        # Currently not accounted for
                        movable = False
                    #Check to make sure user has enough units
                    if courseNode.SJSUCourse.unitPrereq > 0:
                        unitsAtPrevSem = units_completed
                        #Calculate how many units the student will have going into the previous semester
                        #TODO: Test this is correct once we have more data
                        for j in range(0,i-1):
                            unitsAtPrevSem = units_completed + self._numUnitsInSemester(roadmap[j])
                        if unitsAtPrevSem < courseNode.SJSUCourse.unitPrereq:
                            #If they will not have completed enough units to take the class, it can't be moved
                            movable = False
                    if movable:
                        moveCandidates.append(courseNode)

                while self._numUnitsInSemester(roadmap[i]) < units_per_semester and len(moveCandidates) > 0:
                    index = random.randint(0,len(moveCandidates)-1)
                    candidateNode = moveCandidates[index]
                    if self._numUnitsInSemester(roadmap[i]) + candidateNode.getNumUnits() <= units_per_semester:
                        roadmap[i].append(candidateNode)
                        roadmap[i+1].remove(candidateNode)
                    moveCandidates.remove(candidateNode)

        finalRoadmap = []
        for semester in roadmap:
            semesterSchedule = []
            for course in semester:
                semesterSchedule.append(course.getCourse())
            finalRoadmap.append(semesterSchedule)
        return finalRoadmap

    def _traverse(self,node):
        courseList = []

        if node.postReqs is None:
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
