import unittest, os, shutil
from collections import namedtuple

import json

from ..src.id_setup import process


class IDSetupTest(unittest.TestCase):

    def test_process_hybrid_symmetric(self):
        # exp == Expected Outputs
        # obs == Observed Outputs

        data_path = 'IDSort/test/data/id_setup_test/test_process_hybrid_symmetric'
        exp_path  = os.path.join(data_path, 'expected_outputs')
        obs_path  = os.path.join(data_path, 'observed_outputs')

        # Prepare expected output file paths
        exp_json_path = os.path.join(exp_path, 'test_cpmu.json')

        # Prepare observed output file paths
        obs_json_path = os.path.join(obs_path, 'test_cpmu.json')

        # Always clear any observed output files before running test
        shutil.rmtree(obs_path, ignore_errors=True)
        os.makedirs(obs_path)

        # Prepare parameters for process function
        options = {
            'periods'           : 113,
            'fullmagdims'       : (50., 30., 5.76),
            'hemagdims'         : (50., 30., 3.48),
            'htmagdims'         : (50., 30., 0.87),
            'poledims'          : (30., 26., 2.96),
            'interstice'        : 0.04,
            'gap'               : 5.1,
            'type'              : 'Hybrid_Symmetric',
            'name'              : 'test_cpmu',
            'x'                 : (-2.0, 2.1, 2.5),
            'z'                 : (-0.0, 0.1, 0.1),
            'steps'             : 1,
            'endgapsym'         : 5.0,
            'terminalgapsymhyb' : 5.0
        }
        options_named = namedtuple("options", options.keys())(*options.values())

        try:

            # Execute the function under test
            process(options_named, [obs_json_path])

            # Compare the output file to the expected one
            with open(exp_json_path, 'r') as exp_json_file, \
                 open(obs_json_path, 'r') as obs_json_file:

                exp_json = json.load(exp_json_file)
                obs_json = json.load(obs_json_file)

                # dict::__eq__ works for json loaded dictionaries
                assert exp_json == obs_json

        # Use (except + else) instead of (finally) so that output files can be inspected if the test fails
        except Exception as ex: raise ex
        else:

            # Clear any observed output files after running successful test
            shutil.rmtree(obs_path, ignore_errors=True)
            os.makedirs(obs_path)

    def test_process_hybrid_symmetric_shim(self):
        # exp == Expected Outputs
        # obs == Observed Outputs

        data_path = 'IDSort/test/data/id_setup_test/test_process_hybrid_symmetric_shim'
        exp_path  = os.path.join(data_path, 'expected_outputs')
        obs_path  = os.path.join(data_path, 'observed_outputs')

        # Prepare expected output file paths
        exp_json_path = os.path.join(exp_path, 'test_cpmu_shim.json')

        # Prepare observed output file paths
        obs_json_path = os.path.join(obs_path, 'test_cpmu_shim.json')

        # Always clear any observed output files before running test
        shutil.rmtree(obs_path, ignore_errors=True)
        os.makedirs(obs_path)

        # TODO JW find out what makes this a shim id_setup as opposed to a sort id_setup
        # Prepare parameters for process function
        options = {
            'periods'           : 113,
            'fullmagdims'       : (50., 30., 5.76),
            'hemagdims'         : (50., 30., 4.00),
            'htmagdims'         : (50., 30., 1.13),
            'poledims'          : (30., 23., 2.95),
            'interstice'        : 0.0625,
            'gap'               : 5.6,
            'type'              : 'Hybrid_Symmetric',
            'name'              : 'test_cpmu_shim',
            'x'                 : (0, 0.1, 1),
            'z'                 : (0, 0.1, 1),
            'steps'             : 1,
            'endgapsym'         : 3.0,
            'terminalgapsymhyb' : 3.0
        }
        options_named = namedtuple("options", options.keys())(*options.values())

        try:

            # Execute the function under test
            process(options_named, [obs_json_path])

            # Compare the output file to the expected one
            with open(exp_json_path, 'r') as exp_json_file, \
                 open(obs_json_path, 'r') as obs_json_file:

                exp_json = json.load(exp_json_file)
                obs_json = json.load(obs_json_file)

                # dict::__eq__ works for json loaded dictionaries
                assert exp_json == obs_json

        # Use (except + else) instead of (finally) so that output files can be inspected if the test fails
        except Exception as ex: raise ex
        else:

            # Clear any observed output files after running successful test
            shutil.rmtree(obs_path, ignore_errors=True)
            os.makedirs(obs_path)
