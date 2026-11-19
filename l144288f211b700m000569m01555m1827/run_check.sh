#! /bin/bash

ncheck=$1

if [ -z "${ncheck}" ]
then
    echo "Usage $0 <ncheck>"
fi

for((k=0; k<${ncheck}; k++)); do
#for k in 16 17 18 19 20 21
nohup ../scripts/check_completed.py 2>&1 > check${k}.log &
sleep 30
done

