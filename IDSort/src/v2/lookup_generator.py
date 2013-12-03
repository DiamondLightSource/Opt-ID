'''
Created on 3 Dec 2013

@author: ssg37927
'''

import numpy as np
import magnet_tools as mt
import h5py

if __name__ == "__main__":
    import optparse
    usage = "%prog [options] ID_Description_File Output_filename"
    parser = optparse.OptionParser(usage=usage)
    parser.add_option("-o", "--output", dest="output", help="Select the file to write the output to", default=None)
    parser.add_option("-p", "--periods", dest="periods", help="Set the number of full periods for the Device", default=5, type="int")
    parser.add_option("-s", "--symmetric", dest="symmetric", help="Set the device to symmetric rather then Anti-symmetric", action="store_true", default=False)
    parser.add_option("-r", "--random", dest="random", help="Choose the magnets randomly instead of sequentialy", action="store_true", default=False)
    parser.add_option("-v", "--verbose", dest="verbose", help="display debug information", action="store_true", default=False)

    (options, args) = parser.parse_args()
    # Add all the magnets

    magnets = []
    mag = {}
    mag['xmin'] = -5.0
    mag['xmax'] = 5.0
    mag['xstep'] = 1.0
    mag['zmin'] = -2.0
    mag['zmax'] = 2.0
    mag['zstep'] = 1.0
    mag['smin'] = -100.0
    mag['smax'] = 100.0
    mag['sstep'] = 0.1
    mag['magdims'] = (5,5,1)
    mag['mingap'] = 5.0
    magnets.append(mag)

    outfile = h5py.File(args[1], 'w')

    for mag in magnets:
        data = mt.generate_B_array(mag['xmin'], mag['xmax'], mag['xstep'], mag['zmin'], mag['zmax'], mag['zstep'], mag['smin'], mag['smax'], mag['sstep'], mag['magdims'], mag['V1'])
        outfile.create_dataset("vals", data=data)

    outfile.close()

