# Copyright 2017 Diamond Light Source
# 
# Licensed under the Apache License, Version 2.0 (the "License"); 
# you may not use this file except in compliance with the License. 
# You may obtain a copy of the License at
# 
# http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, 
# software distributed under the License is distributed on an 
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, 
# either express or implied. See the License for the specific 
# language governing permissions and limitations under the License.

'''
Created on 5 Dec 2013

@author: ssg37927
'''

import pickle

import random
import numpy as np

from .logging_utils import logging, getLogger
logger = getLogger(__name__)


class Magnets(object):
    '''
    This class deals with all the real magnet information
    '''
    def __init__(self):
        self.magnet_sets = {}
        self.magnet_flip = {}
        self.mean_field = {}

    def add_magnet_set(self, name, filename, flip_vector):
        magnets = {}

        with open(filename, 'r') as fp:
            for line in fp:
                vals = line.split()
                assert len(vals) >= 4
                magnets[vals[0]] = np.array((float(vals[1]), float(vals[2]), float(vals[3])))

        self.magnet_sets[name] = magnets
        self.magnet_flip[name] = np.array(flip_vector)
        self.mean_field[name]  = 0.0
        for magnet in self.magnet_sets[name]:
            self.mean_field[name] += np.linalg.norm(self.magnet_sets[name][magnet])
        self.mean_field[name] = self.mean_field[name] / len(self.magnet_sets[name])
        

    def add_perfect_magnet_set(self, name, number, vector, flip_vector):
        magnets = {}
        for i in range(number):
            magnets['%03i' % (i)] = np.array(vector)
        self.magnet_sets[name] = magnets
        self.magnet_flip[name] = np.array(flip_vector)
    
    def add_perfect_magnet_set_duplicate(self, name, mag_list, vector, flip_vector):
        magnets = {}
        for key in mag_list.keys():
            magnets[key] = np.array(vector)
        self.magnet_sets[name] = magnets
        self.magnet_flip[name] = np.array(flip_vector)
    
    def save(self, filename):
        with open(filename, 'wb') as fp:
            pickle.dump((self.magnet_sets, self.magnet_flip, self.mean_field), fp)
    
    def load(self, filename):
        with open(filename, 'rb') as fp:
            (self.magnet_sets, self.magnet_flip, self.mean_field) = pickle.load(fp)
        
    def availability(self):
        availability = {}

        for key in self.magnet_sets:
            availability[key] = range(len(self.magnet_sets[key]))
            
        return availability

    def __eq__(self, other):
        # Assert set keys within old .mag file are internally consistent
        old_mag_set_keys   = sorted(self.magnet_sets.keys())
        old_mag_flip_keys  = sorted(self.magnet_flip.keys())
        old_mag_field_keys = sorted(self.mean_field.keys())
        assert (old_mag_set_keys == old_mag_flip_keys) and (old_mag_set_keys == old_mag_field_keys)

        # Assert set keys within new .mag file are internally consistent
        new_mag_set_keys   = sorted(other.magnet_sets.keys())
        new_mag_flip_keys  = sorted(other.magnet_flip.keys())
        new_mag_field_keys = sorted(other.mean_field.keys())
        assert (new_mag_set_keys == new_mag_flip_keys) and (new_mag_set_keys == new_mag_field_keys)

        # Assert set keys between old and new .mag files are consistent with one another
        if not ((old_mag_set_keys   == new_mag_set_keys)  and
                (old_mag_flip_keys  == new_mag_flip_keys) and
                (old_mag_field_keys == new_mag_field_keys)): return False

        for set_key in old_mag_set_keys:
            old_mag_set_mag_names   = sorted( self.magnet_sets[set_key].keys())
            new_mag_set_mag_names   = sorted(other.magnet_sets[set_key].keys())

            # Assert magnet names in this magnet set between old and new .mag files are consistent with one another
            if not (old_mag_set_mag_names == new_mag_set_mag_names): return False

            # Assert magnet values in this magnet set between old and new .mag files are consistent with one another
            for magnet in old_mag_set_mag_names:
                if not np.any(self.magnet_sets[set_key][magnet] == other.magnet_sets[set_key][magnet]): return False

            # Assert the flip vectors and mean fields between old and new .mag files are consistent with one another
            if not np.all(self.magnet_flip[set_key] == other.magnet_flip[set_key]): return False
            if not       (self.mean_field[set_key]  ==  other.mean_field[set_key]):  return False

        # If we have reached here the two objects contain the same data
        return True

class MagLists():
    '''
    This class deals with the ordering and specification of several lists
    '''
    
    def __init__(self, magnets):
        self.raw_magnets = magnets
        self.raw_magnets_availability = self.raw_magnets.availability()

        self.magnet_lists = {}
        for magnet_set in magnets.magnet_sets.keys():
            mags = []
            for magnet in magnets.magnet_sets[magnet_set].keys():
                mags.append([magnet, 1, 0])
            self.magnet_lists[magnet_set] = mags
    
    def sort_list(self, name):
        self.magnet_lists[name].sort()
    
    def sort_all(self):
        for name in self.magnet_lists.keys():
            self.sort_list(name)
    
    def shuffle_list(self, name):
        random.shuffle(self.magnet_lists[name])
    
    def shuffle_all(self):
        for name in self.magnet_lists.keys():
            self.shuffle_list(name)
    
    def flip(self, name, numbers):
        for number in numbers:
            self.magnet_lists[name][number][1] *= -1
    
    def swap(self, name, a, b):
        L = self.magnet_lists[name]
        L[a], L[b] = L[b], L[a]
    
    def get_magnet_vals(self, name, number, magnets, flip):
        magnet = self.magnet_lists[name][number]
        magdata = magnets.magnet_sets[name][magnet[0]]
        if magnet[1] < 0:
            magdata = magdata.dot(flip)
        return magdata

    # TODO benchmark severity of logger.debug() on the hot path
    def mutate(self, num_mutations, available=None, flip_prob=0.5):

        # If no availability is given then use the full set of magnet lists
        if available is None:
            logger.debug('No availability lists provides, using full set')
            available = self.raw_magnets_availability
        
        logger.debug('Available magnet lists [%s]', list(available.keys()))

        # Perform a set of mutations using the same availability criteria
        for mutation_index in range(num_mutations):

            # Sample a random magnet list
            list_key = random.choice(list(available.keys()))

            # Sample mutation type
            if random.random() > flip_prob:
                # Swap two random magnets from the magnet list
                mag_a = random.choice(available[list_key])
                mag_b = random.choice(available[list_key])
                self.swap(list_key, mag_a, mag_b)

                logger.debug('%03d of %03d : [%s] Swapping magnets [%s] and [%s]',
                             mutation_index, num_mutations, list_key, mag_a, mag_b)

            else:
                # Flip one random magnet from the magnet list
                mag = random.choice(available[list_key])
                self.flip(list_key, (mag,))

                logger.debug('%03d of %03d : [%s] Flipping magnet [%s]',
                             mutation_index, num_mutations, list_key, mag)

    # TODO benchmark severity of logger.debug() on the hot path
    def mutate_from_list(self, mutation_list):

        # Perform a set of mutations using as specified
        for mutation_index, mutation in enumerate(mutation_list):

            if mutation[0] == 'S':
                # Swap two magnets from the magnet list
                list_key, mag_a, mag_b = mutation[1:4]
                self.swap(list_key, mag_a, mag_b)

                logger.debug('%03d of %03d : [%s] Swapping magnets [%s] and [%s]',
                             mutation_index, len(mutation_list), list_key, mag_a, mag_b)

            else:
                # Flip one magnet from the magnet list
                list_key, mag = mutation[1:3]
                self.flip(list_key, (mag,))

                logger.debug('%03d of %03d : [%s] Flipping magnet [%s]',
                             mutation_index, len(mutation_list), list_key, mag)


    def __eq__(self, other):

        old_mag_lists_keys = sorted( self.magnet_lists.keys())
        new_mag_lists_keys = sorted(other.magnet_lists.keys())

        if not (old_mag_lists_keys == new_mag_lists_keys): return False

        for list_key in old_mag_lists_keys:
            if not (self.magnet_lists[list_key] == other.magnet_lists[list_key]):
                return False

        # Offload raw_magnets comparison to Magnets::__eq__
        if not (self.raw_magnets == other.raw_magnets): return False

        return True

def process(options, args):

    mags = Magnets()

    if options.hmags:
        mags.add_magnet_set('HH', options.hmags, (-1.,-1.,1.))
    if options.hemags:
        mags.add_magnet_set('HE', options.hemags, (-1.,-1.,1.))
    if options.vmags:
        mags.add_magnet_set('VV', options.vmags, (-1.,1.,-1.))
    if options.vemags:
        mags.add_magnet_set('VE', options.vemags, (-1.,1.,-1.))
    if options.htmags:
        mags.add_magnet_set('HT', options.htmags, (-1.,-1.,1.))
    
    mags.save(args[0])

if __name__ == "__main__" :
    import optparse
    usage = "%prog [options] OutputFile"
    parser = optparse.OptionParser(usage=usage)
    parser.add_option(  "-H", "--hmaglist",  dest="hmags",  help="Set the path to the H magnet data",  default='/home/gdy32713/DAWN_stable/optid/Opt-ID/IDSort/data/J13H.sim',   type="string")
    parser.add_option("--HE", "--hemaglist", dest="hemags", help="Set the path to the HE magnet data", default='/home/gdy32713/DAWN_stable/optid/Opt-ID/IDSort/data/J13HEA.sim', type="string")
    parser.add_option(  "-V", "--vmaglist",  dest="vmags",  help="Set the path to the V magnet data",  default=None, type="string")
    parser.add_option("--VE", "--vemaglist", dest="vemags", help="Set the path to the VE magnet data", default=None, type="string")
    parser.add_option("--HT", "--htmaglist", dest="htmags", help="Set the path to the HT magnet data", default=None, type="string")

    (options, args) = parser.parse_args()
    process(options, args)
