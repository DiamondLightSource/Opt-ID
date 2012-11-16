'''
Created on 20 Sep 2011

@author: ssg37927

x = x
y = z
z = s

'''

import random as rand
import numpy as np
import magnet_tools as mt
import h5py

class MagnetStore(object):
    
    horizontal = "HH"
    vertical = "VV"
    horizontal_end = "HE"
    vertical_end = "VE"
    air_gap = "AA"
    
    def __init__(self, filename):
        self.filename = filename
        self.magnets = {}
        self.available = {}
        self.load_magnets()
    
    def load_magnets(self):
        f = open(self.filename)
        for line in f:
            vals = line.split()
            self.magnets[vals[0]] = (float(vals[1]), float(vals[2]), float(vals[3]))
            self.available[vals[0]] = True
    
    def return_all_magnets(self):
        for key in self.available.keys():
            self.available[key] = True
    
    def return_magnet(self, key):
        self.available[key] = True
    
    def borrow_magnet(self, key):
        if self.available[key]:
            self.available[key] = False
            return key
        return None
    
    def borrow_next_magnet_in_sequence(self):
        keys = self.available.keys()
        keys.sort()
        for key in keys:
            if self.available[key]:
                return self.borrow_magnet(key)
    
    def get_random_available_key(self):
        keys= []
        for key in self.available.keys():
            if self.available[key]:
                keys.append(key)
        key = keys[rand.randint(0,len(keys)-1)]
        return key
    
    def borrow_random_magnet(self):
        key = self.get_random_available_key()
        return self.borrow_magnet(key)
    
    def borrow_next_magnet_in_presort(self,key):
        return self.borrow_magnet(key)

class AllMagnets(object):
    
    def __init__(self):
        self.magnet_sets = {}
        
    def add_magnet_set(self, name, filename):
        self.magnet_sets[name] =  MagnetStore(filename)
    
    def return_all_magnets(self):
        for magnet_set in self.magnet_sets.values():
            magnet_set.return_all_magnets()
            

class BeamAssembly(object):
    
    symetric = "SYM"
    antisymetric = "ASYM"
    
    top = "TOP"
    bottom = "BOTTOM"
    
    up = "Y+"
    down = "Y-"
    left = "Z+"
    right = "Z-"
    
    # Global Variables which will hold all the BArray info
    barray          = None
    fint            = None
    sint            = None
    
    start_VE_barray = None
    start_VE_fint   = None
    start_VE_sint   = None
    
    end_VE_barray   = None
    end_VE_fint     = None
    end_VE_sint     = None
    
    start_HE_barray = None
    start_HE_fint   = None
    start_HE_sint   = None
    
    end_HE_barray   = None
    end_HE_fint     = None
    end_HE_sint     = None
    
    real_barray     = None
    
    def __init__(self, periods, id_type, position, magnet_pool,
                random=False,
                presort=None,
                magdims=[41.,16.,5.25],
                xmin=0., xmax=1., xstep=5.,
                zmin=0., zmax=1., zstep=1,
                steps_per_magnet=12, mingap=5.0,
                offset=10.0, shimming=False):
        self.random = random
        self.presort = presort
        self.magnets = []
        self.types = []
        self.direction = []
        self.flip = []
        self.b_arrays = []
        self.fint_arrays = []
        self.sint_arrays = []
        self.id_type = id_type
        self.id_position = position
        self.id_periods = periods
        self.magnet_pool = magnet_pool
        self.steps_per_magnet = steps_per_magnet
        self.magdims = np.array(magdims);
        self.trunc_length=(periods+16)*4*steps_per_magnet
        if(self.id_type == self.symetric):
            self.id_length = self.id_periods*4+9
        else :
            self.id_length = self.id_periods*4+5
            
        self.create_type_list()
        self.create_direction_list()
        self.create_initial_flip(random=random, presort=presort)
        self.fill_magnets(presort=presort)
        
        self.shimming = shimming
        
        self.mag_array = None
        self.mag_fintx_array = None
        self.mag_fintz_array = None
        self.mag_sintx_array = None
        self.mag_sintz_array = None
        self.generate_B_List(xmin, xmax, xstep, zmin, zmax, zstep, mingap, offset)
    
    def generate_B_List(self,xmin, xmax, xstep, zmin, zmax, zstep, mingap, offset):
        '''
        offset is the amount that the air gap in different than a normal block
        or that the HE magnet is bigger
        '''
        
        # full size magnets here
        if (BeamAssembly.barray == None):
            print "Creating BeamAssembly.barray"
            #(BeamAssembly.barray, BeamAssembly.fint, BeamAssembly.sint) = self.create_int_array(xmin, xmax, xstep, zmin, zmax, zstep, self.magdims, mingap)
            BeamAssembly.barray=mt.generate_B_array_with_offsets(xmin, xmax, xstep, 0.0, zmin, zmax, zstep, 0.0, -2*self.get_beam_length(), 2*self.get_beam_length(), self.magdims[2]/self.steps_per_magnet, 0.0, self.magdims, mingap)
        
        for i in range(self.id_length):
            self.b_arrays.append(BeamAssembly.barray)
            self.fint_arrays.append(BeamAssembly.fint)
            self.sint_arrays.append(BeamAssembly.sint)
        
        if self.id_type == BeamAssembly.antisymetric :
            #print "self.magdims is ", self.magdims
            magdims = np.array(self.magdims)
            #print "magdims is ", magdims
            magdims[2] = magdims[2]/2.0
            #print "magdims for VE", magdims 
            if(BeamAssembly.start_VE_barray == None):
                print "Creating BeamAssembly.start_VE_barray"
                #(BeamAssembly.start_VE_barray, BeamAssembly.start_VE_fint, BeamAssembly.start_VE_sint) = self.create_int_array(xmin, xmax, xstep, zmin, zmax, zstep, magdims, mingap)
                BeamAssembly.start_VE_barray = mt.generate_B_array_with_offsets(xmin, xmax, xstep, 0.0, zmin, zmax, zstep, 0.0, -2*self.get_beam_length(), 2*self.get_beam_length(), self.magdims[2]/self.steps_per_magnet, 0.0, magdims, mingap)
            if(BeamAssembly.end_VE_barray == None):
                print "Creating BeamAssembly.end_VE_barray"
                #(BeamAssembly.end_VE_barray, BeamAssembly.end_VE_fint, BeamAssembly.end_VE_sint) = self.create_int_array(xmin, xmax, xstep, zmin, zmax, zstep, magdims, mingap)
                BeamAssembly.end_VE_barray = mt.generate_B_array_with_offsets(xmin, xmax, xstep, 0.0, zmin, zmax, zstep, 0.0, -2*self.get_beam_length(), 2*self.get_beam_length(), self.magdims[2]/self.steps_per_magnet, 0.0, magdims, mingap)
            magdims[2] = magdims[2]+offset
            #print "magdims for HE", magdims 
            if(BeamAssembly.start_HE_barray == None):
                print "Creating BeamAssembly.start_HE_barray"
                #(BeamAssembly.start_HE_barray, BeamAssembly.start_HE_fint, BeamAssembly.start_HE_sint) = self.create_int_array_with_offset(xmin, xmax, xstep, zmin, zmax, zstep, -(offset/2.0), magdims, mingap)
                BeamAssembly.start_HE_barray = mt.generate_B_array_with_offsets(xmin, xmax, xstep, 0.0, zmin, zmax, zstep, 0.0, -2*self.get_beam_length(), 2*self.get_beam_length(), self.magdims[2]/self.steps_per_magnet, -offset/2.0, magdims, mingap)
            if(BeamAssembly.end_HE_barray == None):
                print "Creating BeamAssembly.end_HE_barray"
                #(BeamAssembly.end_HE_barray, BeamAssembly.end_HE_fint, BeamAssembly.end_HE_sint) = self.create_int_array_with_offset(xmin, xmax, xstep, zmin, zmax, zstep, (offset/2.0), magdims, mingap)
                BeamAssembly.end_HE_barray = mt.generate_B_array_with_offsets(xmin, xmax, xstep, 0.0, zmin, zmax, zstep, 0.0, -2*self.get_beam_length(), 2*self.get_beam_length(), self.magdims[2]/self.steps_per_magnet, offset/2.0, magdims, mingap)
            for i in range(self.id_length):
                if self.types[i] == MagnetStore.horizontal_end:
                    if i < (self.id_length/2):
                        self.b_arrays[i] = BeamAssembly.start_HE_barray
                        self.fint_arrays[i] = BeamAssembly.start_HE_fint
                        self.sint_arrays[i] = BeamAssembly.start_HE_sint
                    else :
                        self.b_arrays[i] = BeamAssembly.end_HE_barray
                        self.fint_arrays[i] = BeamAssembly.end_HE_fint
                        self.sint_arrays[i] = BeamAssembly.end_HE_sint
                if self.types[i] == MagnetStore.vertical_end:
                    if i < (self.id_length/2):
                        self.b_arrays[i] = BeamAssembly.start_VE_barray
                        self.fint_arrays[i] = BeamAssembly.start_VE_fint
                        self.sint_arrays[i] = BeamAssembly.start_VE_sint
                    else :
                        self.b_arrays[i] = BeamAssembly.end_VE_barray
                        self.fint_arrays[i] = BeamAssembly.end_VE_fint
                        self.sint_arrays[i] = BeamAssembly.end_VE_sint

    def create_type_list(self):
        # do the first end
        self.type = []
        start = 0
        stop = 0
        vertical = False
        if(self.id_type == self.symetric):
            self.types.append(MagnetStore.horizontal_end)
            self.types.append(MagnetStore.air_gap)
            self.types.append(MagnetStore.vertical_end)
            self.types.append(MagnetStore.horizontal_end)
            start, stop = (4, self.id_length-4)
            vertical = True
        else :
            self.types.append(MagnetStore.horizontal_end)
            self.types.append(MagnetStore.vertical_end)
            start, stop = (2, self.id_length-2)
        
        # now put in all the middle periods
        for i in range(start, stop):
            if vertical :
                self.types.append(MagnetStore.vertical)
                vertical = False
            else :
                self.types.append(MagnetStore.horizontal)
                vertical = True
        
        # finaly add in the other end
        if(self.id_type == self.symetric):
            self.types.append(MagnetStore.horizontal_end)
            self.types.append(MagnetStore.vertical_end)
            self.types.append(MagnetStore.air_gap)
            self.types.append(MagnetStore.horizontal_end)
        else :
            self.types.append(MagnetStore.vertical_end)
            self.types.append(MagnetStore.horizontal_end)
    
    def create_direction_list(self):
        self.direction = []
        for i in range(0,self.id_length-1,4):
            if(self.id_position == BeamAssembly.top) :
                self.direction.append(BeamAssembly.left)
                self.direction.append(BeamAssembly.up)
                self.direction.append(BeamAssembly.right)
                self.direction.append(BeamAssembly.down)
            else :
                self.direction.append(BeamAssembly.right)
                self.direction.append(BeamAssembly.up)
                self.direction.append(BeamAssembly.left)
                self.direction.append(BeamAssembly.down)
                
        # append the last element
        if(self.id_position == BeamAssembly.top):
            self.direction.append(BeamAssembly.left)
        else :
            self.direction.append(BeamAssembly.right)
        
        # Sort out porblems with the air holes
        if self.id_type == BeamAssembly.symetric:
            self.direction.insert(1, "NN")
            self.direction.insert(self.id_length-2, "NN")
            self.direction.pop()
            self.direction.pop()
    
    def create_initial_flip(self, random=False, presort = None):
        self.flip = []
        if presort != None:
            ps=open(self.presort)
            for line in ps:
                if not line.strip():
                    continue
                else:
                    vals = line.split()
                    if int(vals[0]) == 1 and self.id_position == "TOP":
                        self.flip.append(int(vals[4]))
                    elif int(vals[0]) == 2 and self.id_position == "BOTTOM":
                        self.flip.append(int(vals[4]))
        else:
            for i in range(self.id_length):
                if random :
                    val = (rand.randint(0,1)*2)-1
                    self.flip.append(val)
                else :
                    self.flip.append(1)
    
    def fill_magnets(self, presort = None):
        if presort != None:
            ps = open(presort)
            i=0
            for line in ps:
                if not line.strip():
                    continue
                else:
                    vals = line.split()
                    
                    if int(vals[0]) == 1 and self.id_position == "TOP":
                        typ=self.types[i]
                        key =vals[5].rjust(3,"0")
                        self.magnets.append(self.magnet_pool.magnet_sets[typ].borrow_next_magnet_in_presort(key))
                        i+=1
                        
                    elif int(vals[0]) == 2 and self.id_position == "BOTTOM":
                        typ=self.types[i]
                        key =vals[5].rjust(3,"0")
                        self.magnets.append(self.magnet_pool.magnet_sets[typ].borrow_next_magnet_in_presort(key))
                        i+=1
                        #################
                    ########
        else:
            for type in self.types:
                if type == MagnetStore.air_gap:
                    self.magnets.append(None)
                else :
                    if self.random:
                        self.magnets.append(self.magnet_pool.magnet_sets[type].borrow_random_magnet())
                    else:
                        self.magnets.append(self.magnet_pool.magnet_sets[type].borrow_next_magnet_in_sequence())
        
    def get_adapeted_magnet(self, pos) :
        type = self.types[pos]
        if type == "AA" :
            return (0.,0.,0.)
        magnet = self.magnets[pos]
        # returns the tuple of x, y z magnetic moment
        x, y, z = self.magnet_pool.magnet_sets[type].magnets[magnet]
        
        # now modify these based on the type of the array
        direction = self.direction[pos]
        flip = self.flip[pos]
        
        if direction == BeamAssembly.right :
            z = -z
            x = -x
            
        if direction== BeamAssembly.down :
            y = -y
            x = -x
        
        if (flip < 0):
            if "Z" in direction :
                x = -x
                y = -y
            else :
                x = -x
                z = -z
        
        if self.id_position == BeamAssembly.bottom:
            #print "Flicking beam values"
            y = -y
            x = -x
        
        return (x,y,z)
    
    def get_adapted_magnet_array(self):
        xx = []
        yy = []
        zz = []
        for i in range(self.id_length):
            x,y,z = self.get_adapeted_magnet(i)
            xx.append(x)
            yy.append(y)
            zz.append(z)
        return (xx,yy,zz)
    
    def magnet_total_sumation(self):
        xtotal = ytotal = ztotal = 0.0
        for i in range(self.id_length):
            x, y, z = self.get_adapeted_magnet(i)
            xtotal += x
            ytotal += y
            ztotal += z
        return xtotal**2 + ytotal**2 + ztotal**2
    
    def get_beam_length(self):
        return self.id_length*self.magdims[2]
    
    def create_b_array(self, xmin, xmax, xstep, zmin, zmax, zstep, magdims, mingap):
        '''
        use self.magdims for array sizes but use magdims for magnet size as the magnet could be halfsize or different
        '''
        length = self.get_beam_length();
        return mt.generate_B_array(xmin, xmax, xstep, zmin, zmax, zstep, -2*length, 2*length, self.magdims[2]/self.steps_per_magnet, magdims, mingap)
    
    def create_int_array(self, xmin, xmax, xstep, zmin, zmax, zstep, magdims, mingap):
        length = self.get_beam_length();
        #(b, fx, fz, fs, sx, sz, ss) = mt.generate_integral_array(xmin, xmax, xstep, 0.0, zmin, zmax, zstep, 0.0, -2*length, 2*length, self.magdims[2]/self.steps_per_magnet, 0.0, magdims, mingap)
        b = mt.generate_B_array_with_offsets(xmin, xmax, xstep, 0.0, zmin, zmax, zstep, 0.0, -2*length, 2*length, self.magdims[2]/self.steps_per_magnet, 0.0, magdims, mingap)
        #return (b, (fx, fz, fs), (sx, sz, ss))
        return b
    
    def create_int_array_with_offset(self, xmin, xmax, xstep, zmin, zmax, zstep, soff, magdims, mingap):
        length = self.get_beam_length();
        (b, fx, fz, fs, sx, sz, ss) = mt.generate_integral_array(xmin, xmax, xstep, 0.0, zmin, zmax, zstep, 0.0, -2*length, 2*length, self.magdims[2]/self.steps_per_magnet, soff, magdims, mingap)
        return (b, (fx, fz, fs), (sx, sz, ss))
    
    
    def create_b_array_with_offset(self, xmin, xmax, xstep, zmin, zmax, zstep, soff, magdims, mingap):
        '''
        use self.magdims for array sizes but use magdims for magnet size as the magnet could be halfsize or different
        '''
        length = self.get_beam_length();
        return mt.generate_B_array_with_offsets(xmin, xmax, xstep, 0.0, zmin, zmax, zstep, 0.0, -2*length, 2*length, self.magdims[2]/self.steps_per_magnet, soff, magdims, mingap)
    
    def calculate_b_contribution(self, magnet_number):
        x, y, z = self.get_adapeted_magnet(magnet_number)
        #print "Beam", magnet_number,x,y,z
        return mt.calculate_magnetic_components(x, y, z, self.b_arrays[magnet_number]);
    
    def build_b_arrays(self):
        if self.mag_array == None :
            offset = (self.id_length)*self.steps_per_magnet
            length = 3*offset
            x, y, z = self.get_adapeted_magnet(0)
            total = mt.calculate_magnetic_components(x, y, z, self.b_arrays[0][:,:,offset:offset+length,:,:])
            for i in range(1, self.id_length):
                if "E" in self.types[i-1] :
                    if "E" in self.types[i] :
                        offset -= self.steps_per_magnet/2
                    else :
                        offset -= self.steps_per_magnet*3/4
                else :
                    if "E" in self.types[i] :
                        offset -= self.steps_per_magnet*3/4
                    else :
                        offset -= self.steps_per_magnet
                x, y, z = self.get_adapeted_magnet(i)
                #print "Beam", i, self.types[i], x, y, z, offset
                total += mt.calculate_magnetic_components(x, y, z, self.b_arrays[i][:,:,offset:offset+length,:,:])
            if self.id_position == BeamAssembly.bottom:
                total[:,:,:,0] *= -1.0
                total[:,:,:,1] *= -1.0
            #total = np.roll(total, +14, 2)#Test - Ed
            mass = np.abs(total[total.shape[0]/2, total.shape[1]/2, :, 1])
            pos = (np.arange(total.shape[2]))
            com = np.average(pos,axis=0,weights=mass)
            com = int(np.round(com))
            self.mag_array = total[:,:,com-(self.trunc_length/2):com+(self.trunc_length/2),:]
        return self.mag_array
    
    def set_magnet(self, pos, magnet):
        self.mag_array = None
        self.magnets[pos] = magnet
    
    def flip_magnet(self, pos):
        # get the removed magnets field
        offset = (self.id_length)*self.steps_per_magnet
        length = 3*offset
        offset = (self.id_length-pos)*self.steps_per_magnet
        x, y, z = self.get_adapeted_magnet(pos)
        remove = mt.calculate_magnetic_components(x, y, z, self.b_arrays[pos][:,:,offset:offset+length,:,:])
        
        self.flip[pos] *= -1
        
        x, y, z = self.get_adapeted_magnet(pos)
        add = mt.calculate_magnetic_components(x, y, z, self.b_arrays[pos][:,:,offset:offset+length,:,:])
        
        modify = add - remove
        
        if self.id_position == BeamAssembly.bottom:
            modify[:,:,:,0] *= -1.0
            modify[:,:,:,1] *= -1.0
            
        
        if self.shimming:
            self.real_barray += modify[int(modify.shape[0]/2),int(modify.shape[1]/2),((modify.shape[2]-self.trunc_length))/2:-(modify.shape[2]-self.trunc_length)/2,:]
            #self.ppm.real_b_array += modify[int(modify.shape[0]/2),int(modify.shape[1]/2),((modify.shape[2]-self.trunc_length))/2:-(modify.shape[2]-self.trunc_length)/2,:]
        else :
            self.mag_array += modify[:,:,((modify.shape[2]-self.trunc_length))/2:-(modify.shape[2]-self.trunc_length)/2,:]
        
        
        #TODO Correct the integral arrays rather than resetting them
        self.mag_fintx_array = None
        self.mag_fintz_array = None
        self.mag_sintx_array = None
        self.mag_sintz_array = None
        
        return (modify, self.trunc_length)
    
    
    def swap_set_magnet(self, pos, type, key, flip):
        # get the removed magnets field
        offset = (self.id_length)*self.steps_per_magnet
        length = 3*offset
        offset = (self.id_length-pos)*self.steps_per_magnet
        x, y, z = self.get_adapeted_magnet(pos)
        remove = mt.calculate_magnetic_components(x, y, z, self.b_arrays[pos][:,:,offset:offset+length,:,:])
        
        magnet = self.magnets[pos]
        # replace this with a new one
        
        new_magnet = self.magnet_pool.magnet_sets[type].borrow_magnet(key)
        if new_magnet == None:
            print "magnet Not found!!! **************************************************"
            self.magnets[pos] = new_magnet;
            self.magnet_pool.magnet_sets[type].return_magnet(magnet)
        
        # and flip this
        self.flip[pos] = flip
        
        x, y, z = self.get_adapeted_magnet(pos)
        add = mt.calculate_magnetic_components(x, y, z, self.b_arrays[pos][:,:,offset:offset+length,:,:])
        
        modify = add - remove
        if self.id_position == BeamAssembly.bottom:
            modify[:,:,:,0] *= -1.0
            modify[:,:,:,1] *= -1.0
        
        if self.shimming:
            self.real_barray += modify[int(modify.shape[0]/2),int(modify.shape[1]/2),((modify.shape[2]-self.trunc_length))/2:-(modify.shape[2]-self.trunc_length)/2,:]
            #self.ppm.real_b_array += modify[int(modify.shape[0]/2),int(modify.shape[1]/2),((modify.shape[2]-self.trunc_length))/2:-(modify.shape[2]-self.trunc_length)/2,:]
        else :
            self.mag_array += modify[:,:,((modify.shape[2]-self.trunc_length))/2:-(modify.shape[2]-self.trunc_length)/2,:]
        
        #TODO Correct the integral arrays rather than resetting them
        self.mag_fintx_array = None
        self.mag_fintz_array = None
        self.mag_sintx_array = None
        self.mag_sintz_array = None
        
        return (modify, self.trunc_length)
    
    def swap_a_magnet(self, pos):
        mtype = self.types[pos]
        while mtype == "AA":
            # dont swap out air gaps
            pos = rand.randint(0,self.id_length-1)
            mtype = self.types[pos]
        
        key = self.magnet_pool.magnet_sets[mtype].get_random_available_key()
        
        flip = val = (rand.randint(0,1)*2)-1
        
        return self.swap_set_magnet(pos, mtype, key, flip)
    
    def swap_magnet(self):
        pos = rand.randint(0, self.id_length-1)
        return self.swap_a_magnet(pos)
    
    
    def calculate_phase_error(self):
        b_array = self.build_b_arrays()[0,0,:,:].squeeze()
        (self.pherr, self.traj) = mt.calculate_phase_error(self.periods,
                                                           self.magdims[2]/float(self.steps_per_magnet),
                                                           4*self.steps_per_magnet,
                                                           b_array.shape[0],
                                                           b_array)
        b_array = self.top.build_b_arrays()[0,0,:,:].squeeze()
        (self.pherr, self.traj) = mt.calculate_phase_error(self.periods,
                                                           self.magdims[2]/float(self.steps_per_magnet),
                                                           4*self.steps_per_magnet,
                                                           b_array.shape[0],
                                                           b_array)
    
    def build_integral_arrays(self):
        if (self.mag_fintx_array == None) :
            (x,z,s) = self.get_adapeted_magnet(0);
            (fintx, fintz, fints) = self.fint_arrays[0]
            (sintx, sintz, sints) = self.sint_arrays[0]
            (self.mag_fintx_array,self.mag_fintz_array,self.mag_sintx_array,self.mag_sintz_array) = mt.calculate_integral_component(x, z, s, fintx, fintz, sintx, sintz)
            
            for i in range(1, self.id_length):
                (x,z,s) = self.get_adapeted_magnet(i);
                (fintx, fintz, fints) = self.fint_arrays[i]
                (sintx, sintz, sints) = self.sint_arrays[i]
                (firstix,firstiz,secondix,secondiz) = mt.calculate_integral_component(x, z, s, fintx, fintz, sintx, sintz)
                self.mag_fintx_array += firstix
                self.mag_fintz_array += firstiz
                self.mag_sintx_array += secondix
                self.mag_sintz_array += secondiz
        
        return (self.mag_fintx_array,self.mag_fintz_array,self.mag_sintx_array,self.mag_sintz_array)


class Device(object):
    
    def __init__(self):
        pass
    
class PPM(Device):
    
    def __init__(self, magnet_set, periods=2, 
                symetry=BeamAssembly.symetric, 
                random=False, magdims=[41.,16.,6.75], 
                steps_per_magnet=12, offset=10.0, presort = None, 
                bfields = None):
        self.magnets = magnet_set
        self.periods = periods
        self.symetry = symetry
        self.magdims = magdims
        self.offset = offset
        self.steps_per_magnet = steps_per_magnet
        self.presort = presort
        self.bfields = bfields
        self.shimming = False
        if bfields != None:
            self.shimming = True
        self.real_b_array = None
        self.top_beam = BeamAssembly(periods, symetry, BeamAssembly.top, self.magnets, presort=presort, random=random, magdims=magdims, offset=offset, shimming=self.shimming)
        self.bottom_beam = BeamAssembly(periods, symetry, BeamAssembly.bottom, self.magnets, presort=presort, random=random, magdims=magdims, offset=offset, shimming=self.shimming)
        self.ReadBFields()
    
    def __eq__(self, other):
        for i in range(self.get_id_length()) :
            if self.top_beam.magnets[i] != other.top_beam.magnets[i] :
                return False
            if self.bottom_beam.magnets[i] != other.bottom_beam.magnets[i] :
                return False
        return True
    
    def randomize(self):
        self.magnets.return_all_magnets()
        self.top_beam = BeamAssembly(self.periods, self.symetry, BeamAssembly.top, self.magnets, magdims=self.magdims, offset=self.offset, random=True)
        self.bottom_beam = BeamAssembly(self.periods, self.symetry, BeamAssembly.bottom, self.magnets, magdims=self.magdims, offset=self.offset, random=True)
    
    
    def swap_magnet(self, beam, position, type, key, flip):
        # pick top or bottom beam
        swapbeam = self.top_beam
        if beam == 0 :
            swapbeam = self.bottom_beam
        
        (modify, trunc_length) = swapbeam.swap_set_magnet(position, type, key, flip)
        self.real_b_array += modify[int(modify.shape[0]/2),int(modify.shape[1]/2),((modify.shape[2]-trunc_length))/2:-(modify.shape[2]-trunc_length)/2,:]
        
    def flip_magnet(self, beam, position):
        # pick top or bottom beam
        flipbeam = self.top_beam
        if beam == 0 :
            flipbeam = self.bottom_beam
        
        (modify, trunc_length) = flipbeam.flip_magnet(position)
        self.real_b_array += modify[int(modify.shape[0]/2),int(modify.shape[1]/2),((modify.shape[2]-trunc_length))/2:-(modify.shape[2]-trunc_length)/2,:]
    
    def swap_one_magnet(self):
        self.swap_magnet(rand.randint(0,1),rand.randint(0,len(self.top_beam.magnets)-1))
        
    def flip_one_magnet(self):
        self.flip_magnet(rand.randint(0,1),rand.randint(0,len(self.top_beam.magnets)-1))
    
    def get_id_length(self):
        return self.bottom_beam.id_length
    
    def magnet_total_sumation(self):
        return self.top_beam.magnet_total_sumation() + self.bottom_beam.magnet_total_sumation()
    
    def build_b_array(self):
        return self.top_beam.build_b_arrays() + self.bottom_beam.build_b_arrays()
    
    def ReadBFields(self):
        if self.bfields == None:
            return None
        else:
            real_b_fields = []
            top_beam = []
            bottom_beam = []
            rbf = open(self.bfields)
            for line in rbf:
                vals = line.split()
                #TotBx, TotBz, TotBs, TopBx, TopBz, TopBs, BotBx, BotBz, BotBs
                real_b_fields.append((float(vals[0]), float(vals[1]), float(vals[2])))
                top_beam.append((float(vals[3]), float(vals[4]), float(vals[5])))
                bottom_beam.append((float(vals[6]), float(vals[7]), float(vals[8])))
            
            self.real_b_array = np.array(real_b_fields)
            self.top_beam.real_barray = np.array(top_beam)
            self.bottom_beam.real_barray = np.array(bottom_beam)
            
    def calculate_phase_error(self):
        if self.shimming == False:
            b_array = self.top_beam.build_b_arrays()
            b_array = b_array[b_array.shape[0]/2,0,:,:].squeeze()
            (self.top_pherr, self.top_traj) = mt.calculate_phase_error(self.periods,
                                                               self.magdims[2]/float(self.steps_per_magnet),
                                                               4*self.steps_per_magnet,
                                                               b_array.shape[0],
                                                               b_array)
            b_array = self.bottom_beam.build_b_arrays()
            b_array = b_array[b_array.shape[0]/2,0,:,:].squeeze()
            (self.bottom_pherr, self.bottom_traj) = mt.calculate_phase_error(self.periods,
                                                               self.magdims[2]/float(self.steps_per_magnet),
                                                               4*self.steps_per_magnet,
                                                               b_array.shape[0],
                                                               b_array)
            b_array = self.build_b_array()
            
            #Calculate integrals here
            #[0] = firstIX; [1]=firstIZ, [2] = secondIX; [3] = secondIZ
            integrals = np.zeros([4,b_array.shape[0]])
            
            sstep=self.magdims[2]/float(self.steps_per_magnet)
            smin=-(np.shape(b_array)[2]/2)*sstep
            smax=-smin
            
            integrals[0,:] = np.sum(b_array[:,0,:,0], axis=1)*1e4*sstep
            integrals[1,:] = np.sum(b_array[:,0,:,1], axis=1)*1e4*sstep
            scale_factor = -np.arange(smin, smax, sstep)
            
            integrals[2,:] = -np.sum(b_array[:,0,:,0]*scale_factor, axis=1)*1e4*sstep
            integrals[3,:] = -np.sum(b_array[:,0,:,1]*scale_factor, axis=1)*1e4*sstep
            
            
            b_array = b_array[b_array.shape[0]/2,0,:,:].squeeze()
            (self.pherr, self.traj) = mt.calculate_phase_error(self.periods,
                                                               self.magdims[2]/float(self.steps_per_magnet),
                                                               4*self.steps_per_magnet,
                                                               b_array.shape[0],
                                                               b_array)
        
        if self.shimming == True:
            b_array = self.top_beam.real_barray
            (self.top_pherr, self.top_traj) = mt.calculate_phase_error(self.periods,
                                                               self.magdims[2]/float(self.steps_per_magnet),
                                                               4*self.steps_per_magnet,
                                                               b_array.shape[0],
                                                               b_array)
            b_array = self.bottom_beam.real_barray
            (self.bottom_pherr, self.bottom_traj) = mt.calculate_phase_error(self.periods,
                                                               self.magdims[2]/float(self.steps_per_magnet),
                                                               4*self.steps_per_magnet,
                                                               b_array.shape[0],
                                                               b_array)
            b_array = self.real_b_array
            
            #Calculate integrals here
            #[0] = firstIX; [1]=firstIZ, [2] = secondIX; [3] = secondIZ
            integrals = np.zeros([4,1])
            
            sstep=self.magdims[2]/float(self.steps_per_magnet)
            smin=-(np.shape(b_array)[0]/2)*sstep
            smax=-smin
            
            integrals[0,:] = np.sum(b_array[:,0])*1e4*sstep
            integrals[1,:] = np.sum(b_array[:,1])*1e4*sstep
            scale_factor = -np.arange(smin, smax, sstep)
            
            integrals[2,:] = -np.sum(b_array[:,0]*scale_factor)*1e4*sstep
            integrals[3,:] = -np.sum(b_array[:,1]*scale_factor)*1e4*sstep
            
            
            #b_array = b_array[b_array.shape[0]/2,0,:,:].squeeze()
            (self.pherr, self.traj) = mt.calculate_phase_error(self.periods,
                                                               self.magdims[2]/float(self.steps_per_magnet),
                                                               4*self.steps_per_magnet,
                                                               b_array.shape[0],
                                                               b_array)            
        
        return (self.top_pherr, self.top_traj, self.bottom_pherr, self.bottom_traj, self.pherr, self.traj, integrals)
    
    def build_integral_arrays(self):
        (fx1, fz1, sx1, sz1) = self.top_beam.build_integral_arrays()
        (fx2, fz2, sx2, sz2) = self.bottom_beam.build_integral_arrays()
        return (fx1+fx2, fz1+fz2, sx1+sx2, sz1+sz2)
    

    def calculate_beam_fittnes_elements(self):
        #(fintx, fintz, sintx, sintz) = self.build_integral_arrays()
        (top_pherr, top_traj, bottom_pherr, bottom_traj, pherr, traj, integrals) = self.calculate_phase_error()
        (fintx, fintz, sintx, sintz) = integrals
        (strx, strz) = mt.straightness(traj, self.periods)
        IXMax  = np.max(np.abs(fintx))
        IYMax  = np.max(np.abs(fintz))
        IX0    = fintx[fintx.shape[0]/2]
        IY0    = fintz[fintz.shape[0]/2]
        I2XMax = np.max(np.abs(sintx))
        I2YMax = np.max(np.abs(sintz))
        I2X0   = sintx[sintx.shape[0]/2]
        I2Y0   = sintz[sintz.shape[0]/2]
        RMS_A  = pherr
        RMS_T  = top_pherr
        RMS_B  = bottom_pherr
        X_TRAJ = strx
        Y_TRAJ = strz
        
        
        return (IXMax, IYMax, IX0, IY0, I2XMax, I2YMax, I2X0, I2Y0, RMS_A, RMS_T, RMS_B, X_TRAJ, Y_TRAJ)
    
    def evaluate_ppm(self):
        (IXMax, IYMax, IX0, IY0, I2XMax, I2YMax, I2X0, I2Y0, RMS_A, RMS_T, RMS_B, X_TRAJ, Y_TRAJ) = self.calculate_beam_fittnes_elements()
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
    
    def report_beam(self, beam):
        types = beam.types
        dirs = beam.direction
        mag = beam.magnets
        x,y,z = beam.get_adapted_magnet_array()
        
        for i in range(len(types)) :
            print("%s\t%s\t%s\t%1.8f\t%1.8f\t%1.8f" % (types[i], dirs[i], mag[i], x[i], y[i], z[i]))
        print("%s\t%s\t%s\t%1.8f\t%1.8f\t%1.8f" % ("  ","  ", "  ", sum(x), sum(y), sum(z)))
        

    def report(self):
        print "Top Beam"
        self.report_beam(self.top_beam)
        print "Bottom Beam"
        self.report_beam(self.bottom_beam)
    
    def print_to_file(self, filename):
        file = open(filename, 'w')
        types = {}
        types[MagnetStore.horizontal_end] = (4,"Hhalf")
        types[MagnetStore.vertical_end]   = (3,"Vhalf")
        types[MagnetStore.horizontal]     = (2,"Hfull")
        types[MagnetStore.vertical]       = (1,"Vfull")
        types[MagnetStore.air_gap]        = (0,"Air  ")
        directions = {}
        directions[BeamAssembly.up]    =  (1, "UP")
        directions[BeamAssembly.down]  = (-1, "DW")
        directions[BeamAssembly.right] =  (1, "RG")
        directions[BeamAssembly.left]  = (-1, "LF")
        directions["NN"]  = (0, "NN")
        flip = {}
        flip[-1] = (-1, "R")
        flip[1]  = (1, "N")
        
        for beam  in (self.top_beam, self.bottom_beam):
            beam_number = 2
            if beam == self.top_beam:
                beam_number = 1
            for i in range(beam.id_length):
                (type_number, type_name) = types[beam.types[i]]
                (dir_number, dir_name) = directions[beam.direction[i]]
                (flip_number, flip_name) = flip[beam.flip[i]]
                mag_number = 0
                try :
                    mag_number = int(beam.magnets[i])
                except :
                    pass
                if not mag_number == 0 :
                    file.write("%5i %4i %4i %4i %4i %4i %10s %3s %2s\n" % (beam_number, i+1, type_number, dir_number, flip_number, mag_number, type_name, dir_name, flip_name))
            file.write("\n")
        file.close()
    
    def save_to_h5(self, filename):
        f = h5py.File(filename, 'w')
        
        # create the whole system as a big array
        offset = (self.top_beam.id_length)*self.steps_per_magnet
        length = 3*offset
        xt, yt, zt = self.top_beam.get_adapeted_magnet(0)
        xb, yb, zb = self.bottom_beam.get_adapeted_magnet(0)
        totalT = mt.calculate_magnetic_components(xt, yt, zt, self.top_beam.b_arrays[0][:,:,offset:offset+length,:,:])
        totalB = mt.calculate_magnetic_components(xb, yb, zb, self.bottom_beam.b_arrays[0][:,:,offset:offset+length,:,:])
        totalB[:,:,:,0] *= -1.0
        totalB[:,:,:,1] *= -1.0
        total = totalB + totalT
        dataT = f.create_dataset("Top_B_Elements", (self.top_beam.id_length,)+totalT.shape, totalT.dtype)
        dataB = f.create_dataset("Bottom_B_Elements", (self.top_beam.id_length,)+totalB.shape, totalB.dtype)
        data  = f.create_dataset("B_Elements", (self.top_beam.id_length,)+total.shape, total.dtype)
        dataT[0,:,:,:,:] = totalT
        dataB[0,:,:,:,:] = totalB
        data[0,:,:,:,:] = total
        
        for i in range(1, self.top_beam.id_length):
            if "E" in self.top_beam.types[i-1] :
                if "E" in self.top_beam.types[i] :
                    offset -= self.steps_per_magnet/2
                else :
                    offset -= self.steps_per_magnet*3/4
            else :
                if "E" in self.top_beam.types[i] :
                    offset -= self.steps_per_magnet*3/4
                else :
                    offset -= self.steps_per_magnet
            xt, yt, zt = self.top_beam.get_adapeted_magnet(i)
            xb, yb, zb = self.bottom_beam.get_adapeted_magnet(i)
            #print "Beam", i, self.types[i], x, y, z, offset
            nextT = mt.calculate_magnetic_components(xt, yt, zt, self.top_beam.b_arrays[i][:,:,offset:offset+length,:,:])
            nextB = mt.calculate_magnetic_components(xb, yb, zb, self.bottom_beam.b_arrays[i][:,:,offset:offset+length,:,:])
            nextB[:,:,:,0] *= -1.0
            nextB[:,:,:,1] *= -1.0
            next = nextT + nextB
            dataT[i,:,:,:,:] = nextT
            dataB[i,:,:,:,:] = nextB
            data[i,:,:,:,:] = next
            total += next
        total  = f.create_dataset("B", total.shape, total.dtype, total);
        f.close()

if __name__ == "__main__" :
    import optparse
    usage = "%prog [options] horizontal_magnets, vertical_magnets, horizontal_end_magnets, vertical_end_magnets"
    parser = optparse.OptionParser(usage=usage)
    parser.add_option("-o", "--output", dest="output", help="Select the file to write the output to", default=None)
    parser.add_option("-p", "--periods", dest="periods", help="Set the number of full periods for the Device", default=5, type="int")
    parser.add_option("-s", "--symmetric", dest="symmetric", help="Set the device to symmetric rather then Anti-symmetric", action="store_true", default=False)
    parser.add_option("-r", "--random", dest="random", help="Choose the magnets randomly instead of sequentialy", action="store_true", default=False)
    parser.add_option("-v", "--verbose", dest="verbose", help="display debug information", action="store_true", default=False)
    
    (options, args) = parser.parse_args()
    
    if options.verbose:
        print "Horizontal Magnets     = %s" % args[0]
        print "Vertical Magnets       = %s" % args[1]
        print "Horizontal End Magnets = %s" % args[2]
        print "Vertical End Magnets   = %s" % args[3]
    
    # Add all the magnets
    mag = AllMagnets()
    mag.add_magnet_set(MagnetStore.horizontal, args[0])
    mag.add_magnet_set(MagnetStore.vertical, args[1])
    mag.add_magnet_set(MagnetStore.horizontal_end, args[2])
    mag.add_magnet_set(MagnetStore.vertical_end, args[3])
    
    if options.verbose:
        import pprint
        print "Magnet Sets"
        pprint.pprint(mag.magnet_sets)
    
    ## Create the device
    symmetry = BeamAssembly.antisymetric
    if options.symmetric:
        symmetry = BeamAssembly.symetric
        
    ppm = PPM(mag, periods=options.periods, symetry=symmetry, random=options.random)
    
    if options.verbose:
        ppm.report()
    
    if not options.output == None :
        ppm.print_to_file(options.output)
