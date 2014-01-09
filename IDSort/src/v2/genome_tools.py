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
        self.fitness = fg.calculate_cached_trajectory_fitness(info, lookup, magnets, maglist, ref_trajectories)

    def generate_children(self, number_of_children, number_of_mutations, info, lookup, magnets, ref_total_id_field):
        # first age, as we are now creating children
        self.age_bcell()
        children = []
        for i in range(number_of_children):
            maglist = copy.deepcopy(self.genome)
            maglist.mutate(number_of_mutations)
            child = ID_BCell()
            child.mutations = number_of_mutations
            child.create(info, lookup, magnets, maglist, ref_total_id_field)
            children.append(child)
        return children
