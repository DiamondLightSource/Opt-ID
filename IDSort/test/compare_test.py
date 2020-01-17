import os
import unittest
from collections import namedtuple

from IDSort.src.compare import process


class CompareTest(unittest.TestCase):

    def test_process(self):

        test_original_genome_filepath = 'IDSort/data/test_data/1.07788212e-08_000_c0833a96b82c.genome'
        test_shimmed_genome_filepath = 'IDSort/data/test_data/1.21718320e-07_000_A5bd3ebe937ee.genome'
        test_shim_filepath =  'IDSort/data/test_data/test_shim.txt'
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
