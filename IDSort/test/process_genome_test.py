import os, shutil
import unittest
import pickle
from collections import namedtuple

import h5py
import numpy as np

from IDSort.src.process_genome import process, MagLists


class ProcessGenomeTest(unittest.TestCase):

    def test_process(self):
        # inp == Inputs
        # exp == Expected Outputs
        # obs == Observed Outputs

        data_path = 'IDSort/test/data/process_genome_test/test_process'
        inp_path  = os.path.join(data_path, 'inputs')
        exp_path  = os.path.join(data_path, 'expected_outputs')
        obs_path  = os.path.join(data_path, 'observed_outputs')

        # Base name for test genome file
        base_genome_name = '1.12875826e-08_000_7c51ecd01f73.genome'

        # Prepare input file paths
        inp_json_path   = os.path.join(inp_path, 'test_cpmu.json')
        inp_mag_path    = os.path.join(inp_path, 'test_cpmu.mag')
        inp_h5_path     = os.path.join(inp_path, 'test_cpmu.h5')
        inp_genome_path = os.path.join(inp_path, base_genome_name)

        # Prepare expected output file paths
        exp_h5_path  = os.path.join(exp_path, base_genome_name + '.h5')
        exp_inp_path = os.path.join(exp_path, base_genome_name + '.inp')

        # Prepare observed output file paths
        obs_h5_path  = os.path.join(obs_path, base_genome_name + '.h5')
        obs_inp_path = os.path.join(obs_path, base_genome_name + '.inp')

        # Always clear any observed output files before running test
        shutil.rmtree(obs_path, ignore_errors=True)
        os.makedirs(obs_path)

        # TODO refactor to allow output file names to be specified as named parameters
        # Prepare parameters for process function
        options = {
            'analysis'         : True,
            'readable'         : True,
            'id_filename'      : inp_json_path,
            'magnets_filename' : inp_mag_path,
            'id_template'      : inp_h5_path,
            'create_genome'    : False,
            'output_dir'       : obs_path
        }
        options_named = namedtuple("options", options.keys())(*options.values())
        args = [
            inp_genome_path
        ]

        try:

            # Execute the function under test
            process(options_named, args)

            # Compare the output file to the expected one
            with h5py.File(exp_h5_path, 'r') as exp_h5_file, \
                 h5py.File(obs_h5_path, 'r') as obs_h5_file:

                assert sorted(list(exp_h5_file.keys())) == sorted(list(obs_h5_file.keys()))

                for dataset in exp_h5_file.keys():
                    if 'perfect' not in dataset:

                        exp_data = exp_h5_file.get(dataset)[()]
                        obs_data = obs_h5_file.get(dataset)[()]
                        assert np.allclose(exp_data, obs_data)

            # Compare the output file to the expected one
            with open(exp_inp_path, 'r') as exp_inp_file, \
                 open(obs_inp_path, 'r') as obs_inp_file:

                # Bytewise comparison between ASCII files is safe (within reason, need to be careful with file layout)
                assert exp_inp_file.read().strip() == obs_inp_file.read().strip()

        # Use (except + else) instead of (finally) so that output files can be inspected if the test fails
        except Exception as ex: raise ex
        else:

            # Clear any observed output files after running successful test
            shutil.rmtree(obs_path, ignore_errors=True)
            os.makedirs(obs_path)

    def test_process_create_genome(self):
        # inp == Inputs
        # exp == Expected Outputs
        # obs == Observed Outputs

        data_path = 'IDSort/test/data/process_genome_test/test_process_create_genome'
        inp_path  = os.path.join(data_path, 'inputs')
        exp_path  = os.path.join(data_path, 'expected_outputs')
        obs_path  = os.path.join(data_path, 'observed_outputs')

        # Base name for test genome file
        base_inp_name = '1.12875826e-08_000_7c51ecd01f73.genome.inp'

        # Prepare input file paths
        inp_json_path = os.path.join(inp_path, 'test_cpmu.json')
        inp_mag_path  = os.path.join(inp_path, 'test_cpmu.mag')
        inp_h5_path   = os.path.join(inp_path, 'test_cpmu.h5')
        inp_inp_path  = os.path.join(inp_path, base_inp_name)

        # Prepare expected output file paths
        exp_genome_path = os.path.join(exp_path, base_inp_name + '.genome')

        # Prepare observed output file paths
        obs_genome_path = os.path.join(obs_path, base_inp_name + '.genome')

        # Always clear any observed output files before running test
        shutil.rmtree(obs_path, ignore_errors=True)
        os.makedirs(obs_path)

        # TODO refactor to allow output file names to be specified as named parameters
        # Prepare parameters for process function
        options = {
            'create_genome'    : True,
            'readable'         : False,
            'analysis'         : False,
            'id_filename'      : inp_json_path,
            'magnets_filename' : inp_mag_path,
            'id_template'      : inp_h5_path,
            'output_dir'       : obs_path
        }
        options_named = namedtuple("options", options.keys())(*options.values())
        args = [
            inp_inp_path
        ]

        try:

            # Execute the function under test
            process(options_named, args)

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
