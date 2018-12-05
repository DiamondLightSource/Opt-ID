'''
Created on 14 Mar 2014

@author: gdy32713
'''
import numpy as np
import h5py
from scipy import signal
import magnets

'''
'''
#Input Files in the format "Bx0C,Bz0C,Bs0C", copied out of Igor
'''
x0z0=np.genfromtxt('/home/gdy32713/shimming/I02J/X0Z0.bfield')
x1z0=np.genfromtxt('/home/gdy32713/shimming/I02J/X1Z0.bfield')
x2z0=np.genfromtxt('/home/gdy32713/shimming/I02J/X2Z0.bfield')
x3z0=np.genfromtxt('/home/gdy32713/shimming/I02J/X3Z0.bfield')
x4z0=np.genfromtxt('/home/gdy32713/shimming/I02J/X4Z0.bfield')
x0z1=np.genfromtxt('/home/gdy32713/shimming/I02J/X0Z1.bfield')
x1z1=np.genfromtxt('/home/gdy32713/shimming/I02J/X1Z1.bfield')
x2z1=np.genfromtxt('/home/gdy32713/shimming/I02J/X2Z1.bfield')
x3z1=np.genfromtxt('/home/gdy32713/shimming/I02J/X3Z1.bfield')
x4z1=np.genfromtxt('/home/gdy32713/shimming/I02J/X4Z1.bfield')
'''
'''
all_data=np.zeros((5,2,481,3))
all_data[0,0,:,:]=np.genfromtxt('/home/baj17868/MeasurementMiniID/100mm/X0Z0.bfield')
all_data[1,0,:,:]=np.genfromtxt('/home/baj17868/MeasurementMiniID/100mm/X1Z0.bfield')
all_data[2,0,:,:]=np.genfromtxt('/home/baj17868/MeasurementMiniID/100mm/X2Z0.bfield')
all_data[3,0,:,:]=np.genfromtxt('/home/baj17868/MeasurementMiniID/100mm/X3Z0.bfield')
all_data[4,0,:,:]=np.genfromtxt('/home/baj17868/MeasurementMiniID/100mm/X4Z0.bfield')
all_data[0,1,:,:]=np.genfromtxt('/home/baj17868/MeasurementMiniID/100mm/X0Z1.bfield')
all_data[1,1,:,:]=np.genfromtxt('/home/baj17868/MeasurementMiniID/100mm/X1Z1.bfield')
all_data[2,1,:,:]=np.genfromtxt('/home/baj17868/MeasurementMiniID/100mm/X2Z1.bfield')
all_data[3,1,:,:]=np.genfromtxt('/home/baj17868/MeasurementMiniID/100mm/X3Z1.bfield')
all_data[4,1,:,:]=np.genfromtxt('/home/baj17868/MeasurementMiniID/100mm/X4Z1.bfield')
filname='/home/gdy32713/shimming/miniID/meas0a.h5'
f=h5py.File(filname,'w')
f.create_dataset('id_Bfield',data=all_data)
f.close()
'''
mags=magnets.Magnets()
magnets.Magnets.load(mags,'/home/baj17868/test_C.mag')

maglist = magnets.MagLists(mags)

edtest={}

for key in mags.magnet_sets:
    print key
    print np.alen(mags.magnet_sets[key])
    edtest[key]=range(np.alen(mags.magnet_sets[key]))

print edtest
    


