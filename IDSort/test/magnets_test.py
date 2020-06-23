import unittest
from tempfile import NamedTemporaryFile
from collections import namedtuple
from IDSort.src.magnets import process, Magnets, MagLists

class MagnetsTest(unittest.TestCase):

    def test_process(self):

        # Load the expected values from the .mag file (python2 generated cPickle)
        old_mag_filepath = 'IDSort/data/test_data/sort/test_cpmu.mag'

        old_mag = Magnets()
        old_mag.load(old_mag_filepath)

        # Execute the process function on the corresponding .sim files (ascii named field vectors)
        # to generate a new .mag file (python3 generated Pickle)
        options = {
            'hmags'  : 'IDSort/data/I03H.sim',
            'hemags' : 'IDSort/data/I03HEC.sim',
            'htmags' : 'IDSort/data/I03HTE.sim',
            'vmags'  : None,
            'vemags' : None,
        }
        options_named = namedtuple("options", options.keys())(**options)

        with NamedTemporaryFile() as new_mag_file:
            new_mag_filepath = new_mag_file.name

        process(options_named, [new_mag_filepath])

        new_mag = Magnets()
        new_mag.load(new_mag_filepath)

        # Assert set keys within old .mag file are internally consistent
        old_mag_set_keys   = sorted(old_mag.magnet_sets.keys())
        old_mag_flip_keys  = sorted(old_mag.magnet_flip.keys())
        old_mag_field_keys = sorted(new_mag.mean_field.keys())
        assert (old_mag_set_keys == old_mag_flip_keys) and (old_mag_set_keys == old_mag_field_keys)

        # Assert set keys within new .mag file are internally consistent
        new_mag_set_keys   = sorted(new_mag.magnet_sets.keys())
        new_mag_flip_keys  = sorted(new_mag.magnet_flip.keys())
        new_mag_field_keys = sorted(new_mag.mean_field.keys())
        assert (new_mag_set_keys == new_mag_flip_keys) and (new_mag_set_keys == new_mag_field_keys)

        # Assert set keys between old and new .mag files are consistent with one another
        assert (old_mag_set_keys   == new_mag_set_keys)  and \
               (old_mag_flip_keys  == new_mag_flip_keys) and \
               (old_mag_field_keys == new_mag_field_keys)

        for set_key in old_mag_set_keys:

            old_mag_set_mag_names   = sorted(old_mag.magnet_sets[set_key].keys())
            new_mag_set_mag_names   = sorted(new_mag.magnet_sets[set_key].keys())

            # Assert magnet names in this magnet set between old and new .mag files are consistent with one another
            assert (old_mag_set_mag_names == new_mag_set_mag_names)

            # Assert magnet values in this magnet set between old and new .mag files are consistent with one another
            for magnet in old_mag_set_mag_names:
                assert all(old_mag.magnet_sets[set_key][magnet] == new_mag.magnet_sets[set_key][magnet])

            # Assert the flip vectors and mean fields between old and new .mag files are consistent with one another
            assert all(old_mag.magnet_flip[set_key] == new_mag.magnet_flip[set_key])
            assert (old_mag.mean_field[set_key] == new_mag.mean_field[set_key])