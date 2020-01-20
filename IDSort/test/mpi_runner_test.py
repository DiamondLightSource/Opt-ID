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
            'IDSort/data/test_data/sort/1.07788212e-08_000_c0833a96b82c.genome',
            'IDSort/data/test_data/sort/1.13540850e-08_000_98451f1c78c2.genome',
            'IDSort/data/test_data/sort/1.49284583e-08_000_92fab60b32fe.genome',
            'IDSort/data/test_data/sort/1.93191576e-08_000_d67a4cf9dfac.genome'
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
