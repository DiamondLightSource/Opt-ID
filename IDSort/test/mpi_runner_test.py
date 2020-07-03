import unittest, os, shutil
from collections import namedtuple

import pickle

from ..src.magnets import MagLists
from ..src.mpi_runner import process


class MpiRunnerTest(unittest.TestCase):

    def test_process(self):
        # inp == Inputs
        # exp == Expected Outputs
        # obs == Observed Outputs

        data_path = 'IDSort/test/data/mpi_runner_test/test_process'
        inp_path  = os.path.join(data_path, 'inputs')
        exp_path  = os.path.join(data_path, 'expected_outputs')
        obs_path  = os.path.join(data_path, 'observed_outputs')

        # Prepare input file paths
        inp_json_path   = os.path.join(inp_path, 'test_cpmu.json')
        inp_mag_path    = os.path.join(inp_path, 'test_cpmu.mag')
        inp_h5_path     = os.path.join(inp_path, 'test_cpmu.h5')

        # Prepare expected output file paths
        exp_genome_paths = [
            os.path.join(exp_path, '1.12875826e-08_000_7c51ecd01f73.genome'),
            os.path.join(exp_path, '1.49788342e-08_000_b6059e1c0884.genome'),
            os.path.join(exp_path, '1.81441854e-08_000_645a52b2bb2d.genome'),
            os.path.join(exp_path, '4.05007630e-08_000_47a4f43ecf86.genome'),
        ]

        # Always clear any observed output files before running test
        shutil.rmtree(obs_path, ignore_errors=True)
        os.makedirs(obs_path)

        # Prepare parameters for process function
        options = {
            'iterations'       : 3,
            'id_filename'      : inp_json_path,
            'magnets_filename' : inp_mag_path,
            'lookup_filename'  : inp_h5_path,
            'setup'            : 24,
            'c'                : 1,
            'e'                : 0.0,
            'restart'          : False,
            'max_age'          : 10,
            'scale'            : 10.0,
            'singlethreaded'   : True,
            'seed'             : True,
            'seed_value'       : 30
        }
        options_named  = namedtuple("options", options.keys())(*options.values())
        args = [
            obs_path
        ]

        try:

            # Execute the function under test
            process(options_named, args)

            # Compare the output files to the expected ones
            for exp_genome_path in exp_genome_paths:

                # Assert the expected genome exists for comparison
                assert os.path.exists(exp_genome_path)

                # TODO reliance on floating point precision in filename might not be stable between versions
                exp_genome_fitness = os.path.split(exp_genome_path)[1].split('_')[0]

                # Scan file names in the observed output directory and look for the genome with the matching fitness
                obs_genome_path = None
                for candidate_genome_name in os.listdir(obs_path):
                    if exp_genome_fitness in candidate_genome_name:
                        obs_genome_path = os.path.join(obs_path, candidate_genome_name)
                        break

                # Assert we found the matching genome
                assert (obs_genome_path is not None)

                # Compare the output file to the expected one
                with open(exp_genome_path, 'rb') as exp_genome_file, \
                     open(obs_genome_path, 'rb') as obs_genome_file:

                    exp_maglist = pickle.load(exp_genome_file)
                    obs_maglist = pickle.load(obs_genome_file)

                    assert (type(exp_maglist) is MagLists)
                    assert (type(obs_maglist) is MagLists)

                    # Offloads comparison to MagLists::__eq__ method
                    assert exp_maglist == obs_maglist

        # Use (except + else) instead of (finally) so that output files can be inspected if the test fails
        except Exception as ex: raise ex
        else:

            # Clear any observed output files after running successful test
            shutil.rmtree(obs_path, ignore_errors=True)
            os.makedirs(obs_path)

    def test_process_initial_population(self):
        # inp == Inputs
        # exp == Expected Outputs
        # obs == Observed Outputs

        data_path = 'IDSort/test/data/mpi_runner_test/test_process_initial_population'
        inp_path  = os.path.join(data_path, 'inputs')
        exp_path  = os.path.join(data_path, 'expected_outputs')
        obs_path  = os.path.join(data_path, 'observed_outputs')

        # Prepare input file paths
        inp_json_path    = os.path.join(inp_path, 'test_cpmu.json')
        inp_mag_path     = os.path.join(inp_path, 'test_cpmu.mag')
        inp_h5_path      = os.path.join(inp_path, 'test_cpmu.h5')
        inp_genome_paths = [
            os.path.join(inp_path, '1.12875826e-08_000_7c51ecd01f73.genome'),
            os.path.join(inp_path, '1.49788342e-08_000_b6059e1c0884.genome'),
            os.path.join(inp_path, '1.81441854e-08_000_645a52b2bb2d.genome'),
            os.path.join(inp_path, '4.05007630e-08_000_47a4f43ecf86.genome')
        ]

        # Prepare expected output file paths
        exp_genome_paths = [
            os.path.join(exp_path, '1.09170425e-08_000_88d39698a4f7.genome'),
            os.path.join(exp_path, '6.42786056e-09_000_aaf866db3206.genome'),
            os.path.join(exp_path, '7.03009938e-09_000_a90b37ecedb9.genome'),
            os.path.join(exp_path, '7.06840992e-09_000_a12a86932596.genome')
        ]

        # Always clear any observed output files before running test
        shutil.rmtree(obs_path, ignore_errors=True)
        os.makedirs(obs_path)

        # Make a fresh copy of the initial genomes in the observed output directory
        for inp_genome_path in inp_genome_paths:
            # Assert the expected genome exists for comparison
            assert os.path.exists(inp_genome_path)
            shutil.copy(inp_genome_path, obs_path)

        # Prepare parameters for process function
        options = {
            'iterations'       : 3,
            'id_filename'      : inp_json_path,
            'magnets_filename' : inp_mag_path,
            'lookup_filename'  : inp_h5_path,
            'setup'            : 24,
            'c'                : 1,
            'e'                : 0.0,
            'restart'          : True,
            'max_age'          : 10,
            'scale'            : 10.0,
            'singlethreaded'   : True,
            'seed'             : True,
            'seed_value'       : 30
        }
        options_named = namedtuple("options", options.keys())(*options.values())
        args = [
            obs_path
        ]

        try:

            # Execute the function under test
            process(options_named, args)

            # Compare the output files to the expected ones
            for exp_genome_path in exp_genome_paths:

                # Assert the expected genome exists for comparison
                assert os.path.exists(exp_genome_path)

                # TODO reliance on floating point precision in filename might not be stable between versions
                exp_genome_fitness_and_age = '_'.join(os.path.split(exp_genome_path)[1].split('_')[0:2])

                # Scan file names in the observed output directory and look for the genome with the matching fitness
                obs_genome_path = None
                for candidate_genome_name in os.listdir(obs_path):
                    if exp_genome_fitness_and_age in candidate_genome_name:
                        obs_genome_path = os.path.join(obs_path, candidate_genome_name)
                        break

                # Assert we found the matching genome
                assert (obs_genome_path is not None)

                # Compare the output file to the expected one
                with open(exp_genome_path, 'rb') as exp_genome_file, \
                     open(obs_genome_path, 'rb') as obs_genome_file:

                    exp_maglist = pickle.load(exp_genome_file)
                    obs_maglist = pickle.load(obs_genome_file)

                    assert (type(exp_maglist) is MagLists)
                    assert (type(obs_maglist) is MagLists)

                    # Offloads comparison to MagLists::__eq__ method
                    assert exp_maglist == obs_maglist

        # Use (except + else) instead of (finally) so that output files can be inspected if the test fails
        except Exception as ex: raise ex
        else:

            # Clear any observed output files after running successful test
            shutil.rmtree(obs_path, ignore_errors=True)
            os.makedirs(obs_path)

