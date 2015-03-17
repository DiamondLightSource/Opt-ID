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
from pkg_resources import require
require('mpi4py==1.3.1')
require('h5py==2.2.0')
require('numpy') # h5py need to be able to import numpy

# Just to demonstrate that we have zmq in the environment as well
require('pyzmq==13.1.0')
import zmq

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

from field_generator import generate_reference_magnets, generate_id_field


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
parser.add_option("-c", "--numchildren", dest="num_children", help="Set the number of children per machine", default=50, type="int")
parser.add_option("-m", "--mutations", dest="number_of_mutations", help="Set the number of mutations", default=5, type="int")
parser.add_option("-n", "--numnodes", dest="nodes", help="Set the total number of nodes to use", default=10, type="int")
parser.add_option("-s", "--setup", dest="setup", help="set number of genomes to create in setup mode", default=5, type='int')
parser.add_option("-i", "--info", dest="id_filename", help="Set the path to the id data", default='/dls/science/groups/das/ID/I13j/id.json', type="string")
parser.add_option("-l", "--lookup", dest="lookup_filename", help="Set the path to the lookup table", default='/dls/science/groups/das/ID/I13j/unit_chunks.h5', type="string")
parser.add_option("-b", "--bfield", dest="bfield_filename", help="Set the path to the bfield table", default='/dls/science/groups/das/ID/I13j/shim/shim1.meas.h5', type="string")
parser.add_option("-g", "--genome", dest="genome_filename", help="Set the path to the genome", default='/dls/science/groups/das/ID/I13j/intial_genome.genome', type="string")
parser.add_option("--magnets", dest="magnets_filename", help="Set the path to the magnet description file", default='/dls/science/groups/das/ID/I13j/magnets.mag', type="string")
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

logging.debug("Loading Initial Bfield")
f1 = h5py.File(options.bfield_filename, 'r')
real_bfield = f1['id_Bfield'][...]
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

# Load the initial genome
genome = ID_BCell()
genome.load(options.genome_filename)


MPI.COMM_WORLD.Barrier()

# now run the processing
children = genome.generate_children(options.num_children, options.number_of_mutations, info, lookup, mags, ref_trajectories, real_bfield=real_bfield)

children.sort(key=lambda x: x.fitness)

# send the best member of the population for sorting
trans = []
for i in range(size):
    trans.append(children[0])

allpop = MPI.COMM_WORLD.alltoall(trans) 

allpop.sort(key=lambda x: x.fitness)

best = allpop[0]

if rank == 0:
    best.save(args[0])


    new_magnets = fg.generate_per_magnet_array(info, best.genome, mags)
    original_magnets = fg.generate_per_magnet_array(info, genome.genome, mags)
    
    update = fg.compare_magnet_arrays(original_magnets, new_magnets, lookup)
    
    updated_bfield = np.array(real_bfield)
    for beam in update.keys() :
        if update[beam].size != 0:
            updated_bfield = updated_bfield - update[beam]
    
    outfile = os.path.join(args[0], genome.uid+'-'+best.uid+'.h5')
    logging.debug("filename is %s" % (outfile))
    f = h5py.File(outfile, 'w')
    
    total_id_field = real_bfield
    f.create_dataset('id_Bfield_original', data=total_id_field)
    trajectory_information=mt.calculate_phase_error(info, total_id_field)
    f.create_dataset('id_phase_error_original', data = trajectory_information[0])
    f.create_dataset('id_trajectory_original', data = trajectory_information[1])
    
    total_id_field = updated_bfield
    f.create_dataset('id_Bfield_shimmed', data=total_id_field)
    trajectory_information=mt.calculate_phase_error(info, total_id_field)
    f.create_dataset('id_phase_error_shimmed', data = trajectory_information[0])
    f.create_dataset('id_trajectory_shimmed', data = trajectory_information[1])
    
    
    ref_mags=generate_reference_magnets(mags)
    total_id_field = generate_id_field(info, best.genome, ref_mags, lookup)
    
    f.create_dataset('id_Bfield_perfect', data=total_id_field)
    trajectory_information=mt.calculate_phase_error(info, total_id_field)
    f.create_dataset('id_phase_error_perfect', data = trajectory_information[0])
    f.create_dataset('id_trajectory_perfect', data = trajectory_information[1])
    
    f.close()

