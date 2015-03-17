'''
Created on 9 Dec 2013

@author: ssg37927
'''

import magnets as mag
import field_generator as fg
import binascii
import os
import cPickle
import random
import copy
import logging
import numpy as np

class BCell(object):

    def __init__(self):
        self.age = 0
        self.fitness = None
        self.genome = None
        self.uid = binascii.hexlify(os.urandom(6))

    def create(self):
        raise Exception("create needs to be implemented")

    def age_bcell(self):
        self.age += 1

    def save(self, path):
        filename = '%010.8e_%03i_%s.genome' %(self.fitness, self.age, self.uid)
        fp = open(os.path.join(path, filename), 'w')
        cPickle.dump(self.genome, fp)
        fp.close()

    def load(self, filename):
        fp = open(filename, 'r')
        self.genome = cPickle.load(fp)
        fp.close()
        params = os.path.split(filename)[1].split('_')
        self.fitness = float(params[0])
        self.age = int(params[1])
        self.uid = params[2].split('.')[0]

    def generate_children(self, number_of_children, number_of_mutations):
        raise Exception("generate_children needs to be implemented")


class ID_BCell(BCell):

    def __init__(self):
        BCell.__init__(self)
        self.mutations = 0

    def create(self, info, lookup, magnets, maglist, ref_trajectories):
        self.genome = maglist
        field_unused, self.fitness = fg.calculate_cached_trajectory_fitness(info, lookup, magnets, maglist, ref_trajectories)

    def generate_children(self, number_of_children, number_of_mutations, info, lookup, magnets, ref_trajectories, real_bfield=None):
        # first age, as we are now creating children
        self.age_bcell()
        children = []
        
        # Generate the IDfiled for the parent, as we need to calculate it fully here.
        original_bfield = None
        if real_bfield == None:
            original_bfield, calculated_fitness = fg.calculate_cached_trajectory_fitness(info, lookup, magnets, self.genome, ref_trajectories)
            fitness_error = abs(self.fitness - calculated_fitness)
            logging.debug("Estimated fitness to real fitness error %2.10e"%(fitness_error))
            self.fitness = calculated_fitness
        else :
            original_bfield = real_bfield
            logging.debug("Using real bfield")
            
        original_magnets = fg.generate_per_magnet_array(info, self.genome, magnets)

        for i in range(number_of_children):
            maglist = copy.deepcopy(self.genome)
            maglist.mutate(number_of_mutations)
            new_magnets = fg.generate_per_magnet_array(info, maglist, magnets)
            update = fg.compare_magnet_arrays(original_magnets, new_magnets, lookup)
            child = ID_BCell()
            child.mutations = number_of_mutations
            child.genome = maglist
            updated_bfield = np.array(original_bfield)
            for beam in update.keys() :
                if update[beam].size != 0:
                    updated_bfield = updated_bfield - update[beam]
            child.fitness = fg.calculate_trajectory_fitness_from_array(updated_bfield, info, ref_trajectories)
            #child.create(info, lookup, magnets, maglist, ref_total_id_field)
            children.append(child)
            logging.debug("Child created with fitness : %f" % (child.fitness))
        return children

class ID_Shim_BCell(BCell):

    def __init__(self):
        BCell.__init__(self)
        self.mutations = 0

    def create(self, info, lookup, magnets, maglist, ref_trajectories, number_of_changes, original_bfield):
        self.maglist = maglist
        self.changes = number_of_changes
        self.create_genome(number_of_changes)
        
        maglist = copy.deepcopy(self.maglist)
        maglist.mutate_from_list(self.genome)
        new_magnets = fg.generate_per_magnet_array(info, maglist, magnets)
        original_magnets = fg.generate_per_magnet_array(info, self.maglist, magnets)
        update = fg.compare_magnet_arrays(original_magnets, new_magnets, lookup)
        updated_bfield = np.array(original_bfield)
        
        for beam in update.keys() :
            if update[beam].size != 0:
                updated_bfield = updated_bfield - update[beam]
        self.fitness = fg.calculate_trajectory_fitness_from_array(updated_bfield, info, ref_trajectories)

    def create_genome(self, number_of_mutations, available={'VE':range(12), 'HE':range(12), 'HH':range(506), 'VV':range(506)}):
        self.genome = []
        for i in range(number_of_mutations):
            # pick a list at random
            key = random.choice(available.keys())
            # pick a flip or swap
            p1 = random.choice(available[key])
            p2 = random.choice(available[key])
            
            if random.random() > 0.5 :
                # swap
                self.genome.append(('S', key, p1, p2))
            else :
                self.genome.append(('F', key, p1, p2))


    def create_mutant(self, number_of_mutations, available={'VE':range(12), 'HE':range(12), 'HH':range(506), 'VV':range(506)}):
        mutant = copy.deepcopy(self.genome)
        for i in range(number_of_mutations):
            position = random.randint(0,len(mutant)-1)
            # pick a list at random
            key = random.choice(available.keys())
            # pick a flip or swap
            p1 = random.choice(available[key])
            p2 = random.choice(available[key])
            
            if random.random() > 0.5 :
                # swap
                mutant[position] = ('S', key, p1, p2)
            else :
                mutant[position] = ('F', key, p1, p2)
        return mutant


    def generate_children(self, number_of_children, number_of_mutations, info, lookup, magnets, ref_trajectories, real_bfield=None):
        # first age, as we are now creating children
        self.age_bcell()
        children = []
        
        # Generate the IDfiled for the parent, as we need to calculate it fully here.
        original_bfield = None
        original_fitness = None
        if real_bfield == None:
            original_bfield, original_fitness = fg.calculate_cached_trajectory_fitness(info, lookup, magnets, self.genome, ref_trajectories)
            fitness_error = abs(self.fitness - original_fitness)
            logging.debug("Estimated fitness to real fitness error %2.10e"%(fitness_error))

        else :
            original_bfield = real_bfield
            original_fitness = fg.calculate_trajectory_fitness_from_array(original_bfield, info, ref_trajectories)
            fitness_error = abs(self.fitness - original_fitness)
            logging.debug("Using real bfield")
        
        original_magnets = fg.generate_per_magnet_array(info, self.maglist, magnets)

        maglist = copy.deepcopy(self.maglist)
        mutation_list = self.create_mutant(number_of_mutations)
        maglist.mutate_from_list(mutation_list)
        new_magnets = fg.generate_per_magnet_array(info, maglist, magnets)
        update = fg.compare_magnet_arrays(original_magnets, new_magnets, lookup)
        updated_bfield = np.array(original_bfield)
        for beam in update.keys() :
            if update[beam].size != 0:
                updated_bfield = updated_bfield - update[beam]
        self.fitness = fg.calculate_trajectory_fitness_from_array(updated_bfield, info, ref_trajectories)

        for i in range(number_of_children):
            maglist = copy.deepcopy(self.maglist)
            mutation_list = self.create_mutant(number_of_mutations)
            maglist.mutate_from_list(mutation_list)
            new_magnets = fg.generate_per_magnet_array(info, maglist, magnets)
            update = fg.compare_magnet_arrays(original_magnets, new_magnets, lookup)
            child = ID_Shim_BCell()
            child.mutations = number_of_mutations
            child.genome = mutation_list
            child.maglist = self.maglist
            updated_bfield = np.array(original_bfield)
            for beam in update.keys() :
                if update[beam].size != 0:
                    updated_bfield = updated_bfield - update[beam]
            child.fitness = fg.calculate_trajectory_fitness_from_array(updated_bfield, info, ref_trajectories)
            children.append(child)
            logging.debug("Child created with fitness : %2.10e" % (child.fitness))
        return children
