'''
Created on 5 Dec 2013

@author: ssg37927
'''
import numpy as np

import h5py
import json

import magnets


def load_lookup(filename, beam):
    f = h5py.File(filename, 'r')
    return f[beam]


def generate_per_magnet_array(info, magnetlist):
    pos = {}
    pos['VV'] = 0;
    pos['VE'] = 0;
    pos['HH'] = 0;
    pos['HE'] = 0;

    beams = {}

    # for each beam
    for beam in info['beams']:
        magvalues = []
        for mag in beam['mags']:
            magarray = magnetlist.get_magnet_vals(mag['type'], pos[mag['type']])
            pos[mag['type']] += 1
            magvalues.append(magarray)
        beams[beam['name']] = np.transpose(np.vstack(magvalues))
    return beams


def generate_per_magnet_b_field(beam_arrays, lookup):
    fields = {}
    for beam in beam_arrays.keys():
        data = lookup[beam][:,2,:,:,:,:]
        beam_array = beam_arrays[beam]
        result = data * beam_array
        fields[beam] = result
    return fields

if __name__ == "__main__" :
    mags = magnets.Magnets()

    mags.add_perfect_magnet_set('HH', 20 , (0.,0.,1.), (-1.,1.,-1.))
    mags.add_perfect_magnet_set('HE', 5 , (0.,0.,1.), (-1.,1.,-1.))
    mags.add_perfect_magnet_set('VV', 20 , (0.,1.,0.), (-1.,-1.,1.))
    mags.add_perfect_magnet_set('VE', 5 , (0.,1.,0.), (-1.,-1.,1.))

    maglist = magnets.MagLists(mags)

    import h5py
    f1 = h5py.File('test.h5', 'r')

    f2 = open('test.json', 'r')
    info = json.load(f2)

    magarrays = generate_per_magnet_array(info, maglist)
    data = generate_per_magnet_b_field(magarrays, f1)

    f1.close()
    f2.close()
    
    f3 = h5py.File('real.h5', 'w')
    for name in data.keys():
        f3.create_dataset(name, data=data[name])
    f3.close()
