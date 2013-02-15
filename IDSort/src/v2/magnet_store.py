'''
Created on 15 Feb 2013

@author: ssg37927
'''

class MagnetStore(object):
    
    horizontal = "HH"
    vertical = "VV"
    horizontal_end = "HE"
    vertical_end = "VE"
    air_gap = "AA"
    
    
    
    def __init__(self):
        self.magnets = {}
    
    def load_magnets(self, mag_type, filename):
        f = open(self.filename)
        mags = {}
        for line in f:
            vals = line.split()
            dict[vals[0]] = (float(vals[1]), float(vals[2]), float(vals[3]))
        self.magnets[mag_type] = mags
