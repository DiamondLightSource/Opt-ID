#!/bin/bash
MPIRUN=/dls_sw/prod/tools/RHEL6-x86_64/openmpi/1-6-5/prefix/bin/mpirun
PYTHON=/dls_sw/prod/tools/RHEL6-x86_64/defaults/bin/dls-python
wdir=/home/ssg37927/ID/Opt-ID/IDSort/src/v2/

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
        --wd /dls/tmp/ssg37927/id/logs \
        --tag-output \
        $PYTHON /home/ssg37927/ID/Opt-ID/IDSort/src/v2/mpi_runner.py $@