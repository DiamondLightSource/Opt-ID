'''
Created on 24 Apr 2015

@author: gdy32713
'''
import unittest

from v2 import process_genome


class Test(unittest.TestCase):


    def testSimple(self):
        self.fail("Borked")

    def test2(self):
        self.assertLess(2, 1)


    def test3(self):
        a = process_genome.human_output(None, None)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testSimple']
    unittest.main()