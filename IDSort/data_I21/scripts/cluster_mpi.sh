module load global/cluster

DIR=/home/xrp26957/workspace_test/Opt-ID

qsub -pe openmpi 300 \
    -q low.q \
    -l infiniband \
    $DIR/IDSort/data_I21/scripts/mpi_job.sh \
    --iterations 300 \
    -l $DIR/IDSort/data_I21/I21lookup_a.h5 \
    -i $DIR/IDSort/data_I21/I21.json \
    -m $DIR/IDSort/data_I21/I21magnets.mag \
    -s 24 \
    -r \
    --param_c 1 \
    /dls/tmp/xrp26957/I21logs
