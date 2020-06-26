import unittest
import os
import pickle

import shutil
from collections import namedtuple
from tempfile import mkdtemp

import h5py
import numpy as np

from IDSort.src.process_genome import process, MagLists


class ProcessGenomeTest(unittest.TestCase):

    def test_process(self):

        test_json_filepath = 'IDSort/data/test_data/sort/test_cpmu.json'
        test_mag_filepath  = 'IDSort/data/test_data/sort/test_cpmu.mag'
        test_h5_filepath   = 'IDSort/data/test_data/sort/test_cpmu.h5'
        output_dir = mkdtemp()

        options = {
            'analysis'         : True,
            'readable'         : True,
            'id_filename'      : test_json_filepath,
            'magnets_filename' : test_mag_filepath,
            'id_template'      : test_h5_filepath,
            'create_genome'    : False,
            'output_dir'       : output_dir
        }
        options_named = namedtuple("options", options.keys())(*options.values())

        old_genome_filepath = 'IDSort/data/test_data/sort/mpi_runner_output/1.12875826e-08_000_7c51ecd01f73.genome'
        args = [old_genome_filepath]

        new_genome_h5_filename  = os.path.split(old_genome_filepath)[1] + '.h5'
        new_genome_inp_filename = os.path.split(old_genome_filepath)[1] + '.inp'

        new_genome_h5_filepath  = os.path.join(output_dir, new_genome_h5_filename)
        old_genome_h5_filepath  = 'IDSort/data/test_data/sort/process_genome_analyse_output/1.12875826e-08_000_7c51ecd01f73.genome.h5'
        new_genome_inp_filepath = os.path.join(output_dir, new_genome_inp_filename)
        old_genome_inp_filepath = 'IDSort/data/test_data/sort/process_genome_analyse_output/1.12875826e-08_000_7c51ecd01f73.genome.inp'

        try:
            process(options_named, args)

            with h5py.File(new_genome_h5_filepath, 'r') as new_h5_file,  \
                 h5py.File(old_genome_h5_filepath, 'r') as old_h5_file,  \
                          open(new_genome_inp_filepath) as new_inp_file, \
                          open(old_genome_inp_filepath) as old_inp_file:

                for dataset in new_h5_file:
                    if 'perfect' not in dataset:
                        new_data = new_h5_file.get(dataset)[()]
                        old_data = old_h5_file.get(dataset)[()]
                        assert np.allclose(new_data, old_data)

                # Bytewise comparison between ASCII files is safe (within reason, need to be careful with file layout)
                assert new_inp_file.read().strip() == old_inp_file.read().strip()

        finally:
            shutil.rmtree(output_dir)

    def test_process_create_genome(self):

        test_json_filepath = 'IDSort/data/test_data/sort/test_cpmu.json'
        test_mag_filepath  = 'IDSort/data/test_data/sort/test_cpmu.mag'
        test_h5_filepath   = 'IDSort/data/test_data/sort/test_cpmu.h5'
        test_inp_filepath  = 'IDSort/data/test_data/sort/process_genome_analyse_output/1.12875826e-08_000_7c51ecd01f73.genome.inp'
        output_dir = mkdtemp()

        options = {
            'create_genome'    : True,
            'readable'         : False,
            'analysis'         : False,
            'id_filename'      : test_json_filepath,
            'magnets_filename' : test_mag_filepath,
            'id_template'      : test_h5_filepath,
            'output_dir'       : output_dir
        }

        options_named = namedtuple("options", options.keys())(*options.values())
        args = [test_inp_filepath]

        old_genome_filepath = 'IDSort/data/test_data/sort/1.12875826e-08_000_7c51ecd01f73.genome.inp.genome'
        new_genome_filename = os.path.split(test_inp_filepath)[1] + '.genome'
        new_genome_filepath = os.path.join(output_dir, new_genome_filename)

        try:
            process(options_named, args)

            with open(old_genome_filepath, 'rb') as old_genome_file, \
                 open(new_genome_filepath, 'rb') as new_genome_file:

                old_maglist = pickle.load(old_genome_file)
                new_maglist = pickle.load(new_genome_file)

            assert (type(old_maglist) is MagLists)
            assert (type(new_maglist) is MagLists)

            # Offloads comparison to MagLists::__eq__ method
            assert old_maglist == new_maglist

        finally:
            shutil.rmtree(output_dir)
