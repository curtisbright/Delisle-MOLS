#!/bin/bash

mkdir -p log

solver="./cadical-nets/build/cadical-nets"

while getopts "gvS:" opt
do
	case $opt in
		g) g="-g" ;;
		v) v="-v" ;;
		S) seed=$OPTARG ;;
	esac
done
shift $((OPTIND-1))

if [ -z $1 ]
then
	echo "Provide the case number (an integer 1 to 5)"
	echo "Usage: $0 [-gv] [-S seed] case"
	echo "Use -g to check the solutions for equivalence using nauty"
	echo "Use -v to generate and check enumeration certificates"
	echo "Use -S to set the seed provided to the solver (otherwise a random seed is used)"
	exit
fi

./compile-tools.sh $v

case=$1
if [ -z $seed ]
then
	seed=$(shuf -i 0-999999999 -n 1)
fi
logname=$case-$seed
relations=$(sed "${case}q;d" relations.txt)

if [ ! -z $v ]
then
	mkdir -p proofs
	pfname=proofs/$logname.drat
fi

python3 encode.py $relations | $solver /dev/stdin $pfname --seed=$seed | tee log/$logname.log
grep "New solution" log/$logname.log | ./verify.py $relations
if [ "$g" == "-g" ]
then
	grep "New solution" log/$logname.log | ./equivalence-check.py
fi

if [ ! -z $v ]
then
	python3 encode.py $relations | ./drat-trim-t/drat-trim-t /dev/stdin $pfname | tee proofs/$logname.log
fi
