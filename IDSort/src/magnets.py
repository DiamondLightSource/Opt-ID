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
import copy

import random
import numpy as np

from .logging_utils import logging, getLogger, setLoggerLevel
logger = getLogger(__name__)


class Magnets(object):
    '''
    This class deals with all the real magnet information
    '''
    def __init__(self):
        self.magnet_sets = {}
        self.magnet_flip = {}
        self.mean_field  = {}


    def add_magnet_set(self, set_name, magnets_path, flip_vector):
        logger.info('Adding real magnets set [%s]', set_name)

        # Add the loaded set to the class
        self.magnet_sets[set_name] = {}
        self.magnet_flip[set_name] = np.array(flip_vector)

        # Load the Magnets data
        try:
            logger.info('Loading magnets set [%s] from [%s]', set_name, magnets_path)
            with open(magnets_path, 'r') as magnets_file:
                for line in magnets_file:
                    vals = line.split()
                    assert len(vals) >= 4
                    self.magnet_sets[set_name][vals[0]] = np.array((float(vals[1]), float(vals[2]), float(vals[3])))

        except Exception as ex:
            logger.error('Failed to load magnets set [%s] from [%s]', set_name, magnets_path, exc_info=ex)
            raise ex

        # Compute the mean field of the magnets set
        self.mean_field[set_name] = 0.0
        for magnet in self.magnet_sets[set_name]:
            self.mean_field[set_name] += np.linalg.norm(self.magnet_sets[set_name][magnet])
        self.mean_field[set_name] = self.mean_field[set_name] / len(self.magnet_sets[set_name])

        logger.debug('Magnets set [%s] of length [%d] flip [%s] mean [%f]',
                     set_name, len(self.magnet_sets[set_name]), self.magnet_flip[set_name], self.mean_field[set_name])


    def add_perfect_magnet_set(self, set_name, num_magnets, field_vector, flip_vector):
        logger.info('Adding perfect magnets set [%s]', set_name)

        # Add the set to the class
        self.magnet_sets[set_name] = {}
        self.magnet_flip[set_name] = np.array(flip_vector)

        # Populate the magnets dictionary with a set of identical field vectors
        for index in range(num_magnets):
            # TODO reliance on there being less than 1000 magnets of a type in an ID might not be true in the future
            self.magnet_sets[set_name][f'{index:03d}'] = np.array(field_vector)

        # Mean field strength for a perfect set is the norm of the perfect field vector
        self.mean_field[set_name] = np.linalg.norm(np.array(field_vector))

        logger.debug('Magnets set [%s] of length [%d] flip [%s] mean [%f]',
                     set_name, len(self.magnet_sets[set_name]), self.magnet_flip[set_name], self.mean_field[set_name])


    def add_perfect_magnet_set_duplicate(self, set_name, magnet_keys, field_vector, flip_vector):
        logger.info('Adding perfect magnets set [%s] using existing magnets keys', set_name)

        # Add the set to the class
        self.magnet_sets[set_name] = {}
        self.magnet_flip[set_name] = np.array(flip_vector)

        # Populate the magnets dictionary with a set of identical field vectors using the magnet keys provided
        for mag in magnet_keys:
            self.magnet_sets[set_name][mag] = np.array(field_vector)

        # Mean field strength for a perfect set is the norm of the perfect field vector
        self.mean_field[set_name] = np.linalg.norm(np.array(field_vector))

        logger.debug('Magnets set [%s] of length [%d] flip [%s] mean [%f]',
                     set_name, len(self.magnet_sets[set_name]), self.magnet_flip[set_name], self.mean_field[set_name])


    def save(self, filename):
        try:
            logger.info('Saving magnets to [%s]', filename)
            with open(filename, 'wb') as fp:
                pickle.dump((self.magnet_sets, self.magnet_flip, self.mean_field), fp)

        except Exception as ex:
            logger.error('Failed to save magnets to [%s]', filename, exc_info=ex)
            raise ex


    def load(self, filename):
        try:
            logger.info('Loading magnets from [%s]', filename)
            with open(filename, 'rb') as fp:
                (self.magnet_sets, self.magnet_flip, self.mean_field) = pickle.load(fp)

        except Exception as ex:
            logger.error('Failed to load magnets from [%s]', filename, exc_info=ex)
            raise ex


    # TODO remove need for this entirely. In case of no availability list we can just use size of magnets set
    def availability(self):
        # Full availability lists for each magnet set
        return { key : list(range(len(self.magnet_sets[key]))) for key in self.magnet_sets }


    def __eq__(self, other):
        # Assert set keys within exp .mag file are internally consistent
        exp_mag_set_keys   = sorted(self.magnet_sets.keys())
        exp_mag_flip_keys  = sorted(self.magnet_flip.keys())
        exp_mag_field_keys = sorted(self.mean_field.keys())
        assert (exp_mag_set_keys == exp_mag_flip_keys) and (exp_mag_set_keys == exp_mag_field_keys)

        # Assert set keys within obs .mag file are internally consistent
        obs_mag_set_keys   = sorted(other.magnet_sets.keys())
        obs_mag_flip_keys  = sorted(other.magnet_flip.keys())
        obs_mag_field_keys = sorted(other.mean_field.keys())
        assert (obs_mag_set_keys == obs_mag_flip_keys) and (obs_mag_set_keys == obs_mag_field_keys)

        # Assert set keys between exp and obs Magnets classes are consistent with one another
        if not ((exp_mag_set_keys   == obs_mag_set_keys)  and
                (exp_mag_flip_keys  == obs_mag_flip_keys) and
                (exp_mag_field_keys == obs_mag_field_keys)): return False

        for set_name in exp_mag_set_keys:
            exp_mag_set_mag_names   = sorted( self.magnet_sets[set_name].keys())
            obs_mag_set_mag_names   = sorted(other.magnet_sets[set_name].keys())

            # Assert magnet names in this magnet set between exp and obs Magnets classes are consistent with one another
            if not (exp_mag_set_mag_names == obs_mag_set_mag_names): return False

            # Assert magnet values in this magnet set between exp and obs Magnets classes are consistent with one another
            for mag in exp_mag_set_mag_names:
                if not np.any(self.magnet_sets[set_name][mag] == other.magnet_sets[set_name][mag]): return False

            # Assert the flip vectors and mean fields between exp and obs Magnets classes classes are consistent with one another
            if not np.all(self.magnet_flip[set_name] == other.magnet_flip[set_name]): return False
            if not       ( self.mean_field[set_name] ==  other.mean_field[set_name]): return False

        # If we have reached here the two objects contain the same data
        return True


# TODO refactor naming of class
class MagLists():
    '''
    This class deals with the ordering and specification of several lists
    '''
    
    def __init__(self, magnets):
        # Keep a local copy of the raw magnet data used by this magnets list
        self.raw_magnets = copy.deepcopy(magnets)

        # Create an ordered list of magnet positions and flips
        self.magnet_lists = {}
        for set_name in self.raw_magnets.magnet_sets.keys():
            mags = []
            for mag in self.raw_magnets.magnet_sets[set_name].keys():
                # TODO document the components here "mag name", "flipped???", "???"
                mags.append([mag, 1, 0])
            self.magnet_lists[set_name] = mags


    def sort_list(self, name):
        # Invoke sort on the magnet ordering within the given set
        self.magnet_lists[name].sort()


    def sort_all(self):
        # Invoke sort on each magnet set
        for set_name in self.magnet_lists.keys():
            self.sort_list(set_name)


    def shuffle_list(self, set_name):
        # Invoke shuffle on the magnet ordering within the given set
        random.shuffle(self.magnet_lists[set_name])


    def shuffle_all(self):
        # Invoke shuffle on each magnet set
        for set_name in self.magnet_lists.keys():
            self.shuffle_list(set_name)


    def flip(self, set_name, magnet_indices):
        # Flip the field of all the given magnet indices in the magnet set
        for mag in magnet_indices:
            self.magnet_lists[set_name][mag][1] *= -1


    def swap(self, set_name, mag_a, mag_b):
        # Swap the two magnets in the given magnet set
        mag_list = self.magnet_lists[set_name]
        mag_list[mag_a], mag_list[mag_b] = mag_list[mag_b], mag_list[mag_a]


    # TODO determine if external "magnets" parameter is ever different to using "self.raw_magnets"
    def get_magnet_vals(self, set_name, magnet_index, magnets, flip_vector):
        # Extract target magnet values
        magnet       = self.magnet_lists[set_name][magnet_index]
        field_vector = magnets.magnet_sets[set_name][magnet[0]]

        # If this magnet needs flipping apply the flip vector
        return np.dot(field_vector, flip_vector) if (magnet[1] < 0) else field_vector

    # TODO benchmark severity of logger.debug() on the hot path
    def mutate(self, num_mutations, available=None, flip_prob=0.5):
        # If no availability is given then use the full set of magnet lists
        if available is None:
            logger.debug('No availability lists provides, using full set')
            set_keys = list(self.magnet_lists.keys())
        else:
            set_keys = list(available.keys())

        logger.debug('Available magnet lists [%s]', set_keys)

        # Perform a set of mutations using the same availability criteria
        for mutation_index in range(num_mutations):
            # Sample a random magnet set
            set_name = random.choice(set_keys)

            # Sample mutation type
            if random.random() > flip_prob:
                # Swap two random magnets from the magnet list
                if available is None:
                    mag_a, mag_b = random.randint(0, len(self.magnet_lists[set_name]) - 1), \
                                   random.randint(0, len(self.magnet_lists[set_name]) - 1)
                else:
                    mag_a, mag_b = random.choice(available[set_name]), \
                                   random.choice(available[set_name])

                self.swap(set_name, mag_a, mag_b)

                logger.debug('%03d of %03d : [%s] Swapping magnets [%s] and [%s]',
                             mutation_index, num_mutations, set_name, mag_a, mag_b)

            else:
                # Flip one random magnet from the magnet list
                if available is None:
                    mag = random.randint(0, len(self.magnet_lists[set_name]) - 1)
                else:
                    mag = random.choice(available[set_name])

                self.flip(set_name, (mag,))

                logger.debug('%03d of %03d : [%s] Flipping magnet [%s]',
                             mutation_index, num_mutations, set_name, mag)


    # TODO benchmark severity of logger.debug() on the hot path
    def mutate_from_list(self, mutation_list):
        # Perform a set of mutations using as specified
        for mutation_index, mutation in enumerate(mutation_list):

            if mutation[0] == 'S':
                # Swap two magnets from the magnet list
                set_name, mag_a, mag_b = mutation[1:4]
                self.swap(set_name, mag_a, mag_b)

                logger.debug('%03d of %03d : [%s] Swapping magnets [%s] and [%s]',
                             mutation_index, len(mutation_list), set_name, mag_a, mag_b)

            else:
                # Flip one magnet from the magnet list
                set_name, mag = mutation[1:3]
                self.flip(set_name, (mag,))

                logger.debug('%03d of %03d : [%s] Flipping magnet [%s]',
                             mutation_index, len(mutation_list), set_name, mag)


    def __eq__(self, other):
        # Assert set keys between exp and obs MagLists classes are consistent with one another
        exp_mag_lists_keys = sorted( self.magnet_lists.keys())
        obs_mag_lists_keys = sorted(other.magnet_lists.keys())
        if not (exp_mag_lists_keys == obs_mag_lists_keys): return False

        for set_name in exp_mag_lists_keys:
            if not (self.magnet_lists[set_name] == other.magnet_lists[set_name]):
                return False

        # Offload raw_magnets comparison to Magnets::__eq__
        if not (self.raw_magnets == other.raw_magnets): return False

        # If we have reached here the two objects contain the same data
        return True


def process(options, args):

    if hasattr(options, 'verbose'):
        setLoggerLevel(logger, options.verbose)

    logger.debug('Starting')

    if hasattr(options, 'output_path') and (options.output_path is not None):
        if (len(args) > 0):
            logger.warning('Output path argument overrides unnamed trailing argument!')
            logger.warning('Ignoring all %d unnamed arguments [%s]', len(args), args)

        # Output path is the value of the named argument
        output_path = options.output_path
    else:
        if (len(args) == 0):
            error_message = 'Output path argument not provided, so must provide one unnamed trailing argument!'
            logger.error(error_message)
            raise Exception(error_message)

        elif (len(args) > 1):
            logger.warning('Multiple unnamed trailing arguments provided but only need one for output path!')
            logger.warning('Ignoring remaining %d unnamed arguments [%s]', len(args[1:]), args[1:])

        # Output path is first unnamed argument
        output_path = args[0]

    logger.info('Output path set to [%s]', output_path)

    mags = Magnets()

    # TODO make named constant flip vectors when we refactor Magnets class into modules
    if options.hmags  is not None:
        mags.add_magnet_set('HH', options.hmags,  (-1.,-1.,1.))
    if options.hemags is not None:
        mags.add_magnet_set('HE', options.hemags, (-1.,-1.,1.))
    if options.vmags  is not None:
        mags.add_magnet_set('VV', options.vmags,  (-1.,1.,-1.))
    if options.vemags is not None:
        mags.add_magnet_set('VE', options.vemags, (-1.,1.,-1.))
    if options.htmags is not None:
        mags.add_magnet_set('HT', options.htmags, (-1.,-1.,1.))
    
    try:
        mags.save(output_path)
    except Exception as ex:
        logger.error('Failed to save magnets to [%s]', output_path, exc_info=ex)
        raise ex

    logger.debug('Halting')

if __name__ == '__main__' :
    import optparse
    usage = '%prog [options] [output_path?]'
    parser = optparse.OptionParser(usage=usage)
    parser.add_option('-v', '--verbose', dest='verbose', help='Set the verbosity level [0-4]', default=0, type='int')

    parser.add_option(  '-H', '--hmaglist',  dest='hmags',  help='Set the path to the H magnet data',  default=None, type='string')
    parser.add_option('--HE', '--hemaglist', dest='hemags', help='Set the path to the HE magnet data', default=None, type='string')
    parser.add_option(  '-V', '--vmaglist',  dest='vmags',  help='Set the path to the V magnet data',  default=None, type='string')
    parser.add_option('--VE', '--vemaglist', dest='vemags', help='Set the path to the VE magnet data', default=None, type='string')
    parser.add_option('--HT', '--htmaglist', dest='htmags', help='Set the path to the HT magnet data', default=None, type='string')

    parser.add_option('-o', '--output', dest='output_path', help='Set the path to write the output to', default=None, type='string')

    (options, args) = parser.parse_args()

    try:
        process(options, args)
    except Exception as ex:
        logger.critical('Fatal exception in magnets::process', exc_info=ex)
