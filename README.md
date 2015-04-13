# Opt-ID
Code for the Optimisation of ID's using Python and Opt-AI

#Order of things
First run id_setup.py to create a description of the ID - it creates a json.
B) Run magnets.py - this creates the data files for the magnets - a .mag file It requires the raw .sim input files.
iii)run lookup_generator.py. This generates what we could call the ID operator that acts on the real magnet data to create a real ID 
field. It creates an .h5 file

These three steps can be done on Windows or Unix

Then what is needed is to actually run the sort, which is to be run on a cluster. using mpi_runner.py 
