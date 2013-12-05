'''
Created on 5 Dec 2013

@author: ssg37927
'''
import numpy as np
import random

class Magnets(object):
    '''
    This calss deals with all the real magnet information
    '''
    def __init__(self):
        self.magnet_sets = {}

    def add_magnet_set(self, name, filename):
        f = open(filename)
        magnets = {}
        for line in f:
            vals = line.split()
            magnets[vals[0]] = np.array((float(vals[1]), float(vals[2]), float(vals[3])))
        self.magnet_sets[name] = magnets
    
    def add_perfect_magnet_set(self, name, number, vector):
        magnets = {}
        for i in range(number):
            magnets['%03i'%(i)] = np.array(vector)
        self.magnet_sets[name] = magnets
        

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


if __name__ == "__main__" :
    mags = Magnets()
    #mags.add_magnet_set('HH', "../../data/I23H.sim")
    #mags.add_magnet_set('HE', "../../data/I23HEA.sim")
    #mags.add_magnet_set('VV', "../../data/I23V.sim")
    #mags.add_magnet_set('VE', "../../data/I23VE.sim")
    
    mags.add_perfect_magnet_set('HH', 20 , (0.,0.,1.))
    mags.add_perfect_magnet_set('HE', 5 , (0.,0.,1.))
    mags.add_perfect_magnet_set('VV', 20 , (0.,1.,0.))
    mags.add_perfect_magnet_set('VE', 5 , (0.,1.,0.))
    
    import pprint
    pprint.pprint(mags.magnet_sets)
    
    maglist = MagLists(mags)
    
    maglist.sort_all()
    print "Now for the lists"
    pprint.pprint(maglist.magnet_lists['HE'])
    
    maglist.swap('HE', 0, 1)
    
    print "After swap"
    pprint.pprint(maglist.magnet_lists['HE'])
