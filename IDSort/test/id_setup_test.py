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
