from .util import *

class CourseNode:
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

class Graph:
    def __init__(self,user):
        self.user = user

        self.nodes = dict() #Key = 'CMPE 135', value = Node()
        self.standby = dict() #Key = 'CMPE 135', value = Node()
        self.rootNodes = set()
        self._createGraph()

    def _createGraph(self):
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