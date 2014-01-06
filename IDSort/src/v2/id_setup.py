# order  x, z, s
import json


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

    # finally add in the other end
    types.append('VE')
    types.append('HE')

    return types


def create_direction_list_antisymetric_ppm_bottom(nperiods):
    direction = []
    for i in range(0, (4 * nperiods + 1) - 1, 4):
        direction.append((1, 1, 1))
        direction.append((1, 1, 1))
        direction.append((-1, 1, -1))
        direction.append((-1, -1, 1))

    # Append last element
    direction.append((1, 1, 1))
    return direction


def create_direction_list_antisymetric_ppm_top(nperiods):
    direction = []
    for i in range(0, (4 * nperiods + 1) - 1, 4):
        direction.append((-1, 1, -1))
        direction.append((1, 1, 1))
        direction.append((1, 1, 1))
        direction.append((-1, -1, 1))

    # Append last element
    direction.append((-1, 1, -1))
    return direction

def create_location_list_antisymmetric_ppm_top(period, nperiods,fullmagdims,vemagdims,hemagdims,mingap,interstice):
    V1 = []
    length = (4*(nperiods-1)+1)*(fullmagdims[2]+interstice)+2*(vemagdims[2]+interstice)+2*(hemagdims[2]+interstice)-interstice
    x=-fullmagdims[0]/2.0
    z=mingap/2.0
    s=-length/2.0
    V1.append((x,z,s))
    s+=(vemagdims[2]+interstice)
    V1.append((x,z,s))
    s+=(hemagdims[2]+interstice)
    for i in range(2,(4*nperiods+1)-2,1):
        V1.append((x,z,s))
        s+=(fullmagdims[2]+interstice)
    V1.append((x,z,s))
    s+=(hemagdims[2]+interstice)
    V1.append((x,z,s))
    return V1

def create_location_list_antisymmetric_ppm_bottom(period, nperiods,fullmagdims,vemagdims,hemagdims,mingap,interstice):
    V1 = []
    length = (4*(nperiods-1)+1)*fullmagdims[2]+2*vemagdims[2]+2*hemagdims[2]+4*nperiods*interstice
    x=-fullmagdims[0]/2.0
    z=-fullmagdims[1]-mingap/2.0
    s=-length/2.0
    V1.append((x,z,s))
    s+=(vemagdims[2]+interstice)
    V1.append((x,z,s))
    s+=(hemagdims[2]+interstice)
    for i in range(2,(4*nperiods+1)-2,1):
        V1.append((x,z,s))
        s+=(fullmagdims[2]+interstice)
    V1.append((x,z,s))
    s+=(hemagdims[2]+interstice)
    V1.append((x,z,s))
    return V1

if __name__ == "__main__":
    import optparse
    usage = "%prog [options] OutputFile"
    parser = optparse.OptionParser(usage=usage)
    parser.add_option("-p", "--periods", dest="periods", help="Set the number of full periods for the Device", default=108, type="int")
    parser.add_option("--fullmagdims", dest="fullmagdims", help="Set the dimensions of the full magnet blocks (x,z,s) in mm", nargs=3, default=(41., 16., 6.22), type="float")
    parser.add_option("--vemagdims", dest="vemagdims", help="Set the dimensions of the VE magnet blocks (x,z,s) in mm", nargs=3, default=(41., 16., 3.12), type="float")
    parser.add_option("--hemagdims", dest="hemagdims", help="Set the dimensions of the HE magnet blocks (x,z,s) in mm", nargs=3, default=(41., 16., 3.3), type="float")
    parser.add_option("-i", dest="interstice", help="Set the dimensions of the slack between adjacent magnets (interstice) in mm", default=0.03, type="float")
    parser.add_option("-g", "--gap", dest="gap", help="Set the gap for the device to be created at", default=6.15, type="float")
    parser.add_option("-t", "--type", dest="type", help="Set the device type", type="string", default="PPM_AntiSymetric")
    parser.add_option("-v", "--verbose", dest="verbose", help="display debug information", action="store_true", default=False)
    parser.add_option("-n", "--name", dest="name", help="PPM name", default="J13", type="string")
    parser.add_option("-x", "--xstartstopstep", dest="x", help="X start stop and step", nargs=3, default=(-40.0, 41., 20.0), type="float")
    parser.add_option("-z", "--zstartstopstep", dest="z", help="Z start stop and step", nargs=3, default=(0.0, 0.1, 0.1), type="float")
    parser.add_option("-s", "--stepsperperiod", dest="steps", help="Number of steps in S per magnet", default=12, type="float")

    (options, args) = parser.parse_args()

    if options.type == 'PPM_AntiSymetric':
        output = {}
        output['name'] = options.name
        output['type'] = options.type
        output['number_of_beams'] = 2
        output['gap'] = options.gap
        output['periods'] = options.periods
        # TODO needs sorting out
        output['xmin'] = options.x[0]
        output['xmax'] = options.x[1]
        output['xstep'] = options.x[2]
        output['zmin'] = options.z[0]
        output['zmax'] = options.z[1]
        output['zstep'] = options.z[2]
        length = (options.fullmagdims[2]+options.interstice)*4*(options.periods+16)
        output['smin'] = -length/2.0
        output['smax'] = (length/2.0)+(options.fullmagdims[2]/options.steps)
        output['sstep'] = options.fullmagdims[2]/options.steps
        output['interstice'] = options.interstice

        # calculate all magnet values
        types = create_type_list_antisymetric_ppm(options.periods)
        top_directions = create_direction_list_antisymetric_ppm_top(options.periods)
        bottom_directions = create_direction_list_antisymetric_ppm_bottom(options.periods)
        top_positions = create_location_list_antisymmetric_ppm_top(options.fullmagdims[2]*4, options.periods, options.fullmagdims, options.vemagdims, options.hemagdims, options.gap, options.interstice)
        bottom_positions = create_location_list_antisymmetric_ppm_bottom(options.fullmagdims[2]*4, options.periods, options.fullmagdims, options.vemagdims, options.hemagdims, options.gap, options.interstice)

        # output beams
        output['beams'] = []
        top_beam = {}
        top_beam['name'] = "Top Beam"
        top_beam['mags'] = []
        bottom_beam = {}
        bottom_beam = {}
        bottom_beam['name'] = "Bottom Beam"
        bottom_beam['mags'] = []

        # top beam
        for i in range(len(types)):
            mag = {}
            mag['type'] = types[i]
            mag['direction'] = top_directions[i]
            mag['position'] = top_positions[i]
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
            mag['position'] = bottom_positions[i]
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
