from .models import *





def generateRoadmap(student):
    pass
    # This is the algorithm flow, not purely "Call this function to do thing"

    # Have user enter desired GEs and Tech electives
        # Have some kind dynamic web portal
        # Check list of GE requirements
        # Find which ones are not fulfilled
            # Ask user to enter preference for those ones

    # Before generating roadmap, make sure all GE reqs and tech electives are met between preferred courses and transcript


    courseGraph = graph(student)
    #result = courseGraph.depthFirstSearch()

    geneticAlgorithm()

    # Save to database
    # Display to user




def findMissingGE(student):
    pass

    # Look though GE requirements
    # For each course in user transcript, planned-to-take and catalogue
        # If course fulfilles GE, remove requirement from list
    #return list
        # If list is empty, procede
        # If list is not empty, warn user and do not continue

        # Also can be used on dynamic page as list of preference to fill


def getMissingTech(student):
    pass

    # Look at number of tech units
    # Get list of tech elevtives student is taking
        # Something vaugely like: student.preferredCourses.filter(matches course in tech elective table)
    # Add up number of units from items in list
    # Return catalogue number of required tech elective units - (minus) the number from above
    # Return number
        # If number is zero or negative, continue all classes fulfilled
        # If posative, do not continue, warn User

        # Can also be used on dynamic page to get number of units needed to select


class graph
    # Map of nodes

    class node:
    # Prereq list (other nodes)
    # Coreq list (other nodes)
    # Posreq list (other nodes)

    # Course

    def __init__(self,student):
        self.student = student
        self._createGraph()

    def _createGraph(self):
        pass
        # Grab all classes in the catalogue (copy of list)?
        # Add on to list with GEs and Tech elevtives

        # Remove all classes that user had taken and passed from list
            # Check both the trancript of SJSU courses
            # And courses from transfer that articulate

        # Go through list in order
        # Add course



    def _addCourse(self,course):
        pass
        # Make node for course
            # Possibly put in set of added courses, with the 'dict' being the string of(Dept+Course ID) + 'ptr to node'

        # For preqs and coreqs
            # Check if they are in map
            # If not
                # Check if they are in user transcript
                    # If so
                        # continue
                    # If not
                        # Add them to graph (recusrively?)
                        # Connect them as prereq
                            # While doing this, connect self as Postreq

    def _userPassed(self,course):
        pass
        #Check if course is in user transcript and they have a passing grade

    def depthFirstSearch(self):
        # Produces array of arrays
        # (roadmap = arary of semester schedules, which are arrays)
        pass








def geneticAlgorithm():
    pass
    # Run genetic algorithm (requires fitness function)
    # Optimizes array of arrays to be better
    # (Tentative) ex. min 20 generations & fitness above 85%
