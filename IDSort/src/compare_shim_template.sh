#!/bin/bash
module load {{ python_env_module }}

export PYTHONPATH=$PYTHONPATH:{{ project_root_dir }}

first_arg=$1
if [[ $first_arg == --* ]]
then
    # assume the --diff-filename flag has been passed, so then grab the flag as
    # the first param, and the diff filename as the second param
    shift
    second_arg=$1
    shift
    third_arg=$1
    # pass the third param as the shimmed genome file to compare to the
    # original genome
    python -m IDSort.src.optid --compare-shim $first_arg $second_arg {{ yaml_config }} {{ data_dir }} $third_arg
else
    # assume that the --diff-filename flag hasn't been passed (ie, use the
    # default filename) and that the only passed param is the shimmed genome to
    # compare to the original genome
    python -m IDSort.src.optid --compare-shim {{ yaml_config }} {{ data_dir }} $first_arg
fi
