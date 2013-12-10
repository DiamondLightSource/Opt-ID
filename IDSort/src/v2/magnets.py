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
    This class deals with the ordering and speification of several lists
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
    
    def get_magnet_vals(self, name, number, magnets):
        magnet = self.magnet_lists[name][number]
        magdata = magnets.magnet_sets[name][magnet[0]]
        if magnet[1] < 0:
            magdata = magdata*magnets.magnet_flip[name]
        return magdata
    
    def mutate(self, number_of_mutations):
        for i in range(number_of_mutations):
            #TODO add some mutation code in here for ease
            pass



if __name__ == "__main__" :
    mags = Magnets()
    mags.add_magnet_set('HH', "../../data/I23H.sim", (-1.,1.,-1.))
    mags.add_magnet_set('HE', "../../data/I23HEA.sim", (-1.,1.,-1.))
    mags.add_magnet_set('VV', "../../data/I23V.sim", (-1.,-1.,1.))
    mags.add_magnet_set('VE', "../../data/I23VE.sim", (-1.,-1.,1.))
    
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
    
    mags.save('magnets.mag')
