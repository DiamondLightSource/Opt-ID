import os
import pwd
import subprocess
from collections import namedtuple

import nbformat
from nbconvert import PDFExporter
from nbconvert.preprocessors import ExecutePreprocessor
from ruamel.yaml import YAML
from jinja2 import FileSystemLoader, Environment

from definitions import ROOT_DIR
from IDSort.src import id_setup, magnets, lookup_generator, mpi_runner, \
        mpi_runner_for_shim_opt, process_genome, compare


def run_shim_job(config, shimmed_genome_dirpath, processed_data_dir, data_dir, use_cluster):
    # assuming that the shim job is starting with an inp file, it needs to
    # first be converted to a genome file before the mpi runner generates the
    # shimmed genomes
    config['process_genome']['create_genome'] = True
    config['process_genome']['readable'] = False
    config['process_genome']['analysis'] = False
    run_process_genome(config['process_genome'], config['process_genome']['readable_genome_file'], processed_data_dir)

    genome_filename = os.path.split(config['process_genome']['readable_genome_file'])[1] + '.genome'
    genome_filepath = os.path.join(processed_data_dir, genome_filename)
    # rename the newly created genome file to be prefixed with '1.0_000'; this
    # is a temporary hack to get the shimming optimiser to utilise its fullest
    # capabilities, since currently the optimisation is dependent on the
    # fitness and age parts of the genome filename used to start the shim
    split_genome_filename = genome_filename.split('_')
    split_genome_filename[0] = '1.0'
    split_genome_filename[1] = '000'
    renamed_genome_filename = '_'.join(split_genome_filename)
    renamed_genome_filepath = os.path.join(processed_data_dir, renamed_genome_filename)
    os.rename(genome_filepath, renamed_genome_filepath)
    config['mpi_runner_for_shim_opt']['genome_filename'] = renamed_genome_filepath
    run_mpi_runner_for_shim_opt(config['mpi_runner_for_shim_opt'], [shimmed_genome_dirpath], data_dir, use_cluster)

def run_id_setup(options, args):
    options_named = namedtuple("options", options.keys())(*options.values())
    id_setup.process(options_named, args)

def run_magnets(options, args):
    options_named = namedtuple("options", options.keys())(*options.values())
    magnets.process(options_named, args)

def run_lookup_generator(options, args):
    options_named = namedtuple("options", options.keys())(*options.values())
    lookup_generator.process(options_named, args)

def run_mpi_runner(options, args, data_dir, use_cluster):
    options_named = namedtuple("options", options.keys())(*options.values())

    if not use_cluster:
        mpi_runner.process(options_named, args)
    else:
        logfile_dir = 'logfiles/'
        logfile_dirpath = os.path.join(data_dir, logfile_dir)
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
        ] + [os.path.join(ROOT_DIR, 'IDSort/src/mpijob.sh')]

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

def run_mpi_runner_for_shim_opt(options, args, data_dir, use_cluster):
    options_named = namedtuple("options", options.keys())(*options.values())

    if not use_cluster:
        mpi_runner_for_shim_opt.process(options_named, args)
    else:
        logfile_dir = 'logfiles/'
        logfile_dirpath = os.path.join(data_dir, logfile_dir)
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
        ] + [os.path.join(ROOT_DIR, 'IDSort/src/mpi4shimOpt.sh')]

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
    options['output_dir'] = output_dir
    options_named = namedtuple("options", options.keys())(*options.values())
    args = [input_file]
    process_genome.process(options_named, args)

def run_compare(original_genome_path, shimmed_genome_path, diff_filename, data_dir):
    diff_dir = 'shim_diffs/'
    diff_dirpath = os.path.join(data_dir, diff_dir)
    if not os.path.exists(diff_dirpath):
        os.makedirs(diff_dirpath)

    # check the name of the diff filename to see if it's the default one or not
    if diff_filename == 'shim':
        # concatenate the original genome and the shimmed genome to form the
        # diff filename
        original_genome = os.path.split(original_genome_path)[1]
        shimmed_genome = os.path.split(shimmed_genome_path)[1]
        diff_filename += '_' + original_genome + '_' + shimmed_genome

    diff_filepath = os.path.join(diff_dirpath, diff_filename)
    options = {}
    args = [original_genome_path, shimmed_genome_path, diff_filepath]
    options_named = namedtuple("options", options.keys())(*options.values())
    compare.process(options_named, args)

def generate_restart_sort_script(config, config_path, data_dir, use_cluster):
    file_loader = FileSystemLoader(os.path.join(ROOT_DIR, 'IDSort/src'))
    env = Environment(loader=file_loader)
    template = env.get_template('restart_sort_template.sh')

    python_env_module = 'python/3'
    if use_cluster:
        output = template.render(
            python_env_module=python_env_module,
            config_path=config_path,
            output_dir_path=data_dir,
            project_root_dir=ROOT_DIR,
            use_cluster=use_cluster,
            node_os=config['mpi_runner']['node_os'],
            number_of_threads=config['mpi_runner']['number_of_threads'],
            queue=config['mpi_runner']['queue']
        )
    else:
        output = template.render(
            python_env_module=python_env_module,
            config_path=config_path,
            output_dir_path=data_dir,
            project_root_dir=ROOT_DIR,
            use_cluster=use_cluster,
            seed=config['mpi_runner']['seed'],
            seed_value=config['mpi_runner']['seed_value']
        )

    script_name = 'restart_sort.sh'
    script_path = os.path.join(data_dir, script_name)

    with open(script_path, 'w') as script:
        script.write(output)

    os.chmod(script_path, 0o775)

def generate_report_script(job_type, config_path, data_dir, genome_h5_dirpath):
    file_loader = FileSystemLoader(os.path.join(ROOT_DIR, 'IDSort/src'))
    env = Environment(loader=file_loader)
    shell_script_template = env.get_template('generate_report_template.sh')

    notebook_name = 'genome_report.ipynb'
    notebook_path = os.path.join(data_dir, notebook_name)

    python_env_module = 'python/3'
    shell_script_output = shell_script_template.render(
        python_env_module=python_env_module,
        notebook_path=notebook_path,
        yaml_config=config_path,
        data_dir=data_dir,
        project_root_dir=ROOT_DIR
    )

    shell_script_name = 'generate_report.sh'
    shell_script_path = os.path.join(data_dir, shell_script_name)

    with open(shell_script_path, 'w') as shell_script:
        shell_script.write(shell_script_output)

    os.chmod(shell_script_path, 0o775)

def generate_report_notebook(config, job_type, data_dir, processed_data_dir, genome_dirpath, filenames, report_filename):
    file_loader = FileSystemLoader(os.path.join(ROOT_DIR, 'IDSort/src'))
    env = Environment(loader=file_loader)
    report_template = env.get_template('genome_report_template.ipynb')

    if job_type == 'sort':
        # convert given genomes to h5 files, and convert given inp files to
        # genomes and then to h5 files

        inp_to_genome_config = {
            'analysis': False,
            'readable': False,
            'create_genome': True,
            'id_filename': config['process_genome']['id_filename'],
            'magnets_filename': config['process_genome']['magnets_filename'],
            'id_template': config['process_genome']['id_template']
        }
        genome_to_h5_config = {
            'analysis': True,
            'readable': True,
            'create_genome': False,
            'id_filename': config['process_genome']['id_filename'],
            'magnets_filename': config['process_genome']['magnets_filename'],
            'id_template': config['process_genome']['id_template']
        }

        genome_h5_filepaths = []
        for filename in filenames:
            if filename.endswith('.genome'):
                filepath = os.path.join(genome_dirpath, filename)
                run_process_genome(genome_to_h5_config, filepath, processed_data_dir)
                genome_h5_filepaths.append(os.path.join(processed_data_dir, filename + '.h5'))
            elif filename.endswith('.inp'):
                filepath = os.path.join(processed_data_dir, filename)
                run_process_genome(inp_to_genome_config, filepath, genome_dirpath)
                new_genome_filename = filename + '.genome'
                new_genome_filepath = os.path.join(genome_dirpath, new_genome_filename)
                run_process_genome(genome_to_h5_config, new_genome_filepath, processed_data_dir)
                genome_h5_filepaths.append(os.path.join(processed_data_dir, new_genome_filename + '.h5'))
    elif job_type == 'shim':
        genome_h5_filepaths = [os.path.join(genome_dirpath, filename) for filename in filenames]

    report_output = report_template.render(
        job_type=job_type,
        genome_h5_filepaths=genome_h5_filepaths
    )

    notebook_name = 'genome_report.ipynb'
    notebook_path = os.path.join(data_dir, notebook_name)

    with open(notebook_path, 'w') as notebook:
        notebook.write(report_output)

    # create dir for genome reports
    genome_report_dir = 'genome_reports/'
    genome_report_dirpath = os.path.join(data_dir, genome_report_dir)
    if not os.path.exists(genome_report_dirpath):
        os.makedirs(genome_report_dirpath)

    # execute notebook
    with open(notebook_path, 'r') as notebook:
        nb = nbformat.read(notebook, as_version=4)

    ep = ExecutePreprocessor()
    ep.preprocess(nb, {'metadata': {'path': data_dir}})
    pdf_exporter = PDFExporter()
    pdf_exporter.exclude_output_prompt = True
    pdf_exporter.exclude_input = True
    pdf_data, resources = pdf_exporter.from_notebook_node(nb)

    # check the name of the report to see if a specific name has been given or
    # not
    if report_filename == 'genome_report.pdf':
        # concatenate all genome/inp files using "_" as a separator to form the
        # filename
        report_filename = '_'.join(filenames) + '.pdf'

    report_filepath = os.path.join(genome_report_dirpath, report_filename)
    with open(report_filepath, 'wb') as report:
        report.write(pdf_data)

def generate_compare_shim_script(config_path, data_dir):
    file_loader = FileSystemLoader(os.path.join(ROOT_DIR, 'IDSort/src'))
    env = Environment(loader=file_loader)
    shell_script_template = env.get_template('compare_shim_template.sh')

    python_env_module = 'python/3'
    shell_script_output = shell_script_template.render(
        python_env_module=python_env_module,
        yaml_config=config_path,
        data_dir=data_dir,
        project_root_dir=ROOT_DIR
    )

    shell_script_name = 'compare_shim.sh'
    shell_script_path = os.path.join(data_dir, shell_script_name)

    with open(shell_script_path, 'w') as shell_script:
        shell_script.write(shell_script_output)

    os.chmod(shell_script_path, 0o775)

def set_job_parameters(job_type, options, config):
    if job_type == 'sort':
        runner = 'mpi_runner'
    elif job_type == 'shim':
        runner = 'mpi_runner_for_shim_opt'

    if options.use_cluster:
        config[runner]['number_of_threads'] = options.number_of_threads
        config[runner]['queue'] = options.queue
        config[runner]['node_os'] = options.node_os
    else:
        config[runner]['singlethreaded'] = True
        config[runner]['seed'] = options.seed
        config[runner]['seed_value'] = options.seed_value

def generate_mpi_script(job_type):
    file_loader = FileSystemLoader(os.path.join(ROOT_DIR, 'IDSort/src'))
    env = Environment(loader=file_loader)
    if job_type == 'sort':
        shell_script_template = env.get_template('mpijob_template.sh')
    elif job_type == 'shim':
        shell_script_template = env.get_template('mpi4shimOpt_template.sh')

    shell_script_output = shell_script_template.render(
        project_root_dir=ROOT_DIR
    )

    if job_type == 'sort':
        shell_script_name = 'mpijob.sh'
    elif job_type == 'shim':
        shell_script_name = 'mpi4shimOpt.sh'
    shell_script_path = os.path.join(ROOT_DIR, 'IDSort/src', shell_script_name)
    print(shell_script_path)

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
    parser.add_option("--compare-shim", dest="compare_shim", help="Compare a shimmed genome to the starting genome and get a human readable diff of the magnet configurations", action="store_true", default=False)
    parser.add_option("--diff-filename", dest="diff_filename", help="Specify the filename of the human readable magnet configuration diff", default="shim", type="string")
    parser.add_option("--generate-report", dest="generate_report", help="Generate a PDF with some data visualisation of desired genomes", action="store_true", default=False)
    parser.add_option("--report-filename", dest="report_filename", help="Specify the filename of the PDF report", default="genome_report.pdf", type="string")
    parser.add_option("--cluster-on", dest="use_cluster", help="Run job on a cluster", action="store_true")
    parser.add_option("--num-threads", dest="number_of_threads", help="Set the number of threads to use per node", default=10, type="int")
    parser.add_option("--queue", dest="queue", help="Set the desired queue for the cluster job to be added to", default="medium.q", type="string")
    parser.add_option("--node-os", dest="node_os", help="Set the OS of the desired nodes", default="rhel7", type="string")
    parser.add_option("--cluster-off", dest="use_cluster", help="Run job on a local machine", action="store_false")
    parser.add_option("--seed", dest="seed", help="Seed the random number generator", action="store_true", default=False)
    parser.add_option("--seed-value", dest="seed_value", help="Seed value for the random number generator", default=1, type="int")
    (options, args) = parser.parse_args()

    if options.sort and options.shim:
        raise ValueError('A sort and shim job cannot be done simultaneously, please choose only one')

    config_path = args[0]
    data_dir = args[1]

    yaml = YAML(typ='safe')
    with open(config_path, 'r') as config_file:
        config = yaml.load(config_file)

    # grab the user's FedID and create a dir at /dls/tmp/FedID/data_dir where
    # data_dir is the last child directory of the path in the data_dir
    # variable
    fed_id = pwd.getpwuid(os.getuid()).pw_name
    data_dirname = os.path.basename(os.path.normpath(data_dir))
    tmp_dirpath = os.path.join('/dls/tmp/', fed_id, data_dirname)
    if not os.path.exists(tmp_dirpath):
        os.makedirs(tmp_dirpath)

    process_genome_output_dir = 'process_genome_output/'
    processed_data_dir = os.path.join(tmp_dirpath, process_genome_output_dir)
    if not os.path.exists(processed_data_dir):
        os.makedirs(processed_data_dir)
        process_genome_symlink_path = os.path.normpath(os.path.join(data_dir, process_genome_output_dir))
        os.symlink(processed_data_dir, process_genome_symlink_path)

    json_filename = config['id_setup'].pop('output_filename', None)
    json_filepath = os.path.join(data_dir, json_filename)
    mag_filename = config['magnets'].pop('output_filename', None)
    mag_filepath = os.path.join(data_dir, mag_filename)
    # the periods param for this should be the same as the periods param for
    # id_setup.py, so use that same value in config['lookup_generator']
    h5_filename = config['lookup_generator'].pop('output_filename', None)
    h5_filepath = os.path.join(tmp_dirpath, h5_filename)
    config['lookup_generator']['periods'] = config['id_setup']['periods']

    if not options.restart_sort and not options.generate_report and not options.compare_shim:
        run_id_setup(config['id_setup'], [json_filepath])
        run_magnets(config['magnets'], [mag_filepath])
        run_lookup_generator(config['lookup_generator'], [json_filepath, h5_filepath])
        h5_symlink_path = os.path.join(data_dir, h5_filename)
        if not os.path.exists(h5_symlink_path):
            os.symlink(h5_filepath, h5_symlink_path)

    # both a sort and shim's use of process_genome.py need the json, mag, h5
    # filepaths
    if 'process_genome' not in config:
        config['process_genome'] = {}
    config['process_genome']['id_filename'] = json_filepath
    config['process_genome']['magnets_filename'] = mag_filepath
    config['process_genome']['id_template'] = h5_filepath

    if options.sort or options.restart_sort:
        genome_dir = 'genomes/'
        genome_dirpath = os.path.join(tmp_dirpath, genome_dir)
        genome_symlink_path = os.path.normpath(os.path.join(data_dir, genome_dir))

        if not os.path.exists(genome_dirpath):
            os.makedirs(genome_dirpath)
        if not os.path.exists(genome_symlink_path):
            os.symlink(genome_dirpath, genome_symlink_path)
        mpijob_script_path = os.path.join(ROOT_DIR, 'IDSort/src/mpijob.sh')
        if not os.path.exists(mpijob_script_path):
            generate_mpi_script('sort')

        config['mpi_runner']['id_filename'] = json_filepath
        config['mpi_runner']['magnets_filename'] = mag_filepath
        config['mpi_runner']['lookup_filename'] = h5_filepath
        set_job_parameters('sort', options, config)

        if not options.restart_sort:
            config['mpi_runner']['restart'] = False
        else:
            config['mpi_runner']['restart'] = True

        run_mpi_runner(config['mpi_runner'], [genome_dirpath], data_dir, options.use_cluster)
        generate_restart_sort_script(config, config_path, data_dir, options.use_cluster)
        generate_report_script('sort', config_path, data_dir, processed_data_dir)
    elif options.shim:
        shimmed_genome_dir = 'shimmed_genomes/'
        shimmed_genome_dirpath = os.path.join(tmp_dirpath, shimmed_genome_dir)
        shimmed_genome_symlink_path = os.path.normpath(os.path.join(data_dir, shimmed_genome_dir))

        if not os.path.exists(shimmed_genome_dirpath):
            os.makedirs(shimmed_genome_dirpath)
        if not os.path.exists(shimmed_genome_symlink_path):
            os.symlink(shimmed_genome_dirpath, shimmed_genome_symlink_path)
        mpijob_script_path = os.path.join(ROOT_DIR, 'IDSort/src/mpi4shimOpt.sh')
        if not os.path.exists(mpijob_script_path):
            generate_mpi_script('shim')

        config['mpi_runner_for_shim_opt']['id_filename'] = json_filepath
        config['mpi_runner_for_shim_opt']['magnets_filename'] = mag_filepath
        config['mpi_runner_for_shim_opt']['lookup_filename'] = h5_filepath
        set_job_parameters('shim', options, config)
        run_shim_job(config, shimmed_genome_dirpath, processed_data_dir, data_dir, options.use_cluster)
        generate_report_script('shim', config_path, data_dir, shimmed_genome_dirpath)
        generate_compare_shim_script(config_path, data_dir)
    elif options.generate_report:
        job_type = None
        if 'mpi_runner' in config:
            job_type = 'sort'
            genome_dir = 'genomes/'
            genome_dirpath = os.path.join(data_dir, genome_dir)
        elif 'mpi_runner_for_shim_opt' in config:
            job_type = 'shim'
            genome_dir = 'shimmed_genomes/'
            genome_dirpath = os.path.join(data_dir, genome_dir)
        assert job_type is not None
        genome_filenames = args[2:]
        generate_report_notebook(config, job_type, data_dir, processed_data_dir, genome_dirpath, genome_filenames, options.report_filename)
    elif options.compare_shim:
        original_inp = os.path.split(config['process_genome']['readable_genome_file'])[1]
        original_genome = original_inp + '.genome'
        original_genome_path = os.path.join(processed_data_dir, original_genome)
        shimmed_genomes_dir = 'shimmed_genomes/'
        shimmed_genomes_dirpath = os.path.join(tmp_dirpath, shimmed_genomes_dir)
        shimmed_genome = args[2]
        shimmed_genome_path = os.path.join(shimmed_genomes_dirpath, shimmed_genome)
        run_compare(original_genome_path, shimmed_genome_path, options.diff_filename, data_dir)
