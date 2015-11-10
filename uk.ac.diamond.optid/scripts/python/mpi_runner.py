# Run this script with a suitable mpirun command. 
# The DLS controls installation of h5py is built against openmpi version 1.6.5.
# Note that the current default mpirun in the controls environment (module load controls-tools)
# is an older version of mpirun - so use the full path to mpirun as demonstrated in the
# example below.
#
# For documentation, see: http://www.h5py.org/docs/topics/mpi.html
# 
# Example:
# /dls_sw/prod/tools/RHEL6-x86_64/openmpi/1-6-5/prefix/bin/mpirun -np 5 dls-python parallel-hdf5-demo.py
#


# rn this with the following command
# qsub -pe openmpi 80 -q low.q -l release=rhel6 /home/ssg37927/ID/Opt-ID/IDSort/src/v2/mpijob.sh --iterations 100
#
#
# First to pick up the DLS controls environment and versioned libraries
#from pkg_resources import require
#require('mpi4py==1.3.1')
#require('h5py==2.2.0')
#require('numpy') # h5py need to be able to import numpy
#require('scipy')

# Just to demonstrate that we have zmq in the environment as well
#require('pyzmq==13.1.0')
#import zmq

from mpi4py import MPI
import h5py
import numpy as np
import socket

import time

import logging
logging.basicConfig(level=0,format=' %(asctime)s.%(msecs)03d %(threadName)-16s %(levelname)-6s %(message)s', datefmt='%H:%M:%S')

import magnets
from genome_tools import ID_BCell
import field_generator as fg
import magnet_tools as mt

import json

import os

import random

def mutations(c, e_star, fitness, scale):
    inverse_proportional_hypermutation =  abs(((1.0-(e_star/fitness)) * c) + c)
    a = random.random()
    b = random.random()
    hypermacromuation = abs((a-b) * scale)
    return int(inverse_proportional_hypermutation + hypermacromuation)

import optparse

usage = "%prog [options] run_directory"
parser = optparse.OptionParser(usage=usage)
parser.add_option("-f", "--fitness", dest="fitness", help="Set the target fitness", default=0.0, type="float")
parser.add_option("-p", "--processing", dest="processing", help="Set the total number of processing units per file", default=5, type="int")
parser.add_option("-n", "--numnodes", dest="nodes", help="Set the total number of nodes to use", default=10, type="int")
parser.add_option("-s", "--setup", dest="setup", help="set number of genomes to create in setup mode", default=5, type='int')
parser.add_option("-i", "--info", dest="id_filename", help="Set the path to the id data", default='/dls/science/groups/das/ID/I13j/id.json', type="string")
parser.add_option("-l", "--lookup", dest="lookup_filename", help="Set the path to the lookup table", default='/dls/science/groups/das/ID/I13j/unit_chunks.h5', type="string")
parser.add_option("-m", "--magnets", dest="magnets_filename", help="Set the path to the magnet description file", default='/dls/science/groups/das/ID/I13j/magnets.mag', type="string")
parser.add_option("-a", "--maxage", dest="max_age", help="Set the maximum age of a genome", default=10, type='int')
parser.add_option("--param_c", dest="c", help="Set the OPT-AI parameter c", default=10.0, type='float')
parser.add_option("--param_e", dest="e", help="Set the OPT-AI parameter eStar", default=0.0, type='float')
parser.add_option("--param_scale", dest="scale", help="Set the OPT-AI parameter scale", default=10.0, type='float')
parser.add_option("-r", "--restart", dest="restart", help="Don't recreate initial data", action="store_true", default=False)
parser.add_option("--iterations", dest="iterations", help="Number of Iterations to run", default=1, type='int')

(options, args) = parser.parse_args()

rank = MPI.COMM_WORLD.rank  # The process ID (integer 0-3 for 4-process run)
size = MPI.COMM_WORLD.size  # The number of processes in the job.

# get the hostname
ip = socket.gethostbyname(socket.gethostname())

logging.debug("Process %d ip address is : %s" % (rank, ip))


f2 = open(options.id_filename, 'r')
info = json.load(f2)
f2.close()

logging.debug("Loading Lookup")
f1 = h5py.File(options.lookup_filename, 'r')
lookup = {}
for beam in info['beams']:
    logging.debug("Loading beam %s" %(beam['name']))
    lookup[beam['name']] = f1[beam['name']][...]
f1.close()

MPI.COMM_WORLD.Barrier()

logging.debug("Loading magnets")
mags = magnets.Magnets()
mags.load(options.magnets_filename)

ref_mags = fg.generate_reference_magnets(mags)
ref_maglist = magnets.MagLists(ref_mags)
ref_total_id_field = fg.generate_id_field(info, ref_maglist, ref_mags, lookup)
pherr, ref_trajectories = mt.calculate_phase_error(info, ref_total_id_field)

MPI.COMM_WORLD.Barrier()

#epoch_path = os.path.join(args[0], 'epoch')
#next_epoch_path = os.path.join(args[0], 'nextepoch')
# start by creating the directory to put the initial population in 

population = []
estar = options.e


if options.restart and (rank == 0) :
    for filename in os.listdir(args[0]):
        fullpath = os.path.join(args[0],filename)
        try :
            logging.debug("Trying to load %s" % (fullpath))
            genome = ID_BCell()
            genome.load(fullpath)
            population.append(genome)
            logging.debug("Loaded %s" % (fullpath))
        except :
            logging.debug("Failed to load %s" % (fullpath))
    if len(population) < options.setup:
        # Seed with children from first
        children = population[0].generate_children(options.setup-len(population), 20, info, lookup, mags, ref_trajectories)
        # now save the children into the new file
        for child in children:
            population.append(child)
else :
    # make the initial population
    for i in range(options.setup):
        # create a fresh maglist
        maglist = magnets.MagLists(mags)
        maglist.shuffle_all()
        genome = ID_BCell()
        genome.create(info, lookup, mags, maglist, ref_trajectories)
        population.append(genome)

# gather the population
trans = []
for i in range(size):
    trans.append(population)

allpop = MPI.COMM_WORLD.alltoall(trans) 

MPI.COMM_WORLD.Barrier()

newpop = []
for pop in allpop:
    newpop += pop

# Need to deal with replicas and old genomes
popdict = {}
for genome in newpop:
    fitness_key = "%1.8E"%(genome.fitness)
    if fitness_key in popdict.keys():
        if popdict[fitness_key].age < genome.age:
            popdict[fitness_key] = genome
    else :
        popdict[fitness_key] = genome

newpop = []
for genome in popdict.values():
    if genome.age < options.max_age:
        newpop.append(genome)

newpop.sort(key=lambda x: x.fitness)

newpop = newpop[options.setup*rank:options.setup*(rank+1)]

for genome in newpop:
    logging.debug("genome fitness: %1.8E   Age : %2i   Mutations : %4i" % (genome.fitness, genome.age, genome.mutations))

#Checkpoint best solution
if rank == 0:
    newpop[0].save(args[0])

# now run the processing
for i in range(options.iterations):
    
    MPI.COMM_WORLD.Barrier()
    logging.debug("Starting itteration %i" % (i))

    nextpop = []

    for genome in newpop:
                
        # now we have to create the offspring
        # TODO this is for the moment
        logging.debug("Generating children for %s" % (genome.uid))
        number_of_children = options.setup
        number_of_mutations = mutations(options.c, estar, genome.fitness, options.scale)
        children = genome.generate_children(number_of_children, number_of_mutations, info, lookup, mags, ref_trajectories)
        
        # now save the children into the new file
        for child in children:
            nextpop.append(child)
        
        # and save the original
        nextpop.append(genome)
    
    # gather the population
    trans = []
    for i in range(size):
        trans.append(nextpop)
    
    allpop = MPI.COMM_WORLD.alltoall(trans) 
    
    newpop = []
    for pop in allpop:
        newpop += pop
    
    popdict = {}
    for genome in newpop:
        fitness_key = "%1.8E"%(genome.fitness)
        if fitness_key in popdict.keys():
            if popdict[fitness_key].age < genome.age:
                popdict[fitness_key] = genome
        else :
            popdict[fitness_key] = genome
    
    newpop = []
    for genome in popdict.values():
        if genome.age < options.max_age:
            newpop.append(genome)
    
    newpop.sort(key=lambda x: x.fitness)

    estar = newpop[0].fitness * 0.99
    logging.debug("new estar is %f" % (estar) )
    
    newpop = newpop[options.setup*rank:options.setup*(rank+1)]
    
    #Checkpoint best solution
    if rank == 0:
        newpop[0].save(args[0])
    
    for genome in newpop:
        logging.debug("genome fitness: %1.8E   Age : %2i   Mutations : %4i" % (genome.fitness, genome.age, genome.mutations))
    
    MPI.COMM_WORLD.Barrier()

MPI.COMM_WORLD.Barrier()

# gather the population
trans = []
for i in range(size):
    trans.append(nextpop)

allpop = MPI.COMM_WORLD.alltoall(trans) 

newpop = []
for pop in allpop:
    newpop += pop

newpop.sort(key=lambda x: x.fitness)

newpop = newpop[options.setup*rank:options.setup*(rank+1)]

#Checkpoint best solution
if rank == 0:
    newpop[0].save(args[0])

