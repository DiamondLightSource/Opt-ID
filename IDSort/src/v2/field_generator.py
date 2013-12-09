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
        data = lookup[beam][:, 1, :, :, :, :]
        beam_array = beam_arrays[beam]
        result = data * beam_array
        result2 = np.sum(result, 3)
        fields[beam] = result2
    return fields

def generate_per_beam_b_field(fields):
    beam_fields = {}
    for beam in fields.keys():
        beam_fields[beam] = np.sum(fields[beam],3)
    return beam_fields

if __name__ == "__main__" :
    mags = magnets.Magnets()
    ref_mags=magnets.Magnets()

    

#    mags.add_magnet_set('HH', "../../data/I23H.sim", (-1.,1.,-1.))
#    mags.add_magnet_set('HE', "../../data/I23HEA.sim", (-1.,1.,-1.))
#    mags.add_magnet_set('VV', "../../data/I23V.sim", (-1.,-1.,1.))
#    mags.add_magnet_set('VE', "../../data/I23VE.sim", (-1.,-1.,1.))
    
    mags.add_magnet_set('HH', "S:/Technical/IDs/Ed/Bash Sort/I23/I23H.sim", (-1.,1.,-1.))
    mags.add_magnet_set('HE', "S:/Technical/IDs/Ed/Bash Sort/I23/I23HEA.sim", (-1.,1.,-1.))
    mags.add_magnet_set('VV', "S:/Technical/IDs/Ed/Bash Sort/I23/I23V.sim", (-1.,-1.,1.))
    mags.add_magnet_set('VE', "S:/Technical/IDs/Ed/Bash Sort/I23/I23VE.sim", (-1.,-1.,1.))
    
    ref_mags.add_perfect_magnet_set('HH', len(mags.magnet_sets['HH']) , (0.,0.,mags.mean_field['HH']), (-1.,1.,-1.))
    ref_mags.add_perfect_magnet_set('HE', len(mags.magnet_sets['HE']) , (0.,0.,mags.mean_field['HE']), (-1.,1.,-1.))
    ref_mags.add_perfect_magnet_set('VV', len(mags.magnet_sets['VV']) , (0.,1.,mags.mean_field['VV']), (-1.,-1.,1.))
    ref_mags.add_perfect_magnet_set('VE', len(mags.magnet_sets['VE']) , (0.,1.,mags.mean_field['VE']), (-1.,-1.,1.))

#    mags.add_perfect_magnet_set('HH', 40 , (0.,0.,1.), (-1.,1.,-1.))
#    mags.add_perfect_magnet_set('HE', 20 , (0.,0.,1.), (-1.,1.,-1.))
#    mags.add_perfect_magnet_set('VV', 40 , (0.,1.,0.), (-1.,-1.,1.))
#    mags.add_perfect_magnet_set('VE', 20 , (0.,1.,0.), (-1.,-1.,1.))

    maglist = magnets.MagLists(mags)

    maglist.shuffle_all()

    import h5py
    f1 = h5py.File('test.h5', 'r')

    f2 = open('test.json', 'r')
    info = json.load(f2)

    magarrays = generate_per_magnet_array(info, maglist)
    per_mag_field = generate_per_magnet_b_field(magarrays, f1)
    per_beam_field = generate_per_beam_b_field(per_mag_field)

    f1.close()
    f2.close()

    f3 = h5py.File('perfect.h5', 'w')
    for name in per_mag_field.keys():
        f3.create_dataset("%s_per_magnet" % (name), data=per_mag_field[name])
        f3.create_dataset("%s_per_beam" % (name), data=per_beam_field[name])
    f3.close()
