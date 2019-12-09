import unittest
import json
import os
from tempfile import TemporaryFile
from mock import patch
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
            'x': (-5.0, 5.1, 2.5),
            'z': (-0.0, 0.1, 0.1),
            'steps': 5,
            'endgapsym': 5.0,
            'terminalgapsymhyb': 5.0
        }

        options_named = namedtuple("options", options.keys())(*options.values())
        args = ['test_cpmu_new.json']
        test_data_filepath = 'IDSort/data/test_data/test_cpmu.json'

        with open(test_data_filepath) as old_json_file, \
                patch('__builtin__.open', create=True) as mock_json_file:
            mock_json_file.return_value.__enter__.return_value = TemporaryFile('w+')
            process(options_named, args)
            mock_json_file.return_value.__enter__.return_value.seek(0)
            new_json = json.loads(mock_json_file.return_value.__enter__.return_value.read())
            mock_json_file.return_value.__enter__.return_value.seek(0, os.SEEK_END)
            old_json = json.load(old_json_file)
            assert new_json == old_json
