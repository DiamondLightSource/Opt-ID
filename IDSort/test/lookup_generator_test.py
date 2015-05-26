'''
Created on 24 Apr 2015

@author: gdy32713
'''
import unittest
import json
import numpy as np
import h5py
from v2 import magnet_tools as mt


class Test(unittest.TestCase):


    def testName(self):
        pass
    
    def testDataset(self):
        fp = open('/home/gdy32713/DAWN_stable/optid/Opt-ID/IDSort/src/v2/1periodtest.json', 'r')
        data = json.load(fp)
        fp.close()
        
        testpoints=np.mgrid[data['xmin']:data['xmax']:data['xstep'],data['zmin']:data['zmax']:data['zstep'],data['smin']:data['smax']:data['sstep']]        
        
        for b in range(len(data['beams'])):
            count = 0
            print("Processing beam %02i" % (b))    
            for mag in data['beams'][b]['mags']:
                print("processing beam %02i magnet %04i" % (b, count))
                dataset = mt.wrapCalcB(testpoints, np.array(mag['dimensions']), np.array(mag['position']))
                self.assertTrue(np.allclose((dataset * np.array(mag['direction'])), dataset.dot(np.array(mag['direction_matrix'])), rtol=1e-08, atol=1e-08))
                count += 1
            


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()