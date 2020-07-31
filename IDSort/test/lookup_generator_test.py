import unittest, os, shutil
from collections import namedtuple

import subprocess

import h5py
import numpy as np

from ..src.lookup_generator import process


class LookupGeneratorTest(unittest.TestCase):

    def test_process_hybrid_symmetric(self):
        # inp == Inputs
        # exp == Expected Outputs
        # obs == Observed Outputs

        data_path = 'IDSort/test/data/lookup_generator_test/test_process_hybrid_symmetric'
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
            'verbose' : 4,
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

    def test_process_hybrid_symmetric_shim(self):
        # inp == Inputs
        # exp == Expected Outputs
        # obs == Observed Outputs

        data_path = 'IDSort/test/data/lookup_generator_test/test_process_hybrid_symmetric_shim'
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
            'verbose' : 4,
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

    def test_process_ppm_antisymmetric(self):
        # inp == Inputs
        # exp == Expected Outputs
        # obs == Observed Outputs

        data_path = 'IDSort/test/data/lookup_generator_test/test_process_ppm_antisymmetric'
        inp_path  = os.path.join(data_path, 'inputs')
        exp_path  = os.path.join(data_path, 'expected_outputs')
        obs_path  = os.path.join(data_path, 'observed_outputs')

        # Prepare input file paths
        inp_json_path = os.path.join(inp_path, 'test_antippm.json')

        # Prepare expected output file paths
        exp_h5_path = os.path.join(exp_path, 'test_antippm.h5')

        # Prepare observed output file paths
        obs_h5_path = os.path.join(obs_path, 'test_antippm.h5')

        # Always clear any observed output files before running test
        shutil.rmtree(obs_path, ignore_errors=True)
        os.makedirs(obs_path)

        # TODO refactor parameters for process function to take json file as named param
        # Prepare parameters for process function
        options = {
            'verbose' : 4,
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

    def test_process_apple_symmetric(self):
        # inp == Inputs
        # exp == Expected Outputs
        # obs == Observed Outputs

        data_path = 'IDSort/test/data/lookup_generator_test/test_process_apple_symmetric'
        inp_path  = os.path.join(data_path, 'inputs')
        exp_path  = os.path.join(data_path, 'expected_outputs')
        obs_path  = os.path.join(data_path, 'observed_outputs')

        # Prepare input file paths
        inp_json_path = os.path.join(inp_path, 'test_apple.json')

        # Prepare expected output file paths
        exp_h5_path = os.path.join(exp_path, 'test_apple.h5')

        # Expected file test_apple.h5 is 128MB which is larger than Github individual file limit of 100MB
        # The file is versioned as a shared .tar file in 32MB chunks which need to be merged and decompressed
        subprocess.Popen('cat test_apple.h5.tar.* | tar -x', cwd=os.path.abspath(exp_path), shell=True).communicate()
        assert os.path.exists(exp_h5_path)

        # Prepare observed output file paths
        obs_h5_path = os.path.join(obs_path, 'test_apple.h5')

        # Always clear any observed output files before running test
        shutil.rmtree(obs_path, ignore_errors=True)
        os.makedirs(obs_path)

        # TODO refactor parameters for process function to take json file as named param
        # Prepare parameters for process function
        options = {
            'verbose' : 4,
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

        # Remove the extracted expected file so it is not captured by version control
        os.remove(exp_h5_path)
        assert not os.path.exists(exp_h5_path)
