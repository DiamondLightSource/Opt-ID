'''
Created on 23 Apr 2015

@author: gdy32713
'''

import os
import json
import pickle

import numpy as np

from IDSort.src.magnets import Magnets, MagLists
import IDSort.src.field_generator as fg


def human_output(id_info, filename):
    
    maglists = pickle.load( open( filename, "rb" ) )
    
    f2 = open(id_info, 'r')
    info = json.load(f2)
    f2.close()
    
    readable_outfile = (os.path.split(filename)[1]+'.inp')
    
    f3 = open(readable_outfile,'w')
    
    if info['type']=='Hybrid_Symmetric':
        
        #TODO make a proper function somewhere
        #generate idlist here
        a=0
        vv=0
        hh=0
        ve=0
        he=0
        ht=0
        for b in range(len(info['beams'])):
            a=0
            for mag in info['beams'][b]['mags']:
                if info['beams'][b]['mags'][a]['type']=='HT':mag_type=5
                elif info['beams'][b]['mags'][a]['type']=='HE':mag_type=4
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
                    
                if mag_type==5:
                    mag_num=int(maglists.magnet_lists['HT'][ht][0])
                    mag_flip=maglists.magnet_lists['HT'][ht][1]
                    ht+=1
                
                line= ("%5i %4i %4i %4i %4i %03i\n"%(b+1,a+1,mag_type,info['beams'][b]['mags'][a]['direction_matrix'][2][2],mag_flip, mag_num))
                f3.write(line)
                
                a+=1
                
            f3.write("\n")
        
        f3.close()
    
    if info['type']=='PPM_AntiSymmetric':
        
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
                
                line= ("%5i %4i %4i %4i %4i %03i\n"%(b+1,a+1,mag_type,info['beams'][b]['mags'][a]['direction'][0],mag_flip, mag_num))
                f3.write(line)
                
                a+=1
                
            f3.write("\n")
        
        f3.close()


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
                    mag_num=int(maglists.magnet_lists['VV'][vv][0])
                    mag_flip=1
                    vv+=1
                
                elif mag_type==2:
                    mag_num=int(maglists.magnet_lists['HH'][hh][0])
                    mag_flip=maglists.magnet_lists['HH'][hh][1]
                    hh+=1
                    
                elif mag_type==3:
                    mag_num=int(maglists.magnet_lists['VE'][ve][0])
                    mag_flip=1
                    ve+=1
                    
                elif mag_type==4:
                    mag_num=int(maglists.magnet_lists['HE'][he][0])
                    mag_flip=maglists.magnet_lists['HE'][he][1]
                    he+=1
                
                if mag_type==3 or mag_type==1:
                    line= ("%6i %5i %5i %5i %5i %05i\n"%(b+1,a+1,mag_type,info['beams'][b]['mags'][a]['direction_matrix'][1][1],mag_flip, mag_num))
                    
                elif mag_type==2 or mag_type==4:
                    line= ("%6i %5i %5i %5i %5i %05i\n"%(b+1,a+1,mag_type,info['beams'][b]['mags'][a]['direction_matrix'][2][2],mag_flip, mag_num))
                
                f3.write(line)
                
                a+=1
                
            f3.write("\n")
        
        f3.close()

def process(options, args):
    if options.create_genome:
        for filename in args[0::]:
            print("Turning file %s from Human Readable to Genome" % (filename))

            f2 = open(filename, 'r')
            buildlist = np.genfromtxt(filename, dtype=str)
            f2.close()

            mags = Magnets()
            mags.load(options.magnets_filename)

            maglist = MagLists(mags)

            heswap = 0
            veswap = 0
            hhswap = 0
            vvswap = 0

            for line in range(buildlist.shape[0]):

                if int(buildlist[line,2])==4:
                    #maglist.magnet_lists['HE'][heswap][0]=buildlist[line,5]
                    maglist.swap('HE',maglist.magnet_lists['HE'].index([buildlist[line,5],1,0]) , heswap)
                    maglist.magnet_lists['HE'][heswap][1]=int(buildlist[line,4])

                    heswap+=1


                elif int(buildlist[line,2])==3:
                    #maglist.magnet_lists['VE'][veswap][0]=buildlist[line,5]
                    maglist.swap('VE',maglist.magnet_lists['VE'].index([buildlist[line,5],1,0]) , veswap)
                    maglist.magnet_lists['VE'][veswap][1]=int(buildlist[line,4])
                    veswap+=1

                elif int(buildlist[line,2])==2:
                    #maglist.magnet_lists['HH'][hhswap][0]=buildlist[line,5]
                    maglist.swap('HH',maglist.magnet_lists['HH'].index([buildlist[line,5],1,0]) , hhswap)
                    maglist.magnet_lists['HH'][hhswap][1]=int(buildlist[line,4])

                    hhswap+=1

                elif int(buildlist[line,2])==1:
                    #maglist.magnet_lists['VV'][vvswap][0]=buildlist[line,5]
                    maglist.swap('VV',maglist.magnet_lists['VV'].index([buildlist[line,5],1,0]) , vvswap)
                    maglist.magnet_lists['VV'][vvswap][1]=int(buildlist[line,4])

                    vvswap+=1

            outfile = (os.path.split(filename)[1]+'.h5')
            #fg.output_fields(outfile, options.id_filename, options.id_template, options.magnets_filename, maglist)
            fp = open(os.path.split(filename)[1]+'.genome','wb')
            pickle.dump(maglist, fp)
            fp.close()

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


if __name__ == '__main__':
    import optparse
    usage = "%prog [options] Genome_filenames"
    parser = optparse.OptionParser(usage=usage)
    parser.add_option("-a", "--analyse", dest="analysis", help="Analyses the genome and puts results in HDF5 format", action="store_true", default=False)
    parser.add_option("-r", "--readable", dest="readable", help="Writes the genome in a human /Excel readable format", action="store_true", default=False)
    parser.add_option("-g", "--create_genome", dest="create_genome", help="Reverses the analysis option and turns a human readable list to a genome pickle", action="store_true", default=False)
    parser.add_option("-i", "--info", dest="id_filename", help="Set the path to the id data", default='/home/gdy32713/DAWN_stable/optid/Opt-ID/IDSort/src/v2/2015test.json', type="string")
    parser.add_option("-m", "--magnets", dest="magnets_filename", help="Set the path to the magnet description file", default='/home/gdy32713/DAWN_stable/optid/Opt-ID/IDSort/src/v2/magnets.mag', type="string")
    parser.add_option("-t", "--template", dest="id_template", help="Set the path to the magnet description file", default='/home/gdy32713/DAWN_stable/optid/Opt-ID/IDSort/src/v2/2015test.h5', type="string")

    (options, args) = parser.parse_args()
    process(options, args)
