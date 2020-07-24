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
Created on 3 Dec 2013

@author: ssg37927
'''


import h5py
import json
import numpy as np

# TODO refactor this file

def fortPMB_NEW(testpoint,m,i,magdims, V1):
    '''
    This function Calculates the B-field in a single orientation according to the calling function
    '''

    B=0.0

    V2=V1+magdims

    r1=testpoint.copy()
    r2=testpoint.copy()

    for p in range(3):
        r1[p]=r1[p]-V1[p]
        r2[p]=r2[p]-V2[p]

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
            if ((r1[k].all() > 0) and (r2[k].all() > 0 )) :
                r1k=r1[k]
                r2k=r2[k]
            else :
                r1k=-r2[k]
                r2k=-r1[k]

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

            B=B-(m[i]*I1/(4*np.pi))
            B=B-(m[j]*I2/(4*np.pi))

    return B

def wrapCalcB(testpoint, magdims,  V1):
    '''This function takes the arguments 'testpoint' and 's_offset'
    'testpoint' requires an array of floats of length 3 describing the [x,z,s] co-ordinates of the point under consideration
    's_offset' requires a float that describes the s-direction offset of the magnet block
    
    This function calls the main field calculating function, and outputs a 3x3 matrix of the form
    [[Bx(x), Bz(x), Bs(x)]
     [Bx(z), Bz(z), Bs(z)]
     [Bx(s), Bz(s), Bs(s)]].
     
     To calculate the real field component of any block need to get real data sum contributions such that
     Bx=Bx(x)*Mx + Bx(z)*Mz + Bx(s)*Ms'''
    B=np.zeros((testpoint.shape+(3,3))[1:])
    for i in range(3):
        m=np.zeros(3)
        m[i]=1
        for j in range(i,3):
            B[...,i,j]= fortPMB_NEW(testpoint,m,j, magdims, V1)
            if i!=j:
                B[...,j,i]=B[...,i,j]
    return B

def process(options, args):
    # Add all the magnets

    # TODO refactor arguments to accept json file as named parameter
    with open(args[0], 'r') as fp:
        data = json.load(fp)

    # create calculation array
    #meshgrid modified 18/02/19 ZP+MB to calculate no of points in each direction properly (avoid floating point errors)
    testpoints=np.mgrid[data['xmin']:data['xmax']-(data['xstep']/100.0):data['xstep'],
                        data['zmin']:data['zmax']-(data['zstep']/100.0):data['zstep'],
                        data['smin']:data['smax']-(data['sstep']/100.0):data['sstep']]
    # print("xmin %f"%(data['xmin']))
    # print("xmax %f"%(data['xmax']))
    # print("xstep %f"%(data['xstep']))
    # print("zmin %f"%(data['zmin']))
    # print("zmax %f"%(data['zmax']))
    # print("zstep %f"%(data['zstep']))
    # print("smin %f"%(data['smin']))
    # print("smax %f"%(data['smax']))
    # print("sstep %f"%(data['sstep']))

    if data['type'] == 'PPM_AntiSymmetric' or data['type'] == 'Hybrid_Symmetric':

        with h5py.File(args[1], 'w') as outfile:

            for b in range(len(data['beams'])):
                count = 0
                #print("Processing beam %02i" % (b))
                datashape = (testpoints.shape[1], testpoints.shape[2], testpoints.shape[3], 3, 3, len(data['beams'][b]['mags']))
                #print("testpoints.shape[3] %s"%(testpoints.shape[3]))
                chunkshape = (testpoints.shape[1], testpoints.shape[2], testpoints.shape[3], 3, 3, 1)
                #print ("datashape is : " + s(datashape))
                ds = outfile.create_dataset(data['beams'][b]['name'], shape=datashape, dtype=np.float64, chunks=chunkshape)

                for mag in data['beams'][b]['mags']:
                    #print("processing beam %02i magnet %04i" % (b, count))
                    dataset = wrapCalcB(testpoints, np.array(mag['dimensions']), np.array(mag['position']))
                    ds[..., count] = dataset.dot(np.array(mag['direction_matrix']))
                    count += 1
        
    if data['type'] == 'APPLE_Symmetric':

        with h5py.File(args[1], 'w') as outfile:

            for b in range(len(data['beams'])):
                count = 0
                #print("Processing beam %02i" % (b))
                datashape = (testpoints.shape[1], testpoints.shape[2], testpoints.shape[3], 3, 3, len(data['beams'][b]['mags']))
                chunkshape = (testpoints.shape[1], testpoints.shape[2], testpoints.shape[3], 3, 3, 1)
                #print ("datashape is : " + str(datashape))
                ds = outfile.create_dataset(data['beams'][b]['name'], shape=datashape, dtype=np.float64, chunks=chunkshape)

                for mag in data['beams'][b]['mags']:
                    #print("processing beam %02i magnet %04i" % (b, count))

                    datasetblock = wrapCalcB(testpoints, np.array(mag['dimensions']), np.array(mag['position']))
                    if b%2==1:
                        c2pos = np.array(mag['position'])+np.array([mag['dimensions'][0]-data['clampcut'],mag['dimensions'][1]-data['clampcut'],0.0])
                        datasetc1 = wrapCalcB(testpoints, np.array([data['clampcut'],data['clampcut'],mag['dimensions'][2]]), np.array(mag['position']))
                        datasetc2 = wrapCalcB(testpoints, np.array([data['clampcut'],data['clampcut'],mag['dimensions'][2]]), c2pos)
                    if b%2==0:
                        c1pos = np.array(mag['position'])+np.array([mag['dimensions'][0]-data['clampcut'], 0.0, 0.0])
                        c2pos = np.array(mag['position'])+np.array([0.0 ,mag['dimensions'][1]-data['clampcut'], 0.0])
                        datasetc1 = wrapCalcB(testpoints, np.array([data['clampcut'],data['clampcut'],mag['dimensions'][2]]), c1pos)
                        datasetc2 = wrapCalcB(testpoints, np.array([data['clampcut'],data['clampcut'],mag['dimensions'][2]]), c2pos)
                    dataset=datasetblock-datasetc1-datasetc2

                    ds[..., count] = dataset.dot(np.array(mag['direction_matrix']))
                    count += 1

if __name__ == "__main__":
    import optparse
    usage = "%prog [options] ID_Description_File Output_filename"
    parser = optparse.OptionParser(usage=usage)
#    parser.add_option("-o", "--output", dest="output", help="Select the file to write the output to", default=None)
    parser.add_option("-p", "--periods", dest="periods", help="Set the number of full periods for the Device", default=5, type="int")
    parser.add_option("-s", "--symmetric", dest="symmetric", help="Set the device to symmetric rather then Anti-symmetric", action="store_true", default=False)
    parser.add_option("-r", "--random", dest="random", help="Choose the magnets randomly instead of sequentially", action="store_true", default=False)
    parser.add_option("-v", "--verbose", dest="verbose", help="display debug information", action="store_true", default=False)

    (options, args) = parser.parse_args()
    process(options, args)
