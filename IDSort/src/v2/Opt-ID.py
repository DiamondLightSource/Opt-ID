import magnets
import genome_tools
import random
from genome_tools import ID_BCell

E_STAR = 0.0
M_STAR = 1.0

def mutations(c, e_star, fitness, scale):
    inverse_proportional_hypermutation =  abs(((1.0-(e_star/fitness)) * c) + c)
    a = random.random()
    b = random.random()
    hypermacromuation = abs((a-b) * scale)
    return int(inverse_proportional_hypermutation + hypermacromuation)

if __name__ == "__main__":
    import optparse
    usage = "%prog [options] output_dir input_files"
    parser = optparse.OptionParser(usage=usage)
    parser.add_option("-f", "--fitness", dest="fitness", help="Set the target fitness", default=0.0, type="float")
    parser.add_option("-p", "--processing", dest="processing", help="Set the total number of processing units per file", default=5, type="int")
    parser.add_option("-i", "--info", dest="id_filename", help="Set the path to the id data", default='id.json', type="string")
    parser.add_option("-l", "--lookup", dest="lookup_filename", help="Set the path to the lookup table", default='unit.h5', type="string")
    parser.add_option("-m", "--magnets", dest="magnets_filename", help="Set the path to the magnet description file", default='magnets.mag', type="string")
    parser.add_option("-s", "--setup", dest="setup", help="set number of genomes to create in setup mode", default=-1, type='int')
    parser.add_option("--param_c", dest="c", help="Set the OPT-AI parameter c", default=10.0, type='float')
    parser.add_option("--param_e", dest="e", help="Set the OPT-AI parameter eStar", default=0.0, type='float')
    parser.add_option("--param_scale", dest="scale", help="Set the OPT-AI parameter scale", default=10.0, type='float')

    (options, args) = parser.parse_args()

    print("Loading magnets")
    mags = magnets.Magnets()
    mags.load(options.magnets_filename)

    if options.setup > 0:
        print("Running setup")
        for i in range(options.setup):
            # create a fresh maglist
            maglist = magnets.MagLists(mags)
            maglist.shuffle_all()
            genome = ID_BCell(options.id_filename, options.lookup_filename, options.magnets_filename)
            genome.create(maglist)
            genome.save(args[0])
    
    for filename in args[1::]:
        print("Processing file %s" % (filename))
        
        # load the genome
        genome = ID_BCell(options.id_filename, options.lookup_filename, options.magnets_filename)
        genome.load(filename)
        
        # now we have to create the offspring
        # TODO this is for the moment
        number_of_children = options.processing
        number_of_mutations = mutations(options.c, options.e, genome.fitness, options.scale)
        children = genome.generate_children(number_of_children, number_of_mutations)
        
        # now save the children into the new file
        for child in children:
            child.save(args[0])
        
        # and save the original
        genome.save(args[0])

