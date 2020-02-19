import os
import subprocess
from collections import namedtuple

from ruamel.yaml import YAML
from jinja2 import FileSystemLoader, Environment

from IDSort.src import id_setup, magnets, lookup_generator, mpi_runner, \
        mpi_runner_for_shim_opt, process_genome, compare


def run_sort_job(config, genome_dirpath, processed_data_dir, data_dir, restart_sort):
    if not restart_sort:
        config['mpi_runner']['restart'] = False
    else:
        config['mpi_runner']['restart'] = True
    run_mpi_runner(config['mpi_runner'], [genome_dirpath], data_dir)

    # sorting typically involves creating genome.h5 or genome.inp files from a
    # genome after the mpi runner generates the genomes
    if config['process_genome']['analysis'] or config['process_genome']['readable']:
        best_genome_filename = find_best_genome(genome_dirpath)
        genome_path = os.path.join(genome_dirpath, best_genome_filename)
        run_process_genome(config['process_genome'], genome_path, processed_data_dir)

def run_shim_job(config, shimmed_genome_dirpath, processed_data_dir, data_dir):
    # shimming typically involves creating a genome from an inp before the mpi
    # runner generates the genome
    if config['process_genome']['create_genome']:
        run_process_genome(config['process_genome'], config['process_genome']['readable_genome_file'][0], processed_data_dir)

    if 'mpi_runner_for_shim_opt' in config:
        genome_filename = os.path.split(config['process_genome']['readable_genome_file'][0])[1] + '.genome'
        config['mpi_runner_for_shim_opt']['genome_filename'] = os.path.join(processed_data_dir, genome_filename)
        run_mpi_runner_for_shim_opt(config['mpi_runner_for_shim_opt'], [shimmed_genome_dirpath], data_dir)

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

def run_mpi_runner(options, args, data_dir):
    if 'singlethreaded' not in options:
        options['singlethreaded'] = False

    options_named = namedtuple("options", options.keys())(*options.values())

    if not options['restart'] and not os.path.exists(args[0]):
        os.makedirs(args[0])

    if options_named.singlethreaded:
        mpi_runner.process(options_named, args)
    else:
        logfile_dir = 'logfiles/'
        logfile_dirpath = os.path.join(data_dir, logfile_dir)
        env_var_sublist = ['-v', options_named.environment_variables] if 'environment_vars' in options else []
        qsub_args = [
            'qsub',
            '-sync',
            'y',
            '-pe',
            'openmpi',
            str(options_named.number_of_threads),
            '-q',
            options_named.queue,
            '-l',
            'release=' + options_named.node_os,
            '-j',
            'y',
            '-o',
            os.path.join(logfile_dirpath, '$JOB_ID.log')
        ] + env_var_sublist + ['/home/twi18192/wc/Opt-ID/IDSort/src/mpijob.sh']

        mpijob_restart_sublist = ['--restart'] if options_named.restart else []
        mpijob_args = mpijob_restart_sublist + [
            '--iterations',
            str(options_named.iterations),
            '-l',
            options_named.lookup_filename,
            '-i',
            options_named.id_filename,
            '-m',
            options_named.magnets_filename,
            '-s',
            str(options_named.setup),
            '--param_c',
            str(options_named.c),
            args[0]
        ]

        subprocess.call(qsub_args + mpijob_args)

def run_mpi_runner_for_shim_opt(options, args, data_dir):
    if 'singlethreaded' not in options:
        options['singlethreaded'] = False

    options_named = namedtuple("options", options.keys())(*options.values())

    if not os.path.exists(args[0]):
        os.makedirs(args[0])

    if options_named.singlethreaded:
        mpi_runner_for_shim_opt.process(options_named, args)
    else:
        logfile_dir = 'logfiles/'
        logfile_dirpath = os.path.join(data_dir, logfile_dir)
        env_var_sublist = ['-v', options_named.environment_variables] if 'environment_vars' in options else []
        qsub_args = [
            'qsub',
            '-sync',
            'y',
            '-pe',
            'openmpi',
            str(options_named.number_of_threads),
            '-q',
            options_named.queue,
            '-l',
            'release=' + options_named.node_os,
            '-j',
            'y',
            '-o',
            os.path.join(logfile_dirpath, '$JOB_ID.log')
        ] + env_var_sublist + ['/home/twi18192/wc/Opt-ID/IDSort/src/mpi4shimOpt.sh']

        mpijob_args = [
            '--iterations',
            str(options_named.iterations),
            '-m',
            str(options_named.number_of_mutations),
            '-c',
            str(options_named.number_of_changes),
            '-l',
            options_named.lookup_filename,
            '-i',
            options_named.id_filename,
            '--magnets',
            options_named.magnets_filename,
            '-g',
            options_named.genome_filename,
            '-b',
            options_named.bfield_filename,
            '-s',
            str(options_named.setup),
            '--param_c',
            str(options_named.c),
            args[0]
        ]

        subprocess.call(qsub_args + mpijob_args)

def run_process_genome(options, input_file, output_dir):
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

def generate_restart_sort_script(config_path, data_dir):
    file_loader = FileSystemLoader('/home/twi18192/wc/Opt-ID/IDSort/src')
    env = Environment(loader=file_loader)
    template = env.get_template('restart_sort_template.sh')

    python_env_module = 'python/3'
    # can assume that the json, mag, h5 filepaths have been added to
    # config['mpi_runner'] at this point since we'll have gone through a sort
    # process already
    output = template.render(
        python_env_module=python_env_module,
        config_path=config_path,
        output_dir_path=data_dir
    )

    script_name = 'restart_sort.sh'
    script_path = os.path.join(data_dir, script_name)

    with open(script_path, 'w') as script:
        script.write(output)

    os.chmod(script_path, 0o775)

def generate_report_script(job_type, data_dir, genome_h5_dirpath):
    # generate notebook .ipynb file
    file_loader = FileSystemLoader('/home/twi18192/wc/Opt-ID/IDSort/src')
    env = Environment(loader=file_loader)
    report_template = env.get_template('genome_report_template.ipynb')

    report_output = report_template.render(
        genome_h5_dirpath=genome_h5_dirpath,
        job_type=job_type
    )

    notebook_name = 'genome_report.ipynb'
    notebook_path = os.path.join(data_dir, notebook_name)

    with open(notebook_path, 'w') as notebook:
        notebook.write(report_output)

    # generate shell script that runs the notebook
    shell_script_template = env.get_template('generate_report_template.sh')

    python_env_module = 'python/3'
    shell_script_output = shell_script_template.render(
        python_env_module=python_env_module,
        notebook_path=notebook_path
    )

    shell_script_name = 'generate_report.sh'
    shell_script_path = os.path.join(data_dir, shell_script_name)

    with open(shell_script_path, 'w') as shell_script:
        shell_script.write(shell_script_output)

    os.chmod(shell_script_path, 0o775)

if __name__ == "__main__":
    from optparse import OptionParser
    usage = "%prog [options] ConfigFile OutputDataDir"
    parser = OptionParser(usage=usage)
    parser.add_option("--sort", dest="sort", help="Run a sort job", action="store_true", default=False)
    parser.add_option("--restart-sort", dest="restart_sort", help="Run a sort job with an initial population of genomes", action="store_true", default=False)
    parser.add_option("--shim", dest="shim", help="Run a shim job", action="store_true", default=False)
    (options, args) = parser.parse_args()

    if options.sort and options.shim:
        raise ValueError('A sort and shim job cannot be done simultaneously, please choose only one')

    config_path = args[0]
    data_dir = args[1]

    yaml = YAML(typ='safe')
    with open(config_path, 'r') as config_file:
        config = yaml.load(config_file)

    process_genome_output_dir = 'process_genome_output/'
    processed_data_dir = os.path.join(data_dir, process_genome_output_dir)

    json_filename = config['id_setup'].pop('output_filename', None)
    json_filepath = os.path.join(data_dir, json_filename)
    mag_filename = config['magnets'].pop('output_filename', None)
    mag_filepath = os.path.join(data_dir, mag_filename)
    # the periods param for this should be the same as the periods param for
    # id_setup.py, so use that same value in config['lookup_generator']
    h5_filename = config['lookup_generator'].pop('output_filename', None)
    h5_filepath = os.path.join(data_dir, h5_filename)
    config['lookup_generator']['periods'] = config['id_setup']['periods']

    if not options.restart_sort:
        run_id_setup(config['id_setup'], [json_filepath])
        run_magnets(config['magnets'], [mag_filepath])
        run_lookup_generator(config['lookup_generator'], [json_filepath, h5_filepath])

    # both a sort and shim's use of process_genome.py need the json, mag, h5
    # filepaths
    config['process_genome']['id_filename'] = json_filepath
    config['process_genome']['magnets_filename'] = mag_filepath
    config['process_genome']['id_template'] = h5_filepath

    if options.sort or options.restart_sort:
        genome_dir = 'genomes/'
        genome_dirpath = os.path.join(data_dir, genome_dir)
        config['mpi_runner']['id_filename'] = json_filepath
        config['mpi_runner']['magnets_filename'] = mag_filepath
        config['mpi_runner']['lookup_filename'] = h5_filepath
        run_sort_job(config, genome_dirpath, processed_data_dir, data_dir, options.restart_sort)
        generate_restart_sort_script(config_path, data_dir)
        generate_report_script('sort', data_dir, processed_data_dir)
    elif options.shim:
        shimmed_genome_dir = 'shimmed_genomes/'
        shimmed_genome_dirpath = os.path.join(data_dir, shimmed_genome_dir)
        config['mpi_runner_for_shim_opt']['id_filename'] = json_filepath
        config['mpi_runner_for_shim_opt']['magnets_filename'] = mag_filepath
        config['mpi_runner_for_shim_opt']['lookup_filename'] = h5_filepath
        run_shim_job(config, shimmed_genome_dirpath, processed_data_dir, data_dir)
        generate_report_script('shim', data_dir, shimmed_genome_dirpath)
