from .util import *

class CourseNode:
    def __init__(self):
        self.preReqs = []
        self.coReqs = []
        self.postReqs = []
        self.seqReqs = []

        self.SJSUCourse = None
        self.TransferCourse = None

        self.max_sem_level = None

    def getNumUnits(self):
        if self.TransferCourse is None:
            return self.SJSUCourse.numUnits
        else:
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

class Graph:
    def __init__(self,user,rescheduleCurrent=False):
        self.user = user

        self.nodes = dict() #Example Key = 'CMPE 135', value = Node()
        self.standby = dict() #Example Key = 'CMPE 135', value = Node()
        self.rootNodes = set()
        self._createGraph(rescheduleCurrent)

    def _createGraph(self,rescheduleCurrent=False):
        #Count in-progress classes as completed to avoid rescheduling them again
        passedClasses = getPassedClasses(self.user,countInProgress=not rescheduleCurrent)
        #Count completed transfer courses as passed
        transferedClasses = getEquivalentTransferClasses(self.user)
        self.passedClasses = (passedClasses | transferedClasses.exclude(id__in=passedClasses.values('id')))

        coreToTake = self.user.student.catalogue.courses.exclude(id__in=passedClasses.values('id'))
        if self.user.student.separateSV:
            coreToTake = coreToTake.exclude(isCapstone=True)
        else:
            coreToTake = coreToTake.exclude(isAlternateCapstone=True, isCapstone=False)

        optionalToTake = self.user.student.prefCourseList.exclude(id__in=passedClasses.values('id'))

        #Combine list to get all the courses to take, discarding duplicates
        toSchedule = (coreToTake | (optionalToTake.exclude(id__in=coreToTake.values('id'))))

        for course in toSchedule:
            self._addCourse(course)
        if len(self.standby) > 0:
            raise UserWarning("Required Pre/Corequisite classes not taken or planned")

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
        courseNode = CourseNode()
        #Is course Transfer
        if type(course) == TransferCourse:
            return None
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

        #Add 100W as aproximation for having completed WST
        if course.requiresWST:
            approxNode = self._addCourse(Course.objects.filter(department='ENGR').get(courseID='100W'))
            if approxNode is not None:
                courseNode.coReqs.append(approxNode)

        # Check optional co/prereqs to see if needs to be on standby
        numOptCoReq = course.NCoreqs
        if numOptCoReq > 0:
            foundCoReqs = 0
            for coReq in course.NOfCoreqs.all():
                tmp = CourseNode()
                tmp.SJSUCourse = coReq
                if foundCoReqs < numOptCoReq and tmp in self.nodes and self.nodes[tmp] not in courseNode.coReqs:
                    courseNode.coReqs.append(self.nodes[tmp])
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

        #Add any oredered-requirement nodes
        if len(course.sequential.all()) > 0:
            for seqReq in course.sequential.all():
                seqReqNode = self._addCourse(seqReq)
                if seqReq is not None:
                    courseNode.seqReqs.append(seqReqNode)

        #Now that node is added, update standby nodes in case is optional requirement
        self._updateStandby(courseNode)

        return courseNode

    def _userPassed(self,course):
        return self.passedClasses.filter(id=course.id).exists()