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
def generateRoadmap(user):
    pass
    # This is the algorithm flow, not purely "Call this function to do thing"

    # Have user enter desired GEs and Tech electives
        # Have some kind dynamic web portal
        # Check list of GE requirements
        # Find which ones are not fulfilled
            # Ask user to enter preference for those ones

    # Before generating roadmap, make sure all GE reqs and tech electives are met between preferred courses and transcript


    missingGE = getMissingGEAreas(user)
    missingTech = getMissingTech(user)

    #All classes are accounted for
    start = time.time()
    courseGraph = Graph(user)
    generator = RoadMapGenerator(user,courseGraph)

    # TODO: Reset the arguments to the proper default (genNew = False, save=True)
    roadmap = generator.getRoadmap(genNew=True,save=False)

    # TODO: Remove timer
    end = time.time()
    print("Everything took {0:.2f}s".format(end-start))
    return roadmap


class RoadMapGenerator:
    # CourseTracker abstracts memory management of courses
    class CourseTracker:
        def __init__(self,numSemesters):
            #Speed is more important that memory usage, use two dictionaries for fast lookup
            self.courseDict = dict() #Dictioanry of <courseNode,semester>
            self.roadmap = [dict() for _ in range(numSemesters)] #Used as orderd set of nodes, value is set to None

        def swapSemesters(self,sem1,sem2):
            for course in self.roadmap[sem1]:
                self.courseDict[course] = sem2
            for course in self.roadmap[sem2]:
                self.courseDict[course] = sem1
            self.roadmap[sem1], self.roadmap[sem2] = self.roadmap[sem2], self.roadmap[sem1]

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
                self.roadmap[semToRemove].pop(node)
            self.courseDict[node] = semester
            self.roadmap[semester][node] = None
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

        def coursesInSemester(self,semester):
            return len(self.roadmap[semester])

        def unitsUptoSemester(self,semester):
            numUnits = 0
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
        # TODO: Implement friend class matching
        self._friendClasses = None
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

                while len(moveCandidates) > 0 and roadmap.unitsInSemester(i-1) < unitsPerSemester:
                    index = random.randrange(0,len(moveCandidates))
                    candidateNode = moveCandidates[index]
                    if roadmap.unitsInSemester(i-1) + candidateNode.getNumUnits() <= unitsPerSemester:
                        roadmap.placeCourse(candidateNode,i-1)
                    moveCandidates.remove(candidateNode)

        return roadmap

    ##
    # @brief Gets the user's roadmap
    # @param genNew If true, returns a new roadmap regardless of whether the user has an existing one or not
    # If the user does not have a roadmap, one will be generated regardless of value of genNew
    # @param save Whether or not to save the newly generated roadmap to the database
    # @param rescheduleCurrent If false (default), will not modify the currently in-progress semester
    # If true, will disregard the current semester and generate a new roadmap
    ##
    def getRoadmap(self,genNew=False,save=True,rescheduleCurrent=False):
        roadmap = []
        if genNew or not self.user.student.roadmap:
            #Generate new roadmap
            gen0 = self._getGen0Candidate()
            roadmap = gen0

            #Do genetic aglroithm
            newRoadmap = self._geneticAlgorithm().getCourseRoadmap()

            #TODO: Remove any empty semesters
            # And switch to returning genetic result

            #Extract the roadmap of actual classes instead of nodes
            roadmap = roadmap.getCourseRoadmap()

            if not rescheduleCurrent and self.user.student.roadmap:
                # TODO: Add in getting current sem schedule and prepending to roadmap
                pass

            if save:
                self._saveToDB(roadmap)
        else:
            roadmap = self.user.student.roadmap
        return roadmap

    def _saveToDB(self,semList):
        # TODO: Factor in date offsets given start/current date
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
        start = time.time()
        sim = GeneticSimulation(gen0Function=self._getGen0Candidate,
                              fitnessFunction=self._fitnessFunction,
                              childFuntion=self._createChild,
                              mutationFunction=self._mutate)

        sim.setParameters(populationSize=20,
                        numGenerations=120,
                        mutationProbability=0.05,
                        survivalRate=0.55,
                        safteyMargin=1)

        sim.runSimulation()
        end = time.time()
        print("Genetic Algorithm took {0:.2f}s".format(end-start))
        return sim.getResult()

    #=====Define functions used by genetic algorithm=====#
    def _isViable(self,organism):
        #We aren't adding/removeing courses, only reordering
        #If number of courses is different, classes are likely missing
        if len(organism.courseDict) != len(self.graph.nodes):
            return 0

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

        #Check the average number of units in a semester
        unitResult=0
        courseResult = 0

        #Delcare the weights (good/bad) for number of units in a single semester
        UNIT_MAP = dict()
        for i in range(0,1): UNIT_MAP[i] = 0.5
        for i in range(1, 7): UNIT_MAP[i] = 0.5
        for i in range(7, 12): UNIT_MAP[i] = 0.5
        for i in range(12, 17): UNIT_MAP[i] = 0.5
        for i in range(17, 20): UNIT_MAP[i] = 0.5

        #Delcare weights of (good/bad) for number of courses in a single semester
        COURSE_MAP = {
            0:0.5,
            1:0.3,
            2:0.4,
            3:0.8,
            4:1,
            5:0.8,
            6:0.3,
            7:0.1
        }

        for i in range(organism.getNumSemesters()):
            numUnits = organism.unitsInSemester(i)
            numCourses = organism.coursesInSemester(i)

            if numUnits in UNIT_MAP:
                unitResult += UNIT_MAP[numUnits]

            if numCourses in COURSE_MAP:
                courseResult += COURSE_MAP[numCourses]
        unitResult /= organism.getNumSemesters()
        courseResult /= organism.getNumSemesters()

        #Check if the roadmap is vaiable or not, if not heavily penalize it
        viability = self._isViable(organism)

        #Score +-= [weight] * [result: range of 0-1], + are things we want to maximize, - are things to minimize
        # Calculate score based on results and relative weights
        score -= 10 * (1 - viability)
        score += 5 * unitResult
        score += 2 * courseResult
        return score

    #TODO: Improve _mutate function to change oragnisms in a more useful way
    def _mutate(self,organism):
        #Define parameters here
        SEMESTER_SWAP_PROBABILITY = 5
        NUM_CLASSES_TO_MOVE = random.randint(1,5)

        seed = random.randint(0,100)
        #Chance to swap random courses between semesters
        if seed > SEMESTER_SWAP_PROBABILITY:
            for _ in range(NUM_CLASSES_TO_MOVE):
                course = random.choice(list(organism.courseDict.keys()))
                randSemester = random.randrange(0,organism.getNumSemesters())
                organism.placeCourse(course,randSemester)

        #Smaller chance to swap entire semester
        elif seed <= SEMESTER_SWAP_PROBABILITY:
            #Choose 2 semesters to swap
            sem1 = random.randrange(0,organism.getNumSemesters())
            sem2 = random.choice([i for i in range(0,organism.getNumSemesters()) if i != sem1])
            organism.swapSemesters(sem1,sem2)

    #TODO: Improve _createChild to create better organism...
    # See brainstorming discord channel
    def _createChild(self,parents):
        MAX_TRIES = 3 #If child is not viable, will retry up to MAX_TRIES times

        tries = 0
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