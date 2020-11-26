from .models import *
from .util import *
from .graph import CourseNode, Graph
from .genetic import GeneticSimulation
import random
import time


##
# @brief Generates a roadmap for the user based on preferences
# @param user The logged in user
##
def generateRoadmap(user,genNew=False,rescheduleCurrent=False):

    missingGE = getMissingGEAreas(user)
    missingTech = getMissingTech(user)

    #All classes are accounted for
    start = time.time()

    # TODO: Reset argument when no longer testing
    courseGraph = Graph(user,rescheduleCurrent=True)
    generator = RoadMapGenerator(user,courseGraph)
    # TODO: Reset the arguments to the proper default (genNew = False, save=True)
    generator.setParameters(genNew=True,save=False,rescheduleCurrent=True)

    roadmap = generator.getRoadmap()

    # TODO: Remove timer and printout
    end = time.time()
    print("Everything took {0:.2f}s".format(end-start))

    print("NumSems: {0}".format(len(roadmap)))
    for i in range(len(roadmap)):
        numUnits = 0
        for course in roadmap[i][1]:
            numUnits += course.numUnits
        year = "{0} {1}: ".format(roadmap[i][0][1],roadmap[i][0][0])
        courseList = "{}".format(roadmap[i][1])
        print("{0:>13} {1:<130} ({2} courses, {3} units)".format(year,courseList,len(roadmap[i][1]),numUnits))
    return roadmap


class RoadMapGenerator:
    # CourseTracker abstracts memory management of courses
    class CourseTracker:
        def __init__(self,numSemesters,unitsCompleted=0):
            self.unitsCompleted = unitsCompleted

            #Speed is more important that memory usage, use two dictionaries for fast lookup
            self.courseDict = dict() #Dictioanry of <courseNode,semester>
            self.roadmap = [dict() for _ in range(numSemesters)] #Used as orderd set of nodes, value is set to None
            self.semUnits = [0 for _ in range(numSemesters)]
            self.levelOfFreedom = [dict() for i in range(4)]

        def swapSemesters(self,sem1,sem2):
            for course in self.roadmap[sem1]:
                self.courseDict[course] = sem2
            for course in self.roadmap[sem2]:
                self.courseDict[course] = sem1
            self.roadmap[sem1], self.roadmap[sem2] = self.roadmap[sem2], self.roadmap[sem1]

        def getNumSemesters(self):
            return len(self.roadmap)

        def getNumCourses(self):
            return len(self.courseDict)

        def numCoursesInSemester(self,semester):
            return len(self.roadmap[semester])

        def courseScheduled(self,node):
            return node in self.courseDict

        def placeCourse(self,node,semester):
            if semester < 0 or semester > len(self.roadmap)-1:
                return False
            nodeOverwritten = False
            #Handles both moving and inserting courses
            if node in self.courseDict:
                nodeOverwritten = True
                semToRemove = self.courseDict[node]
                self.roadmap[semToRemove].pop(node)
                self.semUnits[semToRemove] -= node.getNumUnits()
            self.courseDict[node] = semester
            self.roadmap[semester][node] = None
            self.semUnits[semester] += node.getNumUnits()

            #Calculate level of freedom
            #Lower number means more freedom
            LOF = 3
            if node.preReqs == []: LOF -= 1
            if node.coReqs == []: LOF -= 1
            if node.postReqs == []: LOF -= 1
            self.levelOfFreedom[LOF][node] = None

            return nodeOverwritten

        def getNodeRoadmap(self):
            roadmap = [None for _ in range(len(self.roadmap))]
            for i in range(len(self.roadmap)):
                #self.roadmap[i].sort(key=str)
                roadmap[i] = [node for node in self.roadmap[i]]
            return roadmap

        def getNodeSemester(self,semester):
            return [node for node in self.roadmap[semester]]

        def getSemesterTaken(self,node):
            if node in self.courseDict:
                return self.courseDict[node]
            else:
                return None

        def maxCoreqSemester(self,node):
            max_sem = -1
            for coReqNode in node.coReqs:
                if coReqNode in self.courseDict:
                    max_sem = max(max_sem,self.courseDict[coReqNode])
                else:
                    return None
            return max_sem

        def maxPrereqSemester(self,node):
            max_sem = -1
            for preReqNode in node.preReqs:
                if preReqNode in self.courseDict:
                    max_sem = max(max_sem,self.courseDict[preReqNode])
                else:
                    return None
            #Check for unit prereq
            if node.SJSUCourse.unitPrereq > self.unitsCompleted:
                for i in range(len(self.roadmap)):
                    max_sem = max(max_sem, i)
                    if self.unitsUptoSemester(i) >= node.SJSUCourse.unitPrereq:
                        break
            return max_sem

        def unitsInSemester(self,semester):
            #numUnits = 0
            #for courseNode in self.roadmap[semester]:
            #    numUnits += courseNode.getNumUnits()
            if semester < 0 or semester >= len(self.semUnits):
                return 0
            return self.semUnits[semester]

        def coursesInSemester(self,semester):
            return len(self.roadmap[semester])

        def unitsUptoSemester(self,semester):
            numUnits = self.unitsCompleted
            for i in range(semester+1):
                numUnits += self.unitsInSemester(i)
            return numUnits

        def getCourseRoadmap(self):
            courses = [[] for _ in range(len(self.roadmap))]
            for i in range(len(self.roadmap)):
                courses[i] = [course.getCourse() for course in self.roadmap[i]]
            return courses


    #Roadmap Generator
    #Need to generate a prereq graph and pass to roadmap generator
    def __init__(self,user,graph):
        self.user = user
        self.graph = graph
        self.setParameters()

    ##
    # @brief Sets the parameters for the roadmap generator to work with
    # @param genNew If true, will always generate a new roadmap
    # If false, will only generate new roadmap if user doesn't have one, otherwise pulls from database
    # @param save Whether or not to save the newly generated roadmap to the database
    # @param rescheduleCurrent If the roadmap generator should keep the in-progress semester the same or not
    ##
    def setParameters(self,genNew=False,save=True,rescheduleCurrent=False):
        self._genNew = genNew
        self._save = save
        self._rescheduleCurrent = rescheduleCurrent

        # Calculate how many semesters the user has left
        currentSemester = semesterToIndex(self.user.student.currentYear, self.user.student.currentTerm,
                                          self.user.student.startYear, self.user.student.startTerm)
        self._num_semester_left = self.user.student.numSemesters - (currentSemester if currentSemester >= 0 else 0)
        if currentSemester >= 0 and self.user.student.roadmap and not self._rescheduleCurrent:
            self._semInProg = True
            self._num_semester_left -= 1
        else:
            self._semInProg = False

        # Account for allowable number of units per semester
        self._maxSemUnits = dict()
        if self._num_semester_left > 2 and not self._semInProg:
            # First semester students may only take 16 units
            self._maxSemUnits[0] = 16
        else:
            self._maxSemUnits[0] = 17
        for i in range(1,self._num_semester_left - 2):
            # Normally students may register for up to 17 units
            self._maxSemUnits[i] = 17
        for i in range(self._num_semester_left-2,self._num_semester_left):
            # Graduating seniors may take up to 21 units
            self._maxSemUnits[i] = 21

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
        for key,node in self.graph.nodes.items():
            longest_chain = self._traverse(node)
            if not node.max_sem_level:
                node.max_sem_level = self._num_semester_left - len(longest_chain)

            for coReqNode in node.coReqs:
                if coReqNode.max_sem_level is None:
                    coReq_longest_chain = self._traverse(coReqNode)
                    coReqNode.max_sem_level = self._num_semester_left - len(coReq_longest_chain)
                if coReqNode.max_sem_level > node.max_sem_level:
                    coReqNode.max_sem_level = node.max_sem_level
            if node.max_sem_level < 0:
                raise UserWarning("Not enough time left to complete class")

        # Very rudimentary generation 0 schedule, based on prereq levels
        roadmap = self.CourseTracker(self._num_semester_left,getUnitsTaken(self.user,countInProgress=self._semInProg))
        for key, node in self.graph.nodes.items():
            roadmap.placeCourse(node,node.max_sem_level)

        #Spread out classes across semester
        roadmap = self._distrubuteClasses(roadmap)
        return roadmap

    def _distrubuteClasses(self,roadmap):
        numSemestersLeft = roadmap.getNumSemesters()
        for _ in range(min(numSemestersLeft,16)):
            for i in range(numSemestersLeft - 1, 0, -1):
                # Create a list of potentially movable classes
                moveCandidates = []

                for courseNode in roadmap.getNodeSemester(i):
                    a = str(courseNode)
                    movable = True

                    # Check if prereqs are met by the previous semester
                    if courseNode.preReqs and roadmap.maxPrereqSemester(courseNode) >= i - 1:
                        movable = False

                    # Check if any coreqs exist
                    # TODO: Handle moving sets of coreqs
                    if courseNode.coReqs and roadmap.maxCoreqSemester(courseNode) > i - 1:
                        movable = False

                    # If after all the checks, movable is still true, we can move the node to the previous semester
                    if movable:
                        moveCandidates.append(courseNode)

                while len(moveCandidates) > 0 and roadmap.unitsInSemester(i - 1) < self._maxSemUnits[i - 1]:
                    index = random.randrange(0, len(moveCandidates))
                    candidateNode = moveCandidates[index]
                    if roadmap.unitsInSemester(i - 1) + candidateNode.getNumUnits() <= self._maxSemUnits[i - 1]:
                        roadmap.placeCourse(candidateNode, i - 1)
                    moveCandidates.remove(candidateNode)

        #Do several passes trying to fill in empty gaps
        for _ in range(min(numSemestersLeft,16)):
            for i in range(numSemestersLeft):
                unitsToSpare = self._maxSemUnits[i] - roadmap.unitsInSemester(i)
                if unitsToSpare > 0:
                    for course in roadmap.courseDict:
                        if course.getNumUnits() > unitsToSpare or roadmap.getSemesterTaken(course) <= i:
                            continue
                        if roadmap.maxCoreqSemester(course) <= i and roadmap.maxPrereqSemester(course) < i:
                            roadmap.placeCourse(course,i)
                            unitsToSpare = self._maxSemUnits[i] - roadmap.unitsInSemester(i)
                        if unitsToSpare <= 0:
                            break

        return roadmap

    ##
    # @brief Gets the user's roadmap
    # @param genNew If true, returns a new roadmap regardless of whether the user has an existing one or not
    # If the user does not have a roadmap, one will be generated regardless of value of genNew
    # @param save Whether or not to save the newly generated roadmap to the database
    # @param rescheduleCurrent If false (default), will not modify the currently in-progress semester
    # If true, will disregard the current semester and generate a new roadmap
    ##
    def getRoadmap(self):
        roadmap = []
        if self._genNew or not self.user.student.roadmap:
            #Do genetic aglroithm
            roadmap = self._geneticAlgorithm().getCourseRoadmap()
            roadmap = [i for i in roadmap if i != []]  # Remove any empty semesters

            #If we are currently in the middle of a semester, we don't want to change classes
            if not self._rescheduleCurrent and self.user.student.roadmap:
                index = semesterToIndex(self.user.student.currentYear,self.user.student.currentTerm,
                                        self.user.student.startYear,self.user.student.startTerm)
                currentSem = getCoursesInSemester(self.user,index)
                if currentSem != []:
                    roadmap.insert(0,currentSem)

            #Convert 2D list into dated semesters
            roadmap = self._listToDatedSemesters(roadmap)

            if self._save:
                self._saveToDB(roadmap)
        else:
            roadmap = self._datedSemestersFromDB(self.user)
        return roadmap

    def _listToDatedSemesters(self,semList):
        # Determine whether to use current or start date
        index = semesterToIndex(self.user.student.currentYear, self.user.student.currentTerm,
                                self.user.student.startYear, self.user.student.startTerm)
        startFromYear = self.user.student.currentYear
        startFromTerm = self.user.student.currentTerm
        if index < 0:
            startFromYear = self.user.student.startYear
            startFromTerm = self.user.student.startTerm

        #Return format [ ((year,semester),[courses]) ]
        retList = []
        for i in range(len(semList)):
            sYear, sTerm = indexToSemester(i, startFromYear, startFromTerm)
            retList.append(((sYear,sTerm),sorted(semList[i],key=str)))
        return retList

    def _datedSemestersFromDB(self,user):
        roadmap = user.student.roadmap

        # Return format [ ((year,semester),[courses]) ]
        retList = []
        for semester in roadmap.semesterSchedules.all():
            retList.append(((semester.year,semester.term),sorted([i for i in semester.courses.all()],key=str)))
        retList.sort(key=lambda tup: tup[0][0]*2+(0 if tup[0][1] == 'Spring' else 1))
        return retList

    def _saveToDB(self,roadmap):
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

        newRoadmap = Roadmap()
        newRoadmap.save()
        for semester in roadmap:
            semesterObject = SemesterSchedule(year=semester[0][0],term=semester[0][1])
            semesterObject.save()
            for course in semester[1]:
                semesterObject.courses.add(course)
            newRoadmap.semesterSchedules.add(semesterObject)

        student.roadmap = newRoadmap
        student.save()


    def _geneticAlgorithm(self):
        self._initGeneticVariables()
        start = time.time()
        sim = GeneticSimulation(gen0Function=self._getGen0Candidate,
                              fitnessFunction=self._fitnessFunction,
                              childFuntion=self._createChild,
                              mutationFunction=self._mutate)

        sim.setParameters(populationSize=100,
                        numGenerations=150,
                        mutationProbability=0.10,
                        survivalRate=0.55,
                        safteyMargin=1,
                        logging=True)

        sim.runSimulation()



        end = time.time()
        print("Genetic Algorithm took {0:.2f}s".format(end-start))
        return sim.getResult()

    def _initGeneticVariables(self):
        # Create list of all friends classes so that they can be compared
        self._friendSchedules = []
        self._totalFriendClasses = 0
        for friend in self.user.student.friends.all():
            friendRoadmap = self._datedSemestersFromDB(friend.user)
            if friendRoadmap != []:
                friendTracker = self.CourseTracker(self._num_semester_left)
                for semester in friendRoadmap:
                    for course in semester[1]:
                        # Base index off of your start date instead of friend's since we need to compare it to your schedule
                        index = semesterToIndex(semester[0][0], semester[0][1], self.user.student.startYear,
                                                self.user.student.startTerm)
                        if self._semInProg:
                            index -= 1
                        # Course tracker works with nodes
                        node = CourseNode()
                        node.SJSUCourse = course  # Comparison just requires that course matches
                        friendTracker.placeCourse(node, index)
                self._friendSchedules.append(friendTracker)
                self._totalFriendClasses += friendTracker.getNumCourses()

        # Delcare the weights (good/bad) for number of units in a single semester
        self._UNIT_MAP = dict()
        for i in range(0, 1): self._UNIT_MAP[i] = 0.2
        for i in range(1, 7): self._UNIT_MAP[i] = 0.7
        for i in range(7, 12): self._UNIT_MAP[i] = 0.8
        for i in range(12, 17): self._UNIT_MAP[i] = 1
        for i in range(17, 19): self._UNIT_MAP[i] = 0.4
        for i in range(19, 22): self._UNIT_MAP[i] = -0.1

        # Delcare weights of (good/bad) for number of courses in a single semester
        self._COURSE_MAP = {
            0: 0.5,
            1: 0.1,
            2: 0.4,
            3: 0.7,
            4: 1,
            5: 0.8,
            6: 0.3,
            7: -0.1
        }


    #=====Define functions used by genetic algorithm=====#
    def _isViable(self,organism):
        #We aren't adding/removeing courses, only reordering
        #If number of courses is different, classes are likely missing
        if len(organism.courseDict) != len(self.graph.nodes):
            return 0

        for semester in range(organism.getNumSemesters()):
            if organism.unitsInSemester(semester) > self._maxSemUnits[semester]:
                return 0.3

        for node,semester in organism.courseDict.items():
                #Check that prereqs will be completed
                if node.preReqs:
                    if organism.maxPrereqSemester(node) >= semester:
                        #Prereqs are not all finished before semester starts
                        return 0.1

                #Check that coreqs will be completed
                if node.coReqs:
                    if organism.maxCoreqSemester(node) > semester:
                        #Coreqs are scheduled after course is taken
                        return 0.2
        return 1

        #Too many units in certain semester: max 17 for first several semester, 19 later? Petition for up to 21?
        #Doesn't graduate on time?

    def _fitnessFunction(self,organism):
        score = 0

        #TODO Define user preferences and friend list
        #Factors to grade on...
            #User preferences
            #Courses with friends
            #Number of courses/units in a semester <- Should allow user to control?
        # Maybe?
            # Balance of core/GEs in a semester (light weight)
            # Graduates in time?

        #Check how many classes match with friends
        matchingClasses = 0
        if len(self._friendSchedules) > 0:
            for course in organism.courseDict:
                for friendSchedule in self._friendSchedules:
                    if course in friendSchedule.courseDict:
                        if organism.getSemesterTaken(course) == friendSchedule.getSemesterTaken(course):
                            matchingClasses += 1
        friendResult = (matchingClasses/self._totalFriendClasses if self._totalFriendClasses != 0 else 0)

        #Check the average number of units in a semester
        unitResult=0
        courseResult = 0
        for i in range(organism.getNumSemesters()):
            numUnits = organism.unitsInSemester(i)
            numCourses = organism.coursesInSemester(i)

            if numUnits in self._UNIT_MAP:
                unitResult += self._UNIT_MAP[numUnits]

            if numCourses in self._COURSE_MAP:
                courseResult += self._COURSE_MAP[numCourses]
        unitResult /= organism.getNumSemesters()
        courseResult /= organism.getNumSemesters()

        #Check if the roadmap is vaiable or not, if not heavily penalize it
        viability = self._isViable(organism)

        #Score +-= [weight] * [result: range of 0-1], + are things we want to maximize, - are things to minimize
        # Calculate score based on results and relative weights
        score -= 10 * (1 - viability)
        score += 3 * friendResult
        score += 6 * unitResult
        score += 4 * courseResult
        return score

    #TODO: Improve _mutate function to change oragnisms in a more useful way
    def _mutate(self,organism):
        #Define parameters here
        SEMESTER_SWAP_CHANCE = 10
        NUM_CLASSES_TO_MOVE = random.randint(1,3)

        seed = random.randint(0,100)
        # Chance to swap random free courses between semesters
        if SEMESTER_SWAP_CHANCE > 60:
            for _ in range(NUM_CLASSES_TO_MOVE):
                LOF = random.choices(range(0,4),weights=[35,35,20,10],k=1)[0]
                if len(organism.levelOfFreedom[LOF]) == 0:
                    continue
                course = random.choice(list(organism.levelOfFreedom[LOF].keys()))
                randSemester = random.randrange(0, organism.getNumSemesters())
                organism.placeCourse(course, randSemester)

        #Smaller chance to swap entire semester
        else:
            #Choose 2 semesters to swap
            sem1 = random.randrange(0,organism.getNumSemesters())
            sem2 = random.choice([i for i in range(0,organism.getNumSemesters()) if i != sem1])
            organism.swapSemesters(sem1,sem2)

    #TODO: Improve _createChild to create better organism...
    # See brainstorming discord channel
    def _createChild(self,parents):
        MAX_TRIES = 3 #If child is not viable, will retry up to MAX_TRIES times

        tries = 0
        child = None
        while tries < MAX_TRIES:
            child = self.CourseTracker(parents[0].getNumSemesters())

            #Among the classes, randomly inherit from either parent
            #Any classes that both parents have in the same semester will always match
            for course in parents[0].courseDict.keys():
                parentToInherit = random.randint(0,1)
                child.placeCourse(course,parents[parentToInherit].courseDict[course])

            tries += 1
            childViability = self._isViable(child)
            if childViability == 1:
                break
        return child