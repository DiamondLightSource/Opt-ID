import unittest, os, shutil
from collections import namedtuple

import pickle
import h5py
import numpy as np

from ..src.magnets import MagLists
from ..src.mpi_runner_for_shim_opt import process


class MpiRunnerForShimOptTest(unittest.TestCase):

    def test_process(self):
        # inp == Inputs
        # exp == Expected Outputs
        # obs == Observed Outputs

        data_path = 'IDSort/test/data/mpi_runner_for_shim_opt_test/test_process'
        inp_path  = os.path.join(data_path, 'inputs')
        exp_path  = os.path.join(data_path, 'expected_outputs')
        obs_path  = os.path.join(data_path, 'observed_outputs')

        # Prepare input file paths
        inp_json_path   = os.path.join(inp_path, 'test_cpmu_shim.json')
        inp_mag_path    = os.path.join(inp_path, 'test_cpmu.mag')
        inp_h5_path     = os.path.join(inp_path, 'test_cpmu_shim.h5')
        inp_genome_path = os.path.join(inp_path, '1.0_000_test_genome.genome') # Renamed from 1.12875826e-08_000_7c51ecd01f73.genome
        inp_bfield_path = os.path.join(inp_path, '1.12875826e-08_000_7c51ecd01f73.genome.h5')

        # Prepare expected output file paths
        # TODO understand the difference between A and non A genome
        exp_genome_nonA_paths = [
            os.path.join(exp_path, '1.20847271e-07_000_85a13cc425d0.genome'),
            os.path.join(exp_path, '1.20952907e-07_000_9228436240f4.genome'),
            os.path.join(exp_path, '1.20965365e-07_000_763473ed8598.genome'),
            os.path.join(exp_path, '1.23262940e-07_000_3fa353e9cf87.genome'),
        ]
        exp_genome_A_paths = [
            os.path.join(exp_path, '1.20847271e-07_000_A85a13cc425d0.genome'),
            os.path.join(exp_path, '1.20952907e-07_000_A9228436240f4.genome'),
            os.path.join(exp_path, '1.20965365e-07_000_A763473ed8598.genome'),
        ]
        exp_h5_paths = [
            os.path.join(exp_path, 'test-A763473ed8598.h5'),
            os.path.join(exp_path, 'test-A85a13cc425d0.h5'),
            os.path.join(exp_path, 'test-A9228436240f4.h5'),
        ]
        exp_genome_test_path = os.path.join(exp_path, '1.00000000e+00_001_test.genome')

        # Prepare observed output file path, others are searched for as filenames can change
        obs_genome_test_path = os.path.join(obs_path, '1.00000000e+00_001_test.genome')

        # Always clear any observed output files before running test
        shutil.rmtree(obs_path, ignore_errors=True)
        os.makedirs(obs_path)

        # Prepare parameters for process function
        options = {
            'iterations'          : 3,
            'number_of_mutations' : 5,
            'id_filename'         : inp_json_path,
            'magnets_filename'    : inp_mag_path,
            'lookup_filename'     : inp_h5_path,
            'bfield_filename'     : inp_bfield_path,
            'genome_filename'     : inp_genome_path,
            'setup'               : 24,
            'number_of_changes'   : 2,
            'mutations'           : 5,
            'c'                   : 2,
            'e'                   : 0.0,
            'restart'             : False,
            'max_age'             : 10,
            'scale'               : 10.0,
            'singlethreaded'      : True,
            'seed'                : True,
            'seed_value'          : 30
        }
        options_named = namedtuple("options", options.keys())(*options.values())
        args = [
            obs_path
        ]

        try:

            # Execute the function under test
            process(options_named, args)

            # Find observed output files
            obs_genome_paths = [os.path.join(obs_path, file_name)
                                for file_name in os.listdir(obs_path) if '.genome' in file_name]

            obs_h5_paths     = [os.path.join(obs_path, file_name)
                                for file_name in os.listdir(obs_path) if '.h5' in file_name]

            # Compare the test genomes
            with open(exp_genome_test_path, 'rb') as exp_genome_file, \
                 open(obs_genome_test_path, 'rb') as obs_genome_file:

                exp_maglist = pickle.load(exp_genome_file)
                obs_maglist = pickle.load(obs_genome_file)

                assert (type(exp_maglist) is MagLists)
                assert (type(obs_maglist) is MagLists)

                # Offloads comparison to MagLists::__eq__ method
                assert exp_maglist == obs_maglist

            # Compare shimlists for each genome
            for exp_genome_path in exp_genome_nonA_paths:

                # Assert the expected genome exists for comparison
                assert os.path.exists(exp_genome_path)

                # TODO reliance on floating point precision in filename might not be stable between versions
                # Extract the fitness from the genome file name
                exp_genome_fitness = os.path.split(exp_genome_path)[1].split('_')[0]

                # Scan file names in the observed output directory and look for the genome with the matching fitness and uid
                obs_genome_path = None
                for candidate_genome_path in obs_genome_paths:
                    candidate_genome_uid = os.path.split(candidate_genome_path)[1].split('_')[2].split('.')[0]

                    # TODO refactor for more robust test than length of UID being 12 or 13 chars with a leading A char
                    if (exp_genome_fitness in candidate_genome_path) and (len(candidate_genome_uid) == 12):
                        obs_genome_path = candidate_genome_path
                        break

                # Assert we found the matching genome
                assert (obs_genome_path is not None)

                # TODO should shimlist and maglist both be .genome files despite holding different class types?
                # Compare the output file to the expected one
                with open(exp_genome_path, 'rb') as exp_genome_file, \
                     open(obs_genome_path, 'rb') as obs_genome_file:

                    exp_shimlist = pickle.load(exp_genome_file)
                    obs_shimlist = pickle.load(obs_genome_file)

                    assert (type(exp_shimlist) is list)
                    assert (type(obs_shimlist) is list)

                    # Offloads comparison to list::__eq__ method
                    assert exp_shimlist == obs_shimlist


            # Used to perform .h5 tests in next phase
            obs_uids = {}

            # Compare maglists for each genome
            for exp_genome_path in exp_genome_A_paths:

                # Assert the expected genome exists for comparison
                assert os.path.exists(exp_genome_path)

                # TODO reliance on floating point precision in filename might not be stable between versions
                # Extract the fitness and uid from the expected genome file name
                exp_genome_name_parts = os.path.split(exp_genome_path)[1].split('_')
                exp_genome_fitness    = exp_genome_name_parts[0]
                exp_genome_uid        = exp_genome_name_parts[2].split('.')[0]

                # Scan file names in the observed output directory and look for the genome with the matching fitness and uid
                obs_genome_path = None
                for candidate_genome_path in obs_genome_paths:
                    candidate_genome_uid = os.path.split(candidate_genome_path)[1].split('_')[2].split('.')[0]

                    # TODO refactor for more robust test than length of UID being 12 or 13 chars with a leading A char
                    if (exp_genome_fitness in candidate_genome_path) and (len(candidate_genome_uid) == 13):
                        obs_genome_path          = candidate_genome_path
                        obs_uids[exp_genome_uid] = candidate_genome_uid
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

            # Compare the h5 files
            for exp_h5_path in exp_h5_paths:

                # Assert the expected genome exists for comparison
                assert os.path.exists(exp_h5_path)

                exp_h5_uid = os.path.split(exp_h5_path)[1].split('-')[1].split('.')[0]

                # Scan file names in the observed output directory and look for the genome with the matching fitness and uid
                obs_h5_path = None
                for candidate_h5_path in obs_h5_paths:
                    if (obs_uids[exp_h5_uid] in candidate_h5_path):
                        obs_h5_path = candidate_h5_path
                        break

                # Assert we found the matching genome
                assert (obs_h5_path is not None)

                # Compare the output file to the expected one
                with h5py.File(exp_h5_path, 'r') as exp_h5_file, \
                     h5py.File(obs_h5_path, 'r') as obs_h5_file:

                    assert sorted(list(exp_h5_file.keys())) == sorted(list(obs_h5_file.keys()))

                    for dataset in exp_h5_file.keys():

                        exp_data = exp_h5_file.get(dataset)[()]
                        obs_data = obs_h5_file.get(dataset)[()]
                        assert np.allclose(exp_data, obs_data)

        # Use (except + else) instead of (finally) so that output files can be inspected if the test fails
        except Exception as ex: raise ex
        else:

            # Clear any observed output files after running successful test
            shutil.rmtree(obs_path, ignore_errors=True)
            os.makedirs(obs_path)
