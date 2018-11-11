#! /bin/bash

# Clean up props and rands

# Usage ./purge_props.sh <LATS> <NCASES>

LATS=$1
NCASES=$2

if [ -z "${NCASES}" ]
then
  NCASES=1
fi

cfgs_milc=( `echo ${LATS} | sed 's|/| |g'` )
for((i=0; i<${NCASES}; i++)); do
  cfg_fnal=`echo ${cfgs_milc[$i]} | awk -F. '{printf("%s%06d",$1,$2)}'`
  echo "Purging props and rands for ${cfg_fnal}"
  find prop/ -name '*.'${cfg_fnal}'.*' -exec /bin/rm '{}' \;
  find rand/ -name '*.'${cfg_fnal}'.*' -exec /bin/rm '{}' \;
done
