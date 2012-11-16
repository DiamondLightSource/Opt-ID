'''
Created on Dec 5, 2011

@author: gdy32713
'''
from __future__ import print_function

import numpy as np
import time as tm

def print_timing(func):    
    def wrapper(*arg):        
        t1 = tm.time()
        res=func(*arg)  
        t2 = tm.time()        
        print ('%s took %0.3f s' % (func.func_name, (t2-t1)))
        return res        
    return wrapper

class IDDevice(object):
    '''
    classdocs
    '''

#b_envelope is ('width in mm','extra periods of array','S steps per period')
    def __init__(self, idtype, symmetry, nperiods, period, mingap, magdims, b_envelope, mag_collection):
        '''
        Constructor
        '''
        self.idtype=idtype
        self.symmety=symmetry
        self.nperiods = nperiods
        self.period = period
        self.mingap = mingap
        self.magdims=magdims
        self.b_envelope=b_envelope
        self.mag_coll=mag_collection
        self.A=np.array([0.,0.,0.,0.,0.,0.,0.,0.])
        self.B=self.C=self.A
        self.I1=self.I2=0.
        self.corners=np.array([(self.magdims[0]/2,-self.mingap/2,self.magdims[2]/2),
                               (-self.magdims[0]/2,-self.mingap/2-self.magdims[1],self.magdims[2]/2),
                               (-self.magdims[0]/2,-self.mingap/2,-self.magdims[2]/2),
                               (self.magdims[0]/2,-self.mingap/2-self.magdims[1],-self.magdims[2]/2),
                               (-self.magdims[0]/2,-self.mingap/2,self.magdims[2]/2),
                               (self.magdims[0]/2,-self.mingap/2-self.magdims[1],self.magdims[2]/2),
                               (self.magdims[0]/2,-self.mingap/2,-self.magdims[2]/2),
                               (-self.magdims[0]/2,-self.mingap/2-self.magdims[1],-self.magdims[2]/2)])
        
        
        self.b_array=np.array([])
        self.x=np.linspace(-self.b_envelope[0]/2, self.b_envelope[0]/2,11)
        self.s=np.linspace(-(self.period*(self.nperiods+self.b_envelope[1])),(self.period*(self.nperiods+self.b_envelope[1])),2*((self.nperiods+self.b_envelope[1])*self.period*self.b_envelope[2])+1)
        self.b=np.empty(3)
        
    def fortPMB_NEW(self,testpoint,m,i,s_offset):
        '''This function Calculates the B-field in a single orientation according to the calling function
        It's pretty much a carbon-copy of the FORTRAN code
        
        '''

        B=0.0

        V1=np.array([-self.magdims[0]/2,-self.mingap/2-self.magdims[1],-self.magdims[2]/2+s_offset])
        V2=np.array([self.magdims[0]/2,-self.mingap/2,self.magdims[2]/2+s_offset])
        
        r1=np.zeros(3)
        r2=np.zeros(3)
        
        for L in range(3):
            r1[L]=testpoint[L]-V1[L]
            r2[L]=testpoint[L]-V2[L]
            
        for j in range(3):
            I1=0.
            I2=0.
            if j==i:
                B=B
            else:
                k=3-i-j
                r1i=r1[i]
                r1j=r1[j]
                r2i=r2[i]
                r2j=r2[j]
                r1k=r1[k]
                r2k=r2[k]
#                r1k=-r2[k]
#                r2k=-r1[k]
                
                a1=np.sqrt(r2i*r2i+r2j*r2j+r2k*r2k)
                a2=np.sqrt(r1i*r1i+r1j*r1j+r2k*r2k)
                a3=np.sqrt(r1i*r1i+r2j*r2j+r1k*r1k)
                a4=np.sqrt(r2i*r2i+r1j*r1j+r1k*r1k)
                a5=np.sqrt(r1i*r1i+r2j*r2j+r2k*r2k)
                a6=np.sqrt(r2i*r2i+r1j*r1j+r2k*r2k)
                a7=np.sqrt(r2i*r2i+r2j*r2j+r1k*r1k)
                a8=np.sqrt(r1i*r1i+r1j*r1j+r1k*r1k)
        
                
                b2=r1i*r2k/(r1j*a2)
                b4=r2i*r1k/(r1j*a4)
                b6=r2i*r2k/(r1j*a6)
                b8=r1i*r1k/(r1j*a8)
        
                b1=r2i*r2k/(r2j*a1)
                b3=r1i*r1k/(r2j*a3)
                b5=r1i*r2k/(r2j*a5)
                b7=r2i*r1k/(r2j*a7)
        
                I1=(np.arctan(b1)+np.arctan(b2)+np.arctan(b3)+np.arctan(b4)-np.arctan(b5)-np.arctan(b6)-np.arctan(b7)-np.arctan(b8))
        
                c1=a1+r2k
                c2=a2+r2k
                c3=a3+r1k
                c4=a4+r1k
                c5=a5+r2k
                c6=a6+r2k
                c7=a7+r1k
                c8=a8+r1k
        
                I2=(np.log(c1*c2*c3*c4/(c5*c6*c7*c8)))
        
                B=B-m[i]*I1/(4*np.pi)
                B=B-m[j]*I2/(4*np.pi)

        return B
    
    def wrapCalcB(self,testpoint,s_offset):
        '''This function takes the arguments 'testpoint' and 's_offset'
        'testpoint' requires an array of floats of length 3 describing the [x,z,s] co-ordinates of the point under consideration
        's_offset' requires a float that describes the s-direction offset of the magnet block
        
        This function calls the main field calculating function, and outputs a 3x3 matrix of the form
        [[Bx(x), Bz(x), Bs(x)]
         [Bx(z), Bz(z), Bs(z)]
         [Bx(s), Bz(s), Bs(s)]].
         
         To calculate the real field component of any block need to get real data sum contributions such that
         Bx=Bx(x)*Mx + Bx(z)*Mz + Bx(s)*Ms'''
        B=np.zeros((3,3))
        for i in range(3):
            m=np.zeros(3)
            m[i]=1
            for j in range(3):
                B[i][j]= self.fortPMB_NEW(testpoint,m,j,s_offset)
        
#        print(B)
        return B


'Testing area'    
mag=np.array([41.,16.,5.25])
barray=(25.,6.,20.) #NA
collection=3 #NA
testpoint=np.array([0.,2.5,4.])
s_offset=5.25

id1=IDDevice("PPM","asym",80.,22.,5.,mag,barray,collection)

B=id1.wrapCalcB(testpoint,s_offset)    

print(B)


# test for mark
x = []
y = []
z = []
for i in range(-1000, 1000):
    testpoint=np.array([0.,2.5,i*0.1])
    B=id1.wrapCalcB(testpoint,s_offset)
    print(B)
    x.append(np.array(B))
    y.append(B[1][1])
    z.append(B[2][2])

import scisoftpy as dnp
all = np.array(x)
dnp.plot.line(dnp.arange(-100.0, 100.0, 0.1), [all[:,1,1]])



help(id1.wrapCalcB)