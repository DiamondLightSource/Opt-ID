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

# TODO marked for deprecation and removal, we'll re-approach this optimization process after re-modularization

import os
import random
import itertools

import json
import h5py

import numpy as np

import socket
from mpi4py import MPI

from .magnets import Magnets, MagLists
from .genome_tools import ID_Shim_BCell, ID_BCell

from .field_generator import generate_reference_magnets, \
                             generate_per_magnet_array,  \
                             generate_bfield,            \
                             compare_magnet_arrays,      \
                             calculate_bfield_phase_error

from .logging_utils import logging, getLogger, setLoggerLevel #
logger = getLogger(__name__)


def mutations(c, e_star, fitness, scale):
    inverse_proportional_hypermutation =  abs(((1.0 - (e_star / fitness)) * c) + c)
    a = random.random()
    b = random.random()
    hypermacromuation = abs((a - b) * scale)
    return int(inverse_proportional_hypermutation + hypermacromuation)

def saveh5(path, best, genome, info, mags, real_bfield, lookup):
    new_magnets = generate_per_magnet_array(info, best.genome, mags)
    original_magnets = generate_per_magnet_array(info, genome.genome, mags)
    
    per_beam_bfield_updates = compare_magnet_arrays(original_magnets, new_magnets, lookup)
    updated_bfield = real_bfield - sum(per_beam_bfield_updates.values())
    
    outfile = os.path.join(path, f'{genome.uid}-{best.uid}.h5')
    logger.debug("filename is %s" % (outfile))

    with h5py.File(outfile, 'w') as fp:
    
        total_id_field = real_bfield
        fp.create_dataset('id_Bfield_original', data=total_id_field)
        trajectory_information = calculate_bfield_phase_error(info, total_id_field)
        fp.create_dataset('id_phase_error_original', data = trajectory_information[0])
        fp.create_dataset('id_trajectory_original', data = trajectory_information[1])

        total_id_field = updated_bfield
        fp.create_dataset('id_Bfield_shimmed', data=total_id_field)
        trajectory_information = calculate_bfield_phase_error(info, total_id_field)
        fp.create_dataset('id_phase_error_shimmed', data = trajectory_information[0])
        fp.create_dataset('id_trajectory_shimmed', data = trajectory_information[1])

        ref_mags=generate_reference_magnets(mags)
        total_id_field = generate_bfield(info, best.genome, ref_mags, lookup)

        fp.create_dataset('id_Bfield_perfect', data=total_id_field)
        trajectory_information = calculate_bfield_phase_error(info, total_id_field)
        fp.create_dataset('id_phase_error_perfect', data = trajectory_information[0])
        fp.create_dataset('id_trajectory_perfect', data = trajectory_information[1])


def process(options, args):

    if hasattr(options, 'verbose'):
        setLoggerLevel(logger, options.verbose)

    logger.debug('Starting')

    output_path = args[0]

    if options.seed:
        logger.info('Random seed set to %d', int(options.seed_value))
        random.seed(int(options.seed_value))

    if options.singlethreaded:
        # Who am I within the set of compute nodes
        comm_rank, comm_size, comm_ip = (0, 1, 'localhost')

        # No synchronization needed in single node case
        def barrier():
            pass

        # No exchange needed in single node case
        def exchange_genomes(local_population):
            return local_population

    else:
        # Who am I within the set of compute nodes
        comm_rank, comm_size, comm_ip = (MPI.COMM_WORLD.rank, MPI.COMM_WORLD.size,
                                         socket.gethostbyname(socket.gethostname()))

        # Use a collective MPI barrier to synchronize all compute nodes
        def barrier():
            MPI.COMM_WORLD.Barrier()

        # TODO need test case that uses multiple MPI nodes to test this communication works properly
        # Exchange local population of genomes between compute nodes so that every node has the global population
        def exchange_genomes(local_population):
            return list(itertools.chain.from_iterable(MPI.COMM_WORLD.alltoall([local_population] * comm_size)))

    logger.info('Node %3d of %3d @ [%s]', comm_rank, comm_size, comm_ip)

    # Attempt to load the ID json data
    try:
        logger.info('Loading ID info from json [%s]', options.id_filename)
        with open(options.id_filename, 'r') as fp:
            info = json.load(fp)

    except Exception as ex:
        logger.error('Failed to load ID info from json [%s]', options.id_filename, exc_info=ex)
        raise ex

    # Attempt to load the ID's lookup table for the eval points defined in the JSON file
    try:
        logger.info('Loading ID lookup table [%s]', options.lookup_filename)
        with h5py.File(options.lookup_filename, 'r') as fp:
            lookup = {}
            for beam in info['beams']:
                lookup[beam['name']] = fp[beam['name']][...]
                logger.debug('Loaded beam [%s] with shape [%s]', beam['name'], lookup[beam['name']].shape)

    except Exception as ex:
        logger.error('Failed to load ID lookup table [%s]', options.lookup_filename, exc_info=ex)
        raise ex

    # Attempt to load the ID's (real world) measured bfield for the eval points defined in the JSON file
    # TODO registration and re-sampling / re-interpolation feature to minimize reality gap
    try:
        logger.info('Loading ID measured bfield [%s]', options.bfield_filename)

        with h5py.File(options.bfield_filename, 'r') as fp:
            real_bfield = fp['id_Bfield'][...]
            logger.debug('Loaded measured bfield with shape [%s]', real_bfield.shape)

    except Exception as ex:
        logger.error('Failed to load ID measured bfield [%s]', options.bfield_filename, exc_info=ex)
        raise ex

    # Attempt to load the real magnet data
    try:
        logger.info('Loading ID magnets [%s]', options.magnets_filename)
        magnet_sets = Magnets()
        magnet_sets.load(options.magnets_filename)

    except Exception as ex:
        logger.error('Failed to load ID info from json [%s]', options.magnets_filename, exc_info=ex)
        raise ex

    # From loaded data construct a perfect magnet array that the loss will be computed with respect to
    logger.info('Constructing perfect reference magnets to shadow real magnets and ideal bfield')
    ref_magnet_sets  = generate_reference_magnets(magnet_sets)
    ref_magnet_lists = MagLists(ref_magnet_sets)
    ref_bfield       = generate_bfield(info, ref_magnet_lists, ref_magnet_sets, lookup)

    ref_phase_error, ref_trajectories = calculate_bfield_phase_error(info, ref_bfield)
    logger.debug('Perfect bfield phase error [%s]', ref_phase_error)

    # TODO currently broken, fix or remove
    # ref_strx, ref_strz = calculate_trajectory_straightness(info, ref_trajectories)
    # logger.debug('Perfect bfield trajectory straightness [%s] [%s]', ref_strx, ref_strz)

    # Attempt to load the reference genome to seed all the new genomes
    try:
        logger.info('Loading reference genome [%s]', options.genome_filename)

        initial_genome = ID_BCell()
        initial_genome.load(options.genome_filename)

        ref_genome = ID_BCell()
        ref_genome.load(options.genome_filename)

        assert initial_genome.genome == ref_genome.genome

    except Exception as ex:
        logger.error('Failed to load reference genome [%s]', options.genome_filename, exc_info=ex)
        raise ex

    barrier()

    # Filter the population for unique fitness values keeping the oldest genome when there are genomes with the same fitness
    def filter_genomes(population):
        genomes = {}
        for genome in population:
            # TODO remove dependency on filename scientific notation encoding
            genome_key = f'{genome.fitness:1.8E}'

            # Keep the genome with the highest age if there are two with the same fitness value
            if (genome_key not in genomes.keys()) or \
               ((genome_key in genomes.keys()) and (genomes[genome_key].age < genome.age)):
                genomes[genome_key] = genome

        # Filter the population to remove genomes that have an age higher than the maximum allowed age
        population = filter((lambda genome : (genome.age < options.max_age)), genomes.values())

        # Sort the population so that the first one is the best genome
        population = sorted(population, key=(lambda genome : genome.fitness))

        # TODO this places all the best genomes on node with rank 0, consider replacing with strided distribution
        #  so all nodes get some of the best and some of the worse genomes
        population = population[(options.setup * comm_rank):(options.setup * (comm_rank + 1))]
        # population = population[comm_rank::comm_size][:options.setup] # Strided distribution of genomes

        return population

    # Synchronize nodes sequentially to print diagnostics about local genome populations
    def log_genomes(population):
        # Early return if logger is not set to at least output INFO messages
        if not logger.isEnabledFor(logging.INFO): return

        # Synchronize nodes sequentially to print diagnostics about local genome populations
        for rank in range(comm_size):
            barrier()
            if rank != comm_rank: continue

            # Compute the min, max, and average for the fitness, age, and mutations for each genome in the local population
            fitness_stats, age_stats, mutation_stats = [(np.min(data), np.max(data), np.mean(data))
                                                        for data in zip(*[(genome.fitness, genome.age, genome.mutations)
                                                                          for genome in population])]

            logger.info('Node %3d of %3d has %d genomes with fitness (min %1.8E, max %1.8E, avg %1.8E) '
                        'age (min %0.0f, max %0.0f, avg %0.2f) mutations (min %0.0f, max %0.0f, avg %0.2f)',
                        comm_rank, comm_size, len(population), *fitness_stats, *age_stats, *mutation_stats)

            if logger.isEnabledFor(logging.DEBUG):
                for genome_index, genome in enumerate(population):
                    logger.debug('Node %3d of %3d Genome %3d of %3d %s with fitness %1.8E age %d mutations %d',
                                 comm_rank, comm_size, genome_index, len(population), genome.uid,
                                 genome.fitness, genome.age, genome.mutations)

    # Initial estar used for sampling mutations
    estar = options.e

    # Array to hold the current population
    population = []

    logger.info('Creating %d randomly initialized shim genomes from the reference genome', options.setup)
    for genome_index in range(options.setup):
        logger.debug('Sampling random genome %d of %d using %d mutations from the reference genome',
                     genome_index, options.setup, options.number_of_changes)

        # Create a new random genome and add it to the population
        shim_genome = ID_Shim_BCell()
        shim_genome.create(info, lookup, magnet_sets, initial_genome.genome, ref_trajectories,
                           options.number_of_changes, real_bfield)
        population.append(shim_genome)

    barrier()

    population = filter_genomes(exchange_genomes(population))
    log_genomes(population)

    # Checkpoint best genome with lowest fitness from the master node
    if comm_rank == 0:
        try:
            best_genome = population[0]
            logger.info('Saving best genome %s with fitness %1.8E age %d mutations %d',
                        best_genome.uid, best_genome.fitness, best_genome.age, best_genome.mutations)
            best_genome.save(output_path)

        except Exception as ex:
            logger.error('Failed to save best genome to [%s]', output_path, exc_info=ex)
            raise ex

    # Perform multiple iterations of mutations and communications
    for iteration in range(options.iterations):
        barrier()
        if comm_rank == 0:
            logger.info('Iteration %d', iteration)

        new_population = []

        # Apply mutations to each genome in the local population
        for genome_index, genome in enumerate(population):

            # For each genome we will generate multiple children by applying randomized numbers of random mutations to the current genome
            num_children  = options.setup
            num_mutations = mutations(options.c, estar, genome.fitness, options.scale)

            # The new population will include the current genome and the random children of the current genome
            new_population += [genome] + genome.generate_children(num_children, num_mutations, info, lookup,
                                                                  magnet_sets, ref_trajectories, real_bfield=real_bfield)

        # Exchange the genomes between compute nodes filter them, and redistribute them fairly between nodes for the next iteration
        population = filter_genomes(exchange_genomes(new_population))

        estar = population[0].fitness * 0.99
        logger.info('Node %3d of %3d updated estar %0.8f', comm_rank, comm_size, estar)

        # Checkpoint best genome with lowest fitness from the master node
        if comm_rank == 0:
            best_shim_genome = population[0]
            best_shim_genome.save(output_path)

            # TODO can't use this refactor until hidden data dependency on initial_genome.genome is removed!
            #      Fixing this breaks expected test outputs because of RNG!!!
            # best_genome = ref_genome.clone()
            # best_genome.genome.mutate_from_list(best_shim_genome.genome)
            # best_genome.fitness = best_shim_genome.fitness
            # best_genome.uid = f'A{best_shim_genome.uid}'
            # best_genome.save(output_path)
            # saveh5(output_path, best_genome, ref_genome, info, magnet_sets, real_bfield, lookup)

            # TODO can't remove this until hidden data dependency on initial_genome.genome is removed!
            #      Fixing this breaks expected test outputs because of RNG!!!
            initial_genome.genome.mutate_from_list(best_shim_genome.genome)
            initial_genome.fitness = best_shim_genome.fitness
            initial_genome.uid = f'A{best_shim_genome.uid}'
            initial_genome.save(output_path)
            saveh5(output_path, initial_genome, ref_genome, info, magnet_sets, real_bfield, lookup)
            initial_genome.load(options.genome_filename)

        log_genomes(population)

    barrier()

    # Checkpoint best genome with lowest fitness from the master node
    if comm_rank == 0:
        best_shim_genome = population[0]
        best_shim_genome.save(output_path)

        # best_genome = ref_genome.clone()
        # best_genome.genome.mutate_from_list(best_shim_genome.genome)
        # best_genome.age_bcell()
        # best_genome.save(output_path)

        initial_genome.genome.mutate_from_list(best_shim_genome.genome)
        initial_genome.age_bcell()
        initial_genome.save(output_path)

    barrier()

    logger.debug('Halting')

if __name__ == "__main__":
    import optparse
    usage = "%prog [options] run_directory"
    parser = optparse.OptionParser(usage=usage)
    parser.add_option('-v', '--verbose', dest='verbose', help='Set the verbosity level [0-4]', default=0, type='int')
    parser.add_option("-f", "--fitness", dest="fitness", help="Set the target fitness", default=0.0, type="float")
    parser.add_option("-p", "--processing", dest="processing", help="Set the total number of processing units per file", default=5, type="int")
    parser.add_option("-n", "--numnodes", dest="nodes", help="Set the total number of nodes to use", default=10, type="int")
    parser.add_option("-s", "--setup", dest="setup", help="set number of genomes to create in setup mode", default=5, type='int')
    parser.add_option("-i", "--info", dest="id_filename", help="Set the path to the id data", default='/dls/science/groups/das/ID/I13j/id.json', type="string")
    parser.add_option("-l", "--lookup", dest="lookup_filename", help="Set the path to the lookup table", default='/dls/science/groups/das/ID/I13j/unit_chunks.h5', type="string")
    parser.add_option("--magnets", dest="magnets_filename", help="Set the path to the magnet description file", default='/dls/science/groups/das/ID/I13j/magnets.mag', type="string")
    parser.add_option("-a", "--maxage", dest="max_age", help="Set the maximum age of a genome", default=10, type='int')
    parser.add_option("--param_c", dest="c", help="Set the OPT-AI parameter c", default=1, type='float')
    parser.add_option("--param_e", dest="e", help="Set the OPT-AI parameter eStar", default=0.0, type='float')
    parser.add_option("--param_scale", dest="scale", help="Set the OPT-AI parameter scale", default=4, type='float')
    parser.add_option("-r", "--restart", dest="restart", help="Don't recreate initial data", action="store_true", default=False)
    parser.add_option("--iterations", dest="iterations", help="Number of Iterations to run", default=1, type='int')
    parser.add_option("-b", "--bfield", dest="bfield_filename", help="Set the path to the bfield table", default='/dls/science/groups/das/ID/I13j/shim/shim1.meas.h5', type="string")
    parser.add_option("-g", "--genome", dest="genome_filename", help="Set the path to the genome", default='/dls/science/groups/das/ID/I13j/intial_genome.genome', type="string")
    parser.add_option("-m", "--mutations", dest="number_of_mutations", help="Set the number of mutations", default=5, type="int")
    parser.add_option("-c", "--changes", dest="number_of_changes", help="Set the number of changes(swaps or flips)", default=4, type="int")
    parser.add_option("--singlethreaded", dest="singlethreaded", help="Set the program to run as singlethreaded", action="store_true", default=False)
    parser.add_option("--seed", dest="seed", help="Seed the random number generator or not", action="store_true", default=False)
    parser.add_option("--seed_value", dest="seed_value", help="Seed value for the random number generator")

    (options, args) = parser.parse_args()

    try:
        process(options, args)
    except Exception as ex:
        logger.critical('Fatal exception in mpi_runner_for_shim_opt::process', exc_info=ex)
