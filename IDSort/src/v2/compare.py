from genome_tools import ID_BCell

if __name__ == '__main__' :
    
    import optparse
    usage = "%prog [options] data"
    parser = optparse.OptionParser(usage=usage)
    (options, args) = parser.parse_args()
    
    g1 = ID_BCell()
    g2 = ID_BCell()
    g1.load(args[0])
    g2.load(args[1])
    
    for listkey in g1.genome.magnet_lists.keys():
        for i in range(len(g1.genome.magnet_lists[listkey])):
            if g1.genome.magnet_lists[listkey][i] != g2.genome.magnet_lists[listkey][i]:
                print listkey
                print i
                print g1.genome.magnet_lists[listkey][i]
                print g2.genome.magnet_lists[listkey][i]
                print ""