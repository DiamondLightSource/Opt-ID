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


def generate_per_magnet_array(info, magnetlist, magnets):
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
            magarray = magnetlist.get_magnet_vals(mag['type'], pos[mag['type']], magnets)
            pos[mag['type']] += 1
            magvalues.append(magarray)
        beams[beam['name']] = np.transpose(np.vstack(magvalues))
    return beams


def generate_per_magnet_b_field(info, maglist, mags, lookup):
    beam_arrays = generate_per_magnet_array(info, maglist, mags)
    fields = {}
    for beam in beam_arrays.keys():
        data = lookup[beam][:, 1, :, :, :, :]
        beam_array = beam_arrays[beam]
        result = data * beam_array
        result2 = np.sum(result, 3)
        fields[beam] = result2
    return fields

def generate_per_beam_b_field(info, maglist, mags, f1):
    fields = generate_per_magnet_b_field(info, maglist, mags, f1)
    beam_fields = {}
    for beam in fields.keys():
        beam_fields[beam] = np.sum(fields[beam],3)
    return beam_fields

def generate_id_field(info, maglist, mags, f1):
    fields = generate_per_beam_b_field(info, maglist, mags, f1)
    id_fields = np.zeros(fields.itervalues().next().shape)
    for beam in fields.keys():
        id_fields+=fields[beam]
    return id_fields

def generate_id_field_cost(field, ref_field):
    cost=field-ref_field
    cost=np.square(cost)
    cost=np.sqrt(cost)
    cost=np.sum(cost)
    
    return cost

def generate_reference_magnets(mags):
    ref_mags=magnets.Magnets()
    for magtype in mags.magnet_sets.keys():
        mag_dir = mags.magnet_sets[magtype].values()[0].argmax()
        unit = np.zeros(3)
        unit[mag_dir] = mags.mean_field[magtype]
        ref_mags.add_perfect_magnet_set(magtype, len(mags.magnet_sets[magtype]) , unit, mags.magnet_flip[magtype])
    return ref_mags

def calculate_fitness(id_filename, lookup_filename, magnets_filename, maglist):
    # TODO this will be slow, but should be optimizable with lookups
    f1 = h5py.File(lookup_filename, 'r')
    f2 = open(id_filename, 'r')
    info = json.load(f2)
    f2.close()

    mags = magnets.Magnets()
    mags.load(magnets_filename)

    total_id_field = generate_id_field(info, maglist, mags, f1)

    ref_mags = generate_reference_magnets(mags)
    ref_maglist = magnets.MagLists(ref_mags)
    ref_total_id_field = generate_id_field(info, ref_maglist, ref_mags, f1)
    f1.close()

    return generate_id_field_cost(total_id_field, ref_total_id_field)


def output_fields(filename, id_filename, lookup_filename, magnets_filename, maglist):
    f1 = h5py.File(lookup_filename, 'r')
    f2 = open(id_filename, 'r')
    info = json.load(f2)
    f2.close()

    mags = magnets.Magnets()
    mags.load(magnets_filename)

    f = h5py.File(filename, 'w')
    per_mag_field = generate_per_magnet_b_field(info, maglist, mags, f1)
    per_beam_field = generate_per_beam_b_field(info, maglist, mags, f1)
    total_id_field = generate_id_field(info, maglist, mags, f1)
    for name in per_mag_field.keys():
        f.create_dataset("%s_per_magnet" % (name), data=per_mag_field[name])
        f.create_dataset("%s_per_beam" % (name), data=per_beam_field[name])
    f.create_dataset('id_Bfield', data=total_id_field)
    f.close()


if __name__ == "__main__" :
    mags = magnets.Magnets()
    
    mags.add_magnet_set('HH', "S:/Technical/IDs/Ed/Bash Sort/I23/I23H.sim", (-1.,1.,-1.))
    mags.add_magnet_set('HE', "S:/Technical/IDs/Ed/Bash Sort/I23/I23HEA.sim", (-1.,1.,-1.))
    mags.add_magnet_set('VV', "S:/Technical/IDs/Ed/Bash Sort/I23/I23V.sim", (-1.,-1.,1.))
    mags.add_magnet_set('VE', "S:/Technical/IDs/Ed/Bash Sort/I23/I23VE.sim", (-1.,-1.,1.))

    ref_mags=generate_reference_magnets(mags)

    maglist = magnets.MagLists(mags)
    ref_maglist = magnets.MagLists(ref_mags)

    maglist.shuffle_all()

    import h5py
    f1 = h5py.File('unit.h5', 'r')

    f2 = open('id.json', 'r')
    info = json.load(f2)

    magarrays = generate_per_magnet_array(info, maglist, mags)
    per_mag_field = generate_per_magnet_b_field(info, maglist, mags, f1)
    per_beam_field = generate_per_beam_b_field(info, maglist, mags, f1)
    total_id_field = generate_id_field(info, maglist, mags, f1)
    
    
    ref_magarrays = generate_per_magnet_array(info, ref_maglist, ref_mags)
    ref_per_mag_field = generate_per_magnet_b_field(info, ref_maglist, ref_mags, f1)
    ref_per_beam_field = generate_per_beam_b_field(info, ref_maglist, ref_mags, f1)
    ref_total_id_field = generate_id_field(info, ref_maglist, ref_mags, f1)
    
    
    cost_total_id_field=generate_id_field_cost(total_id_field,ref_total_id_field)

    f1.close()
    f2.close()

    f3 = h5py.File('real_data.h5', 'w')
    for name in per_mag_field.keys():
        f3.create_dataset("%s_per_magnet" % (name), data=per_mag_field[name])
        f3.create_dataset("%s_per_beam" % (name), data=per_beam_field[name])
    f3.create_dataset('id_Bfield',data=total_id_field)
    f3.close()
    
    f4 = h5py.File('reference.h5', 'w')
    for name in ref_per_mag_field.keys():
        f4.create_dataset("%s_per_magnet" % (name), data=ref_per_mag_field[name])
        f4.create_dataset("%s_per_beam" % (name), data=ref_per_beam_field[name])
    f4.create_dataset('id_Bfield',data=ref_total_id_field)
    f4.close()
