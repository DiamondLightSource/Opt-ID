[![Build Status](https://travis-ci.org/DiamondLightSource/Opt-ID.svg?branch=master)](https://travis-ci.org/DiamondLightSource/Opt-ID)  [![Coverage Status](https://coveralls.io/repos/github/DiamondLightSource/Opt-ID/badge.svg?branch=master)](https://coveralls.io/github/DiamondLightSource/Opt-ID?branch=master)  [![Scrutinizer Code Quality](https://scrutinizer-ci.com/g/DiamondLightSource/Opt-ID/badges/quality-score.png?b=master)](https://scrutinizer-ci.com/g/DiamondLightSource/Opt-ID/?branch=master)

# Opt-ID
Code for the Optimisation of ID's using Python and Opt-AI

## Order of things
  1. From the Excel files supplied by the supplier, create tab delimited .sim files of magnetisation. This is a manual procedure done only on Windows.
  2. Run id_setup.py to create a description of the ID - it creates a json.
  3. Run magnets.py - this creates the data files for the magnets - a .mag file. It requires the raw .sim input files.
  4. Run lookup_generator.py. This generates what we could call the ID operator that acts on the real magnet data to create a real ID field. It requires the .json file created by setup.py and it creates a .h5 file
  5. Run mpi_runner.py. This requires the .json file created from step 2, the .mag database created in step 3 and the .h5 lookup file created in step 5. This requires a cluster and must be done on a UNIX machine.
  6. Run process_genome.py. This creates a human readable output .inp file (also suitable for analysis with old Fortran code) and a viewable .h5 file.

Everything except step 5 can be done in either Windows or Unix.

Then what is needed is to actually run the sort, which is to be run on a cluster. using mpi_runner.py 

## Command line commands
  0. module load python/ana
     This is a python anaconda instalation with mpi4py

  1. Manually create .sim files
     or use the ones in the data folder for testing
  
  2. export IDHOME=/path/to/Opt-ID/IDSort/src
     export IDDATA=/path/to/Opt-ID/IDSort/data
  
  3. python $IDHOME/id_setup.py -p 109 --fullmagdims 41. 16. 6.22 --vemagdims 41. 16. 3.12 --hemagdims 41. 16. 4.0 -i 0.03 -g 6.15 -t "PPM_AntiSymmetric" -n "J13" -x -5.0  5.1  2.5 -z -0.0 .1 0.1 -s 5 myfilename.json

  (Choose your own 'myfilename.json' and type 'python $IDHOME/id_setup.py -h' for meaning of tags)
  
  4. python $IDHOME/magnets.py -H $IDDATA/J13H.sim --HE $IDDATA/J13HEA.sim -V $IDDATA/J13V.sim --VE $IDDATA/J13VE.sim mymagnets.mag

  (Choose your own 'mymagnets.mag' and type 'python $IDHOME/magnets.py -h' for meaning of tags)
  
  5. python $IDHOME/lookup_generator.py -p 109 -r myfilename.json mylookupfilename.h5

  (Use 'myfilename.json' from earlier and choose your own 'mylookupfilename.h5'. Type 'python $IDHOME/lookup_generator.py -h' for meaning of tags)
  
  6. mkdir mylogs; cd mylogs
  
  7. module load global/cluster
  (This loads the cluster and gives access to qsub command)
  
  [8a. Open another terminal and type: 'module load global/cluster' and then 'qstat' This will let you watch the job on the cluster]
  
  8. qsub -pe openmpi 24 -q medium.q -l release=rhel6 -v IDHOME=$IDHOME $IDHOME/mpijob.sh --iterations 5 -l mylookupfilename.h5 -i myfilename.json -m mymagnets.mag -s 24 --param_c 1 mylogs

  (Use 'myfilename.json', 'mymagnets.mag', and 'mylookupfilename.h5' from earlier and the 'mylogs' directory created in step 5.   Type 'python $IDHOME/mpi_runner.py -h' for meaning of tags. Genomes will be created in the mylogs directory with their cost as the first part of the filename - e.g. 4.62409644e-07_000_00bc026cfae7.genome is cost_generation_unique-id.genome)
  
  (use the -r flag to start again if you want to resume from a previous best fit)
  
  9. python $IDHOME/process_genome.py -a -r -i myfilename.json -m mymagnets.mag -t mylookupfilename.h5 mylogs/4.62409644e-07_000_00bc026cfae7.genome

  (Use 'myfilename.json', 'mymagnets.mag', and 'mylookupfilename.h5' from earlier, and the genome of interest within 'mylogs', e.g. 'mylogs/4.62409644e-07_000_00bc026cfae7.genome'. Multiple genomes can be analysed at once, just add extra file locations to the end of the command.  Type 'python $IDHOME/process_genome.py -h' for meaning of tags.)
  
