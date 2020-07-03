import unittest, os, shutil
from collections import namedtuple

from ..src.magnets import process, Magnets


class MagnetsTest(unittest.TestCase):

    def test_process(self):
        # inp == Inputs
        # exp == Expected Outputs
        # obs == Observed Outputs

        data_path = 'IDSort/test/data/magnets_test/test_process'
        inp_path  = os.path.join(data_path, 'inputs')
        exp_path  = os.path.join(data_path, 'expected_outputs')
        obs_path  = os.path.join(data_path, 'observed_outputs')

        # Prepare input file paths
        inp_hmags_path  = os.path.join(inp_path, 'I03H.sim')
        inp_hemags_path = os.path.join(inp_path, 'I03HEC.sim')
        inp_htmags_path = os.path.join(inp_path, 'I03HTE.sim')

        # Prepare expected output file paths
        exp_mag_path = os.path.join(exp_path, 'test_cpmu.mag')

        # Prepare observed output file paths
        obs_mag_path = os.path.join(obs_path, 'test_cpmu.mag')

        # Always clear any observed output files before running test
        shutil.rmtree(obs_path, ignore_errors=True)
        os.makedirs(obs_path)

        # TODO refactor output file path to use named tuple
        # Prepare parameters for process function
        options = {
            'hmags'  : inp_hmags_path,
            'hemags' : inp_hemags_path,
            'htmags' : inp_htmags_path,
            'vmags'  : None,
            'vemags' : None,
        }
        options_named = namedtuple("options", options.keys())(**options)
        args = [
            obs_mag_path
        ]

        try:

            # Execute the process function on the corresponding .sim files (ascii named field vectors)
            # to generate a new .mag file (python3 generated Pickle)
            process(options_named, args)

            # Load the expected values from the .mag file (python2 generated cPickle)
            exp_mag = Magnets()
            exp_mag.load(exp_mag_path)

            obs_mag = Magnets()
            obs_mag.load(obs_mag_path)

            # Offloads comparison to Magents::__eq__ method
            assert exp_mag == obs_mag

        # Use (except + else) instead of (finally) so that output files can be inspected if the test fails
        except Exception as ex: raise ex
        else:

            # Clear any observed output files after running successful test
            shutil.rmtree(obs_path, ignore_errors=True)
            os.makedirs(obs_path)
