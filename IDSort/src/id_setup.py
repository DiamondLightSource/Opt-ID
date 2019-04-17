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

# order  x, z, s
import json


def create_type_list_symmetric_apple(nperiods):
    # do the first end
    types = []
    vertical = True

    types.append('HE')
    types.append('VE')
    types.append('HE')
    
    # now put in all the middle periods
    for i in range(3, (4 * nperiods - 1) - 3, 1):
        if vertical :
            types.append('VV')
            vertical = False
        else :
            types.append('HH')
            vertical = True

    # finally add in the other end
    types.append('HE')
    types.append('VE')
    types.append('HE')

    return types

def create_direction_matrix_list_symmetric_apple_q1(nperiods):
    direction = []
    for i in range(0, (4 * nperiods - 1) - 3, 4):
        direction.append(((1,0,0),(0,1,0),(0,0,1)))
        direction.append(((-1,0,0),(0,-1,0),(0,0,1)))
        direction.append(((0,1,0),(1,0,0),(0,0,-1)))
        direction.append(((1,0,0),(0,1,0),(0,0,1)))

    # Append last elements
    direction.append(((1,0,0),(0,1,0),(0,0,1)))
    direction.append(((-1,0,0),(0,-1,0),(0,0,1)))
    direction.append(((0,1,0),(1,0,0),(0,0,-1)))
    return direction

def create_direction_matrix_list_symmetric_apple_q2(nperiods):
    direction = []
    for i in range(0, (4 * nperiods - 1) - 3, 4):
        direction.append(((0,-1,0),(1,0,0),(0,0,1)))
        direction.append(((1,0,0),(0,-1,0),(0,0,-1)))
        direction.append(((-1,0,0),(0,1,0),(0,0,-1)))
        direction.append(((-1,0,0),(0,1,0),(0,0,-1)))

    # Append last elements
    direction.append(((0,-1,0),(1,0,0),(0,0,1)))
    direction.append(((1,0,0),(0,-1,0),(0,0,-1)))
    direction.append(((-1,0,0),(0,1,0),(0,0,-1)))
    return direction

def create_direction_matrix_list_symmetric_apple_q3(nperiods):
    direction = []
    for i in range(0, (4 * nperiods - 1) - 3, 4):
        direction.append(((0,-1,0),(-1,0,0),(0,0,-1)))
        direction.append(((-1,0,0),(0,-1,0),(0,0,1)))
        direction.append(((-1,0,0),(0,-1,0),(0,0,1)))
        direction.append(((1,0,0),(0,1,0),(0,0,1)))

    # Append last elements
    direction.append(((0,-1,0),(-1,0,0),(0,0,-1)))
    direction.append(((-1,0,0),(0,-1,0),(0,0,1)))
    direction.append(((-1,0,0),(0,-1,0),(0,0,1)))

    return direction

def create_direction_matrix_list_symmetric_apple_q4(nperiods):
    direction = []
    for i in range(0, (4 * nperiods - 1) - 3, 4):
        direction.append(((1,0,0),(0,-1,0),(0,0,-1)))
        direction.append(((1,0,0),(0,-1,0),(0,0,-1)))
        direction.append(((0,1,0),(-1,0,0),(0,0,1)))
        direction.append(((-1,0,0),(0,1,0),(0,0,-1)))

    # Append last elements
    direction.append(((1,0,0),(0,-1,0),(0,0,-1)))
    direction.append(((1,0,0),(0,-1,0),(0,0,-1)))
    direction.append(((0,1,0),(-1,0,0),(0,0,1)))
    
    return direction

def create_flip_matrix_list_symmetric_apple_q1(nperiods):
    flip = []
    for i in range(0, (4 * nperiods - 1) - 3, 4):
        flip.append(((-1,0,0),(0,-1,0),(0,0,1)))
        flip.append(((1,0,0),(0,1,0),(0,0,1)))
        flip.append(((-1,0,0),(0,-1,0),(0,0,1)))
        flip.append(((1,0,0),(0,1,0),(0,0,1)))
    
    # Append last elements
    
    flip.append(((-1,0,0),(0,-1,0),(0,0,1)))
    flip.append(((1,0,0),(0,1,0),(0,0,1)))
    flip.append(((-1,0,0),(0,-1,0),(0,0,1)))
    return flip

def create_flip_matrix_list_symmetric_apple_q2(nperiods):
    flip = []
    for i in range(0, (4 * nperiods - 1) - 3, 4):
        flip.append(((-1,0,0),(0,-1,0),(0,0,1)))
        flip.append(((1,0,0),(0,1,0),(0,0,1)))
        flip.append(((-1,0,0),(0,-1,0),(0,0,1)))
        flip.append(((1,0,0),(0,1,0),(0,0,1)))
    
    # Append last elements
    
    flip.append(((-1,0,0),(0,-1,0),(0,0,1)))
    flip.append(((1,0,0),(0,1,0),(0,0,1)))
    flip.append(((-1,0,0),(0,-1,0),(0,0,1)))
    return flip

def create_flip_matrix_list_symmetric_apple_q3(nperiods):
    flip = []
    for i in range(0, (4 * nperiods - 1) - 3, 4):
        flip.append(((-1,0,0),(0,-1,0),(0,0,1)))
        flip.append(((1,0,0),(0,1,0),(0,0,1)))
        flip.append(((-1,0,0),(0,-1,0),(0,0,1)))
        flip.append(((1,0,0),(0,1,0),(0,0,1)))

    
    # Append last elements
    
    flip.append(((-1,0,0),(0,-1,0),(0,0,1)))
    flip.append(((1,0,0),(0,1,0),(0,0,1)))
    flip.append(((-1,0,0),(0,-1,0),(0,0,1)))

    return flip

def create_flip_matrix_list_symmetric_apple_q4(nperiods):
    flip = []
    for i in range(0, (4 * nperiods - 1) - 3, 4):
        flip.append(((-1,0,0),(0,-1,0),(0,0,1)))
        flip.append(((1,0,0),(0,1,0),(0,0,1)))
        flip.append(((-1,0,0),(0,-1,0),(0,0,1)))
        flip.append(((1,0,0),(0,1,0),(0,0,1)))
    
    # Append last elements
    flip.append(((-1,0,0),(0,-1,0),(0,0,1)))
    flip.append(((1,0,0),(0,1,0),(0,0,1)))
    flip.append(((-1,0,0),(0,-1,0),(0,0,1)))
    return flip
    
def create_location_list_symmetric_apple_q2(period, nperiods, fullmagdims, vemagdims, hemagdims, mingap, interstice, endgap, phasinggap):
    #locate most negative point of block on x,z,s axes
    V1 = []
    length = 4*hemagdims[2]+2*vemagdims[2]+(4*(nperiods-2)+1)*fullmagdims[2]+(4*(nperiods-2)+4)*interstice+2*endgap
    x=-fullmagdims[0]-phasinggap/2.0
    z=mingap/2.0
    s=-length/2.0
    V1.append((x,z,s))
    s+=(hemagdims[2]+endgap)
    V1.append((x,z,s))
    s+=(vemagdims[2]+interstice)
    V1.append((x,z,s))
    s+=(hemagdims[2]+interstice)
    for i in range(3,(4*nperiods-1)-3,1):
        V1.append((x,z,s))
        s+=(fullmagdims[2]+interstice)
    V1.append((x,z,s))
    s+=(hemagdims[2]+interstice)
    V1.append((x,z,s))
    s+=(vemagdims[2]+endgap)
    V1.append((x,z,s))
    return V1

def create_location_list_symmetric_apple_q1(period, nperiods, fullmagdims, vemagdims, hemagdims, mingap, interstice, endgap, phasinggap):
    #locate most negative point of block on x,z,s axes
    V1 = []
    length = 4*hemagdims[2]+2*vemagdims[2]+(4*(nperiods-2)+1)*fullmagdims[2]+(4*(nperiods-2)+4)*interstice+2*endgap
    x=phasinggap/2.0
    z=mingap/2.0
    s=-length/2.0
    V1.append((x,z,s))
    s+=(hemagdims[2]+endgap)
    V1.append((x,z,s))
    s+=(vemagdims[2]+interstice)
    V1.append((x,z,s))
    s+=(hemagdims[2]+interstice)
    for i in range(3,(4*nperiods-1)-3,1):
        V1.append((x,z,s))
        s+=(fullmagdims[2]+interstice)
    V1.append((x,z,s))
    s+=(hemagdims[2]+interstice)
    V1.append((x,z,s))
    s+=(vemagdims[2]+endgap)
    V1.append((x,z,s))
    return V1

def create_location_list_symmetric_apple_q4(period, nperiods, fullmagdims, vemagdims, hemagdims, mingap, interstice, endgap, phasinggap):
    #locate most negative point of block on x,z,s axes
    V1 = []
    length = 4*hemagdims[2]+2*vemagdims[2]+(4*(nperiods-2)+1)*fullmagdims[2]+(4*(nperiods-2)+4)*interstice+2*endgap
    x=phasinggap/2.0
    z=-fullmagdims[1]-mingap/2.0
    s=-length/2.0
    V1.append((x,z,s))
    s+=(hemagdims[2]+endgap)
    V1.append((x,z,s))
    s+=(vemagdims[2]+interstice)
    V1.append((x,z,s))
    s+=(hemagdims[2]+interstice)
    for i in range(3,(4*nperiods-1)-3,1):
        V1.append((x,z,s))
        s+=(fullmagdims[2]+interstice)
    V1.append((x,z,s))
    s+=(hemagdims[2]+interstice)
    V1.append((x,z,s))
    s+=(vemagdims[2]+endgap)
    V1.append((x,z,s))
    return V1

def create_location_list_symmetric_apple_q3(period, nperiods, fullmagdims, vemagdims, hemagdims, mingap, interstice, endgap, phasinggap):
    #locate most negative point of block on x,z,s axes
    V1 = []
    length = 4*hemagdims[2]+2*vemagdims[2]+(4*(nperiods-2)+1)*fullmagdims[2]+(4*(nperiods-2)+4)*interstice+2*endgap
    x=-fullmagdims[0]-phasinggap/2.0
    z=-fullmagdims[1]-mingap/2.0
    s=-length/2.0
    V1.append((x,z,s))
    s+=(hemagdims[2]+endgap)
    V1.append((x,z,s))
    s+=(vemagdims[2]+interstice)
    V1.append((x,z,s))
    s+=(hemagdims[2]+interstice)
    for i in range(3,(4*nperiods-1)-3,1):
        V1.append((x,z,s))
        s+=(fullmagdims[2]+interstice)
    V1.append((x,z,s))
    s+=(hemagdims[2]+interstice)
    V1.append((x,z,s))
    s+=(vemagdims[2]+endgap)
    V1.append((x,z,s))
    return V1

def create_type_list_symmetric_hybrid(nperiods):
    # do the first end
    types = []
    #start = 0
    #stop = 0

    types.append('HT')
    types.append('HE')

    start, stop = (2, (2*nperiods+4)-2)

    # now put in all the middle periods
    for i in range(start, stop):
        types.append('HH')


    # finally add in the other end
    types.append('HE')
    types.append('HT')

    return types

def create_direction_matrix_list_symmetric_hybrid_bottom(nperiods):
    direction = []
    for i in range(0, (2 * nperiods + 4), 2):
        direction.append(((1,0,0),(0,1,0),(0,0,1)))
        #no V magnet in Hybrids
        direction.append(((-1,0,0),(0,1,0),(0,0,-1)))
        #no V magnets in hybrid

    return direction

def create_direction_matrix_list_symmetric_hybrid_top(nperiods):
    direction = []
    for i in range(0, (2 * nperiods + 4), 2):
        range(0, (2 * nperiods + 4), 2)
        {direction.append(((-1,0,0),(0,1,0),(0,0,-1))),
        #no V magnets in Hybrids
        direction.append(((1,0,0),(0,1,0),(0,0,1)))
        }
        #no V magnets in Hybrids

    return direction

def create_flip_matrix_symmetric_hybrid_bottom_top(nperiods):
    flip = []
    for i in range(0, (2 * nperiods + 4)):
        flip.append(((-1,0,0),(0,-1,0),(0,0,1)))

    return flip

def create_location_list_symmetric_hybrid_top(nperiods,fullmagdims,hemagdims,htmagdims,poledims,mingap,endgapsym,terminalgapsymhybrid,interstice):
    V1 = []
    length = nperiods * (2 * poledims[2]+2*fullmagdims[2]+4*interstice)+2*(poledims[2]+interstice + hemagdims[2] + endgapsym + terminalgapsymhybrid + htmagdims[2])
    x=-fullmagdims[0]/2.0
    z= mingap/2.0
    s=-length/2.0
    V1.append((x,z,s))
    s+= (htmagdims[2]+endgapsym + terminalgapsymhybrid + poledims[2]/2)
    V1.append((x,z,s))
    s+=hemagdims[2]+poledims[2]+2*interstice
    for i in range(2,(2*nperiods+4)-2,1):
        V1.append((x,z,s))
        s+=(fullmagdims[2]+poledims[2]+2*interstice)
    V1.append((x,z,s))
    s+=hemagdims[2]+poledims[2]/2+endgapsym+terminalgapsymhybrid
    V1.append((x,z,s))
    return V1

def create_location_list_symmetric_hybrid_bottom(nperiods,fullmagdims,hemagdims,htmagdims,poledims,mingap,endgapsym,terminalgapsymhybrid,interstice):
    V1 = []
    length = nperiods * (2 * poledims[2]+2*fullmagdims[2]+4*interstice)+2*(poledims[2]+interstice + hemagdims[2] + endgapsym + terminalgapsymhybrid + htmagdims[2])
    x=-fullmagdims[0]/2.0
    z= -fullmagdims[1]-mingap/2.0
    s=-length/2.0
    V1.append((x,z,s))
    s+= (htmagdims[2]+endgapsym + terminalgapsymhybrid + poledims[2]/2)
    V1.append((x,z,s))
    s+=hemagdims[2]+poledims[2]+2*interstice
    for i in range(2,(2*nperiods+4)-2,1):
        V1.append((x,z,s))
        s+=(fullmagdims[2]+poledims[2]+2*interstice)
    V1.append((x,z,s))
    s+=hemagdims[2]+poledims[2]/2+endgapsym+terminalgapsymhybrid
    V1.append((x,z,s))
    return V1

def create_type_list_antisymetric_ppm(nperiods):
    # do the first end
    types = []
    #start = 0
    #stop = 0
    vertical = False

    types.append('HE')
    types.append('VE')

    start, stop = (2, (4*nperiods+5)-2)

    # now put in all the middle periods
    for i in range(start, stop):
        if vertical :
            types.append('VV')
            vertical = False
        else :
            types.append('HH')
            vertical = True

    # finally add in the other end
    types.append('VE')
    types.append('HE')

    return types


def create_direction_list_antisymetric_ppm_bottom(nperiods):
    direction = []
    for i in range(0, (4 * nperiods + 5) - 1, 4):
        direction.append((1, 1, 1))
        direction.append((1, 1, 1))
        direction.append((-1, 1, -1))
        direction.append((-1, -1, 1))

    # Append last element
    direction.append((1, 1, 1))
    return direction

def create_direction_matrix_list_antisymetric_ppm_bottom(nperiods):
    direction = []
    for i in range(0, (4 * nperiods + 5) - 1, 4):
        direction.append(((1,0,0),(0,1,0),(0,0,1)))
        direction.append(((1,0,0),(0,1,0),(0,0,1)))
        direction.append(((-1,0,0),(0,1,0),(0,0,-1)))
        direction.append(((-1,0,0),(0,-1,0),(0,0,1)))

    # Append last element
    direction.append(((1,0,0),(0,1,0),(0,0,1)))
    return direction

def create_flip_matrix_antisymmetric_ppm_bottom(nperiods):
    flip = []
    for i in range(0, (4 * nperiods + 5) - 1, 2):
        flip.append(((-1,0,0),(0,-1,0),(0,0,1)))
        flip.append(((-1,0,0),(0,1,0),(0,0,-1)))
    
    flip.append(((-1,0,0),(0,-1,0),(0,0,1)))
    return flip


def create_direction_list_antisymetric_ppm_top(nperiods):
    direction = []
    for i in range(0, (4 * nperiods + 5) - 1, 4):
        direction.append((-1, 1, -1))
        direction.append((1, 1, 1))
        direction.append((1, 1, 1))
        direction.append((-1, -1, 1))

    # Append last element
    direction.append((-1, 1, -1))
    return direction

def create_direction_matrix_list_antisymetric_ppm_top(nperiods):
    direction = []
    for i in range(0, (4 * nperiods + 5) - 1, 4):
        direction.append(((-1,0,0),(0,1,0),(0,0,-1)))
        direction.append(((1,0,0),(0,1,0),(0,0,1)))
        direction.append(((1,0,0),(0,1,0),(0,0,1)))
        direction.append(((-1,0,0),(0,-1,0),(0,0,1)))

    # Append last element
    direction.append(((-1,0,0),(0,1,0),(0,0,-1)))
    return direction

def create_flip_matrix_antisymmetric_ppm_top(nperiods):
    flip = []
    for i in range(0, (4 * nperiods + 5) - 1, 2):
        flip.append(((-1,0,0),(0,-1,0),(0,0,1)))
        flip.append(((-1,0,0),(0,1,0),(0,0,-1)))
    
    flip.append(((-1,0,0),(0,-1,0),(0,0,1)))
    return flip

def create_location_list_antisymmetric_ppm_top(period, nperiods,fullmagdims,vemagdims,hemagdims,mingap,interstice):
    V1 = []
    length = (4*(nperiods)+1)*(fullmagdims[2]+interstice)+2*(vemagdims[2]+interstice)+2*(hemagdims[2]+interstice)-interstice
    x=-fullmagdims[0]/2.0
    z=mingap/2.0
    s=-length/2.0
    V1.append((x,z,s))
    s+=(hemagdims[2]+interstice)
    V1.append((x,z,s))
    s+=(vemagdims[2]+interstice)
    for i in range(2,(4*nperiods+5)-2,1):
        V1.append((x,z,s))
        s+=(fullmagdims[2]+interstice)
    V1.append((x,z,s))
    s+=(vemagdims[2]+interstice)
    V1.append((x,z,s))
    return V1

def create_location_list_antisymmetric_ppm_bottom(period, nperiods,fullmagdims,vemagdims,hemagdims,mingap,interstice):
    V1 = []
    length = (4*(nperiods)+1)*(fullmagdims[2]+interstice)+2*(vemagdims[2]+interstice)+2*(hemagdims[2]+interstice)-interstice
    x=-fullmagdims[0]/2.0
    z=-fullmagdims[1]-mingap/2.0
    s=-length/2.0
    V1.append((x,z,s))
    s+=(hemagdims[2]+interstice)
    V1.append((x,z,s))
    s+=(vemagdims[2]+interstice)
    for i in range(2,(4*nperiods+5)-2,1):
        V1.append((x,z,s))
        s+=(fullmagdims[2]+interstice)
    V1.append((x,z,s))
    s+=(vemagdims[2]+interstice)
    V1.append((x,z,s))
    return V1

if __name__ == "__main__":  #program starts here
    import optparse
    usage = "%prog [options] OutputFile"
    parser = optparse.OptionParser(usage=usage)
    parser.add_option("-p", "--periods", dest="periods", help="Set the number of full periods for the Device", default=109, type="int")
    parser.add_option("--fullmagdims", dest="fullmagdims", help="Set the dimensions of the full magnet blocks (x,z,s) in mm", nargs=3, default=(41., 16., 6.22), type="float")
    parser.add_option("--vemagdims", dest="vemagdims", help="Set the dimensions of the VE magnet blocks (x,z,s) in mm", nargs=3, default=(41., 16., 3.12), type="float")
    parser.add_option("--hemagdims", dest="hemagdims", help="Set the dimensions of the HE magnet blocks (x,z,s) in mm", nargs=3, default=(41., 16., 4.0), type="float")
    parser.add_option("--htmagdims", dest="htmagdims", help="Set the dimensions of the HT magnet blocks (x,z,s) in mm", nargs=3, default=(41., 16., 4.0), type="float")
    parser.add_option("--poledims", dest="poledims", help="Set the dimensions of the iron pole blocks (x,z,s) in mm", nargs=3, default=(41., 16., 4.0), type="float")
    parser.add_option("-i", dest="interstice", help="Set the dimensions of the slack between adjacent magnets (interstice) in mm", default=0.03, type="float")
    parser.add_option("-g", "--gap", dest="gap", help="Set the gap for the device to be created at", default=6.15, type="float")
    parser.add_option("-t", "--type", dest="type", help="Set the device type", type="string", default="PPM_AntiSymmetric")
    parser.add_option("-v", "--verbose", dest="verbose", help="display debug information", action="store_true", default=False)
    parser.add_option("-n", "--name", dest="name", help="PPM name", default="J13", type="string")
    parser.add_option("-x", "--xstartstopstep", dest="x", help="X start stop and step", nargs=3, default=(-5.0, 5.1, 2.5), type="float")
    parser.add_option("-z", "--zstartstopstep", dest="z", help="Z start stop and step", nargs=3, default=(-0.0,.1, 0.1), type="float")
    parser.add_option("-s", "--stepsperperiod", dest="steps", help="Number of steps in S per quarter period", default=5, type="float")
    parser.add_option("--endgapsym", dest="endgapsym", help="Symmetric PPM or APPLE devices require an end gap in the termination structure, set gap length in mm", default=5.0, type="float")
    parser.add_option("--terminalgapsymhyb", dest="terminalgapsymhyb", help="Symmetric hybrid devices require a terminal end gap between the final half pole and the terminal H magnet in the termination structure, set gap length in mm", default=5.0, type="float")
    parser.add_option("--phasinggap", dest="phasinggap", help="Gap between Quadrants 1/2 and 3/4 that allow these axes to phase past each other; in mm. APPLES only", default=0.5, type="float")
    parser.add_option("--clampcut", dest="clampcut", help="Square corners removed to allow magnets to be clamped, dimensioned in mm. APPLEs only", default = 5.0, type="float")
    

    (options, args) = parser.parse_args()

    if options.type == 'Hybrid_Symmetric':
        output = {}
        output['name'] = options.name
        output['type'] = options.type
        output['number_of_beams'] = 2
        output['gap'] = options.gap
        output['periods'] = options.periods
        output['period_length'] = 4*options.interstice+2*options.fullmagdims[2]+2*options.poledims[2]
        # TODO needs sorting out
        output['xmin'] = options.x[0]
        output['xmax'] = options.x[1]
        output['xstep'] = options.x[2]
        output['zmin'] = options.z[0]
        output['zmax'] = options.z[1]
        output['zstep'] = options.z[2]
        length = (options.fullmagdims[2]+options.poledims[2]+2*options.interstice)*2*(options.periods+16)
        output['smin'] = -length/2.0
        output['smax'] = (length/2.0)+2 * (options.fullmagdims[2]+options.poledims[2]+2*options.interstice)/(4*options.steps)
        output['sstep'] = 2 * (options.fullmagdims[2]+options.poledims[2]+2*options.interstice)/(4*options.steps)
        output['sstep'] = (int(round(output['sstep']*100000))/100000.)
        output['interstice'] = options.interstice

        # calculate all magnet values
        types = create_type_list_symmetric_hybrid(options.periods)
        top_directions_matrix = create_direction_matrix_list_symmetric_hybrid_top(options.periods)
        bottom_directions_matrix = create_direction_matrix_list_symmetric_hybrid_bottom(options.periods)
        top_positions = create_location_list_symmetric_hybrid_top(options.periods, options.fullmagdims, options.hemagdims, options.htmagdims, options.poledims, options.gap, options.endgapsym, options.terminalgapsymhyb, options.interstice)
        bottom_positions = create_location_list_symmetric_hybrid_bottom(options.periods, options.fullmagdims, options.hemagdims, options.htmagdims, options.poledims, options.gap, options.endgapsym, options.terminalgapsymhyb,options.interstice)
        top_flip_matrix = create_flip_matrix_symmetric_hybrid_bottom_top(options.periods)
        bottom_flip_matrix = create_flip_matrix_symmetric_hybrid_bottom_top(options.periods)
        # output beams
        output['beams'] = []
        top_beam = {}
        top_beam['name'] = "Top Beam"
        top_beam['mags'] = []
        
        bottom_beam = {}
        bottom_beam['name'] = "Bottom Beam"
        bottom_beam['mags'] = []

        # top beam
        for i in range(len(types)):
            mag = {}
            mag['type'] = types[i]
            mag['direction_matrix'] = top_directions_matrix[i]
            mag['position'] = top_positions[i]
            mag['flip_matrix'] = top_flip_matrix[i]
            if types[i] == 'VV':
                mag['dimensions'] = options.fullmagdims
            elif types[i] == 'HH':
                mag['dimensions'] = options.fullmagdims
            elif types[i] == 'HE':
                mag['dimensions'] = options.hemagdims
            elif types[i] == 'VE':
                mag['dimensions'] = options.vemagdims
            elif types[i] == 'HT':
                mag['dimensions'] = options.htmagdims
            top_beam['mags'].append(mag)

        # bottom beam
        for i in range(len(types)):
            mag = {}
            mag['type'] = types[i]
            mag['direction_matrix'] = bottom_directions_matrix[i]
            mag['position'] = bottom_positions[i]
            mag['flip_matrix'] = bottom_flip_matrix[i]
            if types[i] == 'VV':
                mag['dimensions'] = options.fullmagdims
            elif types[i] == 'HH':
                mag['dimensions'] = options.fullmagdims
            elif types[i] == 'HE':
                mag['dimensions'] = options.hemagdims
            elif types[i] == 'VE':
                mag['dimensions'] = options.vemagdims
            elif types[i] == 'HT':
                mag['dimensions'] = options.htmagdims
            bottom_beam['mags'].append(mag)

        output['beams'].append(top_beam)
        output['beams'].append(bottom_beam)

        fp = open(args[0], 'w')
        json.dump(output, fp, indent=4)
        fp.close()
        
    if options.type == 'PPM_AntiSymmetric':
        output = {}
        output['name'] = options.name
        output['type'] = options.type
        output['number_of_beams'] = 2
        output['gap'] = options.gap
        output['periods'] = options.periods
        output['period_length'] = 4*(options.interstice+options.fullmagdims[2])
        # TODO needs sorting out
        output['xmin'] = options.x[0]
        output['xmax'] = options.x[1]
        output['xstep'] = options.x[2]
        output['zmin'] = options.z[0]
        output['zmax'] = options.z[1]
        output['zstep'] = options.z[2]
        length = (options.fullmagdims[2]+options.interstice)*4*(options.periods+16)
        output['smin'] = -length/2.0
        output['smax'] = (length/2.0)+((options.fullmagdims[2]+options.interstice)/options.steps)
        output['sstep'] = (options.fullmagdims[2]+options.interstice)/options.steps
        output['sstep'] = (int(round(output['sstep']*100000))/100000.)
        output['interstice'] = options.interstice

        # calculate all magnet values
        types = create_type_list_antisymetric_ppm(options.periods)
        top_directions = create_direction_list_antisymetric_ppm_top(options.periods)
        bottom_directions = create_direction_list_antisymetric_ppm_bottom(options.periods)
        top_directions_matrix = create_direction_matrix_list_antisymetric_ppm_top(options.periods)
        bottom_directions_matrix = create_direction_matrix_list_antisymetric_ppm_bottom(options.periods)
        top_positions = create_location_list_antisymmetric_ppm_top(options.fullmagdims[2]*4, options.periods, options.fullmagdims, options.vemagdims, options.hemagdims, options.gap, options.interstice)
        bottom_positions = create_location_list_antisymmetric_ppm_bottom(options.fullmagdims[2]*4, options.periods, options.fullmagdims, options.vemagdims, options.hemagdims, options.gap, options.interstice)
        top_flip_matrix = create_flip_matrix_antisymmetric_ppm_top(options.periods)
        bottom_flip_matrix = create_flip_matrix_antisymmetric_ppm_bottom(options.periods)

        # output beams
        output['beams'] = []
        top_beam = {}
        top_beam['name'] = "Top Beam"
        top_beam['mags'] = []
        
        bottom_beam = {}
        bottom_beam['name'] = "Bottom Beam"
        bottom_beam['mags'] = []

        # top beam
        for i in range(len(types)):
            mag = {}
            mag['type'] = types[i]
            mag['direction'] = top_directions[i]
            mag['direction_matrix'] = top_directions_matrix[i]
            mag['position'] = top_positions[i]
            mag['flip_matrix'] = top_flip_matrix[i]
            if types[i] == 'VV':
                mag['dimensions'] = options.fullmagdims
            elif types[i] == 'HH':
                mag['dimensions'] = options.fullmagdims
            elif types[i] == 'HE':
                mag['dimensions'] = options.hemagdims
            elif types[i] == 'VE':
                mag['dimensions'] = options.vemagdims
            top_beam['mags'].append(mag)

        # bottom beam
        for i in range(len(types)):
            mag = {}
            mag['type'] = types[i]
            mag['direction'] = bottom_directions[i]
            mag['direction_matrix'] = bottom_directions_matrix[i]
            mag['position'] = bottom_positions[i]
            mag['flip_matrix'] = bottom_flip_matrix[i]
            if types[i] == 'VV':
                mag['dimensions'] = options.fullmagdims
            elif types[i] == 'HH':
                mag['dimensions'] = options.fullmagdims
            elif types[i] == 'HE':
                mag['dimensions'] = options.hemagdims
            elif types[i] == 'VE':
                mag['dimensions'] = options.vemagdims
            bottom_beam['mags'].append(mag)

        output['beams'].append(top_beam)
        output['beams'].append(bottom_beam)

        fp = open(args[0], 'w')
        json.dump(output, fp, indent=4)
        fp.close()
        
        
        
    if options.type == 'APPLE_Symmetric':
        output = {}
        output['name'] = options.name
        output['type'] = options.type
        output['number_of_beams'] = 4
        output['gap'] = options.gap
        output['periods'] = options.periods
        output['period_length'] = 4*(options.interstice+options.fullmagdims[2])
        # TODO needs sorting out
        output['xmin'] = options.x[0]
        output['xmax'] = options.x[1]
        output['xstep'] = options.x[2]
        output['zmin'] = options.z[0]
        output['zmax'] = options.z[1]
        output['zstep'] = options.z[2]
        length = (options.fullmagdims[2]+options.interstice)*4*(options.periods+16)
        output['smin'] = -length/2.0
        output['smax'] = (length/2.0)+((options.fullmagdims[2]+options.interstice)/options.steps)
        output['sstep'] = (options.fullmagdims[2]+options.interstice)/options.steps
        output['sstep'] = (int(round(output['sstep']*100000))/100000.)
        output['interstice'] = options.interstice
        output['end_gap'] = options.endgapsym
        output['phasing_gap'] = options.phasinggap
        output['clampcut'] = options.clampcut

        # calculate all magnet values
        types = create_type_list_symmetric_apple(options.periods)
        q1_directions_matrix = create_direction_matrix_list_symmetric_apple_q1(options.periods)
        q2_directions_matrix = create_direction_matrix_list_symmetric_apple_q2(options.periods)
        q3_directions_matrix = create_direction_matrix_list_symmetric_apple_q3(options.periods)
        q4_directions_matrix = create_direction_matrix_list_symmetric_apple_q4(options.periods)

        q1_positions = create_location_list_symmetric_apple_q1(options.fullmagdims[2]*4, options.periods, options.fullmagdims, options.vemagdims, options.hemagdims, options.gap, options.interstice, options.endgapsym, options.phasinggap)
        q2_positions = create_location_list_symmetric_apple_q2(options.fullmagdims[2]*4, options.periods, options.fullmagdims, options.vemagdims, options.hemagdims, options.gap, options.interstice, options.endgapsym, options.phasinggap)
        q3_positions = create_location_list_symmetric_apple_q3(options.fullmagdims[2]*4, options.periods, options.fullmagdims, options.vemagdims, options.hemagdims, options.gap, options.interstice, options.endgapsym, options.phasinggap)
        q4_positions = create_location_list_symmetric_apple_q4(options.fullmagdims[2]*4, options.periods, options.fullmagdims, options.vemagdims, options.hemagdims, options.gap, options.interstice, options.endgapsym, options.phasinggap)

        q1_flip_matrix = create_flip_matrix_list_symmetric_apple_q1(options.periods)
        q2_flip_matrix = create_flip_matrix_list_symmetric_apple_q2(options.periods)
        q3_flip_matrix = create_flip_matrix_list_symmetric_apple_q3(options.periods)
        q4_flip_matrix = create_flip_matrix_list_symmetric_apple_q4(options.periods)
        
        # output beams
        output['beams'] = []
        q1_beam = {}
        q1_beam['name'] = "Q1 Beam"
        q1_beam['mags'] = []
        q2_beam = {}
        q2_beam['name'] = "Q2 Beam"
        q2_beam['mags'] = []
        q3_beam = {}
        q3_beam['name'] = "Q3 Beam"
        q3_beam['mags'] = []
        q4_beam = {}
        q4_beam['name'] = "Q4 Beam"
        q4_beam['mags'] = []

        # q1 beam
        for i in range(len(types)):
            mag = {}
            mag['type'] = types[i]
            mag['direction_matrix'] = q1_directions_matrix[i]
            mag['position'] = q1_positions[i]
            mag['flip_matrix'] = q1_flip_matrix[i]
            if types[i] == 'VV':
                mag['dimensions'] = options.fullmagdims
            elif types[i] == 'HH':
                mag['dimensions'] = options.fullmagdims
            elif types[i] == 'HE':
                mag['dimensions'] = options.hemagdims
            elif types[i] == 'VE':
                mag['dimensions'] = options.vemagdims
            q1_beam['mags'].append(mag)
            
        # q2 beam
        for i in range(len(types)):
            mag = {}
            mag['type'] = types[i]
            mag['direction_matrix'] = q2_directions_matrix[i]
            mag['position'] = q2_positions[i]
            mag['flip_matrix'] = q2_flip_matrix[i]
            if types[i] == 'VV':
                mag['dimensions'] = options.fullmagdims
            elif types[i] == 'HH':
                mag['dimensions'] = options.fullmagdims
            elif types[i] == 'HE':
                mag['dimensions'] = options.hemagdims
            elif types[i] == 'VE':
                mag['dimensions'] = options.vemagdims
            q2_beam['mags'].append(mag)
            
        # q3 beam
        for i in range(len(types)):
            mag = {}
            mag['type'] = types[i]
            mag['direction_matrix'] = q3_directions_matrix[i]
            mag['position'] = q3_positions[i]
            mag['flip_matrix'] = q3_flip_matrix[i]
            if types[i] == 'VV':
                mag['dimensions'] = options.fullmagdims
            elif types[i] == 'HH':
                mag['dimensions'] = options.fullmagdims
            elif types[i] == 'HE':
                mag['dimensions'] = options.hemagdims
            elif types[i] == 'VE':
                mag['dimensions'] = options.vemagdims
            q3_beam['mags'].append(mag)
            
        # q4 beam
        for i in range(len(types)):
            mag = {}
            mag['type'] = types[i]
            mag['direction_matrix'] = q4_directions_matrix[i]
            mag['position'] = q4_positions[i]
            mag['flip_matrix'] = q4_flip_matrix[i]
            if types[i] == 'VV':
                mag['dimensions'] = options.fullmagdims
            elif types[i] == 'HH':
                mag['dimensions'] = options.fullmagdims
            elif types[i] == 'HE':
                mag['dimensions'] = options.hemagdims
            elif types[i] == 'VE':
                mag['dimensions'] = options.vemagdims
            q4_beam['mags'].append(mag)



        output['beams'].append(q1_beam)
        output['beams'].append(q2_beam)
        output['beams'].append(q3_beam)
        output['beams'].append(q4_beam)

        fp = open(args[0], 'w')
        json.dump(output, fp, indent=4)
        fp.close()