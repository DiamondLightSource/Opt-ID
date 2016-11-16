#!/bin/bash
module load global/cluster

rm -rf ${9}/logs
mkdir ${9}/logs

qsub -pe openmpi ${3} \
    -q ${4} \
    -l infiniband \
    ${1} \
    ${2} \
    --iterations ${5} \
    -l ${6} \
    -i ${7} \
    -m ${8} \
    -s 24 \
    --param_c 1 \
    ${9}/logs
