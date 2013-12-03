# order  x, z, s


import json

fp=open('C:/Documents and Settings/gdy32713/My Documents/GitHub/Opt-ID/IDSort/src/v2/IDinput2.json','r')

a=json.load(fp)
fp.close()


def create_type_list_antisymetric_ppm(period):
    # do the first end
    types = []
    start = 0
    stop = 0
    vertical = False

    types.append('HE')
    types.append('VE')

    start, stop = (2, (4*period+1)-2)

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


def create_direction_list_antisymetric_ppm_top(period):
    direction = []
    for i in range(0,(4*period+1)-1,4):
        direction.append((0,0,1))
        direction.append((0,1,0))
        direction.append((0,0,-1))
        direction.append((0,-1,0))
    
    # Append last element
    direction.append((0,0,1))

def create_direction_list_antisymetric_ppm_bottom(period):
    direction = []
    for i in range(0,(4*period+1)-1,4):
        direction.append((0,0,-1))
        direction.append((0,1,0))
        direction.append((0,0,1))
        direction.append((0,-1,0))
    
    # Append last element
    direction.append((0,0,-1))


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
