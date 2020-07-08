'''
Takes 3 arguments:
1. The previous genome 
2. The new genome generated from the shim code
3. The path and name of the file to output eg. $IDDATA/shim1.txt
'''

from IDSort.src.genome_tools import ID_BCell


def process(options, args):
    # TODO refactor arguments to use options named tuple
    g1 = ID_BCell()
    g1.load(args[0])

    g2 = ID_BCell()
    g2.load(args[1])

    filepath = args[2] if (len(args) > 2) else 'compare.txt'

    # TODO convert output to pandas .csv file
    with open(filepath, 'w') as fp:
        fp.write("Type    Shim no.    Original   Orientation    Replacement    Orientation\n")

        for list_key in g1.genome.magnet_lists.keys():
            for i, (g1_mag, g2_mag) in enumerate(zip(g1.genome.magnet_lists[list_key],
                                                     g2.genome.magnet_lists[list_key])):
                if g1_mag != g2_mag:
                    fp.write('%2s \t%3i  \t\t%3s   \t%1i  \t\t%3s  \t\t%1i\n' % (list_key, i,
                                                                                 g1_mag[0], g1_mag[1],
                                                                                 g2_mag[0], g2_mag[1]))

if __name__ == '__main__' :
    import optparse
    usage = "%prog [options] OutputFile"
    parser = optparse.OptionParser(usage=usage)
    # TODO refactor arguments to use named values

    (options, args) = parser.parse_args()
    process(options, args)
