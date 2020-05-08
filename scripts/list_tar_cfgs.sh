#! /bin/bash

for d in run*
do
    echo $d
    ls -1 $d/Job* | awk -F_ '{print $2}' | awk -F. '{print $1}' | sort | uniq -c > $d/foo
done

