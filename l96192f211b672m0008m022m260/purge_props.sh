#! /bin/bash

# Clean up props and rands on Lustre storage

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
  lfs find prop/${cfg_fnal} -t f | awk '{print "/usr/bin/rm",$1}' | /bin/bash
  lfs find rand/${cfg_fnal} -t f | awk '{print "/usr/bin/rm",$1}' | /bin/bash
done


