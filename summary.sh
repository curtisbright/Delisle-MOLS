#!/bin/bash

# Script to summarize the results of the logs (requires the program datamash)

stats=(count mean median min max)

printf "case"

for stat in ${stats[@]}
do
    printf "%11s" $stat
done

printf "\n"

for case in $(seq 1 5)
do
    if ! grep -q "c total process time" log/$case-*.log 2>/dev/null
    then
        continue
    fi
    printf "%4d" $case
    times=$(grep "c total process time" log/$case-*.log | tr -s ' ' | cut -d' ' -f7)

    for stat in ${stats[@]}
    do
        t=$(datamash $stat 1 <<< $times)
        if [ $stat != "count" ]
        then
            t=$(printf "%.1f" "$t")
        fi
        printf "%11s" "$t"
    done

    printf "\n"
done
