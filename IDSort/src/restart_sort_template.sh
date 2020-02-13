module load {{ python_env_module }}
export PYTHONPATH="/home/twi18192/wc/Opt-ID"

python -m IDSort.src.optid --restart-sort {{ config_path }} {{ output_dir_path }}
