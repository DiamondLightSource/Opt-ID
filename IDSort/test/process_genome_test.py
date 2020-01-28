import unittest
import os
from collections import namedtuple

import h5py
import numpy as np

from IDSort.src.process_genome import process


class ProcessGenomeTest(unittest.TestCase):

    def test_process(self):

        test_json_filepath = 'IDSort/data/test_data/sort/test_cpmu.json'
        test_mag_filepath = 'IDSort/data/test_data/sort/test_cpmu.mag'
        test_h5_filepath = 'IDSort/data/test_data/sort/test_cpmu.h5'

        options = {
            'analysis': True,
            'readable': True,
            'id_filename': test_json_filepath,
            'magnets_filename': test_mag_filepath,
            'id_template': test_h5_filepath,
            'create_genome': False
        }

        options_named = namedtuple("options", options.keys())(*options.values())
        old_genome_filepath = 'IDSort/data/test_data/sort/mpi_runner_output/1.12875826e-08_000_7c51ecd01f73.genome'
        args = [old_genome_filepath]

        new_genome_h5_filename = os.path.split(old_genome_filepath)[1] + '.h5'
        new_genome_inp_filename = os.path.split(old_genome_filepath)[1] + '.inp'

        new_genome_h5_filepath = os.path.join(os.getcwd(), new_genome_h5_filename)
        old_genome_h5_filepath = 'IDSort/data/test_data/sort/process_genome_analyse_output/1.12875826e-08_000_7c51ecd01f73.genome.h5'
        new_genome_inp_filepath = os.path.join(os.getcwd(), new_genome_inp_filename)
        old_genome_inp_filepath = 'IDSort/data/test_data/sort/process_genome_analyse_output/1.12875826e-08_000_7c51ecd01f73.genome.inp'

        try:
            process(options_named, args)
            with h5py.File(new_genome_h5_filepath, 'r') as new_h5_file, \
                    h5py.File(old_genome_h5_filepath, 'r') as old_h5_file, \
                    open(new_genome_inp_filepath) as new_inp_file, \
                    open(old_genome_inp_filepath) as old_inp_file:

                for dataset in new_h5_file:
                    if 'perfect' not in dataset:
                        new_data = new_h5_file.get(dataset).value
                        old_data = old_h5_file.get(dataset).value
                        assert np.allclose(new_data, old_data)

                assert new_inp_file.read() == old_inp_file.read()

        finally:
            os.remove(new_genome_h5_filepath)
            os.remove(new_genome_inp_filepath)

    def test_process_create_genome(self):

        test_json_filepath = 'IDSort/data/test_data/sort/test_cpmu.json'
        test_mag_filepath = 'IDSort/data/test_data/sort/test_cpmu.mag'
        test_h5_filepath = 'IDSort/data/test_data/sort/test_cpmu.h5'
        test_inp_filepath = 'IDSort/data/test_data/sort/process_genome_analyse_output/1.07788212e-08_000_c0833a96b82c.genome.inp'

        options = {
            'create_genome': True,
            'readable': False,
            'analysis': False,
            'id_filename': test_json_filepath,
            'magnets_filename': test_mag_filepath,
            'id_template': test_h5_filepath
        }

        options_named = namedtuple("options", options.keys())(*options.values())
        args = [test_inp_filepath]

        old_genome_filepath = 'IDSort/data/test_data/sort/1.07788212e-08_000_c0833a96b82c.genome.inp.genome'
        new_genome_filename = os.path.split(test_inp_filepath)[1] + '.genome'
        new_genome_filepath = os.path.join(os.getcwd(), new_genome_filename)

        try:
            process(options_named, args)
            with open(old_genome_filepath) as old_genome_file, \
                    open(new_genome_filepath) as new_genome_file:
                assert new_genome_file.read() == old_genome_file.read()
        finally:
            os.remove(new_genome_filepath)
