import unittest
import numpy as np
import h5py
from tempfile import NamedTemporaryFile
from collections import namedtuple
from IDSort.src.lookup_generator import process


class LookupGeneratorTest(unittest.TestCase):

    def test_process(self):

        options = {
            'periods': 113,
            'random': False
        }

        options_named = namedtuple("options", options.keys())(*options.values())
        test_json_filepath = 'IDSort/data/test_data/test_cpmu.json'
        test_h5_filepath = 'IDSort/data/test_data/test_cpmu.h5'

        with h5py.File(test_h5_filepath, 'r') as old_h5_file, \
                NamedTemporaryFile() as mock_h5_file:
            process(options, [test_json_filepath, mock_h5_file])
            new_h5_file = h5py.File(mock_h5_file.name)
            for dataset in new_h5_file:
                new_data = new_h5_file.get(dataset).value
                old_data = old_h5_file.get(dataset).value
                assert np.allclose(new_data, old_data)

    def test_process_shim(self):

        options = {
            'periods': 113,
            'random': True
        }

        options_named = namedtuple("options", options.keys())(*options.values())
        test_json_shim_filepath = 'IDSort/data/test_data/test_cpmu_shim.json'
        test_h5_shim_filepath = 'IDSort/data/test_data/test_cpmu_shim.h5'

        with h5py.File(test_h5_shim_filepath, 'r') as old_h5_shim_file, \
                NamedTemporaryFile() as mock_h5_shim_file:
            process(options_named, [test_json_shim_filepath, mock_h5_shim_file.name])
            new_h5_shim_file = h5py.File(mock_h5_shim_file.name)
            for dataset in new_h5_shim_file:
                new_data = new_h5_shim_file.get(dataset).value
                old_data = old_h5_shim_file.get(dataset).value
                assert np.allclose(new_data, old_data)
