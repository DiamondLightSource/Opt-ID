'''
Created on 2 Nov 2011

@author: ssg37927
'''

from clonal import BCell
from setmag import PPM
import copy
import numpy as np
import h5py
import os

class PPM_BCell(BCell):
    
    objective_calls = 0
    
    def __init__(self,ppm):
        self.ppm = ppm
        self.mutations = 0
        BCell.__init__(self)
    
    def random_genome(self):
        if self.ppm.presort == None :
            self.ppm = copy.deepcopy(self.ppm)
            self.ppm.randomize()
    
    def mutate(self, number_of_mutations):
        # pick 2 points at random and switch them
        for i in range(int(number_of_mutations)):
            self.ppm.swap_one_magnet()
            self.mutations += 1
    
    def get_length(self):
        return self.ppm.get_id_length()
    
    def fitness(self):
        PPM_BCell.objective_calls += 1
        (IXMax, IYMax, IX0, IY0, I2XMax, I2YMax, I2X0, I2Y0, RMS_A, RMS_T, RMS_B, X_TRAJ, Y_TRAJ) = self.ppm.calculate_beam_fittnes_elements()
        IXMax*=1e-3
        IYMax*=1e-3
        IX0*=1e-3
        IY0*=1e-3
        I2XMax*=1e-6
        I2YMax*=1e-6
        I2X0*=1e-6
        I2Y0*=1e-6
        X_TRAJ*=1e3
        Y_TRAJ*=1e3
        cost = np.array((IXMax, IYMax, IX0, IY0, I2XMax, I2YMax, I2X0, I2Y0, RMS_A, RMS_T, RMS_B, X_TRAJ, Y_TRAJ))
        return np.square(cost).sum()
    
    def __eq__(self, other):
        return self.ppm == other.ppm
    
    def write_item(self, h5group, epoc_num, mem_num, name, data):
        if not name in h5group.keys() :
            print "Creating the item for ", name
            h5group.create_dataset(name, (1,1,)+data.shape, data.dtype, maxshape=(None, None)+data.shape)
        if(epoc_num >= h5group[name].shape[0]):
            h5group[name].resize(epoc_num+1, 0)
        if(mem_num >= h5group[name].shape[1]):
            h5group[name].resize(mem_num+1, 1)
        h5group[name][epoc_num,mem_num] = data
    
    def write_bcell_to_h5(self, h5group, epoc_number, member_number):
        print "writing element ", epoc_number, member_number
        
        if self.ppm.shimming == True:
            if not 'Shim' in h5group.keys():
                h5group.create_group('Shim')
            func = h5group['Shim']
        else:
            if not 'Sort' in h5group.keys():
                h5group.create_group('Sort')
            func = h5group['Sort']
        
        (Tphase, Ttraj, Bphase, Btraj, phase, traj, integrals) = self.ppm.calculate_phase_error()
        (fintx, fintz, sintx, sintz) = integrals
        b = self.ppm.build_b_array()
        self.write_item(func, epoc_number, member_number, 'B', b)
        self.write_item(func, epoc_number, member_number, 'First_integral_x', fintx*1e-3)
        self.write_item(func, epoc_number, member_number, 'First_integral_z', fintz*1e-3)
        self.write_item(func, epoc_number, member_number, 'Second_integral_x', sintx*1e-6)
        self.write_item(func, epoc_number, member_number, 'Second_integral_z', sintz*1e-6)
        self.write_item(func, epoc_number, member_number, 'Phase', phase)
        self.write_item(func, epoc_number, member_number, 'Trajectories', traj*1e3)
        self.write_item(func, epoc_number, member_number, 'Phase_Top', Tphase)
        self.write_item(func, epoc_number, member_number, 'Trajectories_Top', Ttraj*1e3)
        self.write_item(func, epoc_number, member_number, 'Phase_Bottom', Bphase)
        self.write_item(func, epoc_number, member_number, 'Trajectories_Bottom', Btraj*1e3)
        
        if not 'Objective' in h5group.keys() :
            h5group.create_group('Objective')
        func = h5group['Objective']
        obj = self.ppm.calculate_beam_fittnes_elements()
        (IXMax, IYMax, IX0, IY0, I2XMax, I2YMax, I2X0, I2Y0, RMS_A, RMS_T, RMS_B, X_TRAJ, Y_TRAJ) = obj
        self.write_item(func, epoc_number, member_number, 'IXMAX', IXMax*1e-3)
        self.write_item(func, epoc_number, member_number, 'IYMax', IYMax*1e-3)
        self.write_item(func, epoc_number, member_number, 'IX0', IX0*1e-3)
        self.write_item(func, epoc_number, member_number, 'IY0', IY0*1e-3)
        self.write_item(func, epoc_number, member_number, 'I2XMax', I2XMax*1e-6)
        self.write_item(func, epoc_number, member_number, 'I2YMax', I2YMax*1e-6)
        self.write_item(func, epoc_number, member_number, 'I2X0', I2X0*1e-6)
        self.write_item(func, epoc_number, member_number, 'I2Y0', I2Y0*1e-6)
        self.write_item(func, epoc_number, member_number, 'RMS_A', RMS_A)
        self.write_item(func, epoc_number, member_number, 'RMS_T', RMS_T)
        self.write_item(func, epoc_number, member_number, 'RMS_B', RMS_B)
        self.write_item(func, epoc_number, member_number, 'X_TRAJ', X_TRAJ*1e3)
        self.write_item(func, epoc_number, member_number, 'Y_TRAJ', Y_TRAJ*1e3)
        self.write_item(func, epoc_number, member_number, 'Total', np.sqrt(self.fitness()))
        
        if not 'BCell' in h5group.keys() :
            h5group.create_group('BCell')
        bcellgroup = h5group['BCell']
        self.write_item(bcellgroup, epoc_number, member_number, 'age', np.array(self.bcell_age))
        self.write_item(bcellgroup, epoc_number, member_number, 'mutations', np.array(self.mutations))

    def best_bcell_per_epoc(self, epoc_number, dir):
        self.ppm.print_to_file(os.path.join(dir, "Best_%05i.dat"%epoc_number))
        
        