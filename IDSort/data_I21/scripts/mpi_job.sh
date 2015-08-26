#!/bin/bash
module load global/cluster
module load python/ana
source activate mpi2
module load openmpi/1.6.5

UNIQHOSTS=${TMPDIR}/machines-u
awk '{print $1 }' ${PE_HOSTFILE} | uniq > ${UNIQHOSTS}
uniqslots=$(wc -l <${UNIQHOSTS})
echo "number of uniq hosts: ${uniqslots}"
echo "running on these hosts:"
cat ${UNIQHOSTS}

processes=`bc <<< "$uniqslots"`

echo "Processes running are : ${processes}"

mpirun -np ${processes} \
        -x LD_LIBRARY_PATH \
        --hostfile ${UNIQHOSTS} \
        --wd /dls/tmp/xrp26957/I21logs \
        --tag-output \
        python /home/xrp26957/workspace_test/Opt-ID/IDSort/src/v2/mpi_runner.py $@
