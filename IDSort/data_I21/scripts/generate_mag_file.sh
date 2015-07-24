# Get git root directory
DIR=$(git rev-parse --show-toplevel)

# I21 sims directory
SIMS=$DIR/IDSort/data_I21/sims

python $DIR/IDSort/src/v2/magnets.py \
    -H $SIMS/I21H.sim \
    --HE $SIMS/I21HE.sim \
    -V $SIMS/I21V.sim \
    --VE $SIMS/I21VE.sim \
    $DIR/IDSort/data_I21/I21magnets.mag

