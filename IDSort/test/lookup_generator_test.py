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
            
            
    def testAPPLEdata(self):
        py=h5py.File('/home/gdy32713/DAWN_stable/optid/Opt-ID/IDSort/test/91period_real_data.h5', 'r')
        
        pb1 = py['id_Bfield']
        pb=pb1.value[2,0]
        
        pyf=h5py.File('/home/gdy32713/DAWN_stable/optid/Opt-ID/IDSort/test/91period_4flip_real_data.h5', 'r')
        
        pb1f = pyf['id_Bfield']
        pbf=pb1f.value[2,0]
        
        pb1t = py['id_trajectories']
        pbt = pb1t.value[0]
        
        pb1tf = pyf['id_trajectories']
        pbtf = pb1tf.value[0]
        
        fs=np.loadtxt('/home/gdy32713/DAWN_stable/optid/Opt-ID/IDSort/test/bxy.dat')
        fs/=10000.0
        fst = np.loadtxt('/home/gdy32713/DAWN_stable/optid/Opt-ID/IDSort/test/traj.dat')
        
        fsf=np.loadtxt('/home/gdy32713/DAWN_stable/optid/Opt-ID/IDSort/test/bxyflip.dat')
        fsf/=10000.0
        fstf = np.loadtxt('/home/gdy32713/DAWN_stable/optid/Opt-ID/IDSort/test/traj.dat')
        
        f1 = h5py.File('/home/gdy32713/DAWN_stable/optid/Opt-ID/IDSort/test/compare.h5','w')
        
        f1.create_dataset('Python Sort', data = pb)
        f1.create_dataset('Python Flip Sort', data = pbf)
        f1.create_dataset('Fortran Sort', data=fs)
        f1.create_dataset('Fortran Flip Sort', data=fsf)
        f1.create_dataset('Python Trajectory', data = pbt)
        f1.create_dataset('Python Flip Trajectory', data = pbtf)
        f1.create_dataset('Fortran Trajectory', data=fst)
        f1.create_dataset('Fortran Flip Trajectory', data=fstf)
        
        f1.close()
        
        a=1
        
        self.assertTrue(a,0,'not done yet')
        


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()