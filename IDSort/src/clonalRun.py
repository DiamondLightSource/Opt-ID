'''
Created on 16 Nov 2011

@author: ssg37927
'''

import setmag as sm
import id_bcell as idb
import clonal as cl

import pprint

if __name__ == "__main__" :
    import optparse
    usage = "%prog [options] horizontal_magnets, vertical_magnets, horizontal_end_magnets, vertical_end_magnets, output_filename"
    parser = optparse.OptionParser(usage=usage)
    parser.add_option("-p", "--periods", dest="periods", help="Set the number of full periods for the Device", default=74, type="int")
    parser.add_option("-s", "--symmetric", dest="symmetric", help="Set the device to symmetric rather then Anti-symmetric", action="store_true", default=False)
    parser.add_option("-v", "--verbose", dest="verbose", help="display debug information", action="store_true", default=False)
    parser.add_option("-n", "--agents", dest="agents", help="Set the number of agents for the optimisation", default=20, type="int")
    parser.add_option("-e", "--epochs", dest="epochs", help="Set the number of epochs", default=100, type="int")
    parser.add_option("-a", "--max_age", dest="age", help="Set the maximum age for an agent", default=5, type="int")
    parser.add_option("-d", "--dup", dest="dup", help="Set the dup for the clonal selection", default=2, type="int")
    parser.add_option("-c", "--c", dest="c", help="Set the c parameter for the clonal selection", default=0.5, type="float")
    parser.add_option("-P", "--presort", dest="presort", help="Set the filename for a set of presorted magnets", default=None)
    parser.add_option("-B", "--bfield", dest="bfield", help="Set the filename for the measures bfield", default=None)
    
    
    (options, args) = parser.parse_args()
    
    if options.verbose:
        print "Horizontal Magnets     = %s" % args[0]
        print "Vertical Magnets       = %s" % args[1]
        print "Horizontal End Magnets = %s" % args[2]
        print "Vertical End Magnets   = %s" % args[3]
    
    # Add all the magnets
    mag = sm.AllMagnets()
    mag.add_magnet_set(sm.MagnetStore.horizontal, args[0])
    mag.add_magnet_set(sm.MagnetStore.vertical, args[1])
    mag.add_magnet_set(sm.MagnetStore.horizontal_end, args[2])
    mag.add_magnet_set(sm.MagnetStore.vertical_end, args[3])
    
    if options.verbose:
        print "Magnet Sets"
        pprint.pprint(mag.magnet_sets)
    
    ## Create the device
    symmetry = sm.BeamAssembly.antisymetric
    if options.symmetric:
        symmetry = sm.BeamAssembly.symetric
    
    ppm = sm.PPM(mag, periods=options.periods, symetry=symmetry, magdims=[41.,16.,6.75], offset=0.325, presort=options.presort, bfields=options.bfields)
    
    if options.verbose:
        ppm.report()
    
    if options.bfield == "None" :
        # do the sort
        ppmbc = idb.PPM_BCell(ppm)
        
        cs = cl.ClonalSelection(ppmbc,args[4], population_size=options.agents, max_age= options.age, dup=options.dup, c=options.c)
        
        cs.initialise()
        
        cs.run_epocs(options.epochs)
        
        if options.verbose:
            print "Number of calls :", idb.PPM_BCell.objective_calls
        return
    else:
        ## Do the shim