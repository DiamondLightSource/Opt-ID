'''
Created on 23 Apr 2015

@author: gdy32713
'''

import os
import json
import field_generator as fg
import cPickle as pickle

def human_output(id_info, filename):
    
    maglists = pickle.load( open( filename, "rb" ) )
    
    f2 = open(id_info, 'r')
    info = json.load(f2)
    f2.close()
    
    readable_outfile = (os.path.split(filename)[1]+'.inp')
    
    f3 = open(readable_outfile,'w')
    
    if info['type']=='PPM_AntiSymetric':
        
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


if __name__ == '__main__':
    import optparse
    usage = "%prog [options] Genome_filenames"
    parser = optparse.OptionParser(usage=usage)
    parser.add_option("-a", "--analyse", dest="analysis", help="Analyses the genome and puts results in HDF5 format", action="store_true", default=False)
    parser.add_option("-r", "--readable", dest="readable", help="Writes the genome in a human /Excel readable format", action="store_true", default=False)
    parser.add_option("-i", "--info", dest="id_filename", help="Set the path to the id data", default='/home/gdy32713/DAWN_stable/optid/Opt-ID/IDSort/src/v2/2015test.json', type="string")
    parser.add_option("-m", "--magnets", dest="magnets_filename", help="Set the path to the magnet description file", default='/home/gdy32713/DAWN_stable/optid/Opt-ID/IDSort/src/v2/magnets.mag', type="string")
    parser.add_option("-t", "--template", dest="id_template", help="Set the path to the magnet description file", default='/home/gdy32713/DAWN_stable/optid/Opt-ID/IDSort/src/v2/2015test.h5', type="string")

    
    (options, args) = parser.parse_args()
    
    if options.readable:
        
        for filename in args[0::]:
            print("Making file %s human readable." % (filename))
            
            human_output(options.id_filename, filename)
        
    if options.analysis:
        for filename in args[0::]:
            print("Processing file %s" % (filename))
            # load the genome
            maglists = pickle.load( open( filename, "rb" ) )
            
            outfile = (os.path.split(filename)[1]+'.h5')
            fg.output_fields(outfile, options.id_filename, options.id_template, options.magnets_filename, maglists)
