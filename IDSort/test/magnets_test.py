import unittest
from tempfile import NamedTemporaryFile
from collections import namedtuple
from IDSort.src.magnets import process


class MagnetsTest(unittest.TestCase):

    def test_process(self):

        options = {
            'hmags': 'IDSort/data/I03H.sim',
            'hemags': 'IDSort/data/I03HEC.sim',
            'htmags': 'IDSort/data/I03HTE.sim',
            'vmags': None,
            'vemags': None
        }

        options_named = namedtuple("options", options.keys())(*options.values())
        test_mag_filepath = 'IDSort/data/test_data/test_cpmu.mag'

        with open(test_mag_filepath) as old_mag_file, \
                NamedTemporaryFile() as new_mag_file:
            process(options_named, [new_mag_file.name])
            assert new_mag_file.read() == old_mag_file.read()

    def test_process_shim(self):

        options = {
            'hmags': 'IDSort/data/I03HH.sim',
            'hemags': 'IDSort/data/I03HEA.sim',
            'htmags': 'IDSort/data/I03HTD.sim',
            'vmags': None,
            'vemags': None
        }

        options_named = namedtuple("options", options.keys())(*options.values())
        test_mag_shim_filepath = 'IDSort/data/test_data/test_cpmu_shim.mag'

        with open(test_mag_shim_filepath) as old_mag_shim_file, \
                NamedTemporaryFile() as new_mag_shim_file:
            process(options_named, [new_mag_shim_file.name])
            assert new_mag_shim_file.read() == old_mag_shim_file.read()
