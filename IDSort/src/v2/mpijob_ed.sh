#!/bin/bash
MPIRUN=/dls_sw/prod/tools/RHEL6-x86_64/openmpi/1-6-5/prefix/bin/mpirun
PYTHON=/dls_sw/prod/tools/RHEL6-x86_64/defaults/bin/dls-python
wdir=/home/gdy32713/DAWN_stable/optid/Opt-ID/IDSort/src/v2

UNIQHOSTS=${TMPDIR}/machines-u
awk '{print $1 }' ${PE_HOSTFILE} | uniq > ${UNIQHOSTS}
uniqslots=$(wc -l <${UNIQHOSTS})
echo "number of uniq hosts: ${uniqslots}"
echo "running on these hosts:"
cat ${UNIQHOSTS}

processes=`bc <<< "$uniqslots"`

echo "Processes running are : ${processes}"

$MPIRUN -np ${processes} \
        --hostfile ${UNIQHOSTS} \
        --wd /dls/tmp/gdy32713/id/logs \
        --tag-output \
        $PYTHON /home/gdy32713/DAWN_stable/optid/Opt-ID/IDSort/src/v2/mpi_runner.py $@