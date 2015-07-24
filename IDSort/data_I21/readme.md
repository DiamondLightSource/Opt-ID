## Opt-ID Terminal Commands

Get root directory of git repository and store in the shell variable `DIR`. Current directory must be within git repository before executing the following command.

`export DIR=$(git rev-parse --show-toplevel)`

##### 1: Create ID Description (Output: .json)

`python $DIR/IDSort/src/v2/id_setup.py -p 91 --fullmagdims 33. 33. 13.95 --vemagdims 33. 33. 6.95 --hemagdims 33. 33. 6.95 -i 0.05 -g 20.0 -t "APPLE_Symmetric" -n "I21" -x -5.0 5.1 2.5 -z -5.0 5.1 5.0 -s 5 --endgapsym 5.0 --phasinggap 0.5 --clampcut 6.0 $DIR/IDSort/data_I21/I21.json`

##### 2: Create magnet file (Output: .mag)

`export SIMS=$DIR/IDSort/data_I21/sims`

`python $DIR/IDSort/src/v2/magnets.py -H $SIMS/I21H.sim --HE $SIMS/I21HE.sim -V $SIMS/I21V.sim --VE $SIMS/I21VE.sim $DIR/IDSort/data_I21/I21magnets.mag`

##### 3: Lookup generator (Output: .h5)

Output `I21lookup_a.h5` must be generated in either `/tmp` or `/scratch` since output size is 2-3 GB which exceeds user disk quota

`python $DIR/IDSort/src/v2/lookup_generator.py -p 91 -r $DIR/IDSort/data_I21/I21.json /scratch/I21lookup_a.h5`

