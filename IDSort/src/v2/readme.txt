qsub -pe openmpi 120 -q medium.q -l release=rhel6 /home/ssg37927/ID/Opt-ID/IDSort/src/v2/mpijob.sh --iterations 200 -s 25 -r --param_c 1 /dls/tmp/ssg37927/id/logs


python /home/ssg37927/ID/Opt-ID/IDSort/src/v2/Opt-ID.py -b /dls/tmp/ssg37927/id/logs 1.06139695e-08_000_054e6b35ecdb.genome
python /home/ssg37927/ID/Opt-ID/IDSort/src/v2/Opt-ID.py -b /dls/tmp/ssg37927/id/logs 9.13106363e-07_000_402e6f1b9fb8.genome

qsub -pe openmpi 120 -q medium.q -l release=rhel6 /home/ssg37927/ID/Opt-ID/IDSort/src/v2/mpi4shim.sh -b /dls/tmp/ssg37927/id/logs/9.13106363e-07_000_402e6f1b9fb8.genome.h5 -g /dls
/tmp/ssg37927/id/logs/9.13106363e-07_000_402e6f1b9fb8.genome -m 10 -c 1000 /dls/tmp/ssg37927/id/logs