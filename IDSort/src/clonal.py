'''
Created on 8 Oct 2011

@author: ssg37927
'''

import random
import copy
import h5py
import os

class BCell(object):
    
    scale = 10.0
    
    def __init__(self):
        self.bcell_age = 0
        self.genome = None
        self.length = 0
        self.random_genome()
        self.calculated_fitness = None
        self.num_macromutaion = 0
        self.num_hypermutaion = 0
    
    def random_genome(self):
        raise Exception("This needs to create a new random BCell")
    
    def mutate(self, number_of_mutations):
        raise Exception("Mutate needs to be implemented")
    
    def fitness(self):
        raise Exception("fittness needs to be implemented and return a double")
    
    def evaluate(self):
        self.calculated_fitness = self.fitness()
    
    def clone(self):
        return copy.deepcopy(self)
    
    def get_length(self):
        raise Exception("get length needs to be implemented and return a int")
    
    def age(self):
        self.bcell_age += 1
    
    def inverse_proportional_hypermutation(self, c):
        fit = self.fitness()
        position = (fit-BCell.e_star)/(BCell.m_star-BCell.e_star)
        print "Position = ", position
        if position > 1.0 :
            position = 1.0
        m = ((position**2) * (c * self.get_length()))
        self.mutate(m)
        print "performing proportional Hypermutation %i times fitness (%f) -> (%f) , (%f) * ( %f * %f) " % (m, fit, self.fitness(), (position**2), c, self.get_length())
        self.num_hypermutaion += m
    
    def hypermacromuation(self, c):
        a = random.randint(0, self.get_length()-1)
        b = random.randint(0, self.get_length()-1)
        mutations = abs(a-b)*c
        print "performing Macromutation %i times" % (mutations)
        self.mutate(mutations)
        self.num_macromutaion += mutations
    
    def write_bcell_to_h5(self, h5group, epoc_number, member_number):
        raise Exception("write_bcell_to_h5 needs to be implemented and return a int")
    
    def best_bcell_per_epoc(self, epoc_number):
        raise Exception("best_bcell_per_epoc needs to be implemented")

class SortTest(BCell):
    
    def __init__(self,length):
        self.genome_length = length
        BCell.__init__(self)
    
    def random_genome(self):
        self.genome = []
        for i in range(self.genome_length):
            self.genome.append(i)
        self.mutate(self.genome_length*2)
    
    def mutate(self, number_of_mutations):
        # pick 2 points at random and switch them
        for i in range(number_of_mutations):
            a = random.randint(0, self.genome_length-1)
            b = random.randint(0, self.genome_length-1)
            temp = self.genome[a]
            self.genome[a] = self.genome[b]
            self.genome[b] = temp
    
    def get_length(self):
        return self.genome_length
    
    def fitness(self):
        fit = self.genome_length*self.genome_length
        for i in range(self.genome_length-1):
            for j in range(i+1,self.genome_length-1):
                if (self.genome[i] < self.genome[j]) :
                    fit -= 1
        return fit
    
    def __eq__(self, other):
        for i in range(len(self.genome)):
            if self.genome[i] != other.genome[i] :
                return False
        return True


class ClonalSelection(object):

    def __init__(self,
                 bcell,
                 filename,
                 max_age=5, 
                 population_size=10, 
                 dup=2,
                 c=0.5,
                 debug=True):
        self.initial_bcell = bcell
        self.population_size = population_size
        self.duplication_number = dup
        self.max_age = max_age
        self.c = c
        self.t = 0
        self.pop = {}
        self.average_fitness = []
        self.best = []
        self.worst = []
        self.average_age = []
        self.debug = debug
        self.filename = filename

    def initialise(self):
        BCell.e_star = 0.0
        BCell.m_star = 1.0
        self.t = 0
        self.pop = {}
        self.pop[self.t] = []
        for i in range(self.population_size):
            bcell = self.initial_bcell.clone()
            bcell.random_genome()
            bcell.evaluate()
            self.pop[self.t].append(bcell)
        self.write_current_epoc_to_file()
    
    def make_clones(self, bcells):
        clones = []
        for bcell in bcells:
                for j in range(self.duplication_number):
                    clones.append(bcell.clone())
        return clones
    
    def make_hypermutation(self,bcells):
        clones = self.make_clones(bcells)
        for bcell in clones:
            bcell.bcell_age=0
            bcell.inverse_proportional_hypermutation(self.c)
            bcell.evaluate()
        return clones
    
    def make_hypermacro(self,bcells):
        clones = self.make_clones(bcells)
        for bcell in clones:
            bcell.bcell_age=0
            bcell.hypermacromuation(self.c*self.c)
            bcell.evaluate()
        return clones
    
    def age_group(self, bcells):
        for bcell in bcells:
            bcell.age()
    
    def cull_population(self, bcells):
        population = []
        for bcell in bcells:
            if bcell.bcell_age < self.max_age :
                population.append(bcell)
        return population
    
    def remove_duplicates(self, bcells):
        population = []
        for bcell in bcells:
            append = True
            for cell in population:
                if bcell == cell :
                    append = False
                    continue
            if append :
                population.append(bcell)
        return population
    
    def select_best(self, population):
        pop_culled = self.cull_population(population)
        pop_remove_duplicates = self.remove_duplicates(pop_culled)
        bcells = sorted(pop_remove_duplicates, key=lambda bcell : bcell.calculated_fitness)
        return bcells[0:self.population_size]
    
    def write_current_epoc_to_file(self):
        h5file = h5py.File(self.filename,'a')
        #epoc_group = h5file.create_group("E_%010i"%(self.t));
        for i in range(len(self.pop[self.t])):
        #    member_group = epoc_group.create_group("G_%04i"%(i))
            self.pop[self.t][i].write_bcell_to_h5(h5file, self.t, i)
            #h5file.flush()
        h5file.close()
        # now write the best to the same dir
        pathname = os.path.splitext(self.filename)[0]
        if(not os.path.exists(pathname)) :
            os.mkdir(pathname)
        self.pop[self.t][0].best_bcell_per_epoc(self.t, pathname)
    
    def run_epocs(self, number_of_epocs):
    
        for i in range(number_of_epocs):
            
            print "Processing epoch %i" % (self.t)
            # age all the old bcells
            self.age_group(self.pop[self.t])
            
            # now create the clones
            print "Making clones"
            pop_clone = self.make_clones(self.pop[self.t])
            
            # proform Hypermutation
            print "Performing Hypermutation"
            pop_hyper = self.make_hypermutation(pop_clone)
            print "Performing HyperMacromutation"
            pop_macro = self.make_hypermacro(pop_clone)
            
            pop_all = pop_clone+pop_hyper+pop_macro
            
            self.pop[self.t+1] = self.select_best(pop_all)
            
            # calculate stats
            print "Calculating stats"
            pop = self.pop[self.t+1]
            BCell.e_star = pop[0].calculated_fitness
            self.best.append(pop[0].calculated_fitness)
            BCell.m_star = pop[-1].calculated_fitness
            self.worst.append(pop[-1].calculated_fitness)
            pop_fit = 0
            pop_age = 0
            for genome in pop:
                pop_fit += genome.calculated_fitness
                pop_age += genome.bcell_age*1.0
            self.average_fitness.append(pop_fit/len(pop))
            self.average_age.append(pop_age/len(pop))
            
            if self.debug :
                self.pop[self.t] = None
            
            self.t += 1
            print "Writing to file"
            self.write_current_epoc_to_file();
    


def display_pop(population):
    for bcell in population:
        print bcell.calculated_fitness, bcell.genome, bcell.bcell_age

def get_best_fitness(clonal):
    best = []
    for pop in clonal.pop:
        best.append(pop[0].calculated_fitness)
    return best

def get_clonal_stats(clonal):
    average_fitness = []
    best = []
    worst = []
    average_age = []
    for i in range(clonal.t):
        pop = clonal.pop[i]
        best.append(pop[0].calculated_fitness)
        worst.append(pop[-1].calculated_fitness)
        pop_fit = 0
        pop_age = 0
        for genome in pop:
            pop_fit += genome.calculated_fitness
            pop_age += genome.bcell_age*1.0
        average_fitness.append(pop_fit/len(pop))
        average_age.append(pop_age/len(pop))
    return (average_fitness, best, worst, average_age)

def write_stats_to_file(cs, filename):
    import numpy as np
    f = h5py.File(filename, 'w')
    f.create_dataset("best", data=np.array(cs.best))
    f.create_dataset("worst", data=np.array(cs.worst))
    f.create_dataset("average_age", data=np.array(cs.average_age))
    f.create_dataset("average_fittnes", data=np.array(cs.average_fitness))
    f.close()