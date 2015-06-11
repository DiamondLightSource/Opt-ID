'''
Created on 3 Dec 2013

@author: ssg37927
'''

import numpy as np
import magnet_tools as mt
import h5py
import json

if __name__ == "__main__":
    import optparse
    usage = "%prog [options] ID_Description_File Output_filename"
    parser = optparse.OptionParser(usage=usage)
#    parser.add_option("-o", "--output", dest="output", help="Select the file to write the output to", default=None)
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
    
    outfile = h5py.File(args[1], 'w')
    
    if data['type'] == 'PPM_AntiSymmetric':
    
        for b in range(len(data['beams'])):
            count = 0
            print("Processing beam %02i" % (b))
            datashape = (testpoints.shape[1], testpoints.shape[2], testpoints.shape[3], 3, 3, len(data['beams'][b]['mags']))
            chunkshape = (testpoints.shape[1], testpoints.shape[2], testpoints.shape[3], 3, 3, 1)
            print ("datashape is : " + str(datashape))
            ds = outfile.create_dataset(data['beams'][b]['name'], shape=datashape, dtype=np.float64, chunks=chunkshape)
    
            for mag in data['beams'][b]['mags']:
                print("processing beam %02i magnet %04i" % (b, count))
                dataset = mt.wrapCalcB(testpoints, np.array(mag['dimensions']), np.array(mag['position']))
                ds[:, :, :, :, :, count] = dataset.dot(np.array(mag['direction_matrix']))
                count += 1
                
        outfile.close()
        
    if data['type'] == 'APPLE_Symmetric':
    
        for b in range(len(data['beams'])):
            count = 0
            print("Processing beam %02i" % (b))
            datashape = (testpoints.shape[1], testpoints.shape[2], testpoints.shape[3], 3, 3, len(data['beams'][b]['mags']))
            chunkshape = (testpoints.shape[1], testpoints.shape[2], testpoints.shape[3], 3, 3, 1)
            print ("datashape is : " + str(datashape))
            ds = outfile.create_dataset(data['beams'][b]['name'], shape=datashape, dtype=np.float64, chunks=chunkshape)
    
            for mag in data['beams'][b]['mags']:
                print("processing beam %02i magnet %04i" % (b, count))
                
                datasetblock = mt.wrapCalcB(testpoints, np.array(mag['dimensions']), np.array(mag['position']))
                if b%2==1:
                    c2pos = np.array(mag['position'])+np.array([mag['dimensions'][0]-data['clampcut'],mag['dimensions'][1]-data['clampcut'],0.0])
                    datasetc1 = mt.wrapCalcB(testpoints, np.array([data['clampcut'],data['clampcut'],mag['dimensions'][2]]), np.array(mag['position']))
                    datasetc2 = mt.wrapCalcB(testpoints, np.array([data['clampcut'],data['clampcut'],mag['dimensions'][2]]), c2pos)
                if b%2==0:
                    c1pos = np.array(mag['position'])+np.array([mag['dimensions'][0]-data['clampcut'], 0.0, 0.0])
                    c2pos = np.array(mag['position'])+np.array([0.0 ,mag['dimensions'][1]-data['clampcut'], 0.0])
                    datasetc1 = mt.wrapCalcB(testpoints, np.array([data['clampcut'],data['clampcut'],mag['dimensions'][2]]), c1pos)
                    datasetc2 = mt.wrapCalcB(testpoints, np.array([data['clampcut'],data['clampcut'],mag['dimensions'][2]]), c2pos)
                dataset=datasetblock-datasetc1-datasetc2
                
                ds[:, :, :, :, :, count] = dataset.dot(np.array(mag['direction_matrix']))
#                ds[:, :, :, :, :, count] = np.array(mag['direction_matrix']).dot(dataset)
                count += 1
                
        outfile.close()


