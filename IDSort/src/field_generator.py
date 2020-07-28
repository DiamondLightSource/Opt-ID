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


def generate_per_beam_bfield(info, maglist, mags, lookup, nthreads=8):

    def generate_sub_array(beam_array, chunk, lookup, beam, results):
        # This sum is calculated like this to avoid memory errors
        result = sum(np.sum((lookup[beam][..., m] * beam_array[:, m]), axis=4) for m in chunk)
        results.append(result)

    beam_arrays = generate_per_magnet_array(info, maglist, mags)

    bfields = {}
    for beam, beam_array in beam_arrays.items():

        indexes = range(lookup[beam].shape[5])
        length  = len(indexes) // nthreads
        chunks  = [indexes[x : x+length] for x in range(0, len(indexes), length)]

        results   = []
        processes = []
        for index, chunk in enumerate(chunks):
            process = threading.Thread(name=f'ProcThread-{index:02d}', daemon=True, target=generate_sub_array,
                                       args=(beam_array, chunk, lookup, beam, results))
            process.start()
            processes.append(process)
        
        for process in processes:
            process.join()

        # Merge chunk results
        bfields[beam] = sum(results)

    return bfields


def generate_bfield(info, maglist, mags, lookup, return_per_beam_bfield=False):
    per_beam_bfield = generate_per_beam_bfield(info, maglist, mags, lookup)
    bfield = sum(per_beam_bfield.values())
    return bfield if (not return_per_beam_bfield) else (bfield, per_beam_bfield)


def generate_reference_magnets(mags):
    # Result to hold the set of 'perfect' magnets
    ref_mags = Magnets()

    # Process all magnet types
    for mag_type, mag_set in mags.magnet_sets.items():

        # Observe the major field direction of the 0th magnet of this type (safe^TM due to manufacturing tolerances)
        field_vector = next(iter(mag_set.values())) # next(iter(...)) avoids full list conversion

        # Make a 'perfect' field vector biased in that direction using the mean field strength of the magnet set
        ref_field_vector = np.zeros_like(field_vector)
        ref_field_vector[np.argmax(field_vector)] = mags.mean_field[mag_type]

        # Add a set of 'perfect' magnets using the same name keys as the observed real magnet set
        ref_mags.add_perfect_magnet_set_duplicate(mag_type, mag_set.keys(),
                                                  ref_field_vector, mags.magnet_flip[mag_type])

    return ref_mags


def calculate_bfield_loss(bfield, ref_bfield):
    # TODO why only slice [...,2:4] ?
    return np.sum(np.square(bfield[...,2:4] - ref_bfield[...,2:4]))


def calculate_cached_bfield_loss(info, lookup, magnets, maglist, ref_bfield):
    bfield = generate_bfield(info, maglist, magnets, lookup)
    return calculate_bfield_loss(bfield, ref_bfield)

def calculate_trajectory_loss(trajectories, ref_trajectories):
    # TODO why only slice [...,2:4] ?
    return np.sum(np.square(trajectories[...,2:4] - ref_trajectories[...,2:4]))

def calculate_cached_trajectory_loss(info, lookup, magnets, maglist, ref_trajectories):
    # Calculate bfield loss and also return reference array to reuse later
    bfield = generate_bfield(info, maglist, magnets, lookup)
    phase_error, trajectories = calculate_bfield_phase_error(info, bfield)
    trajectory_loss = calculate_trajectory_loss(trajectories, ref_trajectories)
    return bfield, trajectory_loss

def calculate_trajectory_loss_from_array(info, bfield, ref_trajectories):
    phase_error, trajectories = calculate_bfield_phase_error(info, bfield)
    return calculate_trajectory_loss(trajectories, ref_trajectories)


def calculate_bfield_phase_error(info, bfield):
    # TODO move ring energy into device JSON file as devices are tied to specific facilities
    energy             = 3.0                           # Diamond synchrotron 3 GeV storage ring
    const              = (0.03 / energy) * 1e-2        # Unknown constant... evaluates to 1e-4 for 3 GeV storage ring
    electron_mass      = 0.511e-3                      # Electron resting mass (already in GeV for convenience)
    gamma_sq           = (energy / electron_mass) ** 2 # Ratio of energy of electron to its resting mass
    two_speed_of_light = 2.9911124e8 * 2               # Speed of light in metres per second
    degrees_per_radian = 360.0 / (2.0 * np.pi)

    nskip = 8 # Number of periods at the start and end of the device to skip in the calculations
    nperiods               = info['periods']
    s_step_size            = info['sstep']
    s_total_steps          = int(round((info['smax'] - info['smin']) / s_step_size))
    s_steps_per_period     = int(info['period_length'] / s_step_size)
    s_steps_per_qtr_period = s_steps_per_period // 4

    # bfield.shape == (eval_x, eval_z, eval_s, 3) where 3 refers to slices for the X, Z, and S field strength measurements
    # We only care about integrals of motion in X and Z so discard S measurements below

    # Trapezium rule applied to bfield measurements in X and Z helps compute the second integral of motion
    # TODO roll is on X axis (0) between neighbouring eval points, is this correct? Should be S axis (2)?
    trap_bfield = np.roll(bfield[...,:2], shift=1, axis=0)
    trap_bfield[...,0,:] = 0 # Set first samples on S axis to 0
    trap_bfield = (trap_bfield + bfield[...,:2]) * (s_step_size / 2)

    # Accumulate the second integral of motion w.r.t the X and Z axes, along the orbital S axis
    # TODO why do we swap X,Z for Z,X order for the field measurements?
    traj_2nd_integral = np.cumsum((trap_bfield[...,::-1] * np.array([-const, const])), axis=2)

    # Trapezium rule applied to second integral of motion helps compute the first integral of motion
    # TODO why shift by 4 indices? One period? (no gaurantees on how many world space units 4 indices corresponds to) Should this be 1?
    # TODO roll is on X axis (0) between neighbouring eval points, is this correct? Should be S axis (2)?
    trap_traj_2nd_integral = np.roll(traj_2nd_integral, shift=4, axis=0)
    trap_traj_2nd_integral[:,:,0,:] = 0 # Set first samples on S axis to 0
    trap_traj_2nd_integral = (trap_traj_2nd_integral + traj_2nd_integral) * (s_step_size / 2)

    # Accumulate the first integral of motion w.r.t the X and Z axes, along the orbital S axis
    traj_1st_integral = np.cumsum(trap_traj_2nd_integral, axis=2)

    # Trajectory first and second integrals of motion have been computed, now we compute the phase error of those trajectories
    trajectories = np.concatenate([traj_1st_integral, traj_2nd_integral], axis=-1)

    # Extract the second integral of motion for the central trajectory going down the centre of the eval point grid
    # TODO is +1 and -1 correct? Potentially this is needed in 1 base indexed languages but not python
    i = ((bfield.shape[0] + 1) // 2) - 1
    j = ((bfield.shape[1] + 1) // 2) - 1
    w = np.square(traj_2nd_integral[i,j])

    # Trapezium rule applied to second integral of motion for central trajectory helps computes first integral of motion
    trap_w = np.roll(w, shift=1, axis=0) # TODO Axis 0 is S axis in this np.roll! This makes sense, previous two do not!
    trap_w[0,:] = 0.0 # Set first samples on S axis to 0
    trap_w = (trap_w + w) * 1e-3 * (s_step_size / 2)
    w_1st_integral = np.cumsum(np.sum(trap_w, axis=-1), axis=0) # Cumulative sum along S axis (0)

    # x is regular sampling interval along S axis for computing line of best fit
    x = np.arange(0, s_steps_per_qtr_period * ((4 * nperiods) - (2 * nskip)), s_steps_per_qtr_period) + \
         (s_total_steps // 2) - (nperiods * (s_steps_per_period // 2)) + ((nskip - 1) * s_steps_per_qtr_period)

    # y is derived from w_1st_integral plus a factor that grows linearly along the length of the S axis
    sample_step = s_step_size * (1e-3 / (two_speed_of_light * gamma_sq))
    y = (w_1st_integral / two_speed_of_light) + np.arange(0, sample_step * s_total_steps, sample_step)
    y = y[x[0]:(x[-1] + s_steps_per_qtr_period):s_steps_per_qtr_period] # Resample y at same sample rate as x

    # Compute linear line of best fit for the central trajectory
    m, b = np.linalg.lstsq(np.vstack([x, np.ones_like(x)]).T, y, rcond=None)[0]
    # Compute the squared error between the line of best fit and the observed values
    phase_error_sq = np.square(y - ((m * x) + b))

    # Compute final scaled phase error
    phase_error = np.sqrt((np.sum(phase_error_sq) * np.square((2 * np.pi) / (m * s_steps_per_period))) /
                          (((4 * nperiods) + 1) - (2 * nskip))) * degrees_per_radian

    return phase_error, trajectories

# TODO currently broken and not used anywhere, fix or remove
def calculate_trajectory_straightness(info, trajectories):
    nperiods = info['periods']
    points_per_period = (trajectories.shape[0] / nperiods) / 3

    # Magic number not documented (to do with how data is interleaved into trajectories tensor?)
    nskip  = 2 # Value of 8 in other functions...
    skip   = int((trajectories.shape[0] / 3) + (nskip * points_per_period))

    xmean  = np.mean(trajectories[skip:-skip,0])
    dxmean = trajectories[skip:-skip,0] - xmean
    zabs   = np.abs(trajectories[skip:-skip,1])

    strx   = np.max(dxmean)
    strz   = np.max(zabs)
    return strx, strz


def write_bfields(filename, id_filename, lookup_filename, magnets_filename, maglist):

    # Load JSON configuration for a given device describing magnet types and positions and dimensions
    with open(id_filename, 'r') as fp:
        info = json.load(fp)

    # Load lookup table for a given device configuration measured at a grid of sample locations along the device gap
    with h5py.File(lookup_filename, 'r') as fp:
        lookup = {}
        for beam in info['beams']:
            lookup[beam['name']] = fp[beam['name']][...]

    # Load a set of real magnets and generate a set of perfect reference magnets mimicking the real magnets
    mags = Magnets()
    mags.load(magnets_filename)
    ref_mags = generate_reference_magnets(mags)

    with h5py.File(filename, 'w') as fp:

        # Compute the bfield data for the real magnets
        bfield, per_beam_bfield = generate_bfield(info, maglist, mags, lookup, return_per_beam_bfield=True)

        # Save the full bfield
        fp.create_dataset('id_Bfield', data=bfield)

        # Save the partial bfields for each beam in the device
        for beam_name, beam_bfield in per_beam_bfield.items():
            fp.create_dataset(f'{beam_name}_per_beam', data=beam_bfield)

        # Compute the phase error and electron trajectories through the bfield and save them
        phase_error, trajectories = calculate_bfield_phase_error(info, bfield)
        fp.create_dataset('id_phase_error', data=phase_error)
        fp.create_dataset('id_trajectory',  data=trajectories)

        # Compute the bfield data for the reference magnets
        ref_bfield, ref_per_beam_bfield = generate_bfield(info, maglist, ref_mags, lookup, return_per_beam_bfield=True)

        # Save the full bfield assuming perfect magnets
        fp.create_dataset('id_Bfield_perfect', data=ref_bfield)

        # Save the partial bfields for each beam in the device assuming perfect magnets
        for beam_name, beam_bfield in ref_per_beam_bfield.items():
            fp.create_dataset(f'{beam_name}_per_beam_perfect', data=beam_bfield)

        # Compute the phase error and electron trajectories through the bfield assuming perfect magnets and save them
        ref_phase_error, ref_trajectories = calculate_bfield_phase_error(info, ref_bfield)
        fp.create_dataset('id_phase_error_perfect', data=ref_phase_error)
        fp.create_dataset('id_trajectory_perfect',  data=ref_trajectories)
