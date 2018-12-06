# Copyright 2017 Diamond Light Source
# 
# Licensed under the Apache License, Version 2.0 (the "License"); 
# you may not use this file except in compliance with the License. 
# You may obtain a copy of the License at
# 
# http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, 
# software distributed under the License is distributed on an 
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, 
# either express or implied. See the License for the specific 
# language governing permissions and limitations under the License.



'''
Created on 14 Mar 2014

A small script to help change data files collected in Igor on the measurement bench 
into hdf5 file which can be compared with in the shimming steps.

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
    


