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

        # Offloads comparison to Magents::__eq__ method
        assert old_mag == new_mag