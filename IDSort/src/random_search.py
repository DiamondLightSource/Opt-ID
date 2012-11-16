'''
Created on 26 Jul 2012

'''


'''
Created on 16 Nov 2011

@author: ssg37927
'''

'''
Created on 8 Oct 2011

@author: ssg37927
'''

import random
import copy
import h5py
import os


class RandomSearch(object):

    def __init__(self,
                 ppm,
                 filename,
                 debug=True):
        self.ppm = ppm
        self.debug = debug
        self.filename = filename
        self.currBest = self.ppm.evaluate_ppm()
        self.bestSource = 0

    def initialise(self):
        pass
    
    
    def run_epocs(self, number_of_epocs):
        for x in range(number_of_epocs):
            ppm = copy.deepcopy(self.ppm)
            ppm.randomize()
            #check the fitness
            fitness = ppm.evaluate_ppm()
            
            if (fitness < self.currBest):
                self.currBest = fitness
                self.ppm = ppm
                self.bestSource = x
            
            print("Fitness (Current / Best) : (%f / %f)" % (fitness,self.currBest))
            print("Best found in : %f" % (self.bestSource))
            


class RandomWalk(object):

    def __init__(self,
                 ppm,
                 probFlip,
                 noOps,
                 filename,
                 debug=True):
        #The probability that a random operation is a flip rather than a swap
        self.probFlip = probFlip
        #The number of steps away from the starting config that we will allow
        self.noOps = noOps
        self.ppm = ppm
        self.debug = debug
        self.filename = filename
        self.currBest = self.ppm.evaluate_ppm()
        self.bestSource = 0

    def initialise(self):
        pass
    
    
    def run_epocs(self, number_of_epocs):
        for x in range(number_of_epocs):
            #generate a random step number (1-N)
            numberOfSteps = random.randint(1,self.noOps)
            ppm = copy.deepcopy(self.ppm)
            #for every step
            for i in range(numberOfSteps):
                #is this a flip?
                probCount = random.random()
                if (probCount <= self.probFlip):
                    #flip a random
                    ppm.flip_one_magnet()
                #is this a swap
                else:
                #swap for a random
                    ppm.swap_one_magnet()
            
            #check the fitness
            fitness = ppm.evaluate_ppm()
            
            if (fitness < self.currBest):
                self.currBest = fitness
                #self.ppm = ppm
                self.bestSource = x
            
            print("Fitness (Current / Best) : (%f / %f)" % (fitness,self.currBest))
            print("Best found in : %f" % (self.bestSource))
            
