#! /bin/bash

for d in run3?
do
    echo $d
    ls -1 $d/tar/Job* | awk -F_ '{print $2}' | awk -F. '{print $1}' | sort | uniq -c > $d/tar/foo
done

wc -l run3?/tar/foo

