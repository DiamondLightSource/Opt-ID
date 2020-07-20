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

# Helper functions for APPLE-II Symmetric devices

def create_type_list_apple_symmetric(nperiods):
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

def create_position_list_apple_symmetric_q1(period, nperiods, fullmagdims, vemagdims, hemagdims, mingap, interstice, endgap, phasinggap):
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

def create_position_list_apple_symmetric_q2(period, nperiods, fullmagdims, vemagdims, hemagdims, mingap, interstice, endgap, phasinggap):
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

def create_position_list_apple_symmetric_q4(period, nperiods, fullmagdims, vemagdims, hemagdims, mingap, interstice, endgap, phasinggap):
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

def create_position_list_apple_symmetric_q3(period, nperiods, fullmagdims, vemagdims, hemagdims, mingap, interstice, endgap, phasinggap):
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

def create_direction_matrix_list_apple_symmetric_q1(nperiods):
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

def create_direction_matrix_list_apple_symmetric_q2(nperiods):
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

def create_direction_matrix_list_apple_symmetric_q3(nperiods):
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

def create_direction_matrix_list_apple_symmetric_q4(nperiods):
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

def create_flip_matrix_list_apple_symmetric(nperiods):
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

# Helper functions for Hybrid Symmetric devices

def create_type_list_hybrid_symmetric_top_btm(nperiods):
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

def create_direction_matrix_list_hybrid_symmetric_btm(nperiods):
    direction = []
    for i in range(0, (2 * nperiods + 4), 2):
        direction.append(((1,0,0),(0,1,0),(0,0,1)))
        #no V magnet in Hybrids
        direction.append(((-1,0,0),(0,1,0),(0,0,-1)))
        #no V magnets in hybrid

    return direction

def create_direction_matrix_list_hybrid_symmetric_top(nperiods):
    direction = []
    for i in range(0, (2 * nperiods + 4), 2):
        direction.append(((-1,0,0),(0,1,0),(0,0,-1)))
        #no V magnets in Hybrids
        direction.append(((1,0,0),(0,1,0),(0,0,1)))
        #no V magnets in Hybrids

    return direction

def create_flip_matrix_hybrid_symmetric_top_btm(nperiods):
    flip = []
    for i in range(0, (2 * nperiods + 4)):
        flip.append(((-1,0,0),(0,-1,0),(0,0,1)))

    return flip

def create_position_list_hybrid_symmetric_top(nperiods, fullmagdims, hemagdims, htmagdims, poledims, mingap, endgapsym, terminalgapsymhybrid, interstice):
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

def create_position_list_hybrid_symmetric_btm(nperiods, fullmagdims, hemagdims, htmagdims, poledims, mingap, endgapsym, terminalgapsymhybrid, interstice):
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

# Helper functions for PPM Anti Symmetric devices

def create_type_list_ppm_antisymmetric(nperiods):
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

def create_position_list_ppm_antisymmetric_top(period, nperiods, fullmagdims, vemagdims, hemagdims, mingap, interstice):
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

def create_position_list_ppm_antisymmetric_btm(period, nperiods, fullmagdims, vemagdims, hemagdims, mingap, interstice):
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

def create_direction_list_ppm_antisymmetric_top(nperiods):
    direction = []
    for i in range(0, (4 * nperiods + 5) - 1, 4):
        direction.append((-1, 1, -1))
        direction.append((1, 1, 1))
        direction.append((1, 1, 1))
        direction.append((-1, -1, 1))

    # Append last element
    direction.append((-1, 1, -1))
    return direction

def create_direction_list_ppm_antisymmetric_btm(nperiods):
    direction = []
    for i in range(0, (4 * nperiods + 5) - 1, 4):
        direction.append((1, 1, 1))
        direction.append((1, 1, 1))
        direction.append((-1, 1, -1))
        direction.append((-1, -1, 1))

    # Append last element
    direction.append((1, 1, 1))
    return direction

def create_direction_matrix_list_ppm_antisymmetric_top(nperiods):
    direction = []
    for i in range(0, (4 * nperiods + 5) - 1, 4):
        direction.append(((-1,0,0),(0,1,0),(0,0,-1)))
        direction.append(((1,0,0),(0,1,0),(0,0,1)))
        direction.append(((1,0,0),(0,1,0),(0,0,1)))
        direction.append(((-1,0,0),(0,-1,0),(0,0,1)))

    # Append last element
    direction.append(((-1,0,0),(0,1,0),(0,0,-1)))
    return direction

def create_direction_matrix_list_ppm_antisymmetric_btm(nperiods):
    direction = []
    for i in range(0, (4 * nperiods + 5) - 1, 4):
        direction.append(((1,0,0),(0,1,0),(0,0,1)))
        direction.append(((1,0,0),(0,1,0),(0,0,1)))
        direction.append(((-1,0,0),(0,1,0),(0,0,-1)))
        direction.append(((-1,0,0),(0,-1,0),(0,0,1)))

    # Append last element
    direction.append(((1,0,0),(0,1,0),(0,0,1)))
    return direction

def create_flip_matrix_list_ppm_antisymmetric_top_btm(nperiods):
    flip = []
    for i in range(0, (4 * nperiods + 5) - 1, 2):
        flip.append(((-1, 0, 0), (0, -1, 0), (0, 0, 1)))
        flip.append(((-1, 0, 0), (0, 1, 0), (0, 0, -1)))

    flip.append(((-1, 0, 0), (0, -1, 0), (0, 0, 1)))
    return flip


def process(options, args):

    # Generic data for all device types
    output = {
        # Device identifiers
        'name'       : options.name,
        'type'       : options.type,

        # Generic spacing and length data for all device types
        'gap'        : options.gap,
        'interstice' : options.interstice,
        'periods'    : options.periods,

        # TODO should we consider moving to --xmin, --xmax, --xstep, ect as named arguments?
        # Configure sampling bounds for lookup generator and trajectory evaluation
        # S-axis sampling bounds are device dependent due to full length, X-axis and Z-axis (transverse) are same for all
        'xmin'  : options.x[0], 'xmax'  : options.x[1], 'xstep' : options.x[2],
        'zmin'  : options.z[0], 'zmax'  : options.z[1], 'zstep' : options.z[2],
    }

    if options.type == 'Hybrid_Symmetric':

        # Hybrid Symmetric device has two beams, one top, one bottom
        output['number_of_beams'] = 2

        # A period consists of two horizontally aligned magnets in alternating directions separated by non magnetized iron pole blocks
        output['period_length'] = (4 * options.interstice) + (2 * options.fullmagdims[2]) + (2 * options.poledims[2])

        # Eval length here is only used for S-axis sampling points for lookup generator
        # 16 extra periods is fudge factor to measure overhang on either end of the device
        # TODO this could be calculated from the bounds of the device after magnets have been added, making it the same for all devices
        # TODO only difference between above period_length and this one is due to numerical precision issue
        period_length   = (2 * (options.fullmagdims[2] + options.poledims[2] + (2 * options.interstice)))
        eval_length     = period_length * (options.periods + 16)
        # TODO rounding in this way can probably be avoided
        output['sstep'] = int(round((period_length / (4 * options.steps)) * 100000)) / 100000
        output['smin']  = -(eval_length / 2.0)
        output['smax']  =  (eval_length / 2.0) + output['sstep']

        # Hybrid Symmetric device has the same type ordering and flip matrices on both top and bottom beams
        types         = create_type_list_hybrid_symmetric_top_btm(options.periods)
        flip_matrices = create_flip_matrix_hybrid_symmetric_top_btm(options.periods)

        # Top and bottom beam position functions take same arguments (use dictionary for safety)
        postion_params = {
            'nperiods'            : options.periods,
            'fullmagdims'         : options.fullmagdims,
            'hemagdims'           : options.hemagdims,
            'htmagdims'           : options.htmagdims,
            'poledims'            : options.poledims,
            'mingap'              : options.gap,
            'interstice'          : options.interstice,
            'endgapsym'           : options.endgapsym,
            'terminalgapsymhybrid': options.terminalgapsymhyb,
        }
        top_positions = create_position_list_hybrid_symmetric_top(**postion_params)
        btm_positions = create_position_list_hybrid_symmetric_btm(**postion_params)

        # Top and bottom beams will have same matrices for vertical magnets and alternating for horizontal magnets
        top_direction_matrices = create_direction_matrix_list_hybrid_symmetric_top(options.periods)
        btm_direction_matrices = create_direction_matrix_list_hybrid_symmetric_btm(options.periods)

        # Lookup table mapping magnet type keys to dimension tuples
        magnet_dimensions = {
            # Standard horizontal field magnets
            'HH' : options.fullmagdims,
            # End magnets with different dims to normal magnets (tending to be thinner in the S-axis)
            'HE' : options.hemagdims,
            # Special end kicker magnets
            'HT' : options.htmagdims,
        }

        # Merge the per magnet data arrays computed from each helper function to describe the full top beam
        top_beam = { 'name' : 'Top Beam', 'mags' : [] }
        for index, (type, position, direction_matrix, flip_matrix) in \
                enumerate(zip(types, top_positions, top_direction_matrices, flip_matrices)):

            top_beam['mags'].append({
                'type'             : type,
                'position'         : position,
                'direction_matrix' : direction_matrix,
                'flip_matrix'      : flip_matrix,
                'dimensions'       : magnet_dimensions[type],
            })

        # Merge the per magnet data arrays computed from each helper function to describe the full bottom beam
        btm_beam = { 'name' : 'Bottom Beam', 'mags' : [] }
        for index, (type, position, direction_matrix, flip_matrix) in \
                enumerate(zip(types, btm_positions, btm_direction_matrices, flip_matrices)):

            btm_beam['mags'].append({
                'type'             : type,
                'position'         : position,
                'direction_matrix' : direction_matrix,
                'flip_matrix'      : flip_matrix,
                'dimensions'       : magnet_dimensions[type],
            })

        # Add the complete top and bottom beams to the output data
        output['beams'] = [top_beam, btm_beam]
        
    elif options.type == 'PPM_AntiSymmetric':

        # PPM Anti Symmetric device has two beams, one top, one bottom
        output['number_of_beams'] = 2

        # A period consists of two horizontally aligned and two vertically aligned magnets
        # rotating through 360 degrees on the X-axis (tangent transverse)
        magnet_length = options.interstice + options.fullmagdims[2]
        output['period_length'] = 4 * magnet_length

        # Eval length here is only used for S-axis sampling points for lookup generator
        # 16 extra periods is fudge factor to measure overhang on either end of the device
        # TODO this could be calculated from the bounds of the device after magnets have been added, making it the same for all devices
        eval_length = output['period_length'] * (options.periods + 16)
        # TODO rounding in this way can probably be avoided
        output['sstep'] = int(round((magnet_length / options.steps) * 100000)) / 100000
        output['smin']  = -(eval_length / 2.0)
        output['smax']  =  (eval_length / 2.0) + output['sstep']

        # PPM Anti Symmetric device has the same type ordering and flip matrices on both top and bottom beams
        types         = create_type_list_ppm_antisymmetric(options.periods)
        flip_matrices = create_flip_matrix_list_ppm_antisymmetric_top_btm(options.periods)

        # Top and bottom beam position functions take same arguments (use dictionary for safety)
        position_params = {
            'period'      : options.fullmagdims[2] * 4, 
            'nperiods'    : options.periods, 
            'fullmagdims' : options.fullmagdims, 
            'vemagdims'   : options.vemagdims, 
            'hemagdims'   : options.hemagdims,
            'mingap'      : options.gap, 
            'interstice'  : options.interstice,
        }
        top_positions = create_position_list_ppm_antisymmetric_top(**position_params)
        btm_positions = create_position_list_ppm_antisymmetric_btm(**position_params)
        
        # TODO deprecate and remove this as it is only used for human readable build lists can the direction matrices capture the same information
        top_directions = create_direction_list_ppm_antisymmetric_top(options.periods)
        btm_directions = create_direction_list_ppm_antisymmetric_btm(options.periods)

        # Top and bottom beams will have same matrices for vertical magnets and alternating for horizontal magnets
        top_direction_matrices = create_direction_matrix_list_ppm_antisymmetric_top(options.periods)
        btm_direction_matrices = create_direction_matrix_list_ppm_antisymmetric_btm(options.periods)

        # Lookup table mapping magnet type keys to dimension tuples
        magnet_dimensions = {
            # Standard vertical and horizontal field magnets
            'VV' : options.fullmagdims, 'HH' : options.fullmagdims,
            # End magnets with different dims to normal magnets (tending to be thinner in the S-axis)
            'VE' : options.vemagdims,   'HE' : options.hemagdims,
        }

        # Merge the per magnet data arrays computed from each helper function to describe the full top beam
        top_beam = { 'name' : 'Top Beam', 'mags' : [] }
        for index, (type, position, direction, direction_matrix, flip_matrix) in \
                enumerate(zip(types, top_positions, top_directions, top_direction_matrices, flip_matrices)):

            top_beam['mags'].append({
                'type'             : type,
                'position'         : position,
                # TODO remove direction, only used for human readable output while direction_matrix has same data
                'direction'        : direction,
                'direction_matrix' : direction_matrix,
                'flip_matrix'      : flip_matrix,
                'dimensions'       : magnet_dimensions[type],
            })

        # Merge the per magnet data arrays computed from each helper function to describe the full bottom beam
        btm_beam = { 'name' : 'Bottom Beam', 'mags' : [] }
        for index, (type, position, direction, direction_matrix, flip_matrix) in \
                enumerate(zip(types, btm_positions, btm_directions, btm_direction_matrices, flip_matrices)):

            btm_beam['mags'].append({
                'type'             : type,
                'position'         : position,
                # TODO remove direction, only used for human readable output while direction_matrix has same data
                'direction'        : direction,
                'direction_matrix' : direction_matrix,
                'flip_matrix'      : flip_matrix,
                'dimensions'       : magnet_dimensions[type],
            })

        # Add the complete top and bottom beams to the output data
        output['beams'] = [top_beam, btm_beam]

    elif options.type == 'APPLE_Symmetric':

        # APPLE-II Symmetric device has four beams, two top, two bottom
        output['number_of_beams'] = 4
        output['end_gap']         = options.endgapsym
        output['phasing_gap']     = options.phasinggap
        output['clampcut']        = options.clampcut

        # A period consists of two horizontally aligned and two vertically aligned magnets
        # rotating through 360 degrees on the X-axis (tangent transverse)
        magnet_length = options.interstice + options.fullmagdims[2]
        output['period_length'] = 4 * magnet_length

        # Eval length here is only used for S-axis sampling points for lookup generator
        # 16 extra periods is fudge factor to measure overhang on either end of the device
        # TODO this could be calculated from the bounds of the device after magnets have been added, making it the same for all devices
        eval_length = output['period_length'] * (options.periods + 16)
        # TODO rounding in this way can probably be avoided
        output['sstep'] = int(round((magnet_length / options.steps) * 100000)) / 100000
        output['smin']  = -(eval_length / 2.0)
        output['smax']  =  (eval_length / 2.0) + output['sstep']

        # APPLE-II Symmetric device has the same type ordering and flip matrices on all four beams
        types         = create_type_list_apple_symmetric(options.periods)
        flip_matrices = create_flip_matrix_list_apple_symmetric(options.periods)

        # All beam position functions take same arguments (use dictionary for safety)
        position_params = {
            'period'      : options.fullmagdims[2] * 4,
            'nperiods'    : options.periods,
            'fullmagdims' : options.fullmagdims,
            'vemagdims'   : options.vemagdims,
            'hemagdims'   : options.hemagdims,
            'mingap'      : options.gap,
            'interstice'  : options.interstice,
            'endgap'      : options.endgapsym,
            'phasinggap'  : options.phasinggap
        }
        q1_positions = create_position_list_apple_symmetric_q1(**position_params)
        q2_positions = create_position_list_apple_symmetric_q2(**position_params)
        q3_positions = create_position_list_apple_symmetric_q3(**position_params)
        q4_positions = create_position_list_apple_symmetric_q4(**position_params)

        # Top and bottom beams will have same matrices for vertical magnets and alternating for horizontal magnets
        # Each beam still has a unique direction matrices list because of the transpose between beams
        q1_directions_matrices = create_direction_matrix_list_apple_symmetric_q1(options.periods)
        q2_directions_matrices = create_direction_matrix_list_apple_symmetric_q2(options.periods)
        q3_directions_matrices = create_direction_matrix_list_apple_symmetric_q3(options.periods)
        q4_directions_matrices = create_direction_matrix_list_apple_symmetric_q4(options.periods)

        # Lookup table mapping magnet type keys to dimension tuples
        magnet_dimensions = {
            # Standard vertical and horizontal field magnets
            'VV' : options.fullmagdims, 'HH' : options.fullmagdims,
            # End magnets with different dims to normal magnets (tending to be thinner in the S-axis)
            'VE' : options.vemagdims,   'HE' : options.hemagdims,
        }

        # Merge the per magnet data arrays computed from each helper function to describe the full Q1 beam
        q1_beam = { 'name' : 'Q1 Beam', 'mags' : [] }
        for index, (type, position, direction_matrix, flip_matrix) in \
                enumerate(zip(types, q1_positions, q1_directions_matrices, flip_matrices)):

            q1_beam['mags'].append({
                'type'             : type,
                'position'         : position,
                'direction_matrix' : direction_matrix,
                'flip_matrix'      : flip_matrix,
                'dimensions'       : magnet_dimensions[type],
            })

        # Merge the per magnet data arrays computed from each helper function to describe the full Q2 beam
        q2_beam = { 'name' : 'Q2 Beam', 'mags' : [] }
        for index, (type, position, direction_matrix, flip_matrix) in \
                enumerate(zip(types, q2_positions, q2_directions_matrices, flip_matrices)):

            q2_beam['mags'].append({
                'type'             : type,
                'position'         : position,
                'direction_matrix' : direction_matrix,
                'flip_matrix'      : flip_matrix,
                'dimensions'       : magnet_dimensions[type],
            })

        # Merge the per magnet data arrays computed from each helper function to describe the full Q3 beam
        q3_beam = { 'name' : 'Q3 Beam', 'mags' : [] }
        for index, (type, position, direction_matrix, flip_matrix) in \
                enumerate(zip(types, q3_positions, q3_directions_matrices, flip_matrices)):

            q3_beam['mags'].append({
                'type'             : type,
                'position'         : position,
                'direction_matrix' : direction_matrix,
                'flip_matrix'      : flip_matrix,
                'dimensions'       : magnet_dimensions[type],
            })

        # Merge the per magnet data arrays computed from each helper function to describe the full Q4 beam
        q4_beam = { 'name' : 'Q4 Beam', 'mags' : [] }
        for index, (type, position, direction_matrix, flip_matrix) in \
                enumerate(zip(types, q4_positions, q4_directions_matrices, flip_matrices)):

            q4_beam['mags'].append({
                'type'             : type,
                'position'         : position,
                'direction_matrix' : direction_matrix,
                'flip_matrix'      : flip_matrix,
                'dimensions'       : magnet_dimensions[type],
            })

        # Add the complete quadrant beams to the output data
        output['beams'] = [q1_beam, q2_beam, q3_beam, q4_beam]

    else:
        # TODO raise properly logged exception in logging refactor
        raise Exception('Insertion Device Type no implemented!!!')

    with open(args[0], 'w') as fp:
        json.dump(output, fp, indent=4)


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

    # TODO Arg string says PPM or APPLE but code only applies to Hybrid and APPLE, not PPM which is only anti-symmetric in the code
    parser.add_option("--endgapsym", dest="endgapsym", help="Symmetric PPM or APPLE devices require an end gap in the termination structure, set gap length in mm", default=5.0, type="float")
    parser.add_option("--terminalgapsymhyb", dest="terminalgapsymhyb", help="Symmetric hybrid devices require a terminal end gap between the final half pole and the terminal H magnet in the termination structure, set gap length in mm", default=5.0, type="float")
    parser.add_option("--phasinggap", dest="phasinggap", help="Gap between Quadrants 1/2 and 3/4 that allow these axes to phase past each other; in mm. APPLES only", default=0.5, type="float")
    parser.add_option("--clampcut", dest="clampcut", help="Square corners removed to allow magnets to be clamped, dimensioned in mm. APPLEs only", default = 5.0, type="float")

    (options, args) = parser.parse_args()
    process(options, args)
