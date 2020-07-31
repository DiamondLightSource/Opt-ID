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
Created on 3 Dec 2013

@author: ssg37927
'''


import h5py
import json
import numpy as np

from .logging_utils import logging, getLogger, setLoggerLevel
logger = getLogger(__name__)


def calculate_bfield_axis_contribution(bfield_eval_points, major_axis, minor_axis, dimensions, position):
    # This function calculates the bfield in a single orientation according to the calling function

    # Accumulate the bfield strength at each eval point
    bfield = np.zeros(bfield_eval_points.shape[1:])

    # Transform eval points into the reference frame of the current magnet (spatial region)
    shape = (-1,) + (1,) * (bfield_eval_points.ndim - 1)
    r1 = bfield_eval_points - np.reshape(position, shape)
    r2 = bfield_eval_points - np.reshape(position + dimensions, shape)

    # Process each combination of axes ijk where i is the minor axis and jk are the other two
    # axes if we use the same handedness for all the coordinate systems
    for j in range(3):
        k = (3 - minor_axis) - j
        if (k == major_axis) or (j == minor_axis): continue

        # Rotate the eval points for the bottom-left-near corner of the (magnet) region into the current coordinate system
        r1i = r1[minor_axis]
        r1j = r1[j]
        r1k = r1[k]

        # Rotate the eval points for the upper-right-far corner of the (magnet) region into the current coordinate system
        r2i = r2[minor_axis]
        r2j = r2[j]
        r2k = r2[k]

        # If any values in the k axis are negative in either the bottom-left-near or upper-right-far tensors
        # then swap the k axis components between the two and negate their values
        # TODO marked for removal, does not change the resulting field values in tests for all device types
        if not (np.all(r1k > 0) and np.all(r2k > 0)):
            r1k, r2k = -r2k, -r1k

        # Compute the norms multiple field vectors at each eval point
        a1 = np.sqrt(r2i * r2i + r2j * r2j + r2k * r2k)
        a2 = np.sqrt(r1i * r1i + r1j * r1j + r2k * r2k)
        a3 = np.sqrt(r1i * r1i + r2j * r2j + r1k * r1k)
        a4 = np.sqrt(r2i * r2i + r1j * r1j + r1k * r1k)
        a5 = np.sqrt(r1i * r1i + r2j * r2j + r2k * r2k)
        a6 = np.sqrt(r2i * r2i + r1j * r1j + r2k * r2k)
        a7 = np.sqrt(r2i * r2i + r2j * r2j + r1k * r1k)
        a8 = np.sqrt(r1i * r1i + r1j * r1j + r1k * r1k)

        if major_axis == minor_axis:
            # Calculate and apply the field contributions when we are on the diagonal of the 3x3 bfield matrix
            b1 = r2i * r2k / (r2j * a1)
            b2 = r1i * r2k / (r1j * a2)
            b3 = r1i * r1k / (r2j * a3)
            b4 = r2i * r1k / (r1j * a4)
            b5 = r1i * r2k / (r2j * a5)
            b6 = r2i * r2k / (r1j * a6)
            b7 = r2i * r1k / (r2j * a7)
            b8 = r1i * r1k / (r1j * a8)
            bfield -= (np.arctan(b1) + np.arctan(b2) + np.arctan(b3) + np.arctan(b4) -
                       np.arctan(b5) - np.arctan(b6) - np.arctan(b7) - np.arctan(b8)) / (4 * np.pi)

        elif major_axis == j:
            # Calculate and apply the field contributions when we are off the diagonal of the 3x3 bfield matrix
            c1 = a1 + r2k
            c2 = a2 + r2k
            c3 = a3 + r1k
            c4 = a4 + r1k
            c5 = a5 + r2k
            c6 = a6 + r2k
            c7 = a7 + r1k
            c8 = a8 + r1k
            bfield -= np.log((c1 * c2 * c3 * c4) / (c5 * c6 * c7 * c8)) / (4 * np.pi)

    return bfield

def generate_bfield(bfield_eval_points, dimensions, position):
    # This function calls the main field calculating function and outputs a 3x3 matrix for each evaluation point
    # [[Bx(x), Bz(x), Bs(x)]
    #  [Bx(z), Bz(z), Bs(z)]
    #  [Bx(s), Bz(s), Bs(s)]]
    #
    # To calculate the real field component of any block need to get real data sum contributions such that
    # Bx = Bx(x)*Mx + Bx(z)*Mz + Bx(s)*Ms
    # Bz = Bz(x)*Mx + Bz(z)*Mz + Bz(s)*Ms
    # Bs = Bs(x)*Mx + Bs(z)*Mz + Bs(s)*Ms

    # Allocate a tensor for the resulting bfield to be calculated into
    bfield = np.zeros((*bfield_eval_points.shape[1:], 3, 3))

    # For each major axis compute the bfield contribution w.r.t the other (minor) axes
    for major_axis in range(3):

        # Computes a triangular matrix and copies over the diagonal
        for minor_axis in range(major_axis, 3):

            # Calculate the bfield contribution of the current major axis w.r.t the current minor axis
            bfield[..., major_axis, minor_axis] = calculate_bfield_axis_contribution(
                bfield_eval_points, major_axis, minor_axis, dimensions, position)

            # Only duplicate if we are not on the diagonal
            if major_axis != minor_axis:
                bfield[..., minor_axis, major_axis] = bfield[..., major_axis, minor_axis]

    return bfield

def process(options, args):

    if hasattr(options, 'verbose'):
        setLoggerLevel(logger, options.verbose)

    logger.debug('Starting')

    # TODO refactor arguments to accept json file as named parameter
    with open(args[0], 'r') as fp:
        data = json.load(fp)

    output_path = args[1]

    #meshgrid modified 18/02/19 ZP+MB to calculate no of points in each direction properly (avoid floating point errors)
    # TODO refactor to use np.linspace for step creation
    bfield_eval_points = np.mgrid[data['xmin']:data['xmax']-(data['xstep']/100.0):data['xstep'],
                                  data['zmin']:data['zmax']-(data['zstep']/100.0):data['zstep'],
                                  data['smin']:data['smax']-(data['sstep']/100.0):data['sstep']]

    logger.info('Evaluation points with shape [%s]', bfield_eval_points.shape)

    logger.debug('Evaluation points X-axis | Requested min [%f] max [%f] | Observed min [%f] max [%f]',
                 data['xmin'], data['xmax'], np.min(bfield_eval_points[0]), np.max(bfield_eval_points[0]))

    logger.debug('Evaluation points Z-axis | Requested min [%f] max [%f] | Observed min [%f] max [%f]',
                 data['zmin'], data['zmax'], np.min(bfield_eval_points[1]), np.max(bfield_eval_points[1]))

    logger.debug('Evaluation points S-axis | Requested min [%f] max [%f] | Observed min [%f] max [%f]',
                 data['smin'], data['smax'], np.min(bfield_eval_points[2]), np.max(bfield_eval_points[2]))

    try:

        with h5py.File(output_path, 'w') as outfile:

            for b, beam in enumerate(data['beams']):

                # Make a dataset in the output h5 file for this beams per magnet bfield data
                num_magnets  = len(beam['mags'])
                shape        = (*bfield_eval_points.shape[1:], 3, 3)
                beam_dataset = outfile.create_dataset(beam['name'], shape=(*shape, num_magnets), chunks=(*shape, 1), dtype=np.float64)

                logger.info('Beam %d [%s] with %d magnets and lookup shape [%s]', b, beam['name'], num_magnets, beam_dataset.shape)

                for a, mag in enumerate(beam['mags']):

                    # Extract magnet data
                    position, dimensions = np.array(mag['position']), np.array(mag['dimensions'])

                    # Calculate the ideal bfield contribution of a perfect magnet in this position
                    per_magnet_bfield = generate_bfield(bfield_eval_points, dimensions, position)

                    # APPLE Symmetric devices have clampcut corners to facilitate holding them in the device
                    # we need to compensate for the field strengths contributed by the regions that would be removed
                    if data['type'] == 'APPLE_Symmetric':

                        # Find the size of the region that would be cut out of each magnet
                        clampcut = data['clampcut']
                        clampcut_dimensions = np.array([clampcut, clampcut, dimensions[2]])

                        # Place clampcut regions over the current magnet depending on what beam it is in
                        if beam['name'] in ['Q2 Beam', 'Q4 Beam']:
                            position_c1 = position
                            position_c2 = position + np.array([dimensions[0] - clampcut, dimensions[1] - clampcut, 0])
                        elif beam['name'] in ['Q1 Beam', 'Q3 Beam']:
                            position_c1 = position + np.array([dimensions[0] - clampcut, 0, 0])
                            position_c2 = position + np.array([0, dimensions[1] - clampcut, 0])

                        # Calculate the ideal bfield contribution of the clamp region of a perfect magnet
                        bfield_c1 = generate_bfield(bfield_eval_points, clampcut_dimensions, position_c1)
                        bfield_c2 = generate_bfield(bfield_eval_points, clampcut_dimensions, position_c2)

                        # Bfield of clampcut magnets is the bfield of an uncut magnet minus bfield of the regions to be cut out
                        per_magnet_bfield -= (bfield_c1 + bfield_c2)

                    # Rotate the calculated bfield for this magnet into the coordinate system the magnet is placed in
                    per_magnet_bfield = np.dot(per_magnet_bfield, np.array(mag['direction_matrix']))
                    beam_dataset[..., a] = per_magnet_bfield

                    logger.debug('Beam %d [%s] Magnet %3d bfield with shape [%s]', b, beam['name'], a, per_magnet_bfield.shape)

    except Exception as ex:
        logger.error('Failed to save lookup to [%s]', output_path, exc_info=ex)
        raise ex

    logger.debug('Halting')

if __name__ == "__main__":
    import optparse
    usage = "%prog [options] ID_Description_File Output_filename"
    parser = optparse.OptionParser(usage=usage)
    parser.add_option('-v', '--verbose', dest='verbose', help='Set the verbosity level [0-4]', default=0, type='int')

    (options, args) = parser.parse_args()

    try:
        process(options, args)
    except Exception as ex:
        logger.critical('Fatal exception in lookup_generator::process', exc_info=ex)
