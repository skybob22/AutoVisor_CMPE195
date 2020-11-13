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










#population =[[self._getGen0Candidate(),0,0] for _ in range(POPULATION_SIZE)]
        for i in range(len(population)):
            population[i][1] = self._fitnessFunction(population[i][0])

        for gen in range(NUM_GENERATIONS):
            #TDOD: Try to parallelize anything (fitness function?) if possible?

            #Sort the list based on the fitness
            population.sort(key=lambda tup: tup[1])

            #Kill off the least fit individuals
            newSize = int(POPULATION_SIZE * SURVIVAL_RATE)
            population = population[newSize::]

            #Some organisms may mutate
            for i in range(len(population)-int(SAFETY)):
                if random.randint(0,100) <= MUTATION_PROBABILITY:
                    self._mutate(population[i][0])
                    population[i][1] = self._fitnessFunction(population[i][0])

            #The remaining individuals reproduce
            #TODO: Out of the entire genetic algorithm, this takes the longest.
            # Focus any optimizations here
            children = []
            for i in range(POPULATION_SIZE - len(population)):
                organism1 = random.randrange(0,len(population))
                organism2 = random.choice([j for j in range(len(population)) if j != organism1])
                child = self._createChild((population[organism1][0],population[organism2][0]))
                children.append([child,self._fitnessFunction(child),gen])
            population.extend(children)

        #Get the most fit individual from the last generation
        population.sort(key=lambda tup: tup[1])
    bestResult = population[-1]


def _geneticAlgorithm_1(self):
    # Run genetic algorithm (requires fitness function)
    # Optimizes array of arrays to be better
    # (Tentative) ex. min 20 generations & fitness above 85%

    # Define parameters here
    NUM_GENERATIONS = 120
    POPULATION_SIZE = 20
    MUTATION_PROBABILITY = 5
    SURVIVAL_RATE = 0.55  # This many organisms will be left at the end of each round
    SAFETY = True  # Prevents the highest N fitness oganism(s) from mutating. Should ensure at least 1 valid result

    start = time.time()
    # TODO: Tune parameters and change mutation function, maybe change offspring
    # Tradeoff for population size vs # of generations
    # If all valid organisms mutate to be invalid, there is practically no chance of success

    population = self.populationPool(self._fitnessFunction)
    for _ in range(POPULATION_SIZE):
        population.addOrangism(self._getGen0Candidate())

    for _ in range(NUM_GENERATIONS):
        # Kill off the least fit individuals
        population.removeOrganisms(POPULATION_SIZE * (1 - SURVIVAL_RATE))

        # Some organisms may mutate
        for i in range(population.getPopulationSize() - int(SAFETY)):
            if random.randint(0, 100) <= MUTATION_PROBABILITY:
                self._mutate(population.getOrgansim(i))
                population.recalculate(i)  # If organism changed, fitness needs to be recalcilated

        # The remaining individuals reproduce
        # TODO: Out of the entire genetic algorithm, this takes the longest.
        # Focus optimizations here
        currentPopulation = population.getPopulationSize()
        for i in range(POPULATION_SIZE - currentPopulation):
            org1 = random.randrange(0, currentPopulation)
            org2 = random.choice([j for j in range(currentPopulation) if j != org1])
            population.addOrangism(self._createChild((population.getOrgansim(org1), population.getOrgansim(org2))))

    # TODO: Remove timer
    end = time.time()
    print("Genetic Algorithm took: {0:.2f}s".format(end - start))
    temp = population.getMostFit()
    return population.getMostFit()





class populationPool:

    def __init__(self,fitnessFunction):
        self.fitnessFunction = fitnessFunction
        self.population = []
        self.generation = 0

    def addOrangism(self,organism):
        self.population.append([organism,self.fitnessFunction(organism),self.generation])

    def getOrgansim(self,orgIndex):
        return self.population[orgIndex][0]

    def getPopulationSize(self):
        return len(self.population)

    def recalculate(self,orgIndex):
        self.population[orgIndex][1] = self.fitnessFunction(self.population[orgIndex][0])

    def removeOrganisms(self,number):
        self._sortPopulation()
        newSize = int(len(self.population) - number)
        self.population = self.population[newSize::]
        self.generation = self.generation+1 #After culling, new organisms are next generation

    def _sortPopulation(self):
        self.population.sort(key = lambda tup: tup[1])

    def getMostFit(self):
        self._sortPopulation()
        return self.population[-1][0]