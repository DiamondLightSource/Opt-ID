'''
Created on 5 Dec 2013

@author: ssg37927
'''
import numpy as np
import random
import cPickle


class Magnets(object):
    '''
    This class deals with all the real magnet information
    '''
    def __init__(self):
        self.magnet_sets = {}
        self.magnet_flip = {}
        self.mean_field = {}

    def add_magnet_set(self, name, filename, flip_vector):
        f = open(filename)
        magnets = {}
        for line in f:
            vals = line.split()
            print vals[0]
            magnets[vals[0]] = np.array((float(vals[1]), float(vals[2]), float(vals[3])))
        self.magnet_sets[name] = magnets
        self.magnet_flip[name] = np.array(flip_vector)
        
        self.mean_field[name]=0.0
        for magnet in self.magnet_sets[name]:
            self.mean_field[name]+=np.linalg.norm(self.magnet_sets[name][magnet])
        self.mean_field[name]=self.mean_field[name]/len(self.magnet_sets[name])
        

    def add_perfect_magnet_set(self, name, number, vector, flip_vector):
        magnets = {}
        for i in range(number):
            magnets['%03i' % (i)] = np.array(vector)
        self.magnet_sets[name] = magnets
        self.magnet_flip[name] = np.array(flip_vector)
    
    def add_perfect_magnet_set_duplicate(self, name, mag_list, vector, flip_vector):
        magnets = {}
        for key in mag_list.keys():
            magnets[key] = np.array(vector)
        self.magnet_sets[name] = magnets
        self.magnet_flip[name] = np.array(flip_vector)
    
    def save(self, filename):
        fp = open(filename, 'w')
        cPickle.dump((self.magnet_sets, self.magnet_flip, self.mean_field), fp)
        fp.close()
    
    def load(self, filename):
        fp = open(filename, 'r')
        (self.magnet_sets, self.magnet_flip, self.mean_field) = cPickle.load(fp)
        fp.close()


class MagLists():
    '''
    This class deals with the ordering and specification of several lists
    '''
    
    def __init__(self, magnets):
        self.magnet_lists = {}
        for magnet_set in magnets.magnet_sets.keys():
            mags = []
            for magnet in magnets.magnet_sets[magnet_set].keys():
                mags.append([magnet, 1, 0])
            self.magnet_lists[magnet_set] = mags
    
    def sort_list(self, name):
        self.magnet_lists[name].sort()
    
    def sort_all(self):
        for name in self.magnet_lists.keys():
            self.sort_list(name)
    
    def shuffle_list(self, name):
        random.shuffle(self.magnet_lists[name])
    
    def shuffle_all(self):
        for name in self.magnet_lists.keys():
            self.shuffle_list(name)
    
    def flip(self, name, numbers):
        for number in numbers:
            self.magnet_lists[name][number][1] *= -1
    
    def swap(self, name, a, b):
        L = self.magnet_lists[name]
        L[a], L[b] = L[b], L[a]
    
    def get_magnet_vals(self, name, number, magnets, flip):
        magnet = self.magnet_lists[name][number]
        magdata = magnets.magnet_sets[name][magnet[0]]
        if magnet[1] < 0:
            magdata = magdata.dot(flip)
        return magdata
    
    def mutate(self, number_of_mutations, available={'VE':range(32), 'HE':range(64), 'HH':range(820), 'VV':range(820)}):
        for i in range(number_of_mutations):
            # pick a list at random
            key = random.choice(available.keys())
            # pick a flip or swap
            if random.random() > 0.5 :
                # swap
                p1 = random.choice(available[key])
                p2 = random.choice(available[key])
                self.swap(key, p1, p2)
            else :
                p1 = random.choice(available[key])
                self.flip(key , (p1,))
    
    def mutate_from_list(self, mutation_list):
        for mutation in mutation_list:
            if mutation[0] == 'S':
                key = mutation[1]
                p1 = mutation[2]
                p2 = mutation[3]
                self.swap(key, p1, p2)
            else :
                key = mutation[1]
                p1 = mutation[2]
                self.flip(key , (p1,))


if __name__ == "__main__" :
    import optparse
    usage = "%prog [options] OutputFile"
    parser = optparse.OptionParser(usage=usage)
    parser.add_option("-H", "--hmaglist", dest="hmags", help="Set the path to the H magnet data", default='/home/gdy32713/DAWN_stable/optid/Opt-ID/IDSort/data/J13H.sim', type="string")
    parser.add_option("--HE", "--hemaglist", dest="hemags", help="Set the path to the HE magnet data", default='/home/gdy32713/DAWN_stable/optid/Opt-ID/IDSort/data/J13HEA.sim', type="string")
    parser.add_option("-V", "--vmaglist", dest="vmags", help="Set the path to the V magnet data", default='/home/gdy32713/DAWN_stable/optid/Opt-ID/IDSort/data/J13V.sim', type="string")
    parser.add_option("--VE", "--vemaglist", dest="vemags", help="Set the path to the VE magnet data", default='/home/gdy32713/DAWN_stable/optid/Opt-ID/IDSort/data/J13VE.sim', type="string")
    
    (options, args) = parser.parse_args()
    
    
    
    
    mags = Magnets()
    mags.add_magnet_set('HH', options.hmags, (-1.,-1.,1.))
    mags.add_magnet_set('HE', options.hemags, (-1.,-1.,1.))
    mags.add_magnet_set('VV', options.vmags, (-1.,1.,-1.))
    mags.add_magnet_set('VE', options.vemags, (-1.,1.,-1.))
    
    #mags.add_perfect_magnet_set('HH', 20 , (0.,0.,1.), (-1.,1.,-1.))
    #mags.add_perfect_magnet_set('HE', 5 , (0.,0.,1.), (-1.,1.,-1.))
    #mags.add_perfect_magnet_set('VV', 20 , (0.,1.,0.), (-1.,-1.,1.))
    #mags.add_perfect_magnet_set('VE', 5 , (0.,1.,0.), (-1.,-1.,1.))
    
    import pprint
    pprint.pprint(mags.magnet_sets)
    
    maglist = MagLists(mags)
    
    maglist.sort_all()
    print "Now for the lists"
    pprint.pprint(maglist.magnet_lists['HE'])
    
    maglist.swap('HE', 0, 1)
    
    print "After swap"
    pprint.pprint(maglist.magnet_lists['HE'])
    
    maglist.flip('HH',(107,294,511,626))
    
    print "After flips"
    pprint.pprint(maglist.magnet_lists['HH'])
    
    mags.save(args[0])
