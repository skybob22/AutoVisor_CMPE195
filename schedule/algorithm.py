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
                    self.standby.pop(standbyNode)

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
        if courseNode in self.nodes:
            return self.nodes[courseNode]

        #Node isn't in graph, continue
        self.nodes[courseNode] = courseNode

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
                if foundCoReqs < numOptCoReq and coReq in self.nodes and self.nodes[coReq] not in courseNode.coReqs:
                    courseNode.coReqs.append(self.nodes[coReq])
                    foundCoReqs = foundCoReqs + 1
            if foundCoReqs < numOptCoReq:
                self.standby[courseNode] = courseNode

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
    class CourseTracker:
        def __init__(self,numSemesters):
            #Speed is more important that memory usage, use two dictionaries for fast lookup
            self.courseDict = dict() #Dictioanry of <courseNode,semester>
            self.roadmap = [[] for _ in range(numSemesters)]

        def getNumSemesters(self):
            return len(self.roadmap)

        def numCoursesInSemester(self,semester):
            return len(self.roadmap[semester])

        def courseScheduled(self,node):
            return node in self.courseDict

        def placeCourse(self,node,semester):
            nodeOverwritten = False
            #Handles both moving and inserting courses
            if node in self.courseDict:
                nodeOverwritten = True
                semToRemove = self.courseDict[node]
                self.roadmap[semToRemove].remove(node)
            self.courseDict[node] = semester
            self.roadmap[semester].append(node)
            return nodeOverwritten

        def getNodeRoadmap(self):
            for i in range(len(self.roadmap)):
                self.roadmap[i].sort(key=str)
            return self.roadmap

        def getNodeSemester(self,semester):
            self.roadmap[semester].sort(key=str)
            return self.roadmap[semester]

        def getSemesterTaken(self,node):
            if node in self.courseDict:
                return self.courseDict[node]
            else:
                return None

        def maxCoreqSemester(self,node):
            max_sem = 0
            for coReqNode in node.coReqs:
                if coReqNode in self.courseDict:
                    max_sem = max(max_sem,self.courseDict[coReqNode])
                else:
                    return None
            return max_sem

        def maxPrereqSemester(self,node):
            max_sem = 0
            for preReqNode in node.preReqs:
                if preReqNode in self.courseDict:
                    max_sem = max(max_sem,self.courseDict[preReqNode])
                else:
                    return None
            return max_sem

        def unitsInSemester(self,semester):
            numUnits = 0
            for courseNode in self.roadmap[semester]:
                numUnits += courseNode.getNumUnits()
            return numUnits

        def unitsUptoSemester(self,semester):
            numUnits = 0
            for i in range(semester+1):
                numUnits += self.unitsInSemester(i)
            return numUnits

        def getCourseRoadmap(self):
            courses = [[] for _ in range(len(self.roadmap))]
            for i in range(len(self.roadmap)):
                self.roadmap[i].sort(key=str)
                courses[i] = [course.getCourse() for course in self.roadmap[i]]
            return courses



    def __init__(self,user,graph):
        self.user = user
        self.graph = graph

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

    def _getGen0Candidate(self):
        num_semester_left = self.user.student.numYears * 2

        #roadmap = [[] for y in range(num_semester_left)]
        for key,node in self.graph.nodes.items():
            longest_chain = self._traverse(node)
            if not node.max_sem_level:
                node.max_sem_level = num_semester_left - len(longest_chain)

            for coReqNode in node.coReqs:
                if coReqNode.max_sem_level is None:
                    coReq_longest_chain = self._traverse(coReqNode)
                    coReqNode.max_sem_level = num_semester_left - len(coReq_longest_chain)
                if coReqNode.max_sem_level > node.max_sem_level:
                    coReqNode.max_sem_level = node.max_sem_level
            if node.max_sem_level < 0:
                raise UserWarning("Not enough time left to complete class")

        # Very rudimentary generation 0 schedule, based on prereq levels
        roadmap = self.CourseTracker(self.user.student.numYears * 2)
        for key, node in self.graph.nodes.items():
            #roadmap[node.max_sem_level].append(node)
            roadmap.placeCourse(node,node.max_sem_level)

        #Spread out classes across semester
        roadmap = self._distrubuteClasses(roadmap)
        return roadmap

    def _distrubuteClasses(self,roadmap):
        numSemestersLeft = roadmap.getNumSemesters()
        units_completed = getUnitsTaken(self.user)

        #TODO: Account for different unit allowances
        numUnitsLeft = roadmap.unitsUptoSemester(numSemestersLeft-1)
        unitsPerSemester = max(numUnitsLeft / numSemestersLeft, 16)
        for _ in range(numSemestersLeft):

            #TODO: Does iterating forward or backwards produce better results?
            for i in range(numSemestersLeft-1,0,-1):
                #Create a list of potentially movable classes
                moveCandidates = []

                for courseNode in roadmap.getNodeSemester(i):
                    a = str(courseNode)
                    movable = True

                    #Check if prereqs are met by the previous semester
                    if courseNode.preReqs and roadmap.maxPrereqSemester(courseNode) >= i-1:
                        movable = False

                    #Check if any coreqs exist
                    #TODO: Handle moving sets of coreqs
                    if courseNode.coReqs and roadmap.maxCoreqSemester(courseNode) > i-1:
                        movable = False

                    #Check to make sure user has enough units
                    unitsAtPrevSem = roadmap.unitsUptoSemester(i-2) + units_completed
                    if unitsAtPrevSem < courseNode.SJSUCourse.unitPrereq:
                        movable = False

                    #If after all the checks, movable is still true, we can move the node to the previous semester
                    if movable:
                        moveCandidates.append(courseNode)

                d1 = len(moveCandidates) > 0
                d2 = roadmap.unitsInSemester(i-1) < unitsPerSemester

                while len(moveCandidates) > 0 and roadmap.unitsInSemester(i-1) < unitsPerSemester:
                    index = random.randint(0,len(moveCandidates)-1)
                    candidateNode = moveCandidates[index]
                    if roadmap.unitsInSemester(i-1) + candidateNode.getNumUnits() <= unitsPerSemester:
                        roadmap.placeCourse(candidateNode,i-1)
                    moveCandidates.remove(candidateNode)

        return roadmap

    def getRoadmap(self,genNew=False,save=True):
        genNew = True
        save = False

        roadmap = []
        if genNew or not self.user.student.roadmap:
            #Generate new roadmap
            gen0 = self._getGen0Candidate()
            #Do genetic aglroithm stuff with multiple gen 0s
            testVar = self._geneticAlgorithm()
            roadmap = gen0

            #Extract the roadmap of actual classes instead of nodes
            roadmap = roadmap.getCourseRoadmap()

            if save:
                self._saveToDB(roadmap)
        else:
            roadmap = self.user.student.roadmap
        return roadmap

    def _saveToDB(self,semList):
        student = self.user.student

        #Remove student's current roadmap if it exists
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







    def _geneticAlgorithm(self):
        pass
        # Run genetic algorithm (requires fitness function)
        # Optimizes array of arrays to be better
        # (Tentative) ex. min 20 generations & fitness above 85%

        startingPopulation =[self._getGen0Candidate() for _ in range(10)]

        v1 = self._isViable(startingPopulation[0])
        v2 = self._isViable(startingPopulation[1])

        res1 = self._createChild((startingPopulation[0],startingPopulation[1])).getCourseRoadmap()
        res2 = self._createChild((startingPopulation[1], startingPopulation[2])).getCourseRoadmap()
        res3 = self._createChild((startingPopulation[2], startingPopulation[3])).getCourseRoadmap()
        print('hi')

    def _isViable(self,roadmap):
        #Get the list of all courses from the graph
        courseDict = dict(self.graph.nodes)

        listLayout = roadmap.getNodeRoadmap()
        for i in range(len(listLayout)):
            for j in range(len(listLayout[i])):
                node = listLayout[i][j]

                #Remove node from courses list to indicate that we've seen it
                if node in courseDict:
                    courseDict.pop(node)

                #Check that prereqs will be completed
                if node.preReqs:
                    a = str(node)
                    if roadmap.maxPrereqSemester(node) is None:
                        #Prereqs are not completed/present at all
                        return False
                    elif roadmap.maxPrereqSemester(node) >= i:
                        #Prereqs are not all finished before semester starts
                        return False

                #Check that coreqs will be completed
                if node.coReqs:
                    if roadmap.maxCoreqSemester(node) is None:
                        #Coreqs are not scheduled at all
                        return False
                    elif roadmap.maxCoreqSemester(node) > i:
                        #Coreqs are scheduled after course is taken
                        return False

        if len(courseDict) > 0:
            #Not all the planned courses are present
            return False
        return True

        #Too many units in certain semester: max 17 for first several semester, 19 later? Petition for up to 21?
        #Doesn't graduate on time?

    def _fitnessFunction(self,roadmap):
        pass
        #TODO Define user preferences and friend list

        #Factors to grade on...
            #User preferences
            #Courses with friends
            #Number of courses/units in a semester

            #Maybe?
            #Balance of core/GEs in a semester (light weight)

    def _generateNextGen(self):
        pass

    def _mutate(self,roadmap):
        pass

    def _createChild(self,parents):
        while True:
            child = self.CourseTracker(parents[0].getNumSemesters())
            for i in range(child.getNumSemesters()):

                numCourses = random.choice((parents[0].numCoursesInSemester(i),parents[1].numCoursesInSemester(i)))
                #Choose which classes to inherit from father or mother
                inheritance = [random.choice((0,1)) for _ in range(numCourses)]

                parentCourses = (parents[0].getNodeSemester(i),parents[1].getNodeSemester(i))

                #Inherit courses
                for j in range(len(inheritance)):
                    inheritID = inheritance[j]
                    if j >= len(parentCourses[inheritID]):
                        #Inherit from other parent
                        inheritID = 1-inheritID
                    child.placeCourse(parentCourses[inheritID][j],i)

            testBool = self._isViable(child)
            if testBool:
                break
        return child