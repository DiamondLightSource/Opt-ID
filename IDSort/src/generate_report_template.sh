#!/bin/bash
module load {{ python_env_module }}
module load texlive/2015

export PYTHONPATH="/home/twi18192/wc/Opt-ID"

first_arg=$1
if [[ $first_arg == --* ]]
then
    # assume the --report-filename flag has been passed, so then grab the flag
    # as the first param, and the PDF filename as the second param
    shift
    second_arg=$1
    shift
    if [[ $second_arg != *.pdf ]]
    then
        echo "The --report-filename flag has been passed but the chosen filename does not have a .pdf extension, has the report filename been missed? Please provide a .pdf filename for the report. Exiting..."
        exit 1
    else
        # pass the rest of the params as the genome/inp files at the end of the
        # command
        python -m IDSort.src.optid --generate-report $first_arg $second_arg {{ yaml_config }} {{ data_dir }} $@
    fi
else
    # assume that the --report-filename flag hasn't been passed (ie, use the
    # default filename)
    python -m IDSort.src.optid --generate-report {{ yaml_config }} {{ data_dir }} $@
fi
