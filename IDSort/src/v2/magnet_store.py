'''
Created on 15 Feb 2013

@author: ssg37927

x = x,  y = z,  z = s

'''

import magnet_tools as mt
import numpy as np

class MagnetStore(object):
    ''' 
    object which contains all the real magnets and there values, 
    but not the order of them in the arrays
    '''
    
    HORIZONTAL = "HH"
    VERTICAL = "VV"
    HORIZONTAL_END = "HE"
    VERTICAL_END = "VE"
    AIR_GAP = "AA"
    
    def __init__(self):
        self.magnets = {}
    
    def load_magnets(self, mag_type, filename):
        f = open(self.filename)
        mags = {}
        for line in f:
            vals = line.split()
            dict[vals[0]] = (float(vals[1]), float(vals[2]), float(vals[3]))
        self.magnets[mag_type] = mags


class BArray(object):
    ''' 
    Simple class which contains a single BArray for use in lookups
    It can be specified on construction and used as required. 
    '''
    
    def __init__(self, magdims=[41.,16.,5.25],
                 xmin=0., xmax=1., xstep=1., xoff=0.,
                 zmin=0., zmax=1., zstep=1., zoff=0.,
                 smin=0., smax=1., sstep=1., soff=0.,
                 mingap=5.0):
        
        self.barray = mt.generate_B_array_with_offsets(
            xmin, xmax, xstep, xoff, 
            zmin, zmax, zstep, zoff, 
            smin, smax, sstep, soff, 
            magdims, mingap)


class Beam(object):
    ''' 
    This class contains all the information about a beam for calculating the 
    full barray from it, however it should not include the actual magnet positions
    in the beam array
    '''
    
    SYMETRIC = "SYM"
    ANTISYMETRIC = "ASYM"
    
    TOP = "TOP"
    BOTTOM = "BOTTOM"
    
    UP = "Y+"
    DOWN = "Y-"
    LEFT = "Z+"
    RIGHT = "Z-"
    
    def __init__(self, id_type, position, periods,
                magdims=[41.,16.,5.25],
                xmin=0., xmax=1., xstep=5.,
                zmin=0., zmax=1., zstep=1,
                steps_per_magnet=12, mingap=5.0,
                offset=10.0, shimming=False):
        
        # some specific ID parameters
        self.id_type = id_type
        self.id_position = position
        self.id_periods = periods
        self.id_steps_per_magnet = steps_per_magnet
        
        # the magnet paramets
        self.mag_dims = np.array(magdims);
        self.mag_steps = steps_per_magnet
        
        #TODO remove this if unneeded
        #self.trunc_length=(periods+16)*4*steps_per_magnet
        if(self.id_type == Beam.SYMETRIC):
            self.id_length = self.id_periods*4+9
        else :
            self.id_length = self.id_periods*4+5
            
        
        self.create_type_list()
        self.create_direction_list()
        
        self.mag_array = None
        self.mag_fintx_array = None
        self.mag_fintz_array = None
        self.mag_sintx_array = None
        self.mag_sintz_array = None
        self.generate_B_List(xmin, xmax, xstep, zmin, zmax, zstep, mingap, offset)
    
    def get_beam_length(self):
        return self.id_length*self.mag_dims[2]
    
    def create_type_list(self):
        # do the first end
        self.types = []
        start = 0
        stop = 0
        vertical = False
        if(self.id_type == Beam.SYMETRIC):
            self.types.append(MagnetStore.HORIZONTAL_END)
            self.types.append(MagnetStore.AIR_GAP)
            self.types.append(MagnetStore.VERTICAL_END)
            self.types.append(MagnetStore.HORIZONTAL_END)
            start, stop = (4, self.id_length-4)
            vertical = True
        else :
            self.types.append(MagnetStore.HORIZONTAL_END)
            self.types.append(MagnetStore.VERTICAL_END)
            start, stop = (2, self.id_length-2)
        
        # now put in all the middle periods
        for i in range(start, stop):
            if vertical :
                self.types.append(MagnetStore.VERTICAL)
                vertical = False
            else :
                self.types.append(MagnetStore.HORIZONTAL)
                vertical = True
        
        # finaly add in the other end
        if(self.id_type == Beam.SYMETRIC):
            self.types.append(MagnetStore.HORIZONTAL_END)
            self.types.append(MagnetStore.VERTICAL_END)
            self.types.append(MagnetStore.AIR_GAP)
            self.types.append(MagnetStore.HORIZONTAL_END)
        else :
            self.types.append(MagnetStore.VERTICAL_END)
            self.types.append(MagnetStore.HORIZONTAL_END)
    
    def create_direction_list(self):
        self.direction = []
        for i in range(0,self.id_length-1,4):
            if(self.id_position == Beam.TOP) :
                self.direction.append(Beam.LEFT)
                self.direction.append(Beam.UP)
                self.direction.append(Beam.RIGHT)
                self.direction.append(Beam.DOWN)
            else :
                self.direction.append(Beam.RIGHT)
                self.direction.append(Beam.UP)
                self.direction.append(Beam.LEFT)
                self.direction.append(Beam.DOWN)
                
        # append the last element
        if(self.id_position == Beam.TOP):
            self.direction.append(Beam.LEFT)
        else :
            self.direction.append(Beam.RIGHT)
        
        # Sort out porblems with the air holes
        if self.id_type == Beam.SYMETRIC:
            self.direction.insert(1, "NN")
            self.direction.insert(self.id_length-2, "NN")
            self.direction.pop()
            self.direction.pop()
    
    def generate_B_List(self, xmin, xmax, xstep, zmin, zmax, zstep, mingap, offset):
        '''
        offset is the amount that the air gap in different than a normal block
        or that the HE magnet is bigger
        '''
        self.b_arrays = []
        self.fint_arrays = []
        self.sint_arrays = []
        
        # full size magnets here
        print "Creating BeamAssembly.barray"
        #(BeamAssembly.barray, BeamAssembly.fint, BeamAssembly.sint) = self.create_int_array(xmin, xmax, xstep, zmin, zmax, zstep, self.magdims, mingap)
        self.barray = mt.generate_B_array_with_offsets(xmin, xmax, xstep, 0.0, zmin, zmax, zstep, 0.0, -2 * self.get_beam_length(), 2 * self.get_beam_length(), self.mag_dims[2] / self.mag_steps, 0.0, self.mag_dims, mingap)
        
        for i in range(self.id_length):
            self.b_arrays.append(self.barray)
            #self.fint_arrays.append(self.fint)
            #self.sint_arrays.append(self.sint)
        
        if self.id_type == Beam.ANTISYMETRIC :
            #print "self.magdims is ", self.magdims
            magdims = np.array(self.mag_dims)
            #print "magdims is ", magdims
            magdims[2] = magdims[2] / 2.0
            #print "magdims for VE", magdims 
            print "Creating BeamAssembly.start_VE_barray"
            #(BeamAssembly.start_VE_barray, BeamAssembly.start_VE_fint, BeamAssembly.start_VE_sint) = self.create_int_array(xmin, xmax, xstep, zmin, zmax, zstep, magdims, mingap)
            self.start_VE_barray = mt.generate_B_array_with_offsets(xmin, xmax, xstep, 0.0, zmin, zmax, zstep, 0.0, -2 * self.get_beam_length(), 2 * self.get_beam_length(), self.mag_dims[2] / self.mag_steps, 0.0, magdims, mingap)
            print "Creating BeamAssembly.end_VE_barray"
            #(BeamAssembly.end_VE_barray, BeamAssembly.end_VE_fint, BeamAssembly.end_VE_sint) = self.create_int_array(xmin, xmax, xstep, zmin, zmax, zstep, magdims, mingap)
            self.end_VE_barray = mt.generate_B_array_with_offsets(xmin, xmax, xstep, 0.0, zmin, zmax, zstep, 0.0, -2 * self.get_beam_length(), 2 * self.get_beam_length(), self.mag_dims[2] / self.mag_steps, 0.0, magdims, mingap)
            
            magdims[2] = magdims[2] + offset
            #print "magdims for HE", magdims 
            print "Creating BeamAssembly.start_HE_barray"
            #(BeamAssembly.start_HE_barray, BeamAssembly.start_HE_fint, BeamAssembly.start_HE_sint) = self.create_int_array_with_offset(xmin, xmax, xstep, zmin, zmax, zstep, -(offset/2.0), magdims, mingap)
            self.start_HE_barray = mt.generate_B_array_with_offsets(xmin, xmax, xstep, 0.0, zmin, zmax, zstep, 0.0, -2 * self.get_beam_length(), 2 * self.get_beam_length(), self.mag_dims[2] / self.mag_steps, -offset / 2.0, magdims, mingap)
            
            print "Creating BeamAssembly.end_HE_barray"
            #(BeamAssembly.end_HE_barray, BeamAssembly.end_HE_fint, BeamAssembly.end_HE_sint) = self.create_int_array_with_offset(xmin, xmax, xstep, zmin, zmax, zstep, (offset/2.0), magdims, mingap)
            self.end_HE_barray = mt.generate_B_array_with_offsets(xmin, xmax, xstep, 0.0, zmin, zmax, zstep, 0.0, -2 * self.get_beam_length(), 2 * self.get_beam_length(), self.mag_dims[2] / self.mag_steps, offset / 2.0, magdims, mingap)
            
            for i in range(self.id_length):
                if self.types[i] == MagnetStore.HORIZONTAL_END:
                    if i < (self.id_length / 2):
                        self.b_arrays[i] = self.start_HE_barray
                        #self.fint_arrays[i] = self.start_HE_fint
                        #self.sint_arrays[i] = self.start_HE_sint
                    else :
                        self.b_arrays[i] = self.end_HE_barray
                        #self.fint_arrays[i] = self.end_HE_fint
                        #self.sint_arrays[i] = self.end_HE_sint
                if self.types[i] == MagnetStore.VERTICAL_END:
                    if i < (self.id_length / 2):
                        self.b_arrays[i] = self.start_VE_barray
                        #self.fint_arrays[i] = self.start_VE_fint
                        #self.sint_arrays[i] = self.start_VE_sint
                    else :
                        self.b_arrays[i] = self.end_VE_barray
                        #self.fint_arrays[i] = self.end_VE_fint
                        #self.sint_arrays[i] = self.end_VE_sint

#TODO need to think about how to do this list properly.
class BeamDiscription(object):
    '''
    This is the description of the beam in terms of real magnets
    '''
    
    def __init__(self, beam):
        self.beam = beam
        self.flip = []
        self.magnets = []
    
    
class MagnetProvider(object):
    '''
    Class which contains which magnets have been used in the assembly
    '''
    
    def __init__(self, magnet_store):
        self.magnet_store = magnet_store
        pass


class IDDescription(object):
    '''
    Description of the whole system which can be optimised.
    '''
    
    def __init__(self, beams, magnet_store):
        self.beam_descriptions = []
        for beam in beams:
            self.beam_descriptions.append(BeamDiscription(beam))
        self.magnet_provider = MagnetProvider(magnet_store)
        pass

# OLD CODE BELOW!!!!!

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
