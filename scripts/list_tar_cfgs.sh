#! /bin/bash

for d in run2?
do
    echo $d
    ls -1 $d/tar/Job* | awk -F_ '{print $2}' | awk -F. '{print $1}' | sort | uniq -c > $d/tar/foo
done

wc -l run2?/tar/foo

