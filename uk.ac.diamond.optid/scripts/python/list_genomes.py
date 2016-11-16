import os, sys, datetime

def modification_date(filepath):
    t = os.path.getmtime(filepath)
    return datetime.datetime.fromtimestamp(t).strftime("%Y-%m-%d %H:%M:%S")

# First command-line argument is directory to list files from
dir = sys.argv[1]

# Get file names (without path)
file_list = os.listdir(dir)
# Remove filenames without '.genome' extension
genome_list = [ fi for fi in file_list if fi.endswith(".genome") ]

# For each genome print the following:
# <date> <time> <genome-file-name>
for genome in genome_list:
    # Construct absolute genome path
    genome_path = os.path.join(dir, genome)
    print modification_date(genome_path), genome
