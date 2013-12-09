import magnets
import genome_tools
from genome_tools import ID_BCell



if __name__ == "__main__":
    import optparse
    usage = "%prog [options] output_dir input_files"
    parser = optparse.OptionParser(usage=usage)
    parser.add_option("-f", "--fitness", dest="fitness", help="Set the target fitness", default=0.0, type="float")
    parser.add_option("-p", "--processing", dest="processing", help="Set the total number of processing units per file", default=10, type="int")
    parser.add_option("-l", "--lookup", dest="lookup", help="Set the path to the lookup table", default='lookup.h5', type="string")
    parser.add_option("-m", "--magnets", dest="magnets", help="Set the path to the magnet description file", default='magnets.mag', type="string")
    parser.add_option("-s", "--setup", dest="setup", help="set number of genomes to create in setup mode", default=-1, type='int')

    (options, args) = parser.parse_args()

    print("Loading magnets")
    mags = magnets.Magnets()
    mags.load(options.magnets)

    if options.setup > 0:
        print("Running setup")
        for i in range(options.setup):
            # create a fresh maglist
            maglist = magnets.MagLists(mags)
            genome = ID_BCell()
            genome.create(maglist)
            genome.save(args[0])

