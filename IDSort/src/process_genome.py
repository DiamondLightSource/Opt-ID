'''
Created on 23 Apr 2015

@author: gdy32713
'''

import os
import json
import pickle

import numpy as np

from .magnets import Magnets, MagLists
from .field_generator import output_fields

from .logging_utils import logging, getLogger
logger = getLogger(__name__)


def human_output(id_json_path, genome_path, output_dir):
    logger.debug('Starting')

    # Load the MagLists data
    try:
        logger.info('Loading MagLists from genome [%s]', genome_path)
        with open(genome_path, 'rb') as fp:
            maglists = pickle.load(fp)

    except Exception as ex:
        logger.error('Failed to load MagLists from genome [%s]', genome_path, exc_info=ex)
        raise ex

    # Load the ID json data
    try:
        logger.info('Loading ID info from json [%s]', id_json_path)
        with open(id_json_path, 'r') as fp:
            info = json.load(fp)

    except Exception as ex:
        logger.error('Failed to load ID info from json [%s]', id_json_path, exc_info=ex)
        raise ex

    # TODO refactor file path creation
    output_filename = os.path.split(genome_path)[1] + '.inp'
    output_path     = (os.path.join(output_dir, output_filename))

    try:
        logger.info('Writing human readable genome for [%s] device to [%s]', info['type'], output_path)

        # TODO refactor as pandas .csv file format
        with open(output_path, 'w') as output_file:

            # Lookup table for converting mag names to integers
            mag_types   = {'HT': 5, 'HE': 4, 'VE': 3, 'HH': 2, 'VV': 1}
            # Track the current index of each magnet type
            mag_indices = {'HT': 0, 'HE': 0, 'VE': 0, 'HH': 0, 'VV': 0}

            if info['type'] == 'Hybrid_Symmetric':

                for b, beam in enumerate(info['beams']):
                    for a, mag in enumerate(beam['mags']):

                        # Prepare data for this magnet
                        mag_type = mag_types[mag['type']]
                        mag_data = maglists.magnet_lists[mag['type']][mag_indices[mag['type']]]
                        mag_num  = int(mag_data[0])
                        mag_flip = mag_data[1]

                        # Update the index to the next magnet of this type
                        mag_indices[mag['type']] += 1

                        # Write each magnet in the beam as a new line
                        row_data = ((b + 1), (a + 1), mag_type, mag['direction_matrix'][2][2], mag_flip, mag_num)
                        logger.debug('Beam %d [%s] Magnet %d [%s]', b, beam['name'], a, row_data)
                        output_file.write('%5i %4i %4i %4i %4i %03i\n' % row_data)

                    # New line at the end of the beam
                    output_file.write('\n')

            elif info['type'] == 'PPM_AntiSymmetric':

                for b, beam in enumerate(info['beams']):
                    for a, mag in enumerate(beam['mags']):

                        # Prepare data for this magnet
                        mag_type = mag_types[mag['type']]
                        mag_data = maglists.magnet_lists[mag['type']][mag_indices[mag['type']]]
                        mag_num  = int(mag_data[0])
                        mag_flip = mag_data[1]

                        # Update the index to the next magnet of this type
                        mag_indices[mag['type']] += 1

                        # Write each magnet in the beam as a new line
                        row_data = ((b + 1), (a + 1), mag_type, mag['direction'][0], mag_flip, mag_num)
                        logger.debug('Beam %d [%s] Magnet %d [%s]', b, beam['name'], a, row_data)
                        output_file.write('%5i %4i %4i %4i %4i %03i\n' % row_data)

                    # New line at the end of the beam
                    output_file.write('\n')

            elif info['type'] == 'APPLE_Symmetric':

                for b, beam in enumerate(info['beams']):
                    for a, mag in enumerate(beam['mags']):

                        # Prepare data for this magnet
                        mag_type = mag_types[mag['type']]
                        mag_data = maglists.magnet_lists[mag['type']][mag_indices[mag['type']]]
                        mag_num  = int(mag_data[0])
                        mag_flip = mag_data[1]

                        # Update the index to the next magnet of this type
                        mag_indices[mag['type']] += 1

                        if   mag_type in [1, 3]:
                            mag_direction = mag['direction_matrix'][1][1]
                        elif mag_type in [2, 4]:
                            mag_direction = mag['direction_matrix'][2][2]
                        else:
                            raise Exception(f'Unknown mag_type [{mag_type}]')

                        # Write each magnet in the beam as a new line
                        row_data = ((b + 1), (a + 1), mag_type, mag_direction, mag_flip, mag_num)
                        logger.debug('Beam %d [%s] Magnet %d [%s]', b, beam['name'], a, row_data)
                        output_file.write('%5i %4i %4i %4i %4i %03i\n' % row_data)

                    # New line at the end of the beam
                    output_file.write('\n')

    except Exception as ex:
        logger.error('Failed to write comparison to [%s]', output_path, exc_info=ex)
        raise ex

    logger.debug('Halting')

def process(options, args):
    logger.debug('Starting')

    # Process all genome files converting them from human readable to machine readable files
    if options.create_genome:

        hr_genome_paths = args[0::]
        for index, hr_genome_path in enumerate(hr_genome_paths):
            logger.info('%03d of %03d : Converting human readable genome file to genome file [%s]', index, len(hr_genome_paths), hr_genome_path)

            # TODO refactor to avoid use of np.genfromtxt()
            buildlist = np.genfromtxt(hr_genome_path, dtype=str)

            mags = Magnets()
            mags.load(options.magnets_filename)
            maglist = MagLists(mags)

            # Lookup table for converting mag names to integers
            mag_types   = { 5 : 'HT', 4 : 'HE', 3 : 'VE', 2 : 'HH', 1 : 'VV' }
            # Track the current index of each magnet type
            mag_indices = {'HT': 0, 'HE': 0, 'VE': 0, 'HH': 0, 'VV': 0}

            for line in range(buildlist.shape[0]):

                mag_type_id = int(buildlist[line, 2])
                mag_type    = mag_types[mag_type_id]

                logger.debug('mag_type_id %d mag_type %s buildlist [%s]', mag_type_id, mag_type, buildlist[line])

                maglist.swap(mag_type, maglist.magnet_lists[mag_type].index([buildlist[line, 5], 1, 0]), mag_indices[mag_type])
                maglist.magnet_lists[mag_type][mag_indices[mag_type]][1] = int(buildlist[line, 4])

                mag_indices[mag_type] += 1

            genome_path = os.path.join(options.output_dir, os.path.split(hr_genome_path)[1] + '.genome')
            with open(genome_path,'wb') as fp:
                pickle.dump(maglist, fp)

    # Process all genome files converting them from machine readable files to human readable files
    if options.readable:

        genome_paths = args[0::]
        for index, genome_path in enumerate(genome_paths):
            logger.info('%03d of %03d : Converting genome file to human readable genome file [%s]', index, len(genome_paths), genome_path)

            human_output(options.id_filename, genome_path, options.output_dir)

    # Process all genome files producing analysis files
    if options.analysis:

        genome_paths = args[0::]
        for index, genome_path in enumerate(genome_paths):
            logger.info('%03d of %03d : Producing analysis file from genome file [%s]', index, len(genome_paths), genome_path)

            # Load the MagLists data
            try:
                logger.info('Loading MagLists from genome [%s]', genome_path)
                with open(genome_path, 'rb') as fp:
                    maglists = pickle.load(fp)

            except Exception as ex:
                logger.error('Failed to load MagLists from genome [%s]', genome_path, exc_info=ex)
                raise ex

            # Offload analysis processing to field_generator::output_fields
            analysis_path = os.path.join(options.output_dir, os.path.split(genome_path)[1] + '.h5')
            output_fields(analysis_path, options.id_filename, options.id_template, options.magnets_filename, maglists)

    logger.debug('Halting')

if __name__ == '__main__':
    import optparse
    usage = "%prog [options] Genome_filenames"
    parser = optparse.OptionParser(usage=usage)
    parser.add_option("-a", "--analyse", dest="analysis", help="Analyses the genome and puts results in HDF5 format", action="store_true", default=False)
    parser.add_option("-r", "--readable", dest="readable", help="Writes the genome in a human /Excel readable format", action="store_true", default=False)
    parser.add_option("-g", "--create_genome", dest="create_genome", help="Reverses the analysis option and turns a human readable list to a genome pickle", action="store_true", default=False)
    parser.add_option("-i", "--info", dest="id_filename", help="Set the path to the id data", default='/home/gdy32713/DAWN_stable/optid/Opt-ID/IDSort/src/v2/2015test.json', type="string")
    parser.add_option("-m", "--magnets", dest="magnets_filename", help="Set the path to the magnet description file", default='/home/gdy32713/DAWN_stable/optid/Opt-ID/IDSort/src/v2/magnets.mag', type="string")
    parser.add_option("-t", "--template", dest="id_template", help="Set the path to the magnet description file", default='/home/gdy32713/DAWN_stable/optid/Opt-ID/IDSort/src/v2/2015test.h5', type="string")
    parser.add_option("-o", "--output-dir", dest="output_dir", help="Set the path of the directory that the output files are written to")

    (options, args) = parser.parse_args()
    process(options, args)
