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

import threading
import numpy as np
import h5py
import json

from .magnets import Magnets, MagLists
from .magnet_tools import calculate_phase_error

from .logging_utils import logging, getLogger
logger = getLogger(__name__)

# TODO trace if "magnets" always is equivalent to "maglist.raw_magnets"
def generate_per_magnet_array(info, maglist, magnets):
    # Result dict for each beams data
    beams = {}

    # Track the current index of each magnet type
    mag_indices = {'HT': 0, 'HE': 0, 'VE': 0, 'HH': 0, 'VV': 0}

    # Process each beam in the ID json data
    for b, beam in enumerate(info['beams']):

        # Process all magnets in this beam
        magvalues = []
        for a, mag in enumerate(beam['mags']):

            # Prepare data for this magnet
            magvalues += [maglist.get_magnet_vals(mag['type'], mag_indices[mag['type']], magnets, mag['flip_matrix'])]

            # Update the index to the next magnet of this type
            mag_indices[mag['type']] += 1

        # Stack the resulting rows and transpose them to shape (3, N)
        beams[beam['name']] = np.transpose(np.vstack(magvalues))
        logger.debug('Beam %d [%s] has shape [%s]', b, beam['name'], beams[beam['name']].shape)

    return beams

def compare_magnet_arrays(mag_array_a, mag_array_b, lookup):
    difference_map = {}

    for beam in mag_array_a.keys():

        difference = (mag_array_a[beam] - mag_array_b[beam])
        diff_slice = (np.sum(np.abs(difference), axis=0) > 0)
        field_diff = np.sum((lookup[beam][..., diff_slice] * difference[:,diff_slice]), axis=4)

        difference_map[beam] = np.sum(field_diff, axis=4)

    return difference_map


def generate_per_beam_b_field(info, maglist, mags, lookup):

    # TODO refactor use of results input being destructively modified
    # TODO usage involves multi-threading!!! Can data be corrupted while appending?
    def generate_sub_array(beam_array, eval_list, lookup, beam, results):
        # This sum is calculated like this to avoid memory errors
        result = np.sum((lookup[beam][..., eval_list[0]] * beam_array[:, eval_list[0]]), axis=4)
        for m in eval_list[1:]:
            result += np.sum((lookup[beam][..., m] * beam_array[:, m]), axis=4)
        results.append(result)

    beam_arrays = generate_per_magnet_array(info, maglist, mags) #beam_arrays is a dictionary
    procs = 8
    fields = {}
    for beam in beam_arrays.keys(): #go over Bottom Beam key then Top Beam key
        #logging.debug("beam arrays keys are %s"%(beam_arrays.keys())) #Bottom Beam & Top Beam
        beam_array = beam_arrays[beam]
        #logging.debug("beam array shape is %s"%(s(beam_array.shape))) #(3,234)
        indexes = range(lookup[beam].shape[5]) #lookup is a dictionary
        #logging.debug("lookup[beam] shape is %s"%(s(lookup[beam].shape))) #(17, 5, 2622, 3, 3, 234) 
        #logging.debug("indexes is %s"%(indexes)) #indexes is a list of numbers 0-233
        length = len(indexes)//procs
        #logging.debug("length is %s"%(s(length)))
        chunks=[indexes[x : x+length] for x in range(0, len(indexes), length)]
        #logging.debug("chunks shape is %s"%(s(chunks.shape))) doesn't work
        results = []
        pp = []
        for i in range(len(chunks)):
            chunk = chunks[i]
            pp1 = threading.Thread(name='ProcThread-%02i'%(i), target=generate_sub_array, args = (beam_array, chunk, lookup, beam, results))
            pp1.daemon = True
            pp1.start()
            pp.append(pp1)
        
        for pp1 in pp:
            pp1.join()
        
        # This sum is calculated like this to avoid memory errors
        result = results[0]
        for m in range(1, len(results)):
            result += results[m]
        #logging.debug("results is %d"%(len(results))) #Length = 9
        #logging.debug("result shape is %s"%(result.shape())) "tuple object is not callable
        fields[beam] = result
        #logging.debug("fields is %d"%(len(fields))) #Length = 2 
        #logging.debug("fields keys are %s"%(fields.keys())) #Bottom Beam and Top Beam
        #logging.debug("fields values are %s"%(fields.items())) gives truncated arrays, not helpful
    return fields #returns a dictionary containing keys Bottom Beam and Top Beam


def generate_id_field(info, maglist, mags, f1):
    fields = generate_per_beam_b_field(info, maglist, mags, f1)
    id_fields = np.zeros(next(iter(fields.values())).shape) #iterates over the values in the dictionary fields to create the array id_fields
    #logging.debug("id fields shape is %s"%(str(id_fields.shape))) #(17,5,2622,3)
    for beam in fields.keys():
        id_fields+=fields[beam]
    #logging.debug("id_fields %s"%(str(id_fields.shape))) #(17,5,2622,3)
    return id_fields #returns an array (17,5,2622,3)


def generate_id_field_cost(field, ref_field):
    # TODO why only slice [...,2:4] ?
    return np.sum(np.square(field[...,2:4] - ref_field[...,2:4]))


def generate_reference_magnets(mags):
    ref_mags = Magnets()
    for magtype in list(mags.magnet_sets.keys()):
        mag_dir = list(mags.magnet_sets[magtype].values())[0].argmax()
        unit = np.zeros(3)
        unit[mag_dir] = mags.mean_field[magtype]
        #ref_mags.add_perfect_magnet_set(magtype, len(mags.magnet_sets[magtype]) , unit, mags.magnet_flip[magtype])
        ref_mags.add_perfect_magnet_set_duplicate(magtype, mags.magnet_sets[magtype].keys(), unit, mags.magnet_flip[magtype])
        #logging.debug("ref_mags shape %s"%(str(ref_mags.shape))) magnets object has no attribute shape
    return ref_mags


def calculate_cached_fitness(info, lookup, magnets, maglist, ref_total_id_field):
    total_id_field = generate_id_field(info, maglist, magnets, lookup)
    return generate_id_field_cost(total_id_field, ref_total_id_field)


def calculate_cached_trajectory_fitness(info, lookup, magnets, maglist, ref_trajectories):
    total_id_field = generate_id_field(info, maglist, magnets, lookup)
    pherr, test_array = calculate_phase_error(info, total_id_field)
    return (total_id_field, generate_id_field_cost(test_array, ref_trajectories))


def calculate_trajectory_fitness_from_array(total_id_field, info, ref_trajectories):
    pherr, test_array = calculate_phase_error(info, total_id_field)
    return generate_id_field_cost(test_array, ref_trajectories)

# TODO refactor and remove this code
# def calculate_fitness(id_filename, lookup_filename, magnets_filename, maglist):
#     # TODO this will be slow, but should be optimizable with lookups
#     with open(id_filename, 'r') as fp:
#         info = json.load(fp)
#
#     with h5py.File(lookup_filename, 'r') as lookup:
#
#         mags = Magnets()
#         mags.load(magnets_filename)
#
#         ref_mags           = generate_reference_magnets(mags)
#         ref_maglist        = MagLists(ref_mags)
#         ref_total_id_field = generate_id_field(info, ref_maglist, ref_mags, lookup)
#
#         result = calculate_cached_fitness(info, lookup, mags, maglist, ref_total_id_field)
#
#     return result


def write_bfields(filename, id_filename, lookup_filename, magnets_filename, maglist):

    with open(id_filename, 'r') as fp:
        info = json.load(fp)

    with h5py.File(lookup_filename, 'r') as fp:
        lookup = {}
        for beam in info['beams']:
            lookup[beam['name']] = fp[beam['name']][...]

    mags = Magnets()
    mags.load(magnets_filename)
    ref_mags=generate_reference_magnets(mags)

    with h5py.File(filename, 'w') as fp:
    
        per_beam_field = generate_per_beam_b_field(info, maglist, mags, lookup)
        total_id_field = generate_id_field(info, maglist, mags, lookup)

        for name in per_beam_field.keys():
            fp.create_dataset("%s_per_beam" % (name), data=per_beam_field[name])

        fp.create_dataset('id_Bfield', data=total_id_field)
        trajectory_information=calculate_phase_error(info, total_id_field)
        fp.create_dataset('id_phase_error', data=trajectory_information[0])
        fp.create_dataset('id_trajectory',  data=trajectory_information[1])

        per_beam_field = generate_per_beam_b_field(info, maglist, ref_mags, lookup)
        total_id_field = generate_id_field(info, maglist, ref_mags, lookup)

        for name in per_beam_field.keys():
            fp.create_dataset("%s_per_beam_perfect" % (name), data=per_beam_field[name])

        fp.create_dataset('id_Bfield_perfect', data=total_id_field)
        trajectory_information = calculate_phase_error(info, total_id_field)
        fp.create_dataset('id_phase_error_perfect', data=trajectory_information[0])
        fp.create_dataset('id_trajectory_perfect',  data=trajectory_information[1])
