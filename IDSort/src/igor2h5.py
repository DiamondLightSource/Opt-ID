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

'''
'''
#Input Files in the format "Bx0C,Bz0C,Bs0C", copied out of Igor

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
'''
all_data=np.zeros((1,1,2621,3))
all_data[0,0,:,:]=np.genfromtxt('/home/tow31676/X0Z0.bfield')
filname='/home/tow31676/id_sort_code/test/igor2h5test.h5'
f=h5py.File(filname,'w')
f.create_dataset('id_Bfield',data=all_data)
f.close()
'''
all_data=np.zeros((1,5,2581,3))
all_data[0,0,:,:]=np.genfromtxt('/dls/technical/id/I03_CPMU_build_list/X0Z0.bfield')
all_data[0,1,:,:]=np.genfromtxt('/dls/technical/id/I03_CPMU_build_list/X0Z1.bfield')
all_data[0,2,:,:]=np.genfromtxt('/dls/technical/id/I03_CPMU_build_list/X0Z2.bfield')
all_data[0,3,:,:]=np.genfromtxt('/dls/technical/id/I03_CPMU_build_list/X0Z3.bfield')
all_data[0,4,:,:]=np.genfromtxt('/dls/technical/id/I03_CPMU_build_list/X0Z4.bfield')
filname='/dls/technical/id/I03_CPMU_build_list/field_meas.h5'
f=h5py.File(filname,'w')
f.create_dataset('id_Bfield',data=all_data)
f.close()

