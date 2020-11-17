import random

class GeneticSimulation:
    class populationPool:
        #fitnessFunction should take in an organism and return a number (score)
        def __init__(self,fitnessFunction):
            self._fitnessFunction = fitnessFunction
            self._generation = 0
            self._population = [] #Currently format: [Organism, fitness, generation, is_adult]

        def addOranism(self,organism):
            self._population.append([organism,self._fitnessFunction(organism),self._generation,False])

        def getPopulationSize(self):
            return len(self._population)

        def setPopulationSize(self,newSize):
            self._sortPopulation()
            if newSize >= len(self._population):
                return
            elif newSize == 0:
                self._population = []
            else:
                newSize = -1 * newSize
                self._population = self._population[newSize::]

        #Calls the passed in function with the indexed organism as the parameter
        def mutateOrganisms(self,mutationProbability,mutationFunction,safteyMargin):
            for i in range(len(self._population) - safteyMargin):
                if random.randint(0,100) <= mutationProbability:
                    mutationFunction(self._population[i][0])
                    self._population[i][1] = self._fitnessFunction(self._population[i][0])

        def _sortPopulation(self):
            self._population.sort(key=lambda tup: tup[1])

        def getRandomParents(self):
            org1 = random.choice([j for j in range(len(self._population)) if self._population[j][3]])
            org2 = random.choice([j for j in range(len(self._population)) if self._population[j][3] and j != org1])
            return self._population[org1][0],self._population[org2][0]

        def getMostFit(self):
            if self._population is not None and len(self._population) > 0:
                self._sortPopulation()
                return self._population[-1][0]
            else:
                return None

        def nextGen(self):
            for organism in self._population:
                organism[3] = True #Oganisms that were children become adults
            self._generation += 1

        def getGeneration(self):
            return self._generation

        def getFitness(self):
            fitness = 0
            for organism in self._population:
                fitness += organism[1]
            avg = fitness / self.getPopulationSize() if self.getPopulationSize() > 0 else 0
            self._sortPopulation()
            max = self._population[-1][1]
            min = self._population[0][1]
            return avg,max,min

    #gen0 function should take in no parameters and produce an organism (gen0)
    #fitnessFunction should take in an organism and return a number (score)
    #childFunction should take in a tuple of organisms and return an organism
    #mutationFunction should take in an organism and modify the organism
    def __init__(self,gen0Function,fitnessFunction,childFuntion,mutationFunction):
        #Start with default parameters
        self.setParameters()

        #Functions
        self._gen0Function = gen0Function
        self._fitnessFunction = fitnessFunction
        self._childFunction = childFuntion
        self._mutationFunction = mutationFunction

        #Population
        self._population = None
        self._logbook = dict()

    ##
    # @brief Sets the parameters for a genetic simulation
    # @param populationSize The number of organisms to keep in the population
    # @param numGenerations How many generations the simulation should cycle for
    # @param mutationProbability How likely it is for organisms to mutate
    # @param survivalRate What percentage of organisms survive from one generation to the next
    # @param safetyMargin The top N organisms will not mutate (used to ensure that the max fitness doesn't decrease)
    # @param logging Whether to keep a log of the fitnesses across generations
    def setParameters(self,
                      populationSize=20,
                      numGenerations=100,
                      mutationProbability=0.05,
                      survivalRate=0.55,
                      safteyMargin=1,
                      logging=False):
        self._POPULATION_SIZE = populationSize
        self._NUM_GENERATIONS = numGenerations
        self._MUTATION_PROBABILITY = int(mutationProbability * 100)
        self._SURVIVAL_RATE = survivalRate
        self._SAFTEY_MARGIN = safteyMargin
        self._LOGGING = logging

    def runSimulation(self):
        self._population = self.populationPool(self._fitnessFunction)

        #Start by creating initial population
        for _ in range(self._POPULATION_SIZE):
            self._population.addOranism(self._gen0Function())

        for generation in range(self._NUM_GENERATIONS):
            if self._LOGGING:
                self._logbook[self._population.getGeneration()] = tuple(self._population.getFitness())

            #The least fit individuals are removed
            self._population.setPopulationSize(int(self._POPULATION_SIZE * self._SURVIVAL_RATE))

            #Some oranisms may mutate
            self._population.mutateOrganisms(self._MUTATION_PROBABILITY,self._mutationFunction,self._SAFTEY_MARGIN)

            #Create next generation
            self._population.nextGen()
            currentPopulation = self._population.getPopulationSize()
            for _ in range(self._POPULATION_SIZE - currentPopulation):
                parents = self._population.getRandomParents()
                self._population.addOranism(self._childFunction(tuple(parents)))

        #Return the most fit organism
        return self._population.getMostFit()

    ##
    # @brief Gets the log if logging was set to true for the simulation
    # @return a dictionary with the generation number as a key, and a tuple of fitnesses as the value
    # Value is a tuple of (averageFitness,maxFitness,minFitness) for said generation
    ##
    def getLog(self):
        return self._logbook

    def getResult(self):
        if self._population is not None:
            return self._population.getMostFit()
        else:
            return None