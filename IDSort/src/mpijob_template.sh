#!/bin/bash
module load global/cluster
module load python/3
module load openmpi/3.0.0

export PYTHONPATH=$PYTHONPATH:{{ project_root_dir }}

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
        --tag-output \
        python -m IDSort.src.mpi_runner $@
