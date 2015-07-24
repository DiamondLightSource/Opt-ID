# Get git root directory
DIR=$(git rev-parse --show-toplevel)

python $DIR/IDSort/src/v2/id_setup.py \
    -p 91 \
    --fullmagdims 33. 33. 13.95 \
    --vemagdims 33. 33. 6.95 \
    --hemagdims 33. 33. 6.95 \
    -i 0.05 \
    -g 20.0 \
    -t "APPLE_Symmetric" \
    -n "I21" \
    -x -5.0 5.1 2.5 \
    -z -5.0 5.1 5.0 \
    -s 5 \
    --endgapsym 5.0 \
    --phasinggap 0.5 \
    --clampcut 6.0 \
    $DIR/IDSort/data_I21/I21.json
