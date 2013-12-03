# order  x, z, s


import json

fp=open('C:/Documents and Settings/gdy32713/My Documents/GitHub/Opt-ID/IDSort/src/v2/IDinput2.json','r')

a=json.load(fp)
fp.close()


def create_type_list_antisymetric_ppm(nperiods):
    # do the first end
    types = []
    start = 0
    stop = 0
    vertical = False

    types.append('HE')
    types.append('VE')

    start, stop = (2, (4*nperiods+1)-2)

    # now put in all the middle periods
    for i in range(start, stop):
        if vertical :
            types.append('VV')
            vertical = False
        else :
            types.append('HH')
            vertical = True

    # finaly add in the other end
    types.append('VE')
    types.append('HE')
    
    return types


def create_direction_list_antisymetric_ppm_top(nperiods):
    direction = []
    for i in range(0,(4*nperiods+1)-1,4):
        direction.append((0,0,1))
        direction.append((0,1,0))
        direction.append((0,0,-1))
        direction.append((0,-1,0))
    
    # Append last element
    direction.append((0,0,1))


def create_direction_list_antisymetric_ppm_bottom(nperiods):
    direction = []
    for i in range(0,(4*nperiods+1)-1,4):
        direction.append((0,0,-1))
        direction.append((0,1,0))
        direction.append((0,0,1))
        direction.append((0,-1,0))
    
    # Append last element
    direction.append((0,0,-1))

    
def create_location_list_antisymmetric_ppm_top(period, nperiods,fullmagdims,vemagdims,hemagdims,mingap):
    V1 = []
    length = (4*(nperiods-1)+1)*fullmagdims[2]+2*vemagdims[2]+2*hemagdims[2]
    x=-fullmagdims[0]/2
    z=mingap/2
    s=-length/2.0
    V1.append((x,z,s))
    s+=vemagdims[2]
    V1.append((x,z,s))
    s+=hemagdims[2]
    for i in range(2,(4*period+1)-2,1):
        V1.append((x,z,s))
        s+=fullmagdims[2]
    V1.append((x,z,s))
    s+=hemagdims[2]
    V1.append((x,z,s))
    
    
def create_location_list_antisymmetric_ppm_bottom(period, nperiods,fullmagdims,vemagdims,hemagdims,mingap):
    V1 = []
    length = (4*(nperiods-1)+1)*fullmagdims[2]+2*vemagdims[2]+2*hemagdims[2]
    x=-fullmagdims[0]/2
    z=-fullmagdims[1]-mingap/2
    s=-length/2.0
    V1.append((x,z,s))
    s+=vemagdims[2]
    V1.append((x,z,s))
    s+=hemagdims[2]
    for i in range(2,(4*period+1)-2,1):
        V1.append((x,z,s))
        s+=fullmagdims[2]
    V1.append((x,z,s))
    s+=hemagdims[2]
    V1.append((x,z,s))


if __name__ == "__main__" :
    import optparse
    usage = "%prog [options] OutputFile"
    parser = optparse.OptionParser(usage=usage)
    parser.add_option("-p", "--periods", dest="periods", help="Set the number of full periods for the Device", default=5, type="int")
    parser.add_option("-t", "--type", dest="type", help="Set the device type", type="string", default="PPM_AntiSymetric")
    parser.add_option("-v", "--verbose", dest="verbose", help="display debug information", action="store_true", default=False)

    (options, args) = parser.parse_args()
    
    if options.type == 'PPM_AntiSymetric':
        types = create_type_list_antisymetric_ppm(options.periods)
        top_directions = create_direction_list_antisymetric_ppm_top(options.periods)
        bottom_directions = create_direction_list_antisymetric_ppm_bottom(options.periods)
