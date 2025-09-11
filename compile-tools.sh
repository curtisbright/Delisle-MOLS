#!/bin/bash

# Pass -v to build DRAT-trim-t
while getopts "v" opt
do
	case $opt in
		v) v="-v" ;;
	esac
done
shift $((OPTIND-1))

# Compile custom version of CaDiCaL searching for 4-Nets(10)s
if [ ! -d cadical-nets ]
then
    git clone git@github.com:curtisbright/cadical-nets.git
fi
if [ -d cadical-nets ] && [ ! -f cadical-nets/build/cadical-nets ]
then
    cd cadical-nets
    if [ ! -f makefile ]
    then
        ./configure
    fi
    make -j
    cd "$OLDPWD"
fi

# Compile DRAT-trim-t
if [ ! -z $v ] && [ ! -d drat-trim-t ]
then
    git clone git@github.com:curtisbright/drat-trim-t.git
fi
if [ ! -z $v ] && [ -d drat-trim-t ] && [ ! -f drat-trim-t/drat-trim-t ]
then
    cd drat-trim-t
    make drat-trim-t
    cd "$OLDPWD"
fi
