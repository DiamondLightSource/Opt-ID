'''
Created on 8 Jan 2014

@author: gdy32713
'''
import h5py
import json
import magnet_tools as mt
import numpy as np

import cPickle as pickle

if __name__ == '__main__':
#    fpre = h5py.File('pre.h5', 'r')
    '''fpost = h5py.File('post.h5','r')
    
    f2 = open('id2.json', 'r')
    info = json.load(f2)
    with h5py.File('post.h5', 'r') as fpre:
        B_pre = fpre['id_Bfield'].value
    
    pre_traj = mt.calculate_phase_error(info, B_pre)
    
    a=1'''
    
    
    maglists = pickle.load( open( "2.29512469e-08_000_43070d4126ff.genome", "rb" ) )
    
    f2 = open('id2.json', 'r')
    info = json.load(f2)
    f2.close()
    
    f3 = open('setmag.inp','w')
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
                mag_num=int(maglists.magnet_lists['VV'][vv][0])
                mag_flip=maglists.magnet_lists['VV'][vv][1]
                vv+=1
            
            if mag_type==2:
                mag_num=int(maglists.magnet_lists['HH'][hh][0])
                mag_flip=maglists.magnet_lists['HH'][hh][1]
                hh+=1
                
            if mag_type==3:
                mag_num=int(maglists.magnet_lists['VE'][ve][0])
                mag_flip=maglists.magnet_lists['VE'][ve][1]
                ve+=1
                
            if mag_type==4:
                mag_num=int(maglists.magnet_lists['HE'][he][0])
                mag_flip=maglists.magnet_lists['HE'][he][1]
                he+=1
            
            line= ("%5i %4i %4i %4i %4i %4i\n"%(b+1,a+1,mag_type,info['beams'][b]['mags'][a]['direction'][0],mag_flip, mag_num))
            f3.write(line)
            
            a+=1
            
        f3.write("\n")
    
    f3.close()
    a=1