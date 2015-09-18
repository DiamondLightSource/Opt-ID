'''
Created on 5 Dec 2013

@author: ssg37927
'''
import numpy as np

import h5py
import json

import magnets
import magnet_tools as mt

import threading

import copy


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
            magarray = magnetlist.get_magnet_vals(mag['type'], pos[mag['type']], magnets, mag['flip_matrix'])
            pos[mag['type']] += 1
            magvalues.append(magarray)
        beams[beam['name']] = np.transpose(np.vstack(magvalues))
    return beams

def compare_magnet_arrays(mag_array_a, mag_array_b, lookup):
    difference_map = {}
    for beam in mag_array_a.keys():
        difference = mag_array_a[beam] - mag_array_b[beam]
        diff_slice = (np.abs(difference).sum(0) > 0.)
        field_diff = np.sum(lookup[beam][:, :, :, :, :, diff_slice] * difference[:,diff_slice], 4)
        difference_map[beam] = field_diff.sum(4)
    return difference_map



def generate_sub_array(beam_array, eval_list, lookup, beam, results):
    # This sum is calculated like this to avoid memory errors
    result = np.sum(lookup[beam][:, :, :, :, :, eval_list[0]] * beam_array[:,eval_list[0]], 4)
    for m in eval_list[1:]:
        tmp = np.sum(lookup[beam][:, :, :, :, :, m] * beam_array[:,m], 4)
        result += tmp
    results.append(result)

def generate_per_beam_b_field(info, maglist, mags, lookup):
    beam_arrays = generate_per_magnet_array(info, maglist, mags)
    procs = 8
    fields = {}
    for beam in beam_arrays.keys():
        beam_array = beam_arrays[beam]
        indexes = range(lookup[beam].shape[5])
        length = len(indexes)/procs
        chunks=[indexes[x:x+length] for x in xrange(0, len(indexes), length)]
        results = []
        pp = []
        for i in range(len(chunks)):
            chunk = chunks[i]
            pp1 = threading.Thread(name='ProcThread-%02i'%(i), target=generate_sub_array, args = (beam_array, chunk, lookup, beam, results))
            pp1.daemon = True
            pp1.start()
            pp.append(pp1)
        
        for pp1 in pp:
            pp1.join()
        
        # This sum is calculated like this to avoid memory errors
        result = results[0]
        for m in range(1, len(results)):
            result += results[m]
        fields[beam] = result
    return fields


def generate_id_field(info, maglist, mags, f1):
    fields = generate_per_beam_b_field(info, maglist, mags, f1)
    id_fields = np.zeros(fields.itervalues().next().shape)
    for beam in fields.keys():
        id_fields+=fields[beam]
    return id_fields

def generate_id_field_cost(field, ref_field):
    cost=field-ref_field
    cost=np.square(cost)
    #cost=np.sqrt(cost)
    cost=np.sum(cost[:,:,:,2:4])
    
    return cost

def generate_reference_magnets(mags):
    ref_mags=magnets.Magnets()
    for magtype in mags.magnet_sets.keys():
        mag_dir = mags.magnet_sets[magtype].values()[0].argmax()
        unit = np.zeros(3)
        unit[mag_dir] = mags.mean_field[magtype]
        #ref_mags.add_perfect_magnet_set(magtype, len(mags.magnet_sets[magtype]) , unit, mags.magnet_flip[magtype])
        ref_mags.add_perfect_magnet_set_duplicate(magtype, mags.magnet_sets[magtype] , unit, mags.magnet_flip[magtype])
    return ref_mags


def calculate_cached_fitness(info, lookup, magnets, maglist, ref_total_id_field):
    total_id_field = generate_id_field(info, maglist, magnets, lookup)
    return generate_id_field_cost(total_id_field, ref_total_id_field)


def calculate_cached_trajectory_fitness(info, lookup, magnets, maglist, ref_trajectories):
    total_id_field = generate_id_field(info, maglist, magnets, lookup)
    pherr, test_array = mt.calculate_phase_error(info, total_id_field)
    return (total_id_field, generate_id_field_cost(test_array, ref_trajectories))

def calculate_trajectory_fitness_from_array(total_id_field, info, ref_trajectories):
    pherr, test_array = mt.calculate_phase_error(info, total_id_field)
    return generate_id_field_cost(test_array, ref_trajectories)


def calculate_fitness(id_filename, lookup_filename, magnets_filename, maglist):
    # TODO this will be slow, but should be optimizable with lookups
    lookup = h5py.File(lookup_filename, 'r')
    f2 = open(id_filename, 'r')
    info = json.load(f2)
    f2.close()

    mags = magnets.Magnets()
    mags.load(magnets_filename)

    ref_mags = generate_reference_magnets(mags)
    ref_maglist = magnets.MagLists(ref_mags)
    ref_total_id_field = generate_id_field(info, ref_maglist, ref_mags, lookup)

    result = calculate_cached_fitness(info, lookup, magnets, maglist, ref_total_id_field)
    lookup.close()

    return result


def output_fields(filename, id_filename, lookup_filename, magnets_filename, maglist):
    f2 = open(id_filename, 'r')
    info = json.load(f2)
    f2.close()
    f1 = h5py.File(lookup_filename, 'r')
    lookup = {}
    for beam in info['beams']:
        lookup[beam['name']] = f1[beam['name']][...]
    f1.close()

    mags = magnets.Magnets()
    mags.load(magnets_filename)
    ref_mags=generate_reference_magnets(mags)

    f = h5py.File(filename, 'w')
    
    per_beam_field = generate_per_beam_b_field(info, maglist, mags, lookup)
    total_id_field = generate_id_field(info, maglist, mags, lookup)
    for name in per_beam_field.keys():
        f.create_dataset("%s_per_beam" % (name), data=per_beam_field[name])
    f.create_dataset('id_Bfield', data=total_id_field)
    trajectory_information=mt.calculate_phase_error(info, total_id_field)
    f.create_dataset('id_phase_error', data = trajectory_information[0])
    f.create_dataset('id_trajectory', data = trajectory_information[1])
    
    per_beam_field = generate_per_beam_b_field(info, maglist, ref_mags, lookup)
    total_id_field = generate_id_field(info, maglist, ref_mags, lookup)
    for name in per_beam_field.keys():
        f.create_dataset("%s_per_beam_perfect" % (name), data=per_beam_field[name])
    f.create_dataset('id_Bfield_perfect', data=total_id_field)
    trajectory_information=mt.calculate_phase_error(info, total_id_field)
    f.create_dataset('id_phase_error_perfect', data = trajectory_information[0])
    f.create_dataset('id_trajectory_perfect', data = trajectory_information[1])

    f.close()


if __name__ == "__main__" :
    import optparse
    usage = "%prog ID_Description_File Lookup_File Magnets_File"
    
    parser = optparse.OptionParser(usage=usage)
    (options, args) = parser.parse_args()
    
    #f2 = open('/home/gdy32713/DAWN_stable/optid/Opt-ID/IDSort/src/v2/2015test.json', 'r')
    f2 = open(args[0], 'r')
    info = json.load(f2)
    f2.close()

    #f1 = h5py.File('/home/gdy32713/DAWN_stable/optid/Opt-ID/IDSort/src/v2/2015test.h5', 'r')
    f1 = h5py.File(args[1], 'r')
    lookup = {}
    for beam in info['beams']:
        lookup[beam['name']] = f1[beam['name']][...]
    f1.close()
    

    mags = magnets.Magnets()
    #mags.load('/home/gdy32713/DAWN_stable/optid/Opt-ID/IDSort/src/v2/magnets.mag')
    mags.load(args[2])
    
    ref_mags = generate_reference_magnets(mags)
    ref_maglist = magnets.MagLists(ref_mags)
    ref_total_id_field = generate_id_field(info, ref_maglist, ref_mags, lookup)
    ref_pherr, ref_trajectories = mt.calculate_phase_error(info, ref_total_id_field)

    maglist = magnets.MagLists(mags)
    maglist.shuffle_all()
    original_bfield, maglist_fitness = calculate_cached_trajectory_fitness(info, lookup, mags, maglist, ref_trajectories)
    
    mag_array = generate_per_magnet_array(info, maglist, mags)
    
    for i in range(2):
    

        maglist2 =  copy.deepcopy(maglist)
        maglist2.mutate(1)
        
        mag_array2 = generate_per_magnet_array(info, maglist2, mags)
        
        update = compare_magnet_arrays(mag_array, mag_array2, lookup)
        updated_bfield = original_bfield
        for beam in update.keys() :
            if update[beam].size != 0:
                updated_bfield = updated_bfield - update[beam]
        
        maglist2_fitness_estimate = calculate_trajectory_fitness_from_array(updated_bfield, info, ref_trajectories)
        new_bfield, maglist2_fitness = calculate_cached_trajectory_fitness(info, lookup, mags, maglist2, ref_trajectories)
        
        fitness_error = abs(maglist2_fitness_estimate - maglist2_fitness)
        
        print("Estimated fitness error is %2.10e %2.10e %2.10e"%(maglist2_fitness_estimate, maglist2_fitness, fitness_error))

#     f1 = h5py.File('/dls/science/groups/das/ID/I13j/unit_chunks.h5', 'r')
# 
#     ref_mags=generate_reference_magnets(mags)
#     ref_maglist = magnets.MagLists(ref_mags)
#f1.close()
#    per_mag_field = generate_sub_array(beam_array, eval_list, lookup, beam, per_mag_field)
#    per_mag_field = generate_per_magnet_b_field(info, maglist, mags, f1)
    maglist0 = magnets.MagLists(mags)
    maglist0.sort_all()
    maglist0.flip('HH', (107,294,511,626))
    per_beam_field = generate_per_beam_b_field(info, maglist0, mags, lookup)
    total_id_field = generate_id_field(info, maglist0, mags, lookup)
    pherr, trajectories = mt.calculate_phase_error(info,total_id_field)
#     
#     
#     ref_magarrays = generate_per_magnet_array(info, ref_maglist, ref_mags)
# #    ref_per_mag_field = generate_per_magnet_b_field(info, ref_maglist, ref_mags, f1)
#     ref_per_beam_field = generate_per_beam_b_field(info, ref_maglist, ref_mags, f1)
#     ref_total_id_field = generate_id_field(info, ref_maglist, ref_mags, f1)
#     ref_trajectories = mt.calculate_phase_error(info,ref_total_id_field)
#     
#     
#     cost_total_id_field=generate_id_field_cost(total_id_field,ref_total_id_field)
# 

    f3 = h5py.File('real_data.h5', 'w')
    for name in per_beam_field.keys():
# #        f3.create_dataset("%s_per_magnet" % (name), data=per_mag_field[name])
        f3.create_dataset("%s_per_beam" % (name), data=per_beam_field[name])
    f3.create_dataset('id_Bfield',data=total_id_field)
    f3.create_dataset('id_phase_error',data=trajectories[0])
    f3.create_dataset('id_trajectories',data=trajectories[2])
    f3.close()
    
    f4 = open('I21_setmag.inp','w')
    
    if info['type']=='APPLE_Symmetric':
        
        #TODO make a proper function somewhere
        #generate idlist here
        a=0
        vv=0
        hh=0
        ve=0
        he=0
        for b in range(len(info['beams'])):
            a=0
            for mag in info['beams'][b]['mags']:
                if info['beams'][b]['mags'][a]['type']=='HE':mag_type=4
                elif info['beams'][b]['mags'][a]['type']=='VE':mag_type=3
                elif info['beams'][b]['mags'][a]['type']=='HH':mag_type=2
                elif info['beams'][b]['mags'][a]['type']=='VV':mag_type=1
                
                if mag_type==1:
                    mag_num=int(maglist0.magnet_lists['VV'][vv][0])
                    mag_flip=maglist0.magnet_lists['VV'][vv][1]
                    vv+=1
                
                if mag_type==2:
                    mag_num=int(maglist0.magnet_lists['HH'][hh][0])
                    mag_flip=maglist0.magnet_lists['HH'][hh][1]
                    hh+=1
                    
                if mag_type==3:
                    mag_num=int(maglist0.magnet_lists['VE'][ve][0])
                    mag_flip=maglist0.magnet_lists['VE'][ve][1]
                    ve+=1
                    
                if mag_type==4:
                    mag_num=int(maglist0.magnet_lists['HE'][he][0])
                    mag_flip=maglist0.magnet_lists['HE'][he][1]
                    he+=1
                
                line= ("%5i %4i %4i %4i %4i %4i\n"%(b+1,a+1,mag_type,info['beams'][b]['mags'][a]['direction_matrix'][0][0]+info['beams'][b]['mags'][a]['direction_matrix'][0][1],mag_flip, mag_num))
                f4.write(line)
                
                a+=1
                
            f4.write("\n")
        
        f4.close()
    
#     
#     f4 = h5py.File('reference.h5', 'w')
#     for name in ref_per_beam_field.keys():
# #        f4.create_dataset("%s_per_magnet" % (name), data=ref_per_mag_field[name])
#         f4.create_dataset("%s_per_beam" % (name), data=ref_per_beam_field[name])
#     f4.create_dataset('id_Bfield',data=ref_total_id_field)
#     f4.create_dataset('id_phase_error',data=ref_trajectories[0])
#     f4.create_dataset('id_trajectories',data=ref_trajectories[1])
#     f4.close()
