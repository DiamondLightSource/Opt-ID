#!/bin/bash
module load {{ python_env_module }}
module load texlive/2015

export PYTHONPATH="/home/twi18192/wc/Opt-ID"

python -m IDSort.src.optid --generate-report {{ yaml_config }} {{ data_dir }} $@

jupyter-nbconvert --execute --no-input --to pdf {{ notebook_path }}
