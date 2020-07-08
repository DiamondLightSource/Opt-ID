module load {{ python_env_module }}
export PYTHONPATH=$PYTHONPATH:{{ project_root_dir }}

{% if use_cluster %}
python -m IDSort.src.optid --restart-sort --cluster-on --node-os {{ node_os }} --num-threads {{ number_of_threads }} --queue {{ queue }} {{ config_path }} {{ output_dir_path }}
{% else %}
    {% if seed %}
python -m IDSort.src.optid --restart-sort --cluster-off --seed --seed-value {{ seed_value }} {{ config_path }} {{ output_dir_path }}
    {% else %}
python -m IDSort.src.optid --restart-sort --cluster-off {{ config_path }} {{ output_dir_path }}
    {% endif %}
{% endif %}
