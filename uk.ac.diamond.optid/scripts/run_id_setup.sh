#!/bin/bash

if [ "$#" -eq 23 ]; then
	python ${1} \
	    -p ${2} \
	    --fullmagdims ${3} ${4} ${5} \
	    --vemagdims ${6} ${7} ${8} \
	    --hemagdims ${9} ${10} ${11} \
	    -i ${12} \
	    -g ${13} \
	    -t "${14}" \
	    -n "${15}" \
	    -x ${16} ${17} ${18} \
	    -z ${19} ${20} ${21} \
	    -s ${22} \
	    ${23}
elif [ "$#" -eq 26 ]; then
	python ${1} \
	    -p ${2} \
	    --fullmagdims ${3} ${4} ${5} \
	    --vemagdims ${6} ${7} ${8} \
	    --hemagdims ${9} ${10} ${11} \
	    -i ${12} \
	    -g ${13} \
	    -t "${14}" \
	    -n "${15}" \
	    -x ${16} ${17} ${18} \
	    -z ${19} ${20} ${21} \
	    -s ${22} \
	    --endgapsym ${23} \
	    --phasinggap ${24} \
	    --clampcut ${25} \
	    ${26}
else
	echo "Illegal number of arguments"
fi
