import unittest
import shutil
import os
import pickle
import tempfile
from collections import namedtuple

from IDSort.src.mpi_runner import process, MagLists


class MpiRunnerTest(unittest.TestCase):

    def test_process(self):

        test_json_filepath = 'IDSort/data/test_data/sort/test_cpmu.json'
        test_mag_filepath  = 'IDSort/data/test_data/sort/test_cpmu.mag'
        test_h5_filepath   = 'IDSort/data/test_data/sort/test_cpmu.h5'

        options = {
            'iterations'       : 3,
            'id_filename'      : test_json_filepath,
            'magnets_filename' : test_mag_filepath,
            'lookup_filename'  : test_h5_filepath,
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
        new_genome_dir = tempfile.mkdtemp()
        args           = [new_genome_dir]

        test_genome_filepaths = [
            'IDSort/data/test_data/sort/mpi_runner_output/1.12875826e-08_000_7c51ecd01f73.genome',
            'IDSort/data/test_data/sort/mpi_runner_output/1.49788342e-08_000_b6059e1c0884.genome',
            'IDSort/data/test_data/sort/mpi_runner_output/1.81441854e-08_000_645a52b2bb2d.genome',
            'IDSort/data/test_data/sort/mpi_runner_output/4.05007630e-08_000_47a4f43ecf86.genome'
        ]

        try:
            process(options_named, args)
            new_genome_filenames = os.listdir(new_genome_dir)

            assert len(new_genome_filenames) > 0

            for new_genome_filename in new_genome_filenames:
                genome_to_compare_with = None
                genome_fitness = new_genome_filename.split('_')[0]
                for test_genome_filepath in test_genome_filepaths:
                    if genome_fitness in test_genome_filepath:
                        genome_to_compare_with = test_genome_filepath

                assert genome_to_compare_with is not None

                with open(os.path.join(new_genome_dir, new_genome_filename), 'rb') as new_genome_file, \
                                                open(genome_to_compare_with, 'rb') as old_genome_file:

                    old_maglist = pickle.load(old_genome_file)
                    new_maglist = pickle.load(new_genome_file)

                assert (type(old_maglist) is MagLists)
                assert (type(new_maglist) is MagLists)

                # Offloads comparison to MagLists::__eq__ method
                assert old_maglist == new_maglist

        finally:
            shutil.rmtree(new_genome_dir)

    def test_process_initial_population(self):

        test_json_filepath = 'IDSort/data/test_data/sort/test_cpmu.json'
        test_mag_filepath  = 'IDSort/data/test_data/sort/test_cpmu.mag'
        test_h5_filepath   = 'IDSort/data/test_data/sort/test_cpmu.h5'
        options = {
            'iterations'       : 3,
            'id_filename'      : test_json_filepath,
            'magnets_filename' : test_mag_filepath,
            'lookup_filename'  : test_h5_filepath,
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
        genome_dir    = 'IDSort/data/test_data/sort/mpi_runner_output'
        args          = [genome_dir]

        test_genome_filepaths = [
            'IDSort/data/test_data/sort/mpi_runner_initial_population/1.09170425e-08_000_88d39698a4f7.genome',
            'IDSort/data/test_data/sort/mpi_runner_initial_population/6.42786056e-09_000_aaf866db3206.genome',
            'IDSort/data/test_data/sort/mpi_runner_initial_population/7.03009938e-09_000_a90b37ecedb9.genome',
            'IDSort/data/test_data/sort/mpi_runner_initial_population/7.06840992e-09_000_a12a86932596.genome'
        ]

        try:
            process(options_named, args)

            genome_filenames = os.listdir(genome_dir)

            assert len(genome_filenames) > 0

            new_population = []

            for test_genome_filepath in test_genome_filepaths:
                genome_to_compare_with = None
                test_genome_filename = os.path.split(test_genome_filepath)[1]
                test_genome_split = test_genome_filename.split('_')
                test_genome_fitness_and_age = '_'.join(test_genome_split[0:2])

                for genome_filename in genome_filenames:
                    if test_genome_fitness_and_age in genome_filename:
                        genome_to_compare_with = genome_filename
                        new_population.append(genome_filename)
                        break

                assert genome_to_compare_with is not None

                with open(os.path.join(genome_dir, genome_to_compare_with), 'rb') as new_genome_file, \
                                                 open(test_genome_filepath, 'rb') as old_genome_file:

                    old_maglist = pickle.load(old_genome_file)
                    new_maglist = pickle.load(new_genome_file)

                assert (type(old_maglist) is MagLists)
                assert (type(new_maglist) is MagLists)

                # Offloads comparison to MagLists::__eq__ method
                assert old_maglist == new_maglist

        finally:

            for genome_filename in new_population:
                os.remove(os.path.join(genome_dir, genome_filename))
