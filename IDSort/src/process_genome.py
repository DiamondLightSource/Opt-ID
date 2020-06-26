'''
Created on 23 Apr 2015

@author: gdy32713
'''

import os
import json
import pickle

import numpy as np

from IDSort.src.magnets import Magnets, MagLists
import IDSort.src.field_generator as fg

def human_output(id_info, filepath, output_dir):

    with open(filepath, 'rb') as fp:
        maglists = pickle.load(fp)
    
    with open(id_info, 'r') as fp:
        info = json.load(fp)

    # TODO refactor file path creation
    readable_filename = os.path.split(filepath)[1] + '.inp'
    readable_outfile = (os.path.join(output_dir, readable_filename))

    # TODO make sure there are test files for IDs other than Hybrid_Symmetric

    # Lookup table for converting mag names to integers
    mag_types = { 'HT': 5, 'HE': 4, 'VE': 3, 'HH': 2, 'VV': 1 }
    
    if info['type'] == 'Hybrid_Symmetric':
        # TODO make a proper function somewhere
        with open(readable_outfile, 'w') as fp:

            # Track the current index of each magnet type
            mag_indices = { 'HT': 0, 'HE': 0, 'VE': 0, 'HH': 0, 'VV': 0 }

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
                    fp.write('%5i %4i %4i %4i %4i %03i\n' % ((b + 1), (a + 1),
                                                             mag_type, mag['direction_matrix'][2][2],
                                                             mag_flip, mag_num))
                # New line at the end of the beam
                fp.write('\n')
    
    if info['type']=='PPM_AntiSymmetric':
        #TODO make a proper function somewhere
        with open(readable_outfile, 'w') as fp:

            # Track the current index of each magnet type
            mag_indices = { 'HE': 0, 'VE': 0, 'HH': 0, 'VV': 0 }

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
                    fp.write('%5i %4i %4i %4i %4i %03i\n' % ((b + 1), (a + 1),
                                                             mag_type, mag['direction'][0],
                                                             mag_flip, mag_num))
                # New line at the end of the beam
                fp.write('\n')

    if info['type']=='APPLE_Symmetric':
        #TODO make a proper function somewhere
        with open(readable_outfile, 'w') as fp:

            # Track the current index of each magnet type
            mag_indices = { 'HE': 0, 'VE': 0, 'HH': 0, 'VV': 0 }

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
                    fp.write('%5i %4i %4i %4i %4i %03i\n' % ((b + 1), (a + 1),
                                                             mag_type, mag_direction,
                                                             mag_flip, mag_num))
                # New line at the end of the beam
                fp.write('\n')

def process(options, args):
    if options.create_genome:
        for filepath in args[0::]:
            print("Turning file %s from Human Readable to Genome" % (filepath))

            buildlist = np.genfromtxt(filepath, dtype=str)

            mags = Magnets()
            mags.load(options.magnets_filename)

            maglist = MagLists(mags)

            heswap = 0
            veswap = 0
            hhswap = 0
            vvswap = 0

            for line in range(buildlist.shape[0]):

                if int(buildlist[line,2])==4:
                    #maglist.magnet_lists['HE'][heswap][0]=buildlist[line,5]
                    maglist.swap('HE',maglist.magnet_lists['HE'].index([buildlist[line,5],1,0]) , heswap)
                    maglist.magnet_lists['HE'][heswap][1]=int(buildlist[line,4])

                    heswap+=1


                elif int(buildlist[line,2])==3:
                    #maglist.magnet_lists['VE'][veswap][0]=buildlist[line,5]
                    maglist.swap('VE',maglist.magnet_lists['VE'].index([buildlist[line,5],1,0]) , veswap)
                    maglist.magnet_lists['VE'][veswap][1]=int(buildlist[line,4])
                    veswap+=1

                elif int(buildlist[line,2])==2:
                    #maglist.magnet_lists['HH'][hhswap][0]=buildlist[line,5]
                    maglist.swap('HH',maglist.magnet_lists['HH'].index([buildlist[line,5],1,0]) , hhswap)
                    maglist.magnet_lists['HH'][hhswap][1]=int(buildlist[line,4])

                    hhswap+=1

                elif int(buildlist[line,2])==1:
                    #maglist.magnet_lists['VV'][vvswap][0]=buildlist[line,5]
                    maglist.swap('VV',maglist.magnet_lists['VV'].index([buildlist[line,5],1,0]) , vvswap)
                    maglist.magnet_lists['VV'][vvswap][1]=int(buildlist[line,4])

                    vvswap+=1

            genome_filename = os.path.split(filepath)[1] + '.genome'
            with open(os.path.join(options.output_dir, genome_filename),'wb') as fp:
                pickle.dump(maglist, fp)

    if options.readable:

        for filepath in args[0::]:
            print("Making file %s human readable." % (filepath))

            human_output(options.id_filename, filepath, options.output_dir)

    if options.analysis:
        for filepath in args[0::]:
            print("Processing file %s" % (filepath))
            # load the genome
            with open(filepath, "rb") as fp:
                maglists = pickle.load(fp)

            analysis_filename = os.path.split(filepath)[1]+'.h5'
            outfile = (os.path.join(options.output_dir, analysis_filename))
            fg.output_fields(outfile, options.id_filename, options.id_template, options.magnets_filename, maglists)


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
