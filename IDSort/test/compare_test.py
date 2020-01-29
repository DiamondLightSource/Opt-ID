import os
import unittest
from collections import namedtuple

from IDSort.src.compare import process


class CompareTest(unittest.TestCase):

    def test_process(self):

        test_original_genome_filepath = 'IDSort/data/test_data/sort/mpi_runner_output/1.12875826e-08_000_7c51ecd01f73.genome'
        test_shimmed_genome_filepath = 'IDSort/data/test_data/shim/1.20847271e-07_000_A85a13cc425d0.genome'
        test_shim_filepath =  'IDSort/data/test_data/shim/test_shim.txt'
        new_shim_filename = 'shim'
        options = {}
        options_named = namedtuple("options", options.keys())(*options.values())
        args = [
            test_original_genome_filepath,
            test_shimmed_genome_filepath,
            new_shim_filename
        ]

        try:
            process(options_named, args)
            with open(test_shim_filepath) as old_shim_file, \
                    open(new_shim_filename + '.txt') as new_shim_file:
                assert new_shim_file.read() == old_shim_file.read()
        finally:
            os.remove(new_shim_filename + '.txt')
