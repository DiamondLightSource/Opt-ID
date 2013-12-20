'''
Created on 3 Dec 2013

@author: ssg37927
'''

import numpy as np
import magnet_tools as mt
import h5py
import json
import time

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

    fp = open(args[0], 'r')
    data = json.load(fp)
    fp.close()

    # create calculation array
    
    testpoints=np.mgrid[data['xmin']:data['xmax']:data['xstep'],data['zmin']:data['zmax']:data['zstep'],data['smin']:data['smax']:data['sstep']]
    
    outfile = h5py.File(args[2], 'w')
    
    for b in range(len(data['beams'])):
        count = 0
        print("Processing beam %02i" % (b))
        datashape = (testpoints.shape[1], testpoints.shape[2], testpoints.shape[3], 3, 3, len(data['beams'][b]['mags']))
        chunkshape = (testpoints.shape[1], testpoints.shape[2], testpoints.shape[3], 3, 3, 1)
        print ("datashape is : " + str(datashape))
        ds = outfile.create_dataset(data['beams'][b]['name'], shape=datashape, dtype=np.float64, chunks=chunkshape)

        start_time=time.time()
        for mag in data['beams'][b]['mags']:
            print("processing beam %02i magnet %04i" % (b, count))
            dataset = mt.wrapCalcB(testpoints, np.array(mag['dimensions']), np.array(mag['position']))
            ds[:, :, :, :, :, count] = dataset * np.array(mag['direction'])
            count += 1
            
        end_time=time.time()
        print("Elapsed time was %g seconds" % (end_time - start_time))
    

    outfile.close()


