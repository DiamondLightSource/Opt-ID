import unittest
import shutil
import os
from tempfile import mkdtemp
from collections import namedtuple
from IDSort.src.mpi_runner import process


class MpiRunnerTest(unittest.TestCase):

    def test_process(self):

        test_json_filepath = 'IDSort/data/test_data/sort/test_cpmu.json'
        test_mag_filepath = 'IDSort/data/test_data/sort/test_cpmu.mag'
        test_h5_filepath = 'IDSort/data/test_data/sort/test_cpmu.h5'
        options = {
            'iterations': 3,
            'id_filename': test_json_filepath,
            'magnets_filename': test_mag_filepath,
            'lookup_filename': test_h5_filepath,
            'setup': 24,
            'c': 1,
            'e': 0.0,
            'restart': False,
            'max_age': 10,
            'scale': 10.0,
            'singlethreaded': True,
            'seed': True,
            'seed_value': 30
        }

        options_named = namedtuple("options", options.keys())(*options.values())
        new_genome_dir = mkdtemp()
        args = [new_genome_dir]

        test_genome_filepaths = [
            'IDSort/data/test_data/sort/mpi_runner_output/1.07788212e-08_000_c0833a96b82c.genome',
            'IDSort/data/test_data/sort/mpi_runner_output/1.13540850e-08_000_98451f1c78c2.genome',
            'IDSort/data/test_data/sort/mpi_runner_output/1.49284583e-08_000_92fab60b32fe.genome',
            'IDSort/data/test_data/sort/mpi_runner_output/1.93191576e-08_000_d67a4cf9dfac.genome'
        ]

        try:
            process(options_named, args)
            new_genome_filenames = os.listdir(new_genome_dir)

            for new_genome_filename in new_genome_filenames:
                genome_to_compare_with = None
                genome_fitness = new_genome_filename.split('_')[0]
                for test_genome_filepath in test_genome_filepaths:
                    if genome_fitness in test_genome_filepath:
                        genome_to_compare_with = test_genome_filepath

                assert genome_to_compare_with is not None

                with open(os.path.join(new_genome_dir, new_genome_filename)) as new_genome_file, \
                        open(genome_to_compare_with) as test_genome_file:
                    assert new_genome_file.read() == test_genome_file.read()

        finally:
            shutil.rmtree(new_genome_dir)

    def test_process_initial_population(self):

        test_json_filepath = 'IDSort/data/test_data/sort/test_cpmu.json'
        test_mag_filepath = 'IDSort/data/test_data/sort/test_cpmu.mag'
        test_h5_filepath = 'IDSort/data/test_data/sort/test_cpmu.h5'
        options = {
            'iterations': 3,
            'id_filename': test_json_filepath,
            'magnets_filename': test_mag_filepath,
            'lookup_filename': test_h5_filepath,
            'setup': 24,
            'c': 1,
            'e': 0.0,
            'restart': True,
            'max_age': 10,
            'scale': 10.0,
            'singlethreaded': True,
            'seed': True,
            'seed_value': 30
        }

        options_named = namedtuple("options", options.keys())(*options.values())
        genome_dir = 'IDSort/data/test_data/sort/mpi_runner_output'
        args = [genome_dir]

        test_genome_filepaths = [
            'IDSort/data/test_data/sort/mpi_runner_initial_population/1.07788212e-08_001_c0833a96b82c.genome',
            'IDSort/data/test_data/sort/mpi_runner_initial_population/8.62681680e-09_000_5ffd95460060.genome',
            'IDSort/data/test_data/sort/mpi_runner_initial_population/8.86225773e-09_000_910c79ca1fc4.genome',
            'IDSort/data/test_data/sort/mpi_runner_initial_population/9.90050079e-09_000_5c3b9f36eca8.genome'
        ]

        try:
            process(options_named, args)
            genome_filenames = os.listdir(genome_dir)
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

                with open(os.path.join(genome_dir, genome_to_compare_with)) as new_genome_file, \
                        open(test_genome_filepath) as test_genome_file:
                    assert new_genome_file.read() == test_genome_file.read()

        finally:
            for genome_filename in new_population:
                os.remove(os.path.join(genome_dir, genome_filename))
