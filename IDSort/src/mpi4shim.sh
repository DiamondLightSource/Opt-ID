#!/bin/bash
module load global/cluster
module load python/ana
source activate mpi2
module load openmpi/1.6.5

wdir=/home/gdy32713/DAWN_stable/optid/Opt-ID/IDSort/src

UNIQHOSTS=${TMPDIR}/machines-u
awk '{print $1 }' ${PE_HOSTFILE} | uniq > ${UNIQHOSTS}
uniqslots=$(wc -l <${UNIQHOSTS})
echo "number of uniq hosts: ${uniqslots}"
echo "running on these hosts:"
cat ${UNIQHOSTS}

processes=`bc <<< "$uniqslots"`

echo "Processes running are : ${processes}"

mpirun -np ${processes} \
        --hostfile ${UNIQHOSTS} \
        --wd /dls/tmp/gdy32713/I02J/I02j_analysis/logs \
        --tag-output \
        $PYTHON $wdir/mpi_runner_for_shim.py $@