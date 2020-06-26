import os, shutil
import unittest
import numpy as np
import h5py
from collections import namedtuple
from IDSort.src.lookup_generator import process


class LookupGeneratorTest(unittest.TestCase):

    def test_process(self):
        # inp == Inputs
        # exp == Expected Outputs
        # obs == Observed Outputs

        data_path = 'IDSort/test/data/lookup_generator_test/test_process'
        inp_path  = os.path.join(data_path, 'inputs')
        exp_path  = os.path.join(data_path, 'expected_outputs')
        obs_path  = os.path.join(data_path, 'observed_outputs')

        # Prepare input file paths
        inp_json_path = os.path.join(inp_path, 'test_cpmu.json')

        # Prepare expected output file paths
        exp_h5_path = os.path.join(exp_path, 'test_cpmu.h5')

        # Prepare observed output file paths
        obs_h5_path = os.path.join(obs_path, 'test_cpmu.h5')

        # Always clear any observed output files before running test
        shutil.rmtree(obs_path, ignore_errors=True)
        os.makedirs(obs_path)

        # TODO refactor parameters for process function to take json file as named param
        # Prepare parameters for process function
        options = {
            'periods' : 113,
            'random'  : False
        }
        options_named = namedtuple("options", options.keys())(*options.values())
        args = [
            inp_json_path,
            obs_h5_path
        ]

        try:

            # Execute the function under test
            process(options_named, args)

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

    def test_process_shim(self):
        # inp == Inputs
        # exp == Expected Outputs
        # obs == Observed Outputs

        data_path = 'IDSort/test/data/lookup_generator_test/test_process_shim'
        inp_path  = os.path.join(data_path, 'inputs')
        exp_path  = os.path.join(data_path, 'expected_outputs')
        obs_path  = os.path.join(data_path, 'observed_outputs')

        # Prepare input file paths
        inp_json_path = os.path.join(inp_path, 'test_cpmu_shim.json')

        # Prepare expected output file paths
        exp_h5_path = os.path.join(exp_path, 'test_cpmu_shim.h5')

        # Prepare observed output file paths
        obs_h5_path = os.path.join(obs_path, 'test_cpmu_shim.h5')

        # Always clear any observed output files before running test
        shutil.rmtree(obs_path, ignore_errors=True)
        os.makedirs(obs_path)

        # TODO refactor parameters for process function to take json file as named param
        # Prepare parameters for process function
        options = {
            'periods' : 113,
            'random'  : True
        }
        options_named = namedtuple("options", options.keys())(*options.values())
        args = [
            inp_json_path,
            obs_h5_path
        ]

        try:

            # Execute the function under test
            process(options_named, args)

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
