# Copyright 2017 Diamond Light Source
# 
# Licensed under the Apache License, Version 2.0 (the "License"); 
# you may not use this file except in compliance with the License. 
# You may obtain a copy of the License at
# 
# http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, 
# software distributed under the License is distributed on an 
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, 
# either express or implied. See the License for the specific 
# language governing permissions and limitations under the License.


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

import os
import socket
import logging

import json
import h5py
from mpi4py import MPI

import random
import numpy as np

from .magnets import Magnets, MagLists
from .genome_tools import ID_BCell
from .field_generator import generate_reference_magnets, generate_bfield
from .magnet_tools import calculate_bfield_phase_error


logging.basicConfig(level=0,format=' %(asctime)s.%(msecs)03d %(threadName)-16s %(levelname)-6s %(message)s', datefmt='%H:%M:%S')

def mutations(c, e_star, fitness, scale):
    inverse_proportional_hypermutation =  abs(((1.0 - (e_star / fitness)) * c) + c)
    a = random.random()
    b = random.random()
    hypermacromuation = abs((a - b) * scale)
    return int(inverse_proportional_hypermutation + hypermacromuation)

def barrier(is_single_threaded):
    if not is_single_threaded:
        MPI.COMM_WORLD.Barrier()

def alltoall(is_single_threaded, trans):
    return trans if is_single_threaded else MPI.COMM_WORLD.alltoall(trans)


def process(options, args):

    if options.seed:
        random.seed(int(options.seed_value))

    if options.singlethreaded:
        rank = 0
        size = 1
    else:
        rank = MPI.COMM_WORLD.rank  # The process ID (integer 0-3 for 4-process run)
        size = MPI.COMM_WORLD.size  # The number of processes in the job.

    # get the hostname
    if options.singlethreaded:
        ip = 'localhost'
    else:
        ip = socket.gethostbyname(socket.gethostname())

    logging.debug("Process %d ip address is : %s" % (rank, ip))

    with open(options.id_filename, 'r') as fp:
        info = json.load(fp)

    logging.debug("Loading Lookup")
    with h5py.File(options.lookup_filename, 'r') as fp:
        lookup = {}
        for beam in info['beams']:
            logging.debug("Loading beam %s" %(beam['name']))
            lookup[beam['name']] = fp[beam['name']][...]

    barrier(options.singlethreaded)

    logging.debug("Loading magnets")
    mags = Magnets()
    mags.load(options.magnets_filename)

    ref_mags = generate_reference_magnets(mags)
    ref_maglist = MagLists(ref_mags)
    ref_total_id_field = generate_bfield(info, ref_maglist, ref_mags, lookup)
    #logging.debug("before phase calculate error call")
    #logging.debug(ref_total_id_field.shape())
    phase_error, ref_trajectories = calculate_bfield_phase_error(info, ref_total_id_field)

    barrier(options.singlethreaded)

    #epoch_path = os.path.join(args[0], 'epoch')
    #next_epoch_path = os.path.join(args[0], 'nextepoch')
    # start by creating the directory to put the initial population in

    population = []
    estar = options.e

    if options.restart and (rank == 0) :

        # sort the genome filenames to ensure that when given the same set of
        # files in a directory, population[0] is the same across different
        # orderings of the listed directory contents: this is to fix the test
        # MpiRunnerTest.test_process_initial_population() in mpi_runner_test.py
        # when run on travis
        filenames = sorted(os.listdir(args[0]))

        for filename in filenames:
            fullpath = os.path.join(args[0],filename)

            try :
                logging.debug("Trying to load %s" % (fullpath))
                genome = ID_BCell()
                genome.load(fullpath)
                population.append(genome)
                logging.debug("Loaded %s" % (fullpath))

            except Exception as ex:
                logging.debug("Failed to load %s" % (fullpath))
                raise ex

        if len(population) < options.setup:
            # Seed with children from first
            children = population[0].generate_children(options.setup-len(population), 20, info, lookup, mags, ref_trajectories)
            # now save the children into the new file
            for child in children:
                population.append(child)
    else :
        logging.debug("make the initial population")
        for i in range(options.setup):
            # create a fresh maglist
            maglist = MagLists(mags)
            maglist.shuffle_all()
            genome = ID_BCell()
            genome.create(info, lookup, mags, maglist, ref_trajectories)
            population.append(genome)

    logging.debug("Initial population created")

    # gather the population
    trans = []
    for i in range(size):
        trans.append(population)

    allpop = alltoall(options.singlethreaded, trans)

    barrier(options.singlethreaded)

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

        barrier(options.singlethreaded)
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

        allpop = alltoall(options.singlethreaded, trans)

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

        barrier(options.singlethreaded)

    barrier(options.singlethreaded)

    # gather the population
    trans = []
    for i in range(size):
        trans.append(nextpop)

    allpop = alltoall(options.singlethreaded, trans)

    newpop = []
    for pop in allpop:
        newpop += pop

    newpop.sort(key=lambda x: x.fitness)

    newpop = newpop[options.setup*rank:options.setup*(rank+1)]

    #Checkpoint best solution
    if rank == 0:
        newpop[0].save(args[0])

if __name__ == "__main__":
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
    parser.add_option("--singlethreaded", dest="singlethreaded", help="Set the program to run as singlethreaded", action="store_true", default=False)
    parser.add_option("--seed", dest="seed", help="Seed the random number generator or not", action="store_true", default=False)
    parser.add_option("--seed_value", dest="seed_value", help="Seed value for the random number generator")

    (options, args) = parser.parse_args()
    process(options, args)
