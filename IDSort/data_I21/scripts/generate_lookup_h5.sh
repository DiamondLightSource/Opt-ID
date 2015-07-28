# Get git root directory
DIR=$(git rev-parse --show-toplevel)

# Output .h5 file must be generated in eihter /tmp or /scratch
# Output size is 2-3 GB hence this exceeds user disk quota
python $DIR/IDSort/src/v2/lookup_generator.py \
    -p 91 \
    -r \
    $DIR/IDSort/data_I21/I21.json \
    /scratch/I21lookup_a.h5

rm I21lookup_a.h5 &> /dev/null
ln -s /scratch/I21lookup_a.h5 $DIR/IDSort/data_I21/I21lookup_a.h5
