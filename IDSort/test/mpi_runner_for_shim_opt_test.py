import unittest
import shutil
import os
from tempfile import mkdtemp
from collections import namedtuple

import numpy as np
import h5py

from IDSort.src.mpi_runner_for_shim_opt import process


class MpiRunnerForShimOptTest(unittest.TestCase):

    def test_process(self):

        test_json_filepath = 'IDSort/data/test_data/shim/test_cpmu_shim.json'
        test_mag_filepath = 'IDSort/data/test_data/sort/test_cpmu.mag'
        test_h5_filepath = 'IDSort/data/test_data/shim/test_cpmu_shim.h5'
        test_genome_filepath = 'IDSort/data/test_data/sort/mpi_runner_output/1.12875826e-08_000_7c51ecd01f73.genome'
        test_genome_copy_filepath = '1.0_000_test_genome.genome'
        test_bfield_filepath = 'IDSort/data/test_data/sort/process_genome_analyse_output/1.12875826e-08_000_7c51ecd01f73.genome.h5'

        shutil.copyfile(test_genome_filepath, test_genome_copy_filepath)

        options = {
            'iterations': 3,
            'number_of_mutations': 5,
            'id_filename': test_json_filepath,
            'magnets_filename': test_mag_filepath,
            'lookup_filename': test_h5_filepath,
            'bfield_filename': test_bfield_filepath,
            'genome_filename': test_genome_copy_filepath,
            'setup': 24,
            'number_of_changes': 2,
            'mutations': 5,
            'c': 2,
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

        test_genome_filepath_default = 'IDSort/data/test_data/shim/1.00000000e+00_001_test.genome'
        test_genome_filepaths = [
            'IDSort/data/test_data/shim/1.20847271e-07_000_85a13cc425d0.genome',
            'IDSort/data/test_data/shim/1.20952907e-07_000_9228436240f4.genome',
            'IDSort/data/test_data/shim/1.20965365e-07_000_763473ed8598.genome',
            'IDSort/data/test_data/shim/1.23262940e-07_000_3fa353e9cf87.genome'
        ]

        test_genome_A_filepaths = [
            'IDSort/data/test_data/shim/1.20847271e-07_000_A85a13cc425d0.genome',
            'IDSort/data/test_data/shim/1.20952907e-07_000_A9228436240f4.genome',
            'IDSort/data/test_data/shim/1.20965365e-07_000_A763473ed8598.genome'
        ]

        test_h5_filepaths = [
            'IDSort/data/test_data/shim/test-A763473ed8598.h5',
            'IDSort/data/test_data/shim/test-A85a13cc425d0.h5',
            'IDSort/data/test_data/shim/test-A9228436240f4.h5'
        ]

        try:
            process(options_named, args)
            new_filenames = os.listdir(new_genome_dir)
            new_genome_filenames = [filename for filename in new_filenames if 'genome' in filename]
            new_h5_filenames = [filename for filename in new_filenames if 'genome' not in filename]

            # tests the genome that's always named the same: 1.00000000e+00_001_test.genome
            with open(test_genome_filepath_default, 'rb') as test_genome_file, \
                    open(os.path.join(new_genome_dir, '1.00000000e+00_001_test.genome'), 'rb') as new_genome_file:
                assert new_genome_file.read() == test_genome_file.read()

            # tests all genome files with no leading "A" in their UID
            for test_genome_filepath in test_genome_filepaths:
                genome_to_compare_with = None
                filename = os.path.split(test_genome_filepath)[1]
                fitness = filename.split('_')[0]

                for new_genome_filename in new_genome_filenames:
                    uid = new_genome_filename.split('_')[2].split('.')[0]
                    if fitness in new_genome_filename and len(uid) == 12:
                        genome_to_compare_with = new_genome_filename
                        break

                assert genome_to_compare_with is not None

                with open(os.path.join(new_genome_dir, genome_to_compare_with), 'rb') as new_genome_file, \
                        open(test_genome_filepath, 'rb') as test_genome_file:
                    assert new_genome_file.read() == test_genome_file.read()

            test_to_new_uids = {} # used for matching h5 files for comparison later
            # tests all genome files with a leading "A" in their UID
            for test_genome_A_filepath in test_genome_A_filepaths:
                genome_to_compare_with = None
                filename = os.path.split(test_genome_A_filepath)[1]
                fitness = filename.split('_')[0]
                test_genome_uid = filename.split('_')[2].split('.')[0]

                for new_genome_filename in new_genome_filenames:
                    uid = new_genome_filename.split('_')[2].split('.')[0]
                    if fitness in new_genome_filename and len(uid) == 13:
                        genome_to_compare_with = new_genome_filename
                        test_to_new_uids[test_genome_uid] = uid
                        break

                assert genome_to_compare_with is not None

                with open(os.path.join(new_genome_dir, genome_to_compare_with), 'rb') as new_genome_file, \
                        open(test_genome_A_filepath, 'rb') as test_genome_file:
                    assert new_genome_file.read() == test_genome_file.read()

            # tests all h5 files
            for test_h5_filepath in test_h5_filepaths:
                h5_file_to_compare_with = None
                filename = os.path.split(test_h5_filepath)[1]
                test_h5_uid = filename.split('-')[1].split('.')[0]

                for new_h5_filename in new_h5_filenames:
                    if test_to_new_uids[test_h5_uid] in new_h5_filename:
                        h5_file_to_compare_with = new_h5_filename
                        break

                assert h5_file_to_compare_with is not None

                with h5py.File(test_h5_filepath, 'r') as test_h5_file, \
                        h5py.File(os.path.join(new_genome_dir, h5_file_to_compare_with), 'r') as new_h5_file:
                    for dataset in new_h5_file:
                        new_data = new_h5_file.get(dataset).value
                        old_data = test_h5_file.get(dataset).value
                        assert np.allclose(new_data, old_data)
        finally:
            shutil.rmtree(new_genome_dir)
            os.remove(test_genome_copy_filepath)
