#! /bin/bash

# Purge all props from failed jobs

# Find entries for each job in the todo file
lines=`grep XXfix todo`
echo "${lines}" | while read -r line
do
    echo "================================================================================"
    echo $line
    echo "================================================================================"
    # Format is d.768 F.72 XXfix 7013605 25470
    set $line
    sc=$1
    ts=$2

    ./purge_all_props.sh ${sc} ${ts}
    sleep 5
done
