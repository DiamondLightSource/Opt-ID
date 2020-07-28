import unittest, os, shutil
from collections import namedtuple

import json, h5py
import numpy as np

from ..src.magnets import Magnets, MagLists

from ..src.field_generator import generate_reference_magnets,   \
                                 generate_bfield,              \
                                 calculate_bfield_phase_error

from ..src.logging_utils import logging, getLogger, setLoggerLevel
logger = getLogger(__name__)


class BfieldPhaseErrorTest(unittest.TestCase):

    def test_calculate_bfield_phase_error(self):
        # Enable debug logging
        setLoggerLevel(logger, 4)

        # inp == Inputs
        # exp == Expected Outputs
        # obs == Observed Outputs

        data_path = 'IDSort/test/data/bfield_phase_error_test/test_calculate_bfield_phase_error'
        inp_path  = os.path.join(data_path, 'inputs')
        exp_path  = os.path.join(data_path, 'expected_outputs')
        obs_path  = os.path.join(data_path, 'observed_outputs')

        # Prepare input file paths
        inp_json_path   = os.path.join(inp_path, 'test_cpmu.json')
        inp_mag_path    = os.path.join(inp_path, 'test_cpmu.mag')
        inp_h5_path     = os.path.join(inp_path, 'test_cpmu.h5')

        # Prepare expected output file paths
        exp_ref_phase_error_path  = os.path.join(exp_path, 'ref_phase_error.npy')
        exp_ref_trajectories_path = os.path.join(exp_path, 'ref_trajectories.npy')
        exp_phase_error_path      = os.path.join(exp_path, 'phase_error.npy')
        exp_trajectories_path     = os.path.join(exp_path, 'trajectories.npy')

        # Prepare observed output file paths
        obs_ref_phase_error_path  = os.path.join(obs_path, 'ref_phase_error.npy')
        obs_ref_trajectories_path = os.path.join(obs_path, 'ref_trajectories.npy')
        obs_phase_error_path      = os.path.join(obs_path, 'phase_error.npy')
        obs_trajectories_path     = os.path.join(obs_path, 'trajectories.npy')

        # Always clear any observed output files before running test
        shutil.rmtree(obs_path, ignore_errors=True)
        os.makedirs(obs_path)

        try:

            # Attempt to load the ID json data
            try:
                logger.info('Loading ID info from json [%s]', inp_json_path)
                with open(inp_json_path, 'r') as fp:
                    info = json.load(fp)

            except Exception as ex:
                logger.error('Failed to load ID info from json [%s]', inp_json_path, exc_info=ex)
                raise ex

            # Attempt to load the ID's lookup table for the eval points defined in the JSON file
            try:
                logger.info('Loading ID lookup table [%s]', inp_h5_path)
                with h5py.File(inp_h5_path, 'r') as fp:
                    lookup = {}
                    for beam in info['beams']:
                        logger.debug('Loading beam [%s]', beam['name'])
                        lookup[beam['name']] = fp[beam['name']][...]

            except Exception as ex:
                logger.error('Failed to load ID lookup table [%s]', inp_h5_path, exc_info=ex)
                raise ex

            # Attempt to load the real magnet data
            try:
                logger.info('Loading ID magnets [%s]', inp_mag_path)
                magnet_sets = Magnets()
                magnet_sets.load(inp_mag_path)

            except Exception as ex:
                logger.error('Failed to load ID info from json [%s]', inp_mag_path, exc_info=ex)
                raise ex

            # From loaded data construct a perfect magnet array that the loss will be computed with respect to
            logger.info('Constructing perfect reference magnets to shadow real magnets and ideal bfield')
            ref_magnet_sets  = generate_reference_magnets(magnet_sets)
            ref_magnet_lists = MagLists(ref_magnet_sets)
            ref_bfield       = generate_bfield(info, ref_magnet_lists, ref_magnet_sets, lookup)

            # Execute the function under test for perfect reference magnets
            obs_ref_phase_error, obs_ref_trajectories = calculate_bfield_phase_error(info, ref_bfield)

            # Save the observed values for the reference magnets (for failure inspection)
            np.save(obs_ref_phase_error_path,  obs_ref_phase_error)
            np.save(obs_ref_trajectories_path, obs_ref_trajectories)

            # Load the expected values for the reference magnets
            exp_ref_phase_error  = np.load(exp_ref_phase_error_path)
            exp_ref_trajectories = np.load(exp_ref_trajectories_path)

            logger.debug('Perfect bfield phase error exp [%s] obs [%s] MSE [%s]',
                         exp_ref_phase_error, obs_ref_phase_error,
                         np.mean(np.square(exp_ref_phase_error - obs_ref_phase_error)))

            logger.debug('Perfect bfield trajectories MSE [%s]',
                         np.mean(np.square(exp_ref_trajectories - obs_ref_trajectories)))

            # Execute the function under test for real magnets (with no optimization applied, expect values to be poor)
            magnet_lists = MagLists(magnet_sets)
            bfield       = generate_bfield(info, magnet_lists, magnet_sets, lookup)
            obs_phase_error, obs_trajectories = calculate_bfield_phase_error(info, bfield)

            # Save the observed values for the reference magnets (for failure inspection)
            np.save(obs_phase_error_path,  obs_phase_error)
            np.save(obs_trajectories_path, obs_trajectories)

            # Load the expected values for the real magnets
            exp_phase_error  = np.load(exp_phase_error_path)
            exp_trajectories = np.load(exp_trajectories_path)

            logger.debug('Real (unoptimized) bfield phase error exp [%s] obs [%s] MSE [%s]',
                         exp_phase_error, obs_phase_error,
                         np.mean(np.square(exp_phase_error - obs_phase_error)))

            logger.debug('Real (unoptimized) bfield trajectories MSE [%s]',
                         np.mean(np.square(exp_trajectories - obs_trajectories)))

            # Assert that the observed values are all similar to the expected ones
            assert np.allclose(exp_ref_phase_error,  obs_ref_phase_error)
            assert np.allclose(exp_ref_trajectories, obs_ref_trajectories)

            # Assert that the observed values are all similar to the expected ones
            assert np.allclose(exp_phase_error,  obs_phase_error)
            assert np.allclose(exp_trajectories, obs_trajectories)

        # Use (except + else) instead of (finally) so that output files can be inspected if the test fails
        except Exception as ex: raise ex
        else:

            # Clear any observed output files after running successful test
            shutil.rmtree(obs_path, ignore_errors=True)
            os.makedirs(obs_path)

