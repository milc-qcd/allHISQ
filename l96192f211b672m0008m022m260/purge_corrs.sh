#! /bin/bash

# Remove any prior stray corrs

# Usage ./purge_corrs.sh <LATS> [ <NCASES> ]

LATS=$1
NCASES=$2

if [ -z "${NCASES}" ]
then
  NCASES=1
fi

cfgs_milc=( `echo ${LATS} | sed 's|/| |g'` )
for((i=0; i<${NCASES}; i++)); do
  cfg_fnal=`echo ${cfgs_milc[$i]} | awk -F. '{printf("%s%06d",$1,$2)}'`
  echo "Purging corrs for ${cfg_fnal}"
  find run*/data -name '*'${cfg_fnal} -exec /bin/rm '{}' \;
done
