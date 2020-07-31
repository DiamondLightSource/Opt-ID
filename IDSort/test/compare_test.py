import unittest, os, shutil
from collections import namedtuple

from ..src.compare import process


class CompareTest(unittest.TestCase):

    def test_process(self):
        # inp == Inputs
        # exp == Expected Outputs
        # obs == Observed Outputs

        data_path = 'IDSort/test/data/compare_test/test_process'
        inp_path  = os.path.join(data_path, 'inputs')
        exp_path  = os.path.join(data_path, 'expected_outputs')
        obs_path  = os.path.join(data_path, 'observed_outputs')

        # Prepare input file paths
        inp_original_genome_path = os.path.join(inp_path, 'sort/1.12875826e-08_000_7c51ecd01f73.genome')
        inp_shimmed_genome_path  = os.path.join(inp_path, 'shim/1.20847271e-07_000_A85a13cc425d0.genome')

        # Prepare expected output file paths
        exp_shim_comparison_path = os.path.join(exp_path, 'test_shim.txt')

        # Prepare observed output file paths
        obs_shim_comparison_path = os.path.join(obs_path, 'test_shim.txt')

        # Always clear any observed output files before running test
        shutil.rmtree(obs_path, ignore_errors=True)
        os.makedirs(obs_path)

        # TODO refactor parameters for process function to use named tuple
        # Prepare parameters for process function
        options = {
            'verbose' : 4,
        }
        options_named = namedtuple("options", options.keys())(*options.values())
        args = [
            inp_original_genome_path,
            inp_shimmed_genome_path,
            obs_shim_comparison_path
        ]

        try:

            # Execute the function under test
            process(options_named, args)

            # Compare the output file to the expected one
            with open(exp_shim_comparison_path, 'r') as exp_shim_file, \
                 open(obs_shim_comparison_path, 'r') as obs_shim_file:

                # TODO make comparison more robust based on values not bytes (pandas .csv instead of manual .txt ?)
                # Bytewise file comparison works for now for raw text files
                assert exp_shim_file.read().strip() == obs_shim_file.read().strip()

        # Use (except + else) instead of (finally) so that output files can be inspected if the test fails
        except Exception as ex: raise ex
        else:

            # Clear any observed output files after running successful test
            shutil.rmtree(obs_path, ignore_errors=True)
            os.makedirs(obs_path)
