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
import random as rand
import pprint

class traj_shim_BCell(BCell):
    
    objective_calls = 0
    
    def __init__(self, ppm, flips=5, swaps=2):
        traj_shim_BCell.ppm = ppm
        self.ppm = copy.deepcopy(traj_shim_BCell.ppm)
        self.mutations = 0
        self.flip_count = flips
        self.swap_count = swaps
        self.flips = []
        self.swaps = []
        BCell.__init__(self)
    
    def random_flip(self):
        # random top or bottom beam
        beam_name = 'b'
        beam = rand.randint(0,1)
        if beam > 0 :
            beam_name = 't'
        
        # now pick a random point in the array to flip
        point = rand.randint(0,len(self.ppm.bottom_beam.flip)-1)
        
        return (beam_name, point)
    
    def apply_flips(self):
        for flip in self.flips:
            if flip[0] == 't':
                self.ppm.flip_magnet(1,flip[1])
            else :
                self.ppm.flip_magnet(0,flip[1])
    
    def apply_swaps(self):
        for swap in self.swaps:
            if swap[0] == 't':
                self.ppm.swap_magnet(1,swap[1],swap[2],swap[3],swap[4])
            else :
                self.ppm.swap_magnet(0,swap[1],swap[2],swap[3],swap[4])
     
    def random_swap(self):
        # pick a random point in the array to swap
        point = rand.randint(0,len(self.ppm.bottom_beam.flip)-1)
        
        # Now pick a beam random top or bottom beam
        beam_name = 'b'
        type = self.ppm.bottom_beam.types[point]
        beam = rand.randint(0,1)
        if beam > 0 :
            beam_name = 't'
            type = self.ppm.top_beam.types[point]
        
        # get a free magnet from the appropriate magnet pool
        swap_key = self.ppm.magnets.magnet_sets[type].get_random_available_key()
        
        swap_flip = (rand.randint(0,1)*2)-1
        
        return (beam_name, point, type, swap_key, swap_flip)
    
    def random_genome(self):
        # flips first, simply a list of the items which have flipped
        self.ppm = copy.deepcopy(traj_shim_BCell.ppm)
        self.flips = []
        for i in range(self.flip_count):
            self.flips.append(self.random_flip())
        
        self.swaps = []
        for i in range(self.swap_count):
            swap = self.random_swap()
            self.swaps.append(swap)
            # check out the key so it cannot be used again
            self.ppm.magnets.magnet_sets[swap[2]].borrow_magnet(swap[3])
    
    def mutate(self, number_of_mutations):
        # pick a flip, and change it to a new random one.
        for i in range(int(number_of_mutations)):
            if rand.randint(0,1) > 0 :
                # mutate the flips
                point = rand.randint(0,len(self.flips)-1)
                self.flips[point] = self.random_flip()
            else:
                # mutate the swaps
                point = rand.randint(0,len(self.swaps)-1)
                # put back the magnet, so it can be used again
                swap = self.swaps[point]
                new_swap = self.random_swap()
                self.swaps[point] = new_swap
                self.ppm.magnets.magnet_sets[swap[2]].return_magnet(swap[3])
                self.ppm.magnets.magnet_sets[new_swap[2]].borrow_magnet(new_swap[3])
    
    def get_length(self):
        return self.flip_count+self.swap_count
    
    def evaluate_ppm(self, ppm):
        traj_shim_BCell.objective_calls += 1
        (IXMax, IYMax, IX0, IY0, I2XMax, I2YMax, I2X0, I2Y0, RMS_A, RMS_T, RMS_B, X_TRAJ, Y_TRAJ) = ppm.calculate_beam_fittnes_elements()
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
    
    def fitness(self):
        self.ppm = copy.deepcopy(traj_shim_BCell.ppm)
        self.apply_flips()
        self.apply_swaps()
        return self.evaluate_ppm(self.ppm)
    
    def __eq__(self, other):
        return self.flips == other.flips
    
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
        
        if not 'Shim' in h5group.keys():
            h5group.create_group('Shim')
        func = h5group['Shim']
        
        (Tphase, Ttraj, Bphase, Btraj, phase, traj, integrals) = self.ppm.calculate_phase_error()
        (fintx, fintz, sintx, sintz) = integrals
        if self.ppm.shimming:
            b = self.ppm.real_b_array;
            b_top = self.ppm.top_beam.real_barray;
            b_bottom = self.ppm.bottom_beam.real_barray;
        else:
            b = self.ppm.build_b_array()
            b_top = self.ppm.top_beam.build_b_array();
            b_bottom = self.ppm.bottom_beam.build_b_array();
        self.write_item(func, epoc_number, member_number, 'B', b)
        self.write_item(func, epoc_number, member_number, 'B_Top', b_top)
        self.write_item(func, epoc_number, member_number, 'B_Bottom', b_bottom)
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
        
    def report(self):
        for flip in self.flips:
            beam = "Top"
            magnetNumber = self.ppm.top_beam.magnets[flip[1]]
            magnetType = self.ppm.top_beam.types[flip[1]]
            if flip[0] == 'b':
                beam = "Bottom"
                magnetNumber = self.ppm.bottom_beam.magnets[flip[1]]
                magnetType = self.ppm.bottom_beam.types[flip[1]]
            print "Flip magnet %i on the '%s' beam : magnet number = %s , magnet Type = %s" % (flip[1], beam, magnetNumber, magnetType)
        for swap in self.swaps:
            
            beam = "Top"
            magnetNumber = self.ppm.top_beam.magnets[swap[1]]
            magnetType = self.ppm.top_beam.types[swap[1]]
            if swap[0] == 'b':
                beam = "Bottom"
                magnetNumber = self.ppm.bottom_beam.magnets[swap[1]]
                magnetType = self.ppm.bottom_beam.types[swap[1]]
            print "Swap magnet %i on the '%s' beam : magnet number = %s , magnet Type = %s" % (swap[1], beam, magnetNumber, magnetType)
            print "                           with : magnet number = %s , magnet Type = %s with flip %i" % (swap[3], swap[2], swap[4] )