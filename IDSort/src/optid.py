import os
from collections import namedtuple

from ruamel.yaml import YAML

from IDSort.src import id_setup, magnets, lookup_generator, mpi_runner, \
        mpi_runner_for_shim_opt, process_genome, compare


def extract_params(config, data_dir):
    genome_dir = 'genomes/'
    genome_dirpath = os.path.join(data_dir, genome_dir)
    shimmed_genome_dir = 'shimmed_genomes/'
    shimmed_genome_dirpath = os.path.join(data_dir, shimmed_genome_dir)
    process_genome_output_dir = 'process_genome_output/'
    processed_data_dir = os.path.join(data_dir, process_genome_output_dir)

    json_filename = config['id_setup'].pop('output_filename', None)
    json_filepath = os.path.join(data_dir, json_filename)
    run_id_setup(config['id_setup'], [json_filepath])

    mag_filename = config['magnets'].pop('output_filename', None)
    mag_filepath = os.path.join(data_dir, mag_filename)
    run_magnets(config['magnets'], [mag_filepath])

    # the periods param for this should be the same as the periods param for
    # id_setup.py, so use that same value in config['lookup_generator']
    h5_filename = config['lookup_generator'].pop('output_filename', None)
    h5_filepath = os.path.join(data_dir, h5_filename)
    config['lookup_generator']['periods'] = config['id_setup']['periods']
    run_lookup_generator(config['lookup_generator'], [json_filepath, h5_filepath])

    # shimming typically involves creating a genome from an inp before the mpi
    # runner generates the genome
    if config['process_genome']['create_genome']:
        run_process_genome(config['process_genome'], config['process_genome']['readable_genome_file'][0], json_filepath, mag_filepath, h5_filepath, processed_data_dir)

    if 'mpi_runner' in config:
        if config['mpi_runner']['restart']:
            initial_population_dir = config['mpi_runner']['initial_population_dir']
            run_mpi_runner(config['mpi_runner'], [initial_population_dir], json_filepath, mag_filepath, h5_filepath)
        else:
            run_mpi_runner(config['mpi_runner'], [genome_dirpath], json_filepath, mag_filepath, h5_filepath)

    if 'mpi_runner_for_shim_opt' in config:
        genome_filename = os.path.split(config['process_genome']['readable_genome_file'][0])[1] + '.genome'
        config['mpi_runner_for_shim_opt']['genome_filename'] = os.path.join(processed_data_dir, genome_filename)
        run_mpi_runner_for_shim_opt(config['mpi_runner_for_shim_opt'], [shimmed_genome_dirpath], json_filepath, mag_filepath, h5_filepath)

    # sorting typically involves creating genome.h5 or genome.inp files from a
    # genome after the mpi runner generates the genomes
    if config['process_genome']['analysis'] or config['process_genome']['readable']:
        best_genome_filename = find_best_genome(genome_dirpath)
        genome_path = os.path.join(genome_dirpath, best_genome_filename)
        run_process_genome(config['process_genome'], genome_path, json_filepath, mag_filepath, h5_filepath, processed_data_dir)

    if 'compare' in config:
        best_shimmed_genome_filename = find_best_genome(shimmed_genome_dirpath)
        # grab the genome created from an .inp file from the use of
        # process_genome.py
        original_genome_filename = os.path.split(config['process_genome']['readable_genome_file'][0])[1] + '.genome'
        original_genome_path = os.path.join(processed_data_dir, original_genome_filename)
        shimmed_genome_path = os.path.join(shimmed_genome_dirpath, best_shimmed_genome_filename)
        run_compare(config['compare'], original_genome_path, shimmed_genome_path, data_dir)

def run_id_setup(options, args):
    options_named = namedtuple("options", options.keys())(*options.values())
    id_setup.process(options_named, args)

def run_magnets(options, args):
    options_named = namedtuple("options", options.keys())(*options.values())
    magnets.process(options_named, args)

def run_lookup_generator(options, args):
    options_named = namedtuple("options", options.keys())(*options.values())
    lookup_generator.process(options_named, args)

def run_mpi_runner(params, args, json_filepath, mag_filepath, h5_filepath):
    options = params
    options['id_filename'] = json_filepath
    options['magnets_filename'] = mag_filepath
    options['lookup_filename'] = h5_filepath
    options_named = namedtuple("options", options.keys())(*options.values())

    if not params['restart'] and not os.path.exists(args[0]):
        os.makedirs(args[0])

    mpi_runner.process(options_named, args)

def run_mpi_runner_for_shim_opt(params, args, json_filepath, mag_filepath, h5_filepath):
    options = params
    options['id_filename'] = json_filepath
    options['magnets_filename'] = mag_filepath
    options['lookup_filename'] = h5_filepath
    options_named = namedtuple("options", options.keys())(*options.values())

    if not os.path.exists(args[0]):
        os.makedirs(args[0])

    mpi_runner_for_shim_opt.process(options_named, args)

def run_process_genome(params, input_file, json_filepath, mag_filepath, h5_filepath, output_dir):
    options = params
    options['id_filename'] = json_filepath
    options['magnets_filename'] = mag_filepath
    options['id_template'] = h5_filepath

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    options['output_dir'] = output_dir

    options_named = namedtuple("options", options.keys())(*options.values())
    args = [input_file]
    process_genome.process(options_named, args)

def run_compare(params, original_genome, shimmed_genome, output_dir):
    options = {}
    shim_output_filepath = os.path.join(output_dir, params['output_filename'])
    args = [original_genome] + [shimmed_genome] + [shim_output_filepath]
    options_named = namedtuple("options", options.keys())(*options.values())
    compare.process(options_named, args)

def find_best_genome(genome_dir):
    # find the best genome by looking at the fitnesses
    best_genome = None
    # filter out any files in the given dir that aren't genomes
    genome_filepaths = [filepath for filepath in os.listdir(genome_dir) if 'genome' in filepath]
    # grab all filenames from the filepaths, then grab the fitnesses
    genome_filenames = [os.path.split(filepath)[1] for filepath in genome_filepaths]
    genome_fitnesses = [filename.split('_')[0] for filename in genome_filenames]
    genome_fitnesses.sort(key=float)

    for filename in os.listdir(genome_dir):
        if genome_fitnesses[0] in filename:
            best_genome = filename

    assert best_genome is not None
    return best_genome

if __name__ == "__main__":
    from optparse import OptionParser
    usage = "%prog [options] ConfigFile OutputDataDir"
    parser = OptionParser(usage=usage)
    (options, args) = parser.parse_args()

    yaml = YAML(typ='safe')
    with open(args[0], 'r') as config_file:
        config = yaml.load(config_file)
        extract_params(config, args[1])
