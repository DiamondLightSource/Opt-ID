'''
Takes 3 arguments:
1. The previous genome 
2. The new genome generated from the shim code
3. The path and name of the file to output eg. $IDDATA/shim1.txt
'''

from genome_tools import ID_BCell


def process(options, args):
    g1 = ID_BCell()
    g2 = ID_BCell()
    g1.load(args[0])
    g2.load(args[1])
    if len(args)>2:
        filepath=args[2]
    else:
        filepath="compare"
    
    f1 = open(filepath+".txt",'w')
    f1.write("Type    Shim no.    Original   Orientation    Replacement    Orientation\n")
    
    for listkey in g1.genome.magnet_lists.keys():
        for i in range(len(g1.genome.magnet_lists[listkey])):
            if g1.genome.magnet_lists[listkey][i] != g2.genome.magnet_lists[listkey][i]:
                allwrite=("%2s \t%3i  \t\t%3s   \t%1i  \t\t%3s  \t\t%1i"%(listkey, i, g1.genome.magnet_lists[listkey][i][0], g1.genome.magnet_lists[listkey][i][1], g2.genome.magnet_lists[listkey][i][0], g2.genome.magnet_lists[listkey][i][1]))
                f1.write(allwrite)
                f1.write("\n")
                
    f1.close()

if __name__ == '__main__' :
    import optparse
    usage = "%prog [options] OutputFile"
    parser = optparse.OptionParser(usage=usage)
    (options, args) = parser.parse_args()
    process(options, args)
