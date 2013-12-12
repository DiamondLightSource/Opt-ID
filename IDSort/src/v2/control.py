'''
Created on 12 Dec 2013

@author: ssg37927
'''

import os
import subprocess
import time
import shutil


def chunks(l, n):
    return [l[i:i+n] for i in range(0, len(l), n)]


def run_commands(commands, poll_time=5):
    ids = []
    for input_command in commands:
        command = "qsub %s" % (input_command)
        print command
        proc = subprocess.Popen([command], shell=True, stdout=subprocess.PIPE)
        result = proc.communicate()[0]
        print result
        id_val = result.split()[2].strip()
        id_val = id_val.split('.')[0]
        print id_val
        ids.append(id_val)
    # now we should block until all the process are done, we can poll this infrequently and show some health possibly
    
    waiting = True
    print "time\t" + "\t".join(ids)
    time_passed = 0
    while waiting:
        waiting = False
        command = "qstat"
        proc = subprocess.Popen([command], shell=True, stdout=subprocess.PIPE)
        stat = proc.communicate()[0]
        values = stat.split("\n")
        status = {}
        for line in values[2:]:
            split = line.split()
            if(len(split) > 4) :
                status[split[0].strip()] = split[4]
        stats = []
        for id in ids:
            stat = "F"
            try :
                stat = status[id]
                waiting = True
            except :
                pass
            stats.append(stat)
        print ("%i\t" % (time_passed)) + "\t".join(stats)
        time_passed += poll_time
        if waiting :
            time.sleep(poll_time)
    print "Completed"
    return


def run_batch(number_of_nodes, input_command, poll_time=5):
    commands = []
    for i in range(number_of_nodes):
        commands.append(input_command)
    run_commands(commands, poll_time=poll_time)


def get_file_list(path, number_of_processors, number_of_files_per_processor, max_age):
    pathlist = []
    for p in os.listdir(path):
        params = p.split('_')
        fitness = float(params[0])
        age = int(params[1])
        if age < max_age:
            full_name = os.path.join(path, p)
            pathlist.append((fitness, full_name))
    pathlist.sort()
    pathlist = [x[1] for x in pathlist]
    return chunks(pathlist[0:(number_of_processors*number_of_files_per_processor)], number_of_files_per_processor)

if __name__ == "__main__":
    import optparse
    usage = "%prog [options] run_directory"
    parser = optparse.OptionParser(usage=usage)
    parser.add_option("-f", "--fitness", dest="fitness", help="Set the target fitness", default=0.0, type="float")
    parser.add_option("-p", "--processing", dest="processing", help="Set the total number of processing units per file", default=5, type="int")
    parser.add_option("-n", "--numnodes", dest="nodes", help="Set the total number of nodes to use", default=10, type="int")
    parser.add_option("-s", "--setup", dest="setup", help="set number of genomes to create in setup mode", default=10, type='int')
    parser.add_option("-i", "--info", dest="id_filename", help="Set the path to the id data", default='/dls/tmp/ssg37927/id/lookup/id.json', type="string")
    parser.add_option("-l", "--lookup", dest="lookup_filename", help="Set the path to the lookup table", default='/dls/tmp/ssg37927/id/lookup/unit.h5', type="string")
    parser.add_option("-m", "--magnets", dest="magnets_filename", help="Set the path to the magnet description file", default='/dls/tmp/ssg37927/id/lookup/magnets.mag', type="string")
    parser.add_option("-a", "--maxage", dest="max_age", help="Set the maximum age of a genome", default=10, type=int)
    parser.add_option("--param_c", dest="c", help="Set the OPT-AI parameter c", default=10.0, type='float')
    parser.add_option("--param_e", dest="e", help="Set the OPT-AI parameter eStar", default=0.0, type='float')
    parser.add_option("--param_scale", dest="scale", help="Set the OPT-AI parameter scale", default=10.0, type='float')
    parser.add_option("-r", "--restart", dest="restart", help="Don't recreate initial data", action="store_true", default=False)

    (options, args) = parser.parse_args()

    epoch_path = os.path.join(args[0], 'epoch')
    next_epoch_path = os.path.join(args[0], 'nextepoch')

    # start by creating the directory to put the initial population in 
    if not options.restart:
        print "Creating directories"
        if os.path.exists(args[0]):
            os.rmdir(args[0])
        os.mkdir(args[0])
        print "Creating directory %s" %(epoch_path)
        if os.path.exists(epoch_path):
            os.rmdir(epoch_path)
        os.mkdir(epoch_path)
        print "Creating directory %s" %(next_epoch_path)
        if os.path.exists(next_epoch_path):
            os.rmdir(next_epoch_path)
        os.mkdir(next_epoch_path)

        # make the initial population
        command = "/home/ssg37927/ID/Opt-ID/IDSort/src/v2/Opt-ID.sh -s %i -i %s -l %s -m %s %s" %\
            (options.setup, options.id_filename, options.lookup_filename,
             options.magnets_filename, epoch_path)

        run_batch(options.nodes, command)

    # now run the processing
    for i in range(30):
        files = get_file_list(epoch_path, options.nodes, options.setup, options.max_age)
    
        commands = []
        for filelist in files:
            filestring = ' '.join(filelist)
            print filestring
            command = "/home/ssg37927/ID/Opt-ID/IDSort/src/v2/Opt-ID.sh -i %s -l %s -m %s %s %s" %\
                (options.id_filename, options.lookup_filename,
                 options.magnets_filename, next_epoch_path, filestring)
            commands.append(command)
        
        run_commands(commands)
        
        time.sleep(5)
        
        # copy all the data back into the main epoc directory
        shutil.rmtree(epoch_path)
        shutil.move(next_epoch_path, epoch_path)
        os.mkdir(next_epoch_path)
    
