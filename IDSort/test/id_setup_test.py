import unittest
import json
from tempfile import NamedTemporaryFile
from collections import namedtuple
from IDSort.src.id_setup import process


class IDSetupTest(unittest.TestCase):

    def test_process_hybrid_symmetric(self):

        options = {
            'periods': 113,
            'fullmagdims': (50., 30., 5.76),
            'hemagdims': (50., 30., 3.48),
            'htmagdims': (50., 30., 0.87),
            'poledims': (30., 26., 2.96),
            'interstice': 0.04,
            'gap': 5.1,
            'type': 'Hybrid_Symmetric',
            'name': 'test_cpmu',
            'x': (-2.0, 2.1, 2.5),
            'z': (-0.0, 0.1, 0.1),
            'steps': 1,
            'endgapsym': 5.0,
            'terminalgapsymhyb': 5.0
        }

        options_named = namedtuple("options", options.keys())(*options.values())
        test_data_filepath = 'IDSort/data/test_data/test_cpmu.json'

        with open(test_data_filepath) as old_json_file, \
                NamedTemporaryFile() as new_json_file:
            process(options_named, [new_json_file.name])
            new_json = json.load(new_json_file)
            old_json = json.load(old_json_file)
            assert new_json == old_json

    def test_process_hybrid_symmetric_shim(self):

        options = {
            'periods': 113,
            'fullmagdims': (50., 30., 5.76),
            'hemagdims': (50., 30., 4.00),
            'htmagdims': (50., 30., 1.13),
            'poledims': (30., 23., 2.95),
            'interstice': 0.0625,
            'gap': 5.6,
            'type': 'Hybrid_Symmetric',
            'name': 'test_cpmu_shim',
            'x': (0, 0.1, 1),
            'z': (0, 0.1, 1),
            'steps': 5,
            'endgapsym': 3.0,
            'terminalgapsymhyb': 3.0
        }

        options_named = namedtuple("options", options.keys())(*options.values())
        test_data_filepath = 'IDSort/data/test_data/test_cpmu_shim.json'

        with open(test_data_filepath) as old_json_shim_file, \
                NamedTemporaryFile() as new_json_shim_file:
            process(options_named, [new_json_shim_file.name])
            new_json_shim = json.load(new_json_shim_file)
            old_json_shim = json.load(old_json_shim_file)
            assert new_json_shim == old_json_shim
