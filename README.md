# Opt-ID
Code for the Optimisation of ID's using Python and Opt-AI

## Order of things
  1. From the Excel files supplied by the supplier, create tab delimited .sim files of magnetisation. This is a manual procedure done only on Windows.
  2. Run id_setup.py to create a description of the ID - it creates a json.
  3. Run magnets.py - this creates the data files for the magnets - a .mag file. It requires the raw .sim input files.
  4. Run lookup_generator.py. This generates what we could call the ID operator that acts on the real magnet data to create a real ID field. It requires the .json file created by setup.py and it creates a .h5 file
  5. Run mpi_runner.py. This requires the .json file created from step 2, the .mag database created in step 3 and the .h5 lookup file created in step 5. This requires a cluster and must be done on a UNIX machine.
  6. Run tmp_compare.py. This creates a human readable output .inp file (also suitable for analysis with old Fortran code) and an viewable .h5 file.

Everything except step 5 can be done in either Windows or Unix.

Then what is needed is to actually run the sort, which is to be run on a cluster. using mpi_runner.py 

## Command line commands
  1. Manually create .sim files
  2. 
